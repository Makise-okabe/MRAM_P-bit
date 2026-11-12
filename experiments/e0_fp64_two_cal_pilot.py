#!/usr/bin/env python3
"""E0 FP64 CAL-only solver calibration pilot. No held-out access.

Compare the frozen 50k-update linear schedule against a field-calibrated
geometric schedule at the SAME 500-sweep budget. Log 10 acceptance bins,
four best-cut checkpoints, paired 20-seed gaps and confidence intervals.

--selftest: synthetic graph parity only, no Biq Mac graph access.
--freeze: read ONLY predesignated CAL graph files, freeze their source hashes
          and schedule parameters before any pilot solver runs.
--execute: require identical code/data/protocol, run 80 FP64 solver trials.

All optimality numbers are external original-weight evaluations.
No new format sweep, response variation, or fabricated STT-MRAM claim.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
from types import SimpleNamespace

from experiments.biqmac_maxcut import load_rudy
from experiments.m0_ising_math import sigmoid
from experiments.m1_biqmac_ideal_pilot import (
    beta_from_original_graph, original_cut, prepare, represented_energy,
)
from experiments.m1_biqmac_reference_quality_gate import solve_reference

ROOT = Path(__file__).resolve().parents[1]
GRAPH_NAMES = ("ising2.5-100_5555", "t2g10_5555")
GRAPH_DIR = Path("data/biqmac/raw/ising")
REFERENCE_FILE = Path("docs/BIQMAC_OFFICIAL_OPTIMA_2007.json")
OUT = Path("results/e0_fp64_two_cal_20261112")
BUDGET = 50_000
SEEDS_PER_GRAPH = 20
BASE_SEED = 20261112
SCHEDULES = ("linear_legacy", "geometric_uphill")
CHECKPOINTS = (5_000, 15_000, 30_000, 50_000)
BIN = 5_000
RANDOM_STATES = 80
FIELD_SEED = 202611120
TARGET_HOT = 0.4
TARGET_COLD = 0.001
CI_RESAMPLES = 4000
HASHED_FILES = (
    "experiments/e0_fp64_two_cal_pilot.py",
    "experiments/biqmac_maxcut.py",
    "experiments/m0_ising_math.py",
    "experiments/m1_biqmac_ideal_pilot.py",
    "experiments/m1_biqmac_reference_quality_gate.py",
    "docs/BIQMAC_OFFICIAL_OPTIMA_2007.json",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_hashes():
    return {p: digest(ROOT / p) for p in HASHED_FILES}


def save_json_x(path, obj):
    with path.open("x", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")


def save_csv_x(path, rows):
    if not rows:
        raise ValueError("Refusing empty CSV " + str(path))
    with path.open("x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def load_cal_graphs():
    data = json.loads(REFERENCE_FILE.read_text())
    if data.get("reference_type") != "PUBLISHED_OPTIMUM":
        raise ValueError("Published optimum reference required")
    results = []
    for name in GRAPH_NAMES:
        path = GRAPH_DIR / name
        if not path.is_file():
            raise FileNotFoundError("CAL graph missing: " + str(path))
        graph = load_rudy(path)
        ref = data["graphs"][name]
        if graph.sha256 != ref["sha256"] or graph.n != 100:
            raise ValueError("Original CAL graph SHA/n mismatch: " + name)
        results.append((graph, int(ref["cut"])))
    return results


def uphill_deltas(graph, seed):
    """Conditional strictly-uphill energy changes on random REF64 states."""
    adj = prepare(graph, "ref64", "source")["adjacency"]
    rng = random.Random(seed)
    values = []
    for _ in range(RANDOM_STATES):
        spins = [1 if rng.randrange(2) else -1 for _ in range(graph.n)]
        for i in range(graph.n):
            field = sum(q * spins[j] for j, q in adj[i])
            de = 2.0 * spins[i] * field
            if de > 0.0:
                values.append(de)
    if len(values) < 100 or min(values) <= 0.0:
        raise AssertionError("Too few positive uphill proposals")
    return values


def uphill_acceptance(beta, deltas):
    # For a proposed spin flip with positive DeltaE, a heat-bath
    # update flips with probability 1/(1+exp(beta*DeltaE)).
    total = 0.0
    for de in deltas:
        z = beta * de
        total += (0.0 if z > 740.0 else
                  math.exp(-z)/(1.0 + math.exp(-z)) if z > 40 else
                  1.0/(1.0+math.exp(z)))
    return total / len(deltas)


def solve_for_uphill_target(deltas, target, beta_base):
    if not 0 < target < 0.5:
        raise ValueError("Target uphill probability must be in (0, 0.5)")
    lo, hi = 0.0, float(beta_base)
    for _ in range(80):
        if uphill_acceptance(hi, deltas) < target:
            break
        hi *= 2
    else:
        raise ValueError("Cannot bracket conditional-uphill temperature")
    for _ in range(65):
        mid = (lo+hi)/2.0
        if uphill_acceptance(mid, deltas) > target:
            lo = mid
        else:
            hi = mid
    return hi


def geometry(graph, graph_index):
    beta_base = beta_from_original_graph(graph)
    deltas = uphill_deltas(graph, FIELD_SEED + graph_index * 100000)
    beta_start = solve_for_uphill_target(deltas, TARGET_HOT, beta_base)
    beta_end = solve_for_uphill_target(deltas, TARGET_COLD, beta_base)
    if not 0 < beta_start < beta_end:
        raise AssertionError("Invalid increasing-beta geometric schedule")
    return {
        "base_beta": beta_base,
        "start_beta": beta_start,
        "end_beta": beta_end,
        "n_positive_uphill_proposals": len(deltas),
        "hot_conditional_uphill_mean": uphill_acceptance(beta_start, deltas),
        "cold_conditional_uphill_mean": uphill_acceptance(beta_end, deltas),
        "field_sampling_seed": FIELD_SEED+graph_index*100000,
    }


def beta_at(schedule, profile, step, updates):
    t = step / max(1, updates-1)
    if schedule == "linear_legacy":
        return profile["base_beta"] * (0.5 + 1.5*t)
    if schedule == "geometric_uphill":
        return profile["start_beta"] * (
            (profile["end_beta"]/profile["start_beta"]) ** t
        )
    raise ValueError("Unsupported schedule")


def traced_run(graph, optimum, profile, schedule, seed, updates=BUDGET,
               checkpoints=CHECKPOINTS, bin_size=BIN):
    """RNG order and all incumbent/tie semantics match legacy FP64 solver."""
    rng = random.Random(seed)
    spins = [1 if rng.randrange(2) else -1 for _ in range(graph.n)]
    rep = prepare(graph, "ref64", "source")
    adj = rep["adjacency"]
    fields = [sum(q*spins[j] for j, q in adj[i]) for i in range(graph.n)]
    energy = represented_energy(rep["edges"], spins)
    best_energy, best_state = energy, tuple(spins)
    flips = improvements = 0
    bin_flips = bin_uphill = bin_uphill_flips = bin_downhill = 0
    bins, cps = [], []
    for step in range(updates):
        i = rng.randrange(graph.n)
        u = rng.random()
        b = beta_at(schedule, profile, step, updates)
        old = spins[i]
        de = 2*old*fields[i]
        if de > 0:
            bin_uphill += 1
        elif de < 0:
            bin_downhill += 1
        nxt = 1 if u < sigmoid(2*b*fields[i]) else -1
        if nxt != old:
            ds = nxt-old
            energy += de
            spins[i] = nxt
            flips += 1
            bin_flips += 1
            if de > 0:
                bin_uphill_flips += 1
            for j,q in adj[i]:
                fields[j] += q*ds
        if energy < best_energy:
            best_energy, best_state = energy, tuple(spins)
            improvements += 1
        attempted = step+1
        if attempted % bin_size == 0:
            bins.append({
                "seed":seed,"schedule":schedule,
                "updates_completed":attempted,
                "bin_attempted":bin_size,"bin_flips":bin_flips,
                "bin_flip_rate":bin_flips/bin_size,
                "bin_uphill_proposals":bin_uphill,
                "bin_uphill_accepted":bin_uphill_flips,
                "bin_uphill_accept_rate":(
                    bin_uphill_flips/bin_uphill if bin_uphill else None
                ),
                "bin_downhill_proposals":bin_downhill,
                "beta_at_bin_end":b,
            })
            bin_flips = bin_uphill = bin_uphill_flips = bin_downhill = 0
        if attempted in checkpoints:
            cut = original_cut(graph,best_state)
            if cut > optimum + 1e-6:
                raise AssertionError("Cut exceeds official optimum")
            cps.append({
                "seed":seed,"schedule":schedule,
                "updates_completed":attempted,
                "retained_original_cut":cut,
                "gap_pct":100*(optimum-cut)/optimum,
                "total_flips_to_checkpoint":flips,
                "total_improvements_to_checkpoint":improvements,
            })
    actual = represented_energy(rep["edges"],spins)
    retained = represented_energy(rep["edges"],best_state)
    if not math.isclose(actual,energy,rel_tol=1e-7,abs_tol=1e-7):
        raise AssertionError("Incremental energy mismatch")
    if not math.isclose(retained,best_energy,rel_tol=1e-7,abs_tol=1e-7):
        raise AssertionError("Incumbent energy mismatch")
    if len(cps)!=len(checkpoints) or len(bins)!=updates//bin_size:
        raise AssertionError("Checkpoint/bin count mismatch")
    final_cut = original_cut(graph,best_state)
    return ({
        "seed":seed,"schedule":schedule,"attempted_updates":updates,
        "actual_flips":flips,"improvements":improvements,
        "returned_original_cut":final_cut,
        "gap_pct":100*(optimum-final_cut)/optimum,
        "returned_represented_energy":retained,
        "returned_state_hex":format(
            sum(1<<i for i,si in enumerate(best_state) if si>0),"x"
        ),
    },cps,bins)


def selftest():
    graph = SimpleNamespace(n=4,edges=((0,1,2),(1,2,-3),(2,3,4),(0,3,1)))
    beta = beta_from_original_graph(graph)
    fake = {"base_beta":beta,"start_beta":beta/4,"end_beta":beta*20}
    for seed in (7,12345,3000):
        old = solve_reference(graph,prepare(graph,"ref64","source"),
                              beta,300,seed,"linear")
        new,_,_ = traced_run(graph,10_000,fake,"linear_legacy",
                             seed,updates=300,checkpoints=(100,300),bin_size=100)
        for k in ("returned_state_hex","returned_original_cut",
                  "returned_represented_energy","actual_flips","improvements"):
            if old[k] != new[k]:
                raise AssertionError("Legacy RNG/solver parity failed: "+k)
        test_new,_,_ = traced_run(graph,10_000,fake,"geometric_uphill",
                                  seed,updates=300,checkpoints=(100,300),bin_size=100)
        if test_new["attempted_updates"] != 300:
            raise AssertionError("Geometric trace test failed")
    print("E0 SELFTEST PASS: three exact legacy parity checks and geometric trace")


def make_protocol():
    graph_info = []
    for ix,(graph,opt) in enumerate(load_cal_graphs()):
        graph_info.append({
            "graph":GRAPH_NAMES[ix],"sha256":graph.sha256,"n":graph.n,
            "m_raw":graph.raw_edge_count,"m_nonzero":len(graph.edges),
            "official_optimum":opt,"temperature_profile":geometry(graph,ix)
        })
    return {
        "status":"FROZEN_BEFORE_E0_SOLVER_RUNS",
        "scope":"FP64 only, two previously viewed CAL instances; no held-outs",
        "graphs":graph_info,
        "code_hashes":freeze_hashes(),
        "legacy":"linear beta_G*0.5 to 2.0, U=50000",
        "candidate":"geometric beta schedule fitted to random-state positive DeltaE distribution",
        "conditional_uphill_targets_hot_cold":[TARGET_HOT,TARGET_COLD],
        "random_state_count_per_graph":RANDOM_STATES,
        "random_state_seed_rule":"202611120 + 100000*graph_index",
        "updates":BUDGET,"seeds_per_graph":SEEDS_PER_GRAPH,
        "seed_rule":"20261112+100000*graph_index+k, k=0..19",
        "schedules":list(SCHEDULES),
        "checkpoints":list(CHECKPOINTS),"trace_bin_size":BIN,
        "bootstrap_resamples":CI_RESAMPLES,
        "expected_runs":2*len(SCHEDULES)*SEEDS_PER_GRAPH,
        "target_mean_gap_pct":1.0,
        "decision_policy":"Descriptive pilot: compare at same U=50k; do not change budget or schedule from held-out results. If CAL mean gap >1%, test a separately frozen larger-budget study. Legacy 50k outcomes remain valid short-budget data.",
        "limitations":"Source-only graph calibration; random-state uphill flip target is not trajectory flip target. Not a demonstrated equilibrium schedule nor an STT-MRAM physical model.",
    }


def boot_ci(values, seed, reps=CI_RESAMPLES):
    rng = random.Random(seed)
    n = len(values)
    boots = sorted(sum(values[rng.randrange(n)] for _ in range(n))/n
                   for _ in range(reps))
    return boots[int(.025*reps)], boots[min(reps-1,int(.975*reps))]


def execute():
    path = OUT / "protocol.json"
    if not path.is_file():
        raise ValueError("Protocol missing: run --freeze after --selftest")
    frozen = json.loads(path.read_text())
    if frozen != make_protocol():
        raise ValueError("FROZEN PROTOCOL MISMATCH. Stop; do not modify/execute.")
    if any((OUT / p).exists() for p in
           ("run_rows.csv","checkpoint_rows.csv","trace_rows.csv","manifest.json")):
        raise FileExistsError("E0 results already exist; refusing rerun")
    graph_records = load_cal_graphs()
    runs, all_cps, all_bins = [], [], []
    for ix,(graph,optimum) in enumerate(graph_records):
        prof = frozen["graphs"][ix]["temperature_profile"]
        for schedule in SCHEDULES:
            for k in range(SEEDS_PER_GRAPH):
                seed = BASE_SEED+ix*100000+k
                run,cps,bins = traced_run(graph,optimum,prof,schedule,seed)
                prefix = {"graph":GRAPH_NAMES[ix],"graph_sha256":graph.sha256,
                          "official_optimum":optimum}
                runs.append({**prefix,**run})
                all_cps += [{**prefix,**row} for row in cps]
                all_bins += [{**prefix,**row} for row in bins]
            print(f"FINISHED {GRAPH_NAMES[ix]} {schedule}: "
                  f"{SEEDS_PER_GRAPH} seeds / {BUDGET} updates",flush=True)
    if len(runs)!=80 or len(all_cps)!=320 or len(all_bins)!=800:
        raise AssertionError("Unexpected record counts")
    summary, paired = [], []
    for ix,name in enumerate(GRAPH_NAMES):
        for step in CHECKPOINTS:
            for schedule in SCHEDULES:
                subset=[a["gap_pct"] for a in all_cps if
                        a["graph"]==name and a["schedule"]==schedule
                        and a["updates_completed"]==step]
                lo,hi=boot_ci(subset,BASE_SEED+ix*1000+step+
                              (0 if schedule==SCHEDULES[0] else 1))
                summary.append({"graph":name,"schedule":schedule,
                                "updates_completed":step,"n":len(subset),
                                "mean_gap_pct":statistics.mean(subset),
                                "ci95_lo_pct":lo,"ci95_hi_pct":hi,
                                "fraction_gap_le_1pct":
                                  sum(x<=1.0 for x in subset)/len(subset)})
            a={r["seed"]:r["gap_pct"] for r in all_cps if
               r["graph"]==name and r["updates_completed"]==step
               and r["schedule"]==SCHEDULES[0]}
            b={r["seed"]:r["gap_pct"] for r in all_cps if
               r["graph"]==name and r["updates_completed"]==step
               and r["schedule"]==SCHEDULES[1]}
            if set(a)!=set(b) or len(a)!=SEEDS_PER_GRAPH:
                raise AssertionError("Unpaired schedule records")
            deltas=[b[seed]-a[seed] for seed in sorted(a)]
            lo,hi=boot_ci(deltas,BASE_SEED+ix*9000+step)
            paired.append({"graph":name,"updates_completed":step,
                           "metric":"geometric_gap_minus_legacy_gap_pp",
                           "n_pairs":len(deltas),
                           "mean_delta_pp":statistics.mean(deltas),
                           "ci95_lo_pp":lo,"ci95_hi_pp":hi})
    save_csv_x(OUT/"run_rows.csv",runs)
    save_csv_x(OUT/"checkpoint_rows.csv",all_cps)
    save_csv_x(OUT/"trace_rows.csv",all_bins)
    save_csv_x(OUT/"pilot_summary.csv",summary)
    save_csv_x(OUT/"paired_schedule_contrasts.csv",paired)
    save_json_x(OUT/"manifest.json",{
        "status":"E0_FP64_CAL_PILOT_80_RUNS_COMPLETE",
        "protocol_sha256":digest(path),
        "code_hashes":frozen["code_hashes"],
        "runs":80,"checkpoint_rows":len(all_cps),"acceptance_bin_rows":len(all_bins),
        "run_rows_sha256":digest(OUT/"run_rows.csv"),
        "checkpoint_rows_sha256":digest(OUT/"checkpoint_rows.csv"),
        "trace_rows_sha256":digest(OUT/"trace_rows.csv"),
        "paired_contrast_sha256":digest(OUT/"paired_schedule_contrasts.csv"),
    })
    for x in summary:
        if x["updates_completed"]==BUDGET:
            print(f"FINAL {x['graph']} {x['schedule']} "
                  f"mean_gap={x['mean_gap_pct']:.3f}% "
                  f"95CI=[{x['ci95_lo_pct']:.3f},{x['ci95_hi_pct']:.3f}]")
    print("E0 FP64 CAL PILOT COMPLETE, 80 runs; no held-out access")


def freeze():
    selftest()
    proto = make_protocol()
    if OUT.exists():
        raise FileExistsError("Output already exists: "+str(OUT))
    OUT.mkdir(parents=True,exist_ok=False)
    save_json_x(OUT/"protocol.json",proto)
    for item in proto["graphs"]:
        p=item["temperature_profile"]
        print(f"FROZEN {item['graph']} base_beta={p['base_beta']:.8g} "
              f"hot={p['start_beta']:.8g} cold={p['end_beta']:.8g} "
              f"uphill_p={p['hot_conditional_uphill_mean']:.4f}->"
              f"{p['cold_conditional_uphill_mean']:.4f}")
    print("PROTOCOL FROZEN (no E0 solver runs). Review before --execute")


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest",action="store_true")
    g.add_argument("--freeze",action="store_true")
    g.add_argument("--execute",action="store_true")
    args=ap.parse_args()
    if args.selftest:selftest()
    elif args.freeze:freeze()
    elif args.execute:execute()


if __name__=="__main__":
    main()
