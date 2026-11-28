#!/usr/bin/env python3
"""Read-only final integrity verification; no solver or quality statistics.

Run only after the coordinator confirms that all 150 bundles are complete.
The first operations are the committed freeze gate and frozen verify_all.
This operational audit does not amend any frozen source or scientific registry.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from experiments.fyp_first_block_20261120 import CHECKPOINTS, digest
from experiments.fyp_ideal_campaign import (
    FIRST_BLOCK, sealed_rows, verify_all, verify_freeze,
)
from experiments.fyp_ideal_sources import ANCHORS, CANDIDATES, FAMILIES


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer_cut(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and int(value) == value)


def write_new(path, report):
    if path.exists():
        raise FileExistsError("verification.json already exists; audit evidence must not be overwritten")
    path.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False)+"\n")


def verify_checkpoint(base, freeze, freeze_commit, graph_dir, source_provenance):
    # Keep these as the first substantive operations, before any campaign row is read.
    gate = verify_freeze(freeze, freeze_commit)
    frozen_verification = verify_all(base, gate)

    source_provenance = Path(source_provenance)
    provenance = json.loads(source_provenance.read_text())
    require(provenance["frozen_commit"] == freeze_commit, "official-source provenance freeze mismatch")
    require(provenance["status"] == "POST_FREEZE_OFFICIAL_SOURCES_HASHED", "official-source provenance is incomplete")
    officials = {r["graph"]: r for r in provenance["graphs"]}
    require(len(provenance["graphs"]) == 6 and set(officials) == {a["name"] for a in ANCHORS},
            "official-source provenance must identify exactly six unique anchors")
    official_hashes = {}
    for anchor in ANCHORS:
        name, row = anchor["name"], officials[anchor["name"]]
        path = graph_dir/name
        require(digest(path) == row["sha256"], "official original-source hash mismatch")
        require(path.stat().st_size == row["bytes"], "official original-source byte-count mismatch")
        require(row["source_statistics"]["sha256"] == row["sha256"], "official source-statistics hash mismatch")
        official_hashes[name] = row["sha256"]

    first_path = ROOT/FIRST_BLOCK
    first_hash = digest(first_path)
    require(gate["source_sha256"].get(str(FIRST_BLOCK)) == first_hash,
            "first-block archive absent from or differs from freeze")
    original_records = sealed_rows(first_path)
    require(len(original_records) == 1280, "immutable first-block record count mismatch")
    originals = {r["record_sha256"]: r for r in original_records if r["condition"] == "raw"}
    require(len(originals) == 768, "immutable first-block raw-record count mismatch")

    folders = [base/"generated"/FAMILIES[family]/f"{index:03d}"
               for family in FAMILIES for index in range(72)]
    folders += [base/"anchors"/anchor["name"] for anchor in ANCHORS]
    observed_keys, observed_fidelity, reused_hashes = set(), set(), set()
    counts, family_counts, candidate_counts, stage_fidelity = Counter(), Counter(), Counter(), Counter()
    missing_latest = 0
    bundle_hashes = {}
    allowed_reuse_additions = {
        "stage", "family", "family_name", "index", "replicate", "gain", "offset_logit",
        "R_last", "R_last_status", "source_record_sha256", "provenance", "record_sha256",
    }
    for folder in folders:
        manifest = json.loads((folder/"manifest.json").read_text())
        bundle_hashes[folder.relative_to(ROOT).as_posix()+"/manifest.json"] = digest(folder/"manifest.json")
        rows = sealed_rows(folder/"records.jsonl.gz")
        reference_states = {}
        for row in rows:
            key = (row["family"], row["index"], row["stage"], row["representation"], row["seed"])
            require(key not in observed_keys, "duplicate global registered run key")
            observed_keys.add(key)
            require(row["attempted_updates"] == 50000, "nonregistered update budget")
            require(row["gain"] == 1 and row["offset_logit"] == 0, "nonideal response in ideal campaign")
            require(row["condition"] == "raw" and row["schedule"] == "linear", "nonregistered response/schedule condition")
            require(math.isfinite(row["beta_G"]) and row["beta_G"] > 0
                    and row["applied_beta_G"] == row["beta_G"], "source/applied beta mismatch")
            require(row["R"] == row["returned_original_cut"], "returned cut differs from R")
            require(all(integer_cut(row[k]) for k in ("V", "M", "R")), "noninteger/nonfinite original cut")
            require(row["V"] >= row["M"] >= row["R"], "pathwise V/M/R ordering failure")
            require(row["representation"] in CANDIDATES, "unregistered candidate")
            require(row["family_name"] == FAMILIES[row["family"]], "family name/index mismatch")
            require([p["attempt"] for p in row["checkpoints"]] == list(CHECKPOINTS),
                    "unregistered checkpoint attempts/order")
            reused = row["provenance"]["kind"] == "reused_first_block"
            if reused:
                require(row["stage"] == "anchor", "reused record outside anchor stage")
                source_hash = row["source_record_sha256"]
                require(source_hash in originals and source_hash not in reused_hashes,
                        "missing/duplicated immutable original-record provenance")
                original = originals[source_hash]
                for field, value in original.items():
                    if field != "record_sha256":
                        require(field in row and row[field] == value,
                                "reused payload changed an original field")
                require(set(row)-set(original) <= allowed_reuse_additions,
                        "unexpected addition to immutable reused record")
                require(row["provenance"]["archive"] == str(FIRST_BLOCK)
                        and row["provenance"]["archive_sha256"] == first_hash,
                        "reused archive provenance mismatch")
                require(row.get("R_last") is None
                        and row["R_last_status"] == "unavailable_in_immutable_first_block",
                        "first-block R_last was backfilled")
                require(all("R_last" not in point for point in row["checkpoints"]),
                        "first-block checkpoint R_last was backfilled")
                reused_hashes.add(source_hash)
                missing_latest += 1
            else:
                require(row["provenance"]["kind"] == "new_frozen_campaign"
                        and row["provenance"]["freeze_commit"] == freeze_commit,
                        "new-run freeze provenance mismatch")
                require("source_record_sha256" not in row, "new run incorrectly carries reused-record identity")
                require(integer_cut(row.get("R_last")) and row["M"] >= row["R_last"],
                        "new record lacks a valid passive R_last")
                require(all(integer_cut(point.get("R_last")) for point in row["checkpoints"]),
                        "new checkpoint lacks passive R_last")
            counts[row["stage"]] += 1
            family_counts[FAMILIES[row["family"]]] += 1
            candidate_counts[row["representation"]] += 1
            if row["representation"] == "ref64" and row["stage"] in ("main", "anchor"):
                for point in row["checkpoints"]:
                    reference_states[(row["stage"], row["seed"], point["attempt"])] = point
        fidelity_rows = sealed_rows(folder/"fidelity.jsonl.gz")
        require(len(fidelity_rows) == manifest["fidelity_records"], "bundle fidelity count mismatch")
        for row in fidelity_rows:
            key = (row["family"], row["index"], row["stage"], row["representation"], row["seed"], row["attempt"])
            require(key not in observed_fidelity, "duplicate global fidelity key")
            observed_fidelity.add(key)
            require(row["graph"] == manifest["graph"] and row["graph_sha256"] == manifest["graph_sha256"],
                    "fidelity original-source identity mismatch")
            point = reference_states[(row["stage"], row["seed"], row["attempt"])]
            require(row["reference_state_hex"] == point["current_state_hex"]
                    and row["reference_beta"] == point["beta"], "fidelity is not on the registered FP64 state/beta")
            require(all(math.isfinite(row[k]) and row[k] >= 0
                        for k in ("field_rms", "logit_rms", "probability_mae")), "invalid fidelity metric")
            require(row["probability_mae"] <= 1, "probability error outside its mathematical range")
            require(row["logit_rms"] == 2*row["reference_beta"]*row["field_rms"],
                    "field/logit scaling identity mismatch")
            stage_fidelity[row["stage"]] += 1

    require(len(observed_keys) == 88320, "global raw-record count mismatch")
    require(dict(counts) == {"main": 64512, "reference": 18432, "anchor": 5376}, "global stage counts mismatch")
    require(len(observed_fidelity) == 239616, "global fidelity-record count mismatch")
    require(dict(stage_fidelity) == {"main": 221184, "anchor": 18432}, "fidelity stage counts mismatch")
    require(missing_latest == 768 and reused_hashes == set(originals), "R_last missing/reused coverage mismatch")
    require(digest(first_path) == first_hash, "first-block archive changed during verification")
    return {
        "status": "PASS", "scope": "read-only integrity and registered-condition audit; no solver or quality statistics",
        "freeze_commit": freeze_commit, "freeze_manifest_sha256": gate["freeze_manifest_sha256"],
        "frozen_verification": frozen_verification, "raw_records": len(observed_keys),
        "new_records": len(observed_keys)-missing_latest, "reused_records": len(reused_hashes),
        "R_last_missing_exactly_reused": missing_latest, "fidelity_records": len(observed_fidelity),
        "stage_counts": dict(counts), "family_counts": dict(family_counts),
        "candidate_counts": dict(candidate_counts), "fidelity_stage_counts": dict(stage_fidelity),
        "official_source_sha256": official_hashes,
        "post_freeze_source_manifest_sha256": digest(source_provenance),
        "first_block_archive_sha256": first_hash, "freeze_source_sha256": gate["source_sha256"],
        "bundle_manifest_sha256": bundle_hashes, "verification_script_sha256": digest(Path(__file__)),
        "checks": ["frozen gate and frozen verify_all first", "sealed raw/fidelity hashes",
                   "global unique registered keys and exact counts", "ideal response, linear 50000-update solver",
                   "source beta unchanged", "V/M/R and passive latest-tie invariants",
                   "768 original raw records reused exactly once with every original field unchanged",
                   "R_last unavailable exactly on 768 reused records; no checkpoint backfill",
                   "common FP64 states and actual checkpoint beta", "all six official source hashes"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", type=Path, default=ROOT/"docs/FYP_IDEAL_FREEZE_20261120.json")
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--out", type=Path, default=ROOT/"results/fyp_ideal_20261120")
    parser.add_argument("--graph-dir", type=Path, default=ROOT/"data/biqmac/raw/ising")
    parser.add_argument("--source-provenance", type=Path)
    args = parser.parse_args()
    output = args.out/"operational/verification.json"
    if output.exists():
        raise SystemExit("Verification evidence already exists; refusing to overwrite or rerun")
    provenance = args.source_provenance or args.out/"provenance/post_freeze_source_manifest.json"
    try:
        result = verify_checkpoint(args.out, args.freeze, args.freeze_commit, args.graph_dir, provenance)
    except Exception as exc:
        write_new(output, {"status": "STOP_REQUIRED", "exception_type": type(exc).__name__,
                           "error": str(exc), "freeze_commit": args.freeze_commit,
                           "verification_script_sha256": digest(Path(__file__))})
        print(json.dumps({"status": "STOP_REQUIRED"}), flush=True)
        raise SystemExit(1)
    write_new(output, result)
    print(json.dumps({key: result[key] for key in ("status", "raw_records", "new_records",
                                                  "reused_records", "fidelity_records")}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
