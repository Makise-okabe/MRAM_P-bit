#!/usr/bin/env python3
"""Frozen ideal campaign: deterministic graph bundles, immutable first-block reuse.

Every executable path first validates the committed freeze. Partial graph bundles
are never resumed automatically: their seeds may already have been consumed.
Progress output contains counts and engineering timings, not solution quality.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import time

from experiments.biqmac_maxcut import load_rudy
from experiments.fyp_first_block_20261120 import (
    CHECKPOINTS, canonical, digest, projection, seal, state_from_hex,
)
from experiments.fyp_ideal_analysis import fixed_reference_pool
from experiments.fyp_ideal_solver import (
    exact_original_cut, field_fidelity, representation, representation_metrics,
    solve_logged,
)
from experiments.fyp_ideal_sources import (
    ANCHORS, ANCHOR_SEEDS, CANDIDATES, FAMILIES, GRAPHS_PER_FAMILY,
    MAIN_SEEDS, REFERENCE_SEEDS, UPDATES, anchor_seed, graph_name,
    graph_relative_path, require_numpy_version, solver_seed,
)
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph

ROOT = Path(__file__).resolve().parents[1]
FIRST_BLOCK = Path("results/fyp_first_block_20261120/records.jsonl")
BUNDLE_FILES = ("records.jsonl.gz", "fidelity.jsonl.gz", "representation_metrics.json")
REQUIRED_FREEZE_SOURCES = (
    "experiments/fyp_ideal_campaign.py", "experiments/fyp_ideal_solver.py",
    "experiments/fyp_ideal_analysis.py", "experiments/fyp_ideal_sources.py",
    "docs/FYP_STUDY_LOCK_20261120.md",
)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n")


def sealed_rows(path):
    """Require a valid canonical payload hash on every archived/new record."""
    opener = gzip.open if path.suffix == ".gz" else open
    rows = []
    with opener(path, "rt", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            row = json.loads(line)
            tag = row.get("record_sha256")
            payload = {k: v for k, v in row.items() if k != "record_sha256"}
            if not tag or hashlib.sha256(canonical(payload).encode()).hexdigest() != tag:
                raise ValueError(f"record hash mismatch: {path}:{line_number}")
            rows.append(row)
    return rows


def write_gzip_rows(path, rows, *, fidelity=False):
    keys = ((lambda r: (r["stage"], r["representation"], r["seed"], r["attempt"]))
            if fidelity else (lambda r: (r["stage"], r["representation"], r["seed"])))
    payloads = []
    for row in sorted(rows, key=keys):
        payload = {k: v for k, v in row.items() if k != "record_sha256"}
        payloads.append(canonical(seal(payload)))
    data = ("\n".join(payloads)+"\n").encode()
    path.write_bytes(gzip.compress(data, compresslevel=9, mtime=0))


def verify_freeze(freeze_path, freeze_commit, *, root=ROOT):
    """Check the committed protocol before any solver or heldout graph access."""
    require_numpy_version()
    root = Path(root).resolve()
    path = Path(freeze_path)
    path = (root/path).resolve() if not path.is_absolute() else path.resolve()
    relative = path.relative_to(root).as_posix()
    if not re.fullmatch(r"[0-9a-f]{40}", freeze_commit):
        raise ValueError("freeze commit must be a full lowercase 40-character SHA")
    subprocess.run(["git", "merge-base", "--is-ancestor", freeze_commit, "HEAD"],
                   cwd=root, check=True, capture_output=True)
    committed = subprocess.check_output(["git", "show", f"{freeze_commit}:{relative}"], cwd=root)
    if path.read_bytes() != committed:
        raise ValueError("freeze JSON differs from committed freeze")
    frozen = json.loads(committed)
    hashes = frozen["source_sha256"]
    if not set(REQUIRED_FREEZE_SOURCES).issubset(hashes):
        raise ValueError("freeze omits required implementation/lock sources")
    for name, expected in sorted(hashes.items()):
        source = (root/name).resolve()
        source.relative_to(root)
        if digest(source) != expected:
            raise ValueError(f"frozen source hash mismatch: {name}")
    source_manifest = frozen["source_manifest_path"]
    if hashes.get(source_manifest) != frozen["source_manifest_sha256"]:
        raise ValueError("generated source-manifest hash not included in freeze")
    if digest(root/source_manifest) != frozen["source_manifest_sha256"]:
        raise ValueError("generated source-manifest hash mismatch")
    return {"freeze_commit": freeze_commit, "freeze_manifest": relative,
            "freeze_manifest_sha256": hashlib.sha256(committed).hexdigest(),
            "source_manifest_sha256": frozen["source_manifest_sha256"],
            "source_sha256": hashes}


def expected_keys(kind, family, index):
    if kind == "generated":
        main = {("main", f, solver_seed("main", family, index, r))
                for f in CANDIDATES for r in range(MAIN_SEEDS)}
        refs = {("reference", "ref64", solver_seed("reference", family, index, r))
                for r in range(REFERENCE_SEEDS)}
        return main | refs
    if kind == "anchor":
        return {("anchor", f, anchor_seed(index, r))
                for f in CANDIDATES for r in range(ANCHOR_SEEDS)}
    raise ValueError("unknown bundle kind")


def validate_record_keys(rows, kind, family, index):
    keys = [(r["stage"], r["representation"], int(r["seed"])) for r in rows]
    if len(set(keys)) != len(keys) or set(keys) != expected_keys(kind, family, index):
        raise ValueError("duplicate, missing, unexpected or unpaired registered run key")
    if any(r["family"] != family or r["index"] != index for r in rows):
        raise ValueError("record family/index mismatch")
    return {stage: sum(r["stage"] == stage for r in rows) for stage in sorted({r["stage"] for r in rows})}


def archived_raw_rows(path=FIRST_BLOCK):
    """Return immutable raw payloads and original hashes, never rerun/backfill."""
    all_rows = sealed_rows(path)
    if len(all_rows) != 1280:
        raise ValueError("closed first block must contain exactly 1280 records")
    selected = {}
    for row in all_rows:
        if row["condition"] != "raw":
            continue
        key = (row["graph"], row["representation"], int(row["seed"]))
        if key in selected:
            raise ValueError("duplicate first-block raw row")
        if row["representation"] not in ("ref64", "fp5", "int6"):
            raise ValueError("unexpected first-block raw representation")
        selected[key] = row
    if len(selected) != 768:
        raise ValueError("closed first block must contain exactly 768 raw records")
    return selected


def reused_record(row, *, family, index, replicate, archive_sha256):
    if row["condition"] != "raw" or row["representation"] not in ("ref64", "fp5", "int6"):
        raise ValueError("only registered raw first-block observations may be reused")
    original = {k: v for k, v in row.items() if k != "record_sha256"}
    result = dict(original)
    result.update(stage="anchor", family=family, family_name=FAMILIES[family],
                  index=index, replicate=replicate, gain=1.0, offset_logit=0.0,
                  R_last=None, R_last_status="unavailable_in_immutable_first_block",
                  source_record_sha256=row["record_sha256"],
                  provenance={"kind": "reused_first_block", "archive": str(FIRST_BLOCK),
                              "archive_sha256": archive_sha256})
    return result


def source_metrics(graph, reps):
    result = {}
    for fmt, rep in reps.items():
        item = {k: v for k, v in rep.items() if k not in ("edges", "adjacency")}
        item.update(representation_metrics(graph, rep))
        item["zeroed_weight_mass_fraction"] = item["zeroed_abs_weight_mass_fraction"]
        item["nonzero_count"] = item["retained_nonzero_edges"]
        result[fmt] = item
    return {"graph_sha256": graph.sha256, "representations": result}


def reference_pool(graph, rows, kind):
    rescore = lambda value: exact_original_cut(graph, state_from_hex(value, graph.n))
    if kind == "generated":
        return fixed_reference_pool([r for r in rows if r["stage"] == "main"],
                                    [r for r in rows if r["stage"] == "reference"],
                                    verify_cut=rescore)
    pool = {"B_g": 0, "value_field": "V", "witness_state_hex": "0",
            "witness_representation": "empty_cut", "witness_seed": None,
            "witness_stage": "empty_cut", "pool_anchor_count": len(rows)}
    for row in sorted(rows, key=lambda r: (r["representation"], r["seed"])):
        value = row["V"]
        if value != int(value):
            raise ValueError("noninteger reference-pool cut")
        if value > pool["B_g"]:
            pool.update(B_g=int(value), witness_state_hex=row["V_state_hex"],
                        witness_representation=row["representation"],
                        witness_seed=row["seed"], witness_stage="anchor")
    if rescore(pool["witness_state_hex"]) != pool["B_g"]:
        raise ValueError("anchor reference witness does not rescore exactly")
    pool.update(rescore_verified=True, reference_label="descriptive anchor trajectory maximum, not denominator")
    return pool


def verify_bundle(folder, gate, *, graph=None):
    """Validate completed bytes, registered keys, fidelity, and feasible B witness."""
    folder = Path(folder)
    if (folder/"IN_PROGRESS.json").exists() or (folder/"FAILED.json").exists() or not (folder/"manifest.json").exists():
        raise RuntimeError(f"partial bundle: stop, do not rerun consumed seeds: {folder}")
    manifest = json.loads((folder/"manifest.json").read_text())
    if manifest["status"] != "COMPLETE" or manifest["freeze_commit"] != gate["freeze_commit"]:
        raise ValueError("bundle freeze/status mismatch")
    if manifest["freeze_manifest_sha256"] != gate["freeze_manifest_sha256"]:
        raise ValueError("bundle freeze-manifest mismatch")
    if set(manifest["file_sha256"]) != set(BUNDLE_FILES):
        raise ValueError("bundle file registry mismatch")
    for name, expected in manifest["file_sha256"].items():
        if digest(folder/name) != expected:
            raise ValueError(f"bundle hash mismatch: {folder/name}")
    rows, fidelity = sealed_rows(folder/"records.jsonl.gz"), sealed_rows(folder/"fidelity.jsonl.gz")
    kind, family, index = manifest["kind"], manifest["family"], manifest["index"]
    counts = validate_record_keys(rows, kind, family, index)
    if counts != manifest["stage_counts"]:
        raise ValueError("bundle stage counts mismatch")
    main_stage = "main" if kind == "generated" else "anchor"
    main = [r for r in rows if r["stage"] == main_stage]
    expected_fidelity = {(main_stage, f, r["seed"], t) for r in main if r["representation"] == "ref64"
                         for f in CANDIDATES if f != "ref64" for t in CHECKPOINTS}
    actual_fidelity = [(r["stage"], r["representation"], r["seed"], r["attempt"]) for r in fidelity]
    if len(actual_fidelity) != len(set(actual_fidelity)) or set(actual_fidelity) != expected_fidelity:
        raise ValueError("missing/duplicate/unregistered fidelity observation")
    if any(r["graph"] != manifest["graph"] or r["graph_sha256"] != manifest["graph_sha256"] for r in rows):
        raise ValueError("row/source identity mismatch")
    if graph is None:
        graph = load_rudy(ROOT/manifest["source_path"])
    if graph.sha256 != manifest["graph_sha256"]:
        raise ValueError("bundle original-source hash mismatch")
    pool = reference_pool(graph, rows, kind)
    if pool != manifest["reference_pool"] or pool["B_g"] != manifest["B_g"]:
        raise ValueError("bundle frozen reference-pool mismatch")
    if sum(r.get("provenance", {}).get("kind") == "reused_first_block" for r in rows) != manifest["reused_records"]:
        raise ValueError("reuse count mismatch")
    return manifest


def run_bundle(kind, family, index, *, source_dir, graph_dir, out, gate):
    started = time.perf_counter()
    if kind == "generated":
        name = graph_name(family, index)
        source = source_dir/graph_relative_path(family, index)
        folder = out/"generated"/FAMILIES[family]/f"{index:03d}"
        optimum, stage, seeds = None, "main", MAIN_SEEDS
    else:
        anchor = ANCHORS[index]
        if family != anchor["family"]:
            raise ValueError("anchor family mismatch")
        name, optimum = anchor["name"], anchor["published_optimum"]
        source, folder = graph_dir/name, out/"anchors"/name
        stage, seeds = "anchor", ANCHOR_SEEDS
    if folder.exists():
        manifest = verify_bundle(folder, gate)
        print(f"VERIFIED {kind}/{name}: {sum(manifest['stage_counts'].values())} existing records", flush=True)
        return manifest
    folder.mkdir(parents=True)
    write_json(folder/"IN_PROGRESS.json", {"kind": kind, "graph": name,
               "family": family, "index": index, "freeze_commit": gate["freeze_commit"]})
    try:
        source_relative = source.resolve().relative_to(ROOT).as_posix()
        if kind == "generated" and source_relative not in gate["source_sha256"]:
            raise ValueError("generated graph not in committed freeze")
        if source_relative in gate["source_sha256"] and digest(source) != gate["source_sha256"][source_relative]:
            raise ValueError("original graph differs from committed freeze")
        graph = load_rudy(source)
        if graph.n != 100:
            raise ValueError("locked graph size must be 100")
        reps = {fmt: representation(graph, fmt) for fmt in CANDIDATES}
        beta = beta_from_original_graph(graph)
        projections = {fmt: 1.0 if fmt == "ref64" else projection(graph, rep) for fmt, rep in reps.items()}
        fit_seconds = time.perf_counter()-started
        archived = archived_raw_rows() if kind == "anchor" and index in (0, 2) else {}
        archive_hash = digest(FIRST_BLOCK) if archived else None
        records, reused, new_runs = [], 0, 0
        runs_started = time.perf_counter()
        plan = [(stage, fmt, replicate) for fmt in CANDIDATES for replicate in range(seeds)]
        if kind == "generated":
            plan += [("reference", "ref64", replicate) for replicate in range(REFERENCE_SEEDS)]
        for this_stage, fmt, replicate in plan:
            seed = (anchor_seed(index, replicate) if kind == "anchor" else
                    solver_seed(this_stage, family, index, replicate))
            key = (name, fmt, seed)
            if key in archived:
                row = reused_record(archived[key], family=family, index=index,
                                    replicate=replicate, archive_sha256=archive_hash)
                if row["graph_sha256"] != graph.sha256:
                    raise ValueError("reused original-source identity mismatch")
                checks = {"seed": seed, "representation": fmt, "condition": "raw",
                          "source_scale": reps[fmt]["scale"], "beta_G": beta,
                          "applied_beta_G": beta, "schedule": "linear",
                          "attempted_updates": UPDATES, "official_optimum": optimum}
                if any(row.get(key) != value for key, value in checks.items()):
                    raise ValueError("reused row differs from locked scale/seed/solver/response")
                reused += 1
            else:
                sample = solve_logged(graph, reps[fmt], beta, UPDATES, seed, source_rep=reps["ref64"])
                row = {"graph": name, "graph_sha256": graph.sha256, "family": family,
                       "family_name": FAMILIES[family], "index": index, "stage": this_stage,
                       "replicate": replicate, "representation": fmt, "arm": fmt,
                       "condition": "raw", "gain": 1.0, "offset_logit": 0.0,
                       "source_projection_a": projections[fmt], "source_scale": reps[fmt]["scale"],
                       "beta_G": beta, "applied_beta_G": beta, "schedule": "linear",
                       "provenance": {"kind": "new_frozen_campaign", "freeze_commit": gate["freeze_commit"]},
                       **sample}
                if optimum is not None:
                    row.update(official_optimum=optimum, gap_pct=100*(optimum-row["R"])/optimum)
                new_runs += 1
            if optimum is not None and row["V"] > optimum:
                raise ValueError("published anchor optimum exceeded")
            records.append(row)
        run_seconds = time.perf_counter()-runs_started
        counts = validate_record_keys(records, kind, family, index)
        expected_reuse = 384 if kind == "anchor" and index in (0, 2) else 0
        if reused != expected_reuse:
            raise ValueError("immutable first-block reuse count mismatch")
        pool = reference_pool(graph, records, kind)
        fidelity = []
        fidelity_started = time.perf_counter()
        for row in records:
            if row["stage"] != stage or row["representation"] != "ref64":
                continue
            for point in row["checkpoints"]:
                for fmt in CANDIDATES:
                    if fmt == "ref64":
                        continue
                    fidelity.append({"graph": name, "graph_sha256": graph.sha256,
                                     "family": family, "index": index, "stage": stage,
                                     "seed": row["seed"], "representation": fmt,
                                     "attempt": point["attempt"], "reference_beta": point["beta"],
                                     "reference_state_hex": point["current_state_hex"],
                                     **field_fidelity(graph, point["current_state_hex"], reps[fmt],
                                                      point["beta"], source_rep=reps["ref64"])})
        fidelity_seconds = time.perf_counter()-fidelity_started
        write_gzip_rows(folder/"records.jsonl.gz", records)
        write_gzip_rows(folder/"fidelity.jsonl.gz", fidelity, fidelity=True)
        write_json(folder/"representation_metrics.json", source_metrics(graph, reps))
        manifest = {"status": "COMPLETE", "kind": kind, "graph": name, "family": family,
                    "family_name": FAMILIES[family], "index": index, "source_path": source_relative,
                    "graph_sha256": graph.sha256, "freeze_commit": gate["freeze_commit"],
                    "freeze_manifest_sha256": gate["freeze_manifest_sha256"],
                    "stage_counts": counts, "reused_records": reused, "new_records": new_runs,
                    "fidelity_records": len(fidelity), "reference_pool": pool, "B_g": pool["B_g"],
                    "normalization_denominator": optimum if optimum is not None else pool["B_g"],
                    "denominator_label": "published_original_optimum" if optimum is not None else "frozen_best_observed_B_g_not_optimum",
                    "R_last_missing": reused, "file_sha256": {f: digest(folder/f) for f in BUNDLE_FILES}}
        if optimum is not None:
            manifest["published_optimum"] = optimum
        write_json(folder/"manifest.json", manifest)
        (folder/"IN_PROGRESS.json").unlink()
        verify_bundle(folder, gate, graph=graph)
        timing_dir = out/"timings"
        timing_dir.mkdir(exist_ok=True)
        write_json(timing_dir/f"{kind}-{family}-{index:03d}.json",
                   {"kind": kind, "family": family, "index": index, "new_runs": new_runs,
                    "reused_runs": reused, "prepare_seconds": fit_seconds, "solver_seconds": run_seconds,
                    "fidelity_seconds": fidelity_seconds, "total_seconds": time.perf_counter()-started,
                    "python": platform.python_version(), "scope": "engineering timing only"})
        print(f"COMPLETE {kind}/{name}: {len(records)} records ({reused} reused), {time.perf_counter()-started:.2f} s", flush=True)
        return manifest
    except Exception as exc:
        write_json(folder/"FAILED.json", {"status": "STOP_REQUIRED", "error": str(exc),
                   "exception_type": type(exc).__name__, "freeze_commit": gate["freeze_commit"]})
        raise


def verify_all(out, gate):
    manifests = []
    for family in FAMILIES:
        for index in range(GRAPHS_PER_FAMILY):
            manifests.append(verify_bundle(out/"generated"/FAMILIES[family]/f"{index:03d}", gate))
    for anchor in ANCHORS:
        manifests.append(verify_bundle(out/"anchors"/anchor["name"], gate))
    counts = {stage: sum(m["stage_counts"].get(stage, 0) for m in manifests)
              for stage in ("main", "reference", "anchor")}
    expected = {"main": 144*64*7, "reference": 144*128, "anchor": 6*128*7}
    if counts != expected or sum(m["reused_records"] for m in manifests) != 768:
        raise ValueError("complete campaign registered-count mismatch")
    print("VERIFIED COMPLETE CAMPAIGN: 150 graph bundles; 88320 records; 768 reused", flush=True)
    return {"status": "PASS", "stage_counts": counts, "bundle_count": len(manifests),
            "reused_records": 768, "new_records": sum(m["new_records"] for m in manifests)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--freeze", type=Path, required=True)
    p.add_argument("--freeze-commit", required=True)
    p.add_argument("--source-dir", type=Path, default=Path("data/fyp_locked_20261120"))
    p.add_argument("--graph-dir", type=Path, default=Path("data/biqmac/raw/ising"))
    p.add_argument("--out", type=Path, default=Path("results/fyp_ideal_20261120"))
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--family", type=int, choices=(0, 1))
    mode.add_argument("--anchor-index", type=int, choices=range(6))
    mode.add_argument("--verify-freeze", action="store_true")
    mode.add_argument("--verify-all", action="store_true")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--stop", type=int, default=72)
    args = p.parse_args()
    gate = verify_freeze(args.freeze, args.freeze_commit)
    if args.verify_freeze:
        print("VERIFIED COMMITTED FREEZE: source/code/analysis hashes match", flush=True)
    elif args.verify_all:
        verify_all(args.out, gate)
    elif args.anchor_index is not None:
        run_bundle("anchor", ANCHORS[args.anchor_index]["family"], args.anchor_index,
                   source_dir=args.source_dir, graph_dir=args.graph_dir, out=args.out, gate=gate)
    else:
        if not 0 <= args.start < args.stop <= GRAPHS_PER_FAMILY:
            p.error("generated range must satisfy 0 <= start < stop <= 72")
        for index in range(args.start, args.stop):
            run_bundle("generated", args.family, index, source_dir=args.source_dir,
                       graph_dir=args.graph_dir, out=args.out, gate=gate)


if __name__ == "__main__":
    main()
