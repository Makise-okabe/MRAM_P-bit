#!/usr/bin/env python3
"""Viewed-source historical parity and engineering timing; no fresh outcomes."""
from __future__ import annotations

import json
from pathlib import Path
import platform
import time
import unittest

import numpy as np

from experiments.biqmac_maxcut import load_rudy
from experiments.fyp_ideal_solver import representation, solve_logged
from experiments.fyp_tail_probe import (
    ARMS, CONTROLS, ROOT, UPDATES, build_arms, digest, json_bytes, legacy_fields,
    save_new, solve_buffered,
)
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph


OUT = ROOT/"results/fyp_tail_preflight_20261121"


def main():
    if (OUT/"preflight.json").exists():
        raise FileExistsError("preflight already executed; no implicit repeat")
    suite = unittest.defaultTestLoader.discover(str(ROOT/"tests"), pattern="test_fyp_tail_probe.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError("meaningful unit checks failed")
    old_freeze = json.loads((ROOT/"docs/FYP_IDEAL_FREEZE_20261120.json").read_text())
    baseline = {}
    for p in (ROOT/"experiments").glob("*.py"):
        relative = p.relative_to(ROOT).as_posix()
        if relative in old_freeze["source_sha256"]:
            if digest(p) != old_freeze["source_sha256"][relative]:
                raise AssertionError("pinned baseline changed: "+relative)
            baseline[relative] = digest(p)
    plan_path = ROOT/"results/fyp_ideal_preflight_20261120/archived_parity_plan.json"
    plan = json.loads(plan_path.read_text())
    controls = [c for c in plan["controls"] if c["representation"] in CONTROLS]
    graphs, reps, checks = {}, {}, []
    for c in controls:
        if digest(ROOT/c["archive"]) != c["archive_sha256"]:
            raise ValueError("historical archive digest mismatch: "+c["archive"])
        name, arm = c["graph"], c["representation"]
        if name not in graphs:
            p = ROOT/"data/biqmac/raw/ising"/name
            if digest(p) != c["graph_sha256"]:
                raise ValueError("historical source digest mismatch")
            graphs[name] = load_rudy(p)
        graph = graphs[name]
        if (name, arm) not in reps:
            reps[name, arm] = representation(graph, arm)
        rep = reps[name, arm]
        beta = beta_from_original_graph(graph)
        new = solve_buffered(graph, rep, beta, UPDATES, c["seed"])
        for field, expected in c["expected"].items():
            if (new[field] != str(expected) if field == "returned_state_hex" else new[field] != float(expected)):
                raise AssertionError(f"archived parity mismatch: {name}/{arm}/{field}")
        old = solve_logged(graph, rep, beta, UPDATES, c["seed"])
        if legacy_fields(new) != old:
            raise AssertionError("full trajectory metadata parity mismatch")
        checks.append({"source": c["source"], "graph": name, "representation": arm,
                       "seed": c["seed"], "archive_sha256": c["archive_sha256"],
                       "all_archived_fields": "EXACT", "full_legacy_output": "EXACT"})
    timings = []
    for name, seed in (("ising2.5-100_7777", 20661201), ("t2g10_5555", 20261112)):
        graph = graphs[name]
        beta = beta_from_original_graph(graph)
        prepared = build_arms(graph)
        for arm in ARMS:
            start = time.monotonic()
            solve_buffered(graph, prepared[arm], beta, UPDATES, seed, source_rep=prepared["ref64"])
            timings.append({"viewed_graph": name, "arm": arm, "seconds": time.monotonic()-start})
    evidence = {"status": "PASS", "unit_test_methods": result.testsRun,
                "archived_controls": len(checks), "checks": checks, "timings": timings,
                "python": platform.python_version(), "numpy": np.__version__,
                "baseline_sources_sha256": baseline, "parity_plan_sha256": digest(plan_path),
                "fresh_graph_solver_runs": 0, "timing_runs": len(timings),
                "scope": "viewed historical controls and synthetic checks only"}
    save_new(OUT/"preflight.json", json_bytes(evidence))
    print(json.dumps({"status": "PASS", "test_methods": result.testsRun,
                      "archived_controls": len(checks), "timings": timings}, indent=2))


if __name__ == "__main__":
    main()
