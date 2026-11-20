#!/usr/bin/env python3
"""Build a source-only executable freeze after preflight, before outcomes."""
from pathlib import Path
import json
import platform

import numpy as np

from experiments.fyp_tail_analysis import registry
from experiments.fyp_tail_probe import (
    ARMS, BASE_COMMIT, FREEZE, GRAPHS, K, ROOT, SEEDS, SOURCE_DIR, UPDATES,
    RESULT_DIR, digest, json_bytes, save_new, solver_seed,
)


def assemble():
    if FREEZE.exists() or RESULT_DIR.exists():
        raise ValueError("freeze or outcomes already exist")
    preflight = ROOT/"results/fyp_tail_preflight_20261121/preflight.json"
    proof = json.loads(preflight.read_text())
    if proof["status"] != "PASS" or proof["archived_controls"] != 21 or proof["fresh_graph_solver_runs"] != 0:
        raise ValueError("required preflight evidence missing")
    sources = json.loads((SOURCE_DIR/"source_manifest.json").read_text())
    if len(sources["graphs"]) != 48:
        raise ValueError("exactly 48 sources required")
    for g in sources["graphs"]:
        if digest(ROOT/g["file"]) != g["sha256"]:
            raise ValueError("source hash mismatch")
    analysis_path = ROOT/"docs/FYP_TAIL_ANALYSIS_REGISTRY_20261121.json"
    save_new(analysis_path, json_bytes(registry()))
    seed_path = SOURCE_DIR/"seed_manifest.json"
    save_new(seed_path, json_bytes({"graphs": [
        {"family": f, "index": g, "graph_entropy": [20261121, 910, f, g],
         "paired_solver_seeds": [solver_seed(f, g, r) for r in range(SEEDS)]}
        for f in (0, 1) for g in range(GRAPHS)]}))
    files = set((ROOT/"experiments").glob("*.py"))
    files.add(ROOT/"tests/test_fyp_tail_probe.py")
    files.update(SOURCE_DIR.rglob("*.rudy"))
    files.update((SOURCE_DIR/"source_manifest.json", seed_path, analysis_path, preflight,
                  ROOT/"docs/FYP_WEAK_TAIL_PROTOCOL_20261121.md",
                  ROOT/"docs/FYP_STUDY_LOCK_20261120.md",
                  ROOT/"docs/FYP_IDEAL_FREEZE_20261120.json",
                  ROOT/"results/fyp_ideal_preflight_20261120/archived_parity_plan.json"))
    file_hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(files)}
    frozen = {"schema": "fyp-weak-tail-freeze-v1", "date": "2026-11-21",
              "status": "FROZEN_BEFORE_FRESH_SOLVER_OUTCOMES", "base_commit": BASE_COMMIT,
              "parameters": {"arms": list(ARMS), "graphs_per_family": GRAPHS,
                             "paired_seeds": SEEDS, "updates": UPDATES, "buffer_capacity": K,
                             "gain": 1, "offset": 0, "expected_runs": 18432},
              "analysis": registry(), "file_sha256": file_hashes,
              "runtime": {"python": platform.python_version(), "numpy": np.__version__},
              "publication_requirement": "publish this file and all new sources before execution; verify remote bytes and record full commit SHA",
              "checkpoint": "STOP after mechanism analysis; no device or hardware work"}
    save_new(FREEZE, json_bytes(frozen))
    print(json.dumps({"freeze": str(FREEZE.relative_to(ROOT)), "sha256": digest(FREEZE),
                      "files": len(file_hashes), "expected_runs": 18432}, sort_keys=True))


if __name__ == "__main__":
    assemble()
