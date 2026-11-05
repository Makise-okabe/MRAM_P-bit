#!/usr/bin/env python3
"""M0: fresh paired PT/Gibbs original-task time-to-target comparison.

E1 ideal-device SOFTWARE ONLY. This tests solver suitability, not precision
formats, measured magnetic p-bit response, silicon performance, or novelty.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import m0_reference as model
import m0_parallel_tempering as pt

DEFAULT_BETAS = (0.03, 0.05, 0.08, 0.12, 0.18, 0.27, 0.38, 0.50)

def gibbs_trial(instance, beta, seed, budget_updates, target):
    n = len(instance["h"])
    if budget_updates % n or budget_updates < n or beta <= 0:
        raise ValueError("budget must be positive and divisible by n")
    rng = random.Random(seed)
    s = [rng.choice((-1, 1)) for _ in range(n)]
    first_hit = 0 if pt.at_target(instance, s, target) else None
    transitions = 0
    previously = tuple(s)
    # One checkpoint after every n *attempted* single-spin updates.
    # This benefits Gibbs relative to PT, which checks only after all replicas
    # have each received n updates and exchanges have been attempted.
    for completed in range(n, budget_updates + 1, n):
        for _ in range(n):
            model.update(instance["J"], instance["h"], s, beta, rng)
        state = tuple(s)
        transitions += (state != previously)
        previously = state
        if first_hit is None and pt.at_target(instance, s, target):
            first_hit = completed
    return dict(first_hit_updates=first_hit, hit=first_hit is not None,
                observed_cold_state_changes=transitions,
                checkpoints=budget_updates // n,
                swap_attempts=0, swap_attempts_to_hit=0 if first_hit == 0 else None,
                replicas=1, total_spin_updates=budget_updates)

def run_case(instance, seed, cycles, betas):
    n = len(instance["h"])
    k = len(betas)
    budget = cycles * n * k
    target = pt.target_from_exact(instance)
    trial_pt = pt.pt_run(instance, betas, seed=seed, burnin=0, collect=cycles,
                         sweeps=1)
    if trial_pt["all_replica_spin_update_attempts"] != budget:
        raise AssertionError("PT update accounting mismatch")
    gibbs = gibbs_trial(instance, betas[-1], seed, budget, target)
    rows = []
    for method, result in (
        ("PT", dict(first_hit_updates=trial_pt["cold_first_target_spin_updates"],
                    hit=trial_pt["target_hit"],
                    observed_cold_state_changes=trial_pt["cold_state_changes"],
                    checkpoints=trial_pt["cold_checkpoint_count"],
                    swap_attempts=trial_pt["replica_swap_attempts"],
                    swap_attempts_to_hit=trial_pt["cold_first_target_swap_attempts"],
                    replicas=k, total_spin_updates=budget)),
        ("Gibbs", gibbs),
    ):
        rows.append(dict(method=method, solver_seed=seed, original_task_target=target,
                         **result))
    return rows

def summarize(rows, family, n, instances, seeds, cycles, betas):
    grouped = {}
    for r in rows:
        key = (r["instance_seed"], r["solver_seed"])
        grouped.setdefault(key, {})[r["method"]] = r
    counts = {"both":0,"pt_only":0,"gibbs_only":0,"neither":0}
    for pair in grouped.values():
        a, b = pair["PT"]["hit"], pair["Gibbs"]["hit"]
        label = "both" if a and b else ("pt_only" if a else ("gibbs_only" if b else "neither"))
        counts[label] += 1
    return {
        "evidence":"E1 new ideal-device software; no MRAM or precision results",
        "scope":"M0 solver-gate pilot; all targets computed by exact small-N oracle",
        "family":family, "size":n,"independent_instances":instances,
        "nested_solver_seeds_per_instance":seeds, "cycles":cycles,
        "betas":list(betas),"paired_outcome_counts":counts,
        "pt_hit_fraction":sum(r["hit"] for r in rows if r["method"]=="PT")/(instances*seeds),
        "gibbs_hit_fraction":sum(r["hit"] for r in rows if r["method"]=="Gibbs")/(instances*seeds),
        "caution":"Paired seed labels do not imply common random-number streams. "
        "Spin updates are counted, but replica storage, swap arithmetic, target-oracle "
        "overhead and checkpoint costs are not monetized. Instances (not trials) are "
        "the statistical units. 4-city symmetric TSP is only an M0 diagnostic.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--family",choices=("tsp","maxcut"),default="tsp")
    p.add_argument("--size",type=int,default=4)
    p.add_argument("--instances",type=int,default=4)
    p.add_argument("--trials",type=int,default=4)
    p.add_argument("--cycles",type=int,default=250)
    p.add_argument("--instance-seed",type=int,default=2026110600)
    p.add_argument("--solver-seed",type=int,default=2026110700)
    p.add_argument("--betas",default=",".join(str(x) for x in DEFAULT_BETAS))
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    try:
        betas=tuple(float(x.strip()) for x in a.betas.split(","))
        if not (a.instances>0 and a.trials>0 and a.cycles>0):
            raise ValueError("instances/trials/cycles must be positive")
        if len(betas)<2 or any(not math.isfinite(x) or x<=0 for x in betas) or any(x>=y for x,y in zip(betas,betas[1:])):
            raise ValueError("betas must be positive, finite and increasing")
        if not ((a.family=="tsp" and a.size in (3,4)) or (a.family=="maxcut" and 2<=a.size<=16)):
            raise ValueError("M0 exact oracle supports 3/4-city TSP or 2-16 spin MaxCut")
        if a.output.exists():
            raise FileExistsError("output directory already exists")
        # Only create output after input validation; never overwrite prior runs.
        out=[]
        for ii in range(a.instances):
            seed=a.instance_seed+ii
            inst=(model.tsp_instance(a.size,seed) if a.family=="tsp" else model.maxcut_instance(a.size,seed))
            for jj in range(a.trials):
                trial_seed=a.solver_seed+jj
                for row in run_case(inst,trial_seed,a.cycles,betas):
                    out.append(dict(instance_seed=seed,trial_index=jj,**row))
        summary=summarize(out,a.family,a.size,a.instances,a.trials,a.cycles,betas)
        summary["source_sha256"]={path.name:hashlib.sha256(path.read_bytes()).hexdigest()
          for path in (Path(__file__),Path(model.__file__),Path(pt.__file__))}
        a.output.mkdir(parents=True,exist_ok=False)
        (a.output/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
        with (a.output/"paired_runs.csv").open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(out[0]))
            w.writeheader()
            w.writerows(out)
        digests={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in a.output.iterdir()}
        (a.output/"SHA256SUMS.json").write_text(json.dumps(digests,indent=2,sort_keys=True)+"\n")
        print(json.dumps(summary,indent=2))
    except (ValueError,FileExistsError) as exc:
        p.error(str(exc))

if __name__=="__main__":
    main()
