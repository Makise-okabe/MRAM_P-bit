#!/usr/bin/env python3
"""Deterministically package the completed locked ideal campaign.

Run only after the campaign's --verify-all gate has passed. Packaging checks
metadata, registered counts and exact bytes; it does not inspect cut quality,
recompute an outcome, run a solver, or change the executable freeze.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
import tempfile


FILES = ("fidelity.jsonl.gz", "manifest.json", "records.jsonl.gz",
         "representation_metrics.json")
PAYLOAD_FILES = set(FILES) - {"manifest.json"}
ANCHORS = (
    "ising2.5-100_5555", "ising2.5-100_6666", "ising2.5-100_7777",
    "t2g10_5555", "t2g10_6666", "t2g10_7777",
)
FAMILIES = ("ring", "torus")
SCHEMA = "fyp-ideal-raw-archives-v1"
DEFAULT_ROOT = Path(__file__).resolve().parents[1]
COUNTS = {
    "bundles": 150,
    "generated_bundles": 144,
    "anchor_bundles": 6,
    "generated_main_records": 64_512,
    "independent_fp64_reference_records": 18_432,
    "official_anchor_records": 5_376,
    "represented_trajectory_records": 88_320,
    "reused_first_block_records": 768,
    "new_solver_trajectories": 87_552,
    "fidelity_records": 239_616,
    "archive_count": 13,
    "archived_files": 600,
}


def canonical(obj):
    return json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n"


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checked_digest(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError(f"invalid SHA256: {label}")
    return value


def bundle_specs():
    specs = []
    for family, name in enumerate(FAMILIES):
        for index in range(72):
            specs.append({
                "path": f"generated/{name}/{index:03d}", "kind": "generated",
                "family": family, "index": index, "graph": f"{name}_{index:03d}",
                "stage_counts": {"main": 448, "reference": 128},
                "reused_records": 0, "new_records": 576, "fidelity_records": 1536,
            })
    for index, name in enumerate(ANCHORS):
        reused = 384 if index in (0, 2) else 0
        specs.append({
            "path": f"anchors/{name}", "kind": "anchor", "family": index // 3,
            "index": index, "graph": name, "stage_counts": {"anchor": 896},
            "reused_records": reused, "new_records": 896-reused,
            "fidelity_records": 3072,
        })
    return specs


def archive_plan():
    """Fixed scheduling partitions; no data-dependent grouping."""
    plan = []
    for family in FAMILIES:
        for start in range(0, 72, 12):
            plan.append({
                "file": f"generated-{family}-{start:03d}-{start+11:03d}.tar.gz",
                "bundles": [f"generated/{family}/{i:03d}" for i in range(start, start+12)],
            })
    plan.append({"file": "official-anchors.tar.gz",
                 "bundles": sorted(f"anchors/{name}" for name in ANCHORS)})
    return plan


def entry_paths(bundles):
    return sorted(f"{bundle}/{name}" for bundle in bundles for name in FILES)


def validate_campaign(root, freeze_commit):
    """Read manifests and hash payloads; never parse trajectory outcomes."""
    root = Path(root).resolve()
    specs = bundle_specs()
    expected_paths = set(entry_paths(spec["path"] for spec in specs))
    markers = sorted(str(p.relative_to(root)) for marker in ("IN_PROGRESS.json", "FAILED.json")
                     for p in root.rglob(marker))
    if markers:
        raise ValueError("incomplete/failed campaign markers: " + ", ".join(markers))
    observed_paths = set()
    for subtree in ("generated", "anchors"):
        directory = root/subtree
        if not directory.is_dir() or directory.is_symlink():
            raise ValueError(f"missing/nonregular campaign subtree: {subtree}")
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise ValueError(f"symlink not permitted in a scientific bundle: {path.relative_to(root)}")
            if path.is_file():
                observed_paths.add(path.relative_to(root).as_posix())
    if observed_paths != expected_paths:
        raise ValueError("campaign bundle file coverage mismatch; missing=" +
                         repr(sorted(expected_paths-observed_paths)) + "; unexpected=" +
                         repr(sorted(observed_paths-expected_paths)))
    entries, metadata = {}, {}
    freeze_hashes = set()
    totals = Counter()
    for spec in specs:
        folder = root/spec["path"]
        manifest = json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
        if manifest.get("status") != "COMPLETE":
            raise ValueError("bundle is not COMPLETE: " + spec["path"])
        for key in ("kind", "family", "index", "graph", "stage_counts", "reused_records",
                    "new_records", "fidelity_records"):
            if manifest.get(key) != spec[key]:
                raise ValueError(f"registered bundle metadata mismatch: {spec['path']} {key}")
        if manifest.get("freeze_commit") != freeze_commit:
            raise ValueError("bundle freeze-commit mismatch: " + spec["path"])
        freeze_hashes.add(checked_digest(manifest.get("freeze_manifest_sha256"), "freeze manifest"))
        expected_hashes = manifest.get("file_sha256", {})
        if set(expected_hashes) != PAYLOAD_FILES:
            raise ValueError("bundle manifest lacks the exact three payload hashes: " + spec["path"])
        for name in FILES:
            path = folder/name
            digest = file_hash(path)
            if name != "manifest.json" and digest != checked_digest(expected_hashes[name], name):
                raise ValueError("bundle payload hash mismatch: " + str(path.relative_to(root)))
            relative = path.relative_to(root).as_posix()
            entries[relative] = {"path": relative, "sha256": digest, "bytes": path.stat().st_size}
        metadata[spec["path"]] = spec
        totals.update(spec["stage_counts"])
        totals["reused"] += spec["reused_records"]
        totals["new"] += spec["new_records"]
        totals["fidelity"] += spec["fidelity_records"]
    if len(freeze_hashes) != 1:
        raise ValueError("bundles refer to different executable freeze manifests")
    expected_totals = {"main": 64_512, "reference": 18_432, "anchor": 5_376,
                       "reused": 768, "new": 87_552, "fidelity": 239_616}
    if dict(totals) != expected_totals:
        raise ValueError("registered campaign count mismatch")
    return entries, metadata, freeze_hashes.pop()


def validate_archive(path, expected_entries):
    """Check exact regular-file membership, canonical tar metadata and bytes."""
    path = Path(path)
    expected = {entry["path"]: entry for entry in expected_entries}
    with path.open("rb") as stream:
        header = stream.read(10)
    if (len(header) != 10 or header[:3] != b"\x1f\x8b\x08" or header[3] != 0
            or header[4:8] != b"\x00\x00\x00\x00"):
        raise ValueError("gzip header must omit filename and have mtime 0: " + path.name)
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        if [m.name for m in members] != sorted(expected):
            raise ValueError("archive member count/order/path mismatch: " + path.name)
        for member in members:
            relative = PurePosixPath(member.name)
            if relative.is_absolute() or ".." in relative.parts or not member.isfile():
                raise ValueError("unsafe/nonregular archive member: " + member.name)
            if (member.uid != 0 or member.gid != 0 or member.mtime != 0 or
                    member.uname != "" or member.gname != "" or member.mode != 0o644):
                raise ValueError("noncanonical tar metadata: " + member.name)
            if member.pax_headers:
                raise ValueError("unexpected PAX metadata: " + member.name)
            if member.size != expected[member.name]["bytes"]:
                raise ValueError("archive member size mismatch: " + member.name)
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("unreadable archive member: " + member.name)
            digest = hashlib.sha256()
            with stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            if digest.hexdigest() != expected[member.name]["sha256"]:
                raise ValueError("archive member SHA256 mismatch: " + member.name)


def write_archive(path, root, entries):
    """Keep an existing valid archive; otherwise publish one atomic archive."""
    if path.exists():
        validate_archive(path, entries)
        return
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", prefix="."+path.name+".",
                                         suffix=".tmp", dir=path.parent, delete=False) as output:
            temp_name = Path(output.name)
            with gzip.GzipFile(filename="", mode="wb", fileobj=output, compresslevel=9, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
                    for entry in entries:
                        info = tarfile.TarInfo(entry["path"])
                        info.size = entry["bytes"]
                        info.uid = info.gid = info.mtime = 0
                        info.uname = info.gname = ""
                        info.mode = 0o644
                        info.type = tarfile.REGTYPE
                        with (root/entry["path"]).open("rb") as source:
                            archive.addfile(info, source)
            output.flush()
            os.fsync(output.fileno())
        validate_archive(temp_name, entries)
        if path.exists():
            raise ValueError("archive appeared concurrently; use one final publisher: " + path.name)
        temp_name.replace(path)
        temp_name = None
    finally:
        if temp_name is not None:
            temp_name.unlink(missing_ok=True)


def stable_text(path, text):
    """Do not overwrite an inconsistent existing final registry or README."""
    payload = text.encode("utf-8")
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError("existing packaging metadata differs: " + path.name)
        return
    with path.open("xb") as stream:
        stream.write(payload)


def verify_registry(archive_dir, freeze_commit):
    registry = json.loads((archive_dir/"archive_registry.json").read_text(encoding="utf-8"))
    if registry.get("schema") != SCHEMA or registry.get("status") != "COMPLETE_VERIFIED_RAW_ARCHIVES":
        raise ValueError("unrecognized or incomplete archive registry")
    if registry.get("frozen_commit") != freeze_commit or registry.get("campaign_counts") != COUNTS:
        raise ValueError("archive registry freeze/count mismatch")
    checked_digest(registry.get("freeze_manifest_sha256"), "freeze manifest")
    plan = archive_plan()
    archives = registry.get("archives", [])
    if [row["file"] for row in archives] != [row["file"] for row in plan]:
        raise ValueError("archive registry differs from the fixed 13-archive plan")
    if {p.name for p in archive_dir.glob("*.tar.gz")} != {row["file"] for row in plan}:
        raise ValueError("unexpected or missing tar.gz archive")
    for record, spec in zip(archives, plan):
        if record["bundles"] != spec["bundles"] or record["bundle_count"] != len(spec["bundles"]):
            raise ValueError("archive bundle-coverage mismatch")
        if [entry["path"] for entry in record["entries"]] != entry_paths(spec["bundles"]):
            raise ValueError("archive registry entry-coverage mismatch")
        path = archive_dir/record["file"]
        if file_hash(path) != checked_digest(record["sha256"], record["file"]):
            raise ValueError("archive file SHA256 mismatch: " + path.name)
        if path.stat().st_size != record["bytes"]:
            raise ValueError("archive file size mismatch: " + path.name)
        validate_archive(path, record["entries"])
    return registry


def readme(freeze_commit):
    return f"""# Verified raw scientific result archives

