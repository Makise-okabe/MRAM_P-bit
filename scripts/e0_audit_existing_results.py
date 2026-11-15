#!/usr/bin/env python3
"""Read-only post-run audit for E0-A FP64 CAL pilot.

Reads only the existing E0 result folder and frozen source files.
Does NOT call a solver, load graphs, alter results or generate new samples.
The paired contrasts and time-bin statistics are recomputed from archived CSV.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
from statistics import mean
import math

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "results/e0_fp64_two_cal_20261112"
GRAPHS = ("ising2.5-100_5555", "t2g10_5555")
SCHEDULES = ("linear_legacy", "geometric_uphill")
CHECKPOINTS = (5000, 15000, 30000, 50000)
BINS = tuple(range(5000, 50001, 5000))
BASE = 20261112


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(name):
    with (P / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(x):
    return float(x)


def close(a, b, tol=1e-8):
    if not math.isclose(float(a), float(b), abs_tol=tol, rel_tol=tol):
        raise AssertionError(f"Mismatch: {a} != {b}")


def one(rows, **attrs):
    v = [r for r in rows if all(str(r[k]) == str(val) for k, val in attrs.items())]
    if len(v) != 1:
        raise AssertionError(f"Expected one {attrs}, got {len(v)}")
    return v[0]


def main():
    manifest = json.loads((P / "manifest.json").read_text())
    protocol = json.loads((P / "protocol.json").read_text())
    assert protocol["status"] == "FROZEN_BEFORE_E0_SOLVER_RUNS"
    assert protocol["schedules"] == list(SCHEDULES)
    assert protocol["checkpoints"] == list(CHECKPOINTS)
    assert protocol["expected_runs"] == 80
    assert protocol["updates"] == 50000
    assert protocol["seeds_per_graph"] == 20
    assert [g["graph"] for g in protocol["graphs"]] == list(GRAPHS)
    assert manifest["status"] == "E0_FP64_CAL_PILOT_80_RUNS_COMPLETE"
    assert (manifest["runs"], manifest["checkpoint_rows"],
            manifest["acceptance_bin_rows"]) == (80, 320, 800)
    assert manifest["protocol_sha256"] == sha(P / "protocol.json")
    assert manifest["code_hashes"] == protocol["code_hashes"]
    for path, hash_expected in protocol["code_hashes"].items():
        assert sha(ROOT / path) == hash_expected, "Frozen code changed: " + path

    for field, name in (
        ("run_rows_sha256", "run_rows.csv"),
        ("checkpoint_rows_sha256", "checkpoint_rows.csv"),
        ("trace_rows_sha256", "trace_rows.csv"),
        ("paired_contrast_sha256", "paired_schedule_contrasts.csv"),
    ):
        assert manifest[field] == sha(P / name), "File hash mismatch: " + name

    runs = read_csv("run_rows.csv")
    checkpoints = read_csv("checkpoint_rows.csv")
    trace = read_csv("trace_rows.csv")
    summary = read_csv("pilot_summary.csv")
    paired = read_csv("paired_schedule_contrasts.csv")
    assert [len(v) for v in (runs, checkpoints, trace, summary, paired)] == [
        80, 320, 800, 16, 8
    ]
    assert len({(r["graph"], r["schedule"], r["seed"]) for r in runs}) == 80
    assert len({(r["graph"], r["schedule"], r["seed"], r["updates_completed"])
                for r in checkpoints}) == 320
    assert len({(r["graph"], r["schedule"], r["seed"], r["updates_completed"])
                for r in trace}) == 800
    assert len({(r["graph"], r["schedule"], r["updates_completed"])
                for r in summary}) == 16
    assert len({(r["graph"], r["updates_completed"]) for r in paired}) == 8

    expected_keys = set()
    for ix, g in enumerate(protocol["graphs"]):
        for sch in SCHEDULES:
            for seed in range(BASE + ix * 100000, BASE + ix * 100000 + 20):
                expected_keys.add((g["graph"], sch, str(seed)))
    assert {(r["graph"], r["schedule"], r["seed"]) for r in runs} == expected_keys

    graph_info = {g["graph"]: g for g in protocol["graphs"]}
    for r in runs:
        g = graph_info[r["graph"]]
        assert r["graph_sha256"] == g["sha256"]
        assert int(r["official_optimum"]) == g["official_optimum"]
        assert int(r["attempted_updates"]) == 50000
        assert 0 <= float(r["returned_original_cut"]) <= g["official_optimum"]
        close(r["gap_pct"], 100 * (
            g["official_optimum"] - float(r["returned_original_cut"])
        ) / g["official_optimum"])
        c = one(checkpoints, graph=r["graph"], schedule=r["schedule"],
                seed=r["seed"], updates_completed=50000)
        close(r["gap_pct"], c["gap_pct"])
        total_flips = sum(int(v["bin_flips"]) for v in trace
                          if v["graph"] == r["graph"]
                          and v["schedule"] == r["schedule"]
                          and v["seed"] == r["seed"])
        assert total_flips == int(r["actual_flips"])

    for row in trace:
        assert int(row["bin_attempted"]) == 5000
        assert int(row["updates_completed"]) in BINS
        assert 0 <= int(row["bin_uphill_accepted"]) <= int(row["bin_uphill_proposals"])
        assert 0 <= int(row["bin_flips"]) <= 5000
        close(row["bin_flip_rate"], int(row["bin_flips"]) / 5000)
        if int(row["bin_uphill_proposals"]):
            close(row["bin_uphill_accept_rate"],
                  int(row["bin_uphill_accepted"]) / int(row["bin_uphill_proposals"]))

    print("E0 AUDIT PASS: frozen protocol and code hashes; 80 unique solver records;")
    print("               320 checkpoints; 800 trace bins; 16 quality summaries;")
    print("               8 paired contrasts; original optimum scoring consistent.")
    print()
    print("GEOMETRIC minus LINEAR paired optimum-gap contrasts (pp)")
    for graph in GRAPHS:
        print("\n" + graph)
        for step in CHECKPOINTS:
            p = one(paired, graph=graph, updates_completed=step)
            a = {r["seed"]: float(r["gap_pct"]) for r in checkpoints
                 if r["graph"] == graph and r["schedule"] == SCHEDULES[0]
                 and int(r["updates_completed"]) == step}
            b = {r["seed"]: float(r["gap_pct"]) for r in checkpoints
                 if r["graph"] == graph and r["schedule"] == SCHEDULES[1]
                 and int(r["updates_completed"]) == step}
            assert set(a) == set(b)
            diffs = [b[k]-a[k] for k in sorted(a)]
            close(p["mean_delta_pp"], mean(diffs))
            print(f"  {step:5} updates: delta={float(p['mean_delta_pp']):+.4f} pp "
                  f"95% CI=[{float(p['ci95_lo_pp']):+.4f},"
                  f"{float(p['ci95_hi_pp']):+.4f}]")
        print("  mean final gap, flip rates by time bin:")
        for sch in SCHEDULES:
            rr = [v for v in runs if v["graph"] == graph and v["schedule"] == sch]
            close(one(summary, graph=graph, schedule=sch,
                      updates_completed=50000)["mean_gap_pct"],
                  mean(float(v["gap_pct"]) for v in rr))
            first = [v for v in trace if v["graph"] == graph
                     and v["schedule"] == sch
                     and int(v["updates_completed"]) == 5000]
            last = [v for v in trace if v["graph"] == graph
                    and v["schedule"] == sch
                    and int(v["updates_completed"]) == 50000]
            def uphill_fraction(rows):
                proposed = sum(int(v["bin_uphill_proposals"]) for v in rows)
                return (sum(int(v["bin_uphill_accepted"]) for v in rows)
                        / proposed if proposed else float("nan"))
            print(f"  {sch:18} gap={mean(float(v['gap_pct']) for v in rr):.3f}% "
                  f"flip first/last="
                  f"{mean(float(v['bin_flip_rate']) for v in first):.4f}/"
                  f"{mean(float(v['bin_flip_rate']) for v in last):.4f} "
                  f"uphill first/last={uphill_fraction(first):.4f}/"
                  f"{uphill_fraction(last):.4f}")
    print("\nE0 READ-ONLY AUDIT COMPLETE — NO NEW SOLVER RUNS")


if __name__ == "__main__":
    main()
