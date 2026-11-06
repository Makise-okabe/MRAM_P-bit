#!/usr/bin/env python3
"""Bounded E1 reference-only Gibbs operating-point diagnostic for official Mac graphs.

Not a format-selection sweep, not magnetic device data, not an optimal solver.
Use calibration graphs ONLY to select one solver schedule/update budget,
then hold that decision fixed before any precision/held-out comparison.

Design frozen: attempts=5000/20000/50000, six paired solver seeds,
fixed beta vs linear anneal 0.5*beta -> 2*beta over attempted updates.
One independent graph is ONE statistical unit; multiple seeds are nested.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random

from experiments.biqmac_maxcut import load_rudy
from experiments.m0_ising_math import sigmoid
from experiments.m1_biqmac_ideal_pilot import (
    beta_from_original_graph, original_cut, prepare, represented_energy, solve
)

DEFAULT_BUDGETS = (5000, 20000, 50000)
SCHEDULES = ("fixed", "linear")


def schedule_beta(beta, schedule, step, updates):
    if schedule == "fixed":
        return beta
    if schedule == "linear":
        t = step / max(1, updates - 1)
        return beta * (0.5 + 1.5 * t)
    raise ValueError(f"unknown schedule {schedule}")


def solve_reference(graph, rep, beta, updates, seed, schedule):
    """Reference-only. For fixed, reuse original M1 solver bit-for-bit."""
    if updates < 1 or beta <= 0:
        raise ValueError("updates, beta must be positive")
    if schedule == "fixed":
        return solve(graph, rep, beta, updates, seed)
    if schedule != "linear":
        raise ValueError("unknown schedule")
    rng = random.Random(seed)
    spins = [1 if rng.randrange(2) else -1 for _ in range(graph.n)]
    adj = rep["adjacency"]
    fields = [sum(q * spins[j] for j, q in adj[i]) for i in range(graph.n)]
    energy = represented_energy(rep["edges"], spins)
    best_e = energy
    best_state = tuple(spins)
    flips = 0
    improvements = 0
    for step in range(updates):
        i = rng.randrange(graph.n)
        u = rng.random()
        b = schedule_beta(beta, schedule, step, updates)
        old = spins[i]
        nxt = 1 if u < sigmoid(2 * b * fields[i]) else -1
        if nxt != old:
            delta = nxt - old
            energy += 2 * old * fields[i]
            spins[i] = nxt
            flips += 1
            for j, q in adj[i]:
                fields[j] += q * delta
        if energy < best_e:
            best_e = energy
            best_state = tuple(spins)
            improvements += 1
    actual = represented_energy(rep["edges"], spins)
    saved = represented_energy(rep["edges"], best_state)
    if not math.isclose(actual, energy, rel_tol=1e-7, abs_tol=1e-7):
        raise AssertionError("energy update mismatch")
    if not math.isclose(saved, best_e, rel_tol=1e-7, abs_tol=1e-7):
        raise AssertionError("retained state energy mismatch")
    return {
        "seed": seed, "attempted_updates": updates,
        "actual_flips": flips, "improvements": improvements,
        "returned_original_cut": original_cut(graph, best_state),
        "final_original_cut": original_cut(graph, spins),
        "returned_represented_energy": saved,
        "final_represented_energy": actual,
        "returned_state_hex": format(sum(1 << i for i, s in enumerate(best_state) if s > 0), "x")
    }


def official_reference(graph, entry, source):
    if entry["sha256"] != graph.sha256:
        raise ValueError(f"reference hash mismatch for {graph.source}")
    cut = entry["cut"]
    if not isinstance(cut, int) or cut <= 0:
        raise ValueError("this normalized gap requires a positive documented optimum")
    return cut


def examine(graphs, references_path, budgets, schedules, seeds, base_seed, out):
    if out.exists():
        raise ValueError("output already exists")
    if not budgets or not schedules or seeds < 1 or any(x < 1 for x in budgets):
        raise ValueError("invalid experiment dimensions")
    if any(x not in SCHEDULES for x in schedules):
        raise ValueError("unsupported schedule")
    refs = json.loads(references_path.read_text(encoding="utf-8"))
    if refs.get("reference_type") != "PUBLISHED_OPTIMUM":
        raise ValueError("only official optimum rows supported")
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    for gix, path in enumerate(graphs):
        graph = load_rudy(path)
        entry = refs["graphs"].get(path.name)
        if entry is None:
            raise ValueError(f"no official reference for {path.name}")
        optimum = official_reference(graph, entry, refs)
        rep = prepare(graph, "ref64", "source")
        beta = beta_from_original_graph(graph)
        for schedule in schedules:
            for updates in budgets:
                # Seed choice does NOT depend on schedule or update budget.
                for k in range(seeds):
                    seed = base_seed + 100000 * gix + k
                    run = solve_reference(graph, rep, beta, updates, seed, schedule)
                    score = float(run["returned_original_cut"])
                    if score > optimum + 1e-7:
                        raise AssertionError(f"cut {score} exceeds official {optimum}: {path.name} seed={seed}")
                    rows.append({
                        "graph": path.name, "sha256": graph.sha256,
                        "official_optimum": optimum, "reference_type": "PUBLISHED_OPTIMUM",
                        "official_table": entry["table"], "official_page": entry["pdf_page"],
                        "beta": beta, "schedule": schedule,
                        "updates": updates, "seed": seed,
                        "returned_original_cut": score,
                        "normalized_quality": score / optimum,
                        "gap": optimum - score,
                        "gap_pct": 100 * (optimum - score) / optimum,
                        "actual_flips": run["actual_flips"],
                        "improvements": run["improvements"],
                        "returned_state_hex": run["returned_state_hex"]
                    })
    with (out / "reference_runs.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    grouped = {}
    for r in rows:
        key = (r["graph"], r["schedule"], r["updates"])
        grouped.setdefault(key, []).append(r)
    summaries = []
    for (graph, sch, budget), values in sorted(grouped.items()):
        summaries.append({
            "graph": graph, "schedule": sch, "updates": budget,
            "n_seeds": len(values), "official_optimum": values[0]["official_optimum"],
            "mean_original_cut": sum(r["returned_original_cut"] for r in values) / len(values),
            "mean_gap_pct": sum(r["gap_pct"] for r in values) / len(values),
            "min_gap_pct": min(r["gap_pct"] for r in values),
            "max_gap_pct": max(r["gap_pct"] for r in values),
            "mean_flips": sum(r["actual_flips"] for r in values) / len(values)
        })
    with (out / "reference_summary.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    # Predeclared operating-point rule: average the original-cut optimum
    # gap in percentage points with one equal vote per CALIBRATION graph.
    # Choose the lowest attempted-update budget within 1.0 percentage point
    # of the best observed equal-graph mean gap; break ties toward a fixed
    # schedule (less control complexity). This does NOT require 1% gap.
    ngraphs = len(graphs)
    aggregate = []
    for sch in schedules:
        for budget in budgets:
            matching = [r for r in summaries if r["schedule"] == sch and r["updates"] == budget]
            if len(matching) != ngraphs:
                raise AssertionError("unequal graph coverage in operating-point decision")
            aggregate.append({"schedule": sch, "updates": budget,
                              "mean_equal_graph_gap_pct": sum(r["mean_gap_pct"] for r in matching) / ngraphs})
    best_observed = min(x["mean_equal_graph_gap_pct"] for x in aggregate)
    viable = [x for x in aggregate if x["mean_equal_graph_gap_pct"] <= best_observed + 1.0 + 1e-12]
    selected = min(viable, key=lambda x: (x["updates"], x["schedule"] != "fixed"))
    policy = {
        "rule": "min budget within 1.0 absolute percentage point of best equal-graph mean published-optimum gap, tie fixed",
        "is_optimum_gap_requirement": False,
        "calibration_graph_count": ngraphs,
        "configurations": aggregate,
        "best_observed_mean_gap_pct": best_observed,
        "selected": selected,
        "future_freeze": "Check this CALIBRATION result then freeze schedule/budget for FP/INT/BFP and held-out graphs; do not reselect on their scores.",
        "status": "CALIBRATION_RECOMMENDATION_NOT_HELDOUT"
    }
    (out / "operating_point_recommendation.json").write_text(json.dumps(policy, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "status": "REFERENCE_QUALITY_PROBE_COMPLETE",
        "source": str(references_path),
        "reference_json_sha256": hashlib.sha256(references_path.read_bytes()).hexdigest(),
        "reference_type": "published optimum, matched to original graph SHA256",
        "graphs": [{"name":p.name, "sha256": load_rudy(p).sha256} for p in graphs],
        "budgets": list(budgets), "schedules": list(schedules),
        "schedule_details": "fixed beta_G or linear beta(t)=beta_G*(0.5+1.5*t/(updates-1))",
        "beta_rule": "Original source weights and mean nonzero degree; identical normalization for every format later",
        "seed_count_per_graph": seeds, "base_seed": base_seed,
        "selection": "best represented Ising energy visited; original cut used only after return",
        "purpose": "bounded reference-only quality-vs-budget comparison, calibration graphs; no format tuning or device modeling",
        "caveat": "Do not compare all seed runs as independent graph instances; freeze chosen schedule and budget across later formats and held-out graphs. Pilot results remain historical.",
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "n_runs": len(rows)
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for r in summaries:
        print(f"{r['graph']:20s} {r['schedule']:6s} {r['updates']:6d} "
              f"mean_gap={r['mean_gap_pct']:.3f}% "
              f"range=[{r['min_gap_pct']:.3f},{r['max_gap_pct']:.3f}] "
              f"mean_flips={r['mean_flips']:.1f}", flush=True)
    print("PREDECLARED CALIBRATION OPERATING POINT:", selected["schedule"], selected["updates"], "updates", f"mean gap {selected['mean_equal_graph_gap_pct']:.3f}%")
    print("REFERENCE QUALITY PROBE COMPLETE: ", out, len(rows), "calibration solver runs")
    return rows, summaries


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--graph", type=Path, required=True, action="append")
    ap.add_argument("--references", type=Path, default=Path("docs/BIQMAC_OFFICIAL_OPTIMA_2007.json"))
    ap.add_argument("--budgets", type=int, nargs="+", default=list(DEFAULT_BUDGETS))
    ap.add_argument("--schedules", nargs="+", default=list(SCHEDULES))
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--seed", type=int, default=20261107)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    examine(a.graph, a.references, a.budgets, a.schedules, a.seeds, a.seed, a.out)


if __name__ == "__main__":
    main()