Executable freeze: `{freeze_commit}`.

This directory contains 12 generated-graph archives (two families, fixed
12-index ranges) and one archive for all six official anchors. Each graph
bundle contains exactly `records.jsonl.gz`, `fidelity.jsonl.gz`,
`representation_metrics.json` and `manifest.json`. Files retain their exact
original bytes and their paths relative to `results/fyp_ideal_20261120`.
Scientific arrays are not regenerated during packaging. Timings, operational
logs, analysis outputs and original graph source files are excluded.

`archive_registry.json` records every archive SHA256/size, each member path,
SHA256/size, and all registered campaign counts. Its 88,320 trajectory records
include 768 immutable first-block records, so 87,552 trajectories are new.
There are 150 graph bundles, 239,616 common-state fidelity rows and 600 archived
files. Per-bundle payload hashes are checked against each COMPLETE bundle
manifest; the registry separately hashes the exact manifest bytes.

The packaging gate requires all 150 registered bundles, exact manifest counts,
one executable freeze and no IN_PROGRESS/FAILED markers. The campaign's full
`--verify-all` gate remains the prerequisite for packaging. Packaging verifies
bytes and metadata, not scientific quality or the statistical conclusions.

## Safe verification and extraction

Use the registry from the trusted result commit. Verify the 13 archive hashes,
all 600 member hashes, sorted exact member names and regular-file types before
extracting. The script's verification-only mode does not require the original
unpacked graph bundles:

```bash
python results/fyp_ideal_20261120/operational/archive.py \\
  --freeze-commit {freeze_commit} --verify-only
```

After successful verification, extract into a fresh directory. The keep-old
option prevents silently replacing existing files:

```bash
mkdir -p recovered_fyp_ideal
for archive in results/fyp_ideal_20261120/raw_archives/*.tar.gz; do
  tar --extract --gzip --file "$archive" --directory recovered_fyp_ideal \\
    --keep-old-files --no-same-owner --no-same-permissions
done
```

The verifier rejects unexpected member paths, directory traversal, links,
duplicate members and extra archives. Archived members have mode 0644,
UID/GID/mtime 0 and empty owner names. USTAR ordering is fixed and gzip omits
an original filename and has mtime 0. Original official `_6666` graph files
and their acquisition provenance are committed separately, not hidden inside
these scientific-result archives.
"""


def create_archives(root, freeze_commit):
    entries, metadata, freeze_hash = validate_campaign(root, freeze_commit)
    out = root/"raw_archives"
    out.mkdir(parents=True, exist_ok=True)
    plan = archive_plan()
    unexpected = {p.name for p in out.glob("*.tar.gz")} - {row["file"] for row in plan}
    if unexpected:
        raise ValueError("unexpected existing archives: " + repr(sorted(unexpected)))
    archived = []
    for spec in plan:
        members = [entries[path] for path in entry_paths(spec["bundles"])]
        path = out/spec["file"]
        write_archive(path, root, members)
        stages = Counter()
        for bundle in spec["bundles"]:
            stages.update(metadata[bundle]["stage_counts"])
        archived.append({
            **spec, "bundle_count": len(spec["bundles"]), "stage_counts": dict(stages),
            "trajectory_records": sum(stages.values()), "sha256": file_hash(path),
            "bytes": path.stat().st_size, "entries": members,
        })
    # Reject any change to source bundle bytes/metadata during packaging.
    final_entries, final_metadata, final_freeze_hash = validate_campaign(root, freeze_commit)
    if (entries, metadata, freeze_hash) != (final_entries, final_metadata, final_freeze_hash):
        raise ValueError("completed campaign changed during packaging")
    registry = {
        "schema": SCHEMA, "status": "COMPLETE_VERIFIED_RAW_ARCHIVES",
        "frozen_commit": freeze_commit, "freeze_manifest_sha256": freeze_hash,
        "campaign_counts": COUNTS, "archives": archived,
        "format": {"tar": "USTAR", "tar_order": "lexicographic result-relative paths",
                   "tar_uid": 0, "tar_gid": 0, "tar_mtime": 0, "tar_mode": "0644",
                   "tar_uname": "", "tar_gname": "", "gzip_mtime": 0,
                   "gzip_filename": "", "gzip_compresslevel": 9},
        "scope": "Exact raw scientific bytes and manifest/count verification; no quality analysis",
        "full_campaign_verification": "Prerequisite: frozen campaign runner --verify-all passed",
        "excluded": ["timings", "operational files", "analysis outputs", "original graph sources"],
    }
    stable_text(out/"archive_registry.json", canonical(registry))
    stable_text(out/"README.md", readme(freeze_commit))
    return verify_registry(out, freeze_commit)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--verify-only", action="store_true",
                        help="verify archived bytes only; original unpacked bundles not required")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.freeze_commit):
        parser.error("--freeze-commit must be a full lowercase 40-character SHA")
    root = args.result_root.resolve()
    registry = (verify_registry(root/"raw_archives", args.freeze_commit) if args.verify_only
                else create_archives(root, args.freeze_commit))
    print(canonical({"status": registry["status"], "campaign_counts": registry["campaign_counts"],
                     "archives": [{k: row[k] for k in ("file", "sha256", "bytes")}
                                  for row in registry["archives"]]}), end="")


if __name__ == "__main__":
    main()
