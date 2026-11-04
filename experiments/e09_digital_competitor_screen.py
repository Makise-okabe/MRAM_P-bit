#!/usr/bin/env python3
"""NEW E09C ideal-digital Max-Cut pilot. NO analog MRAM errors or speed claims.

Measure the exact digital incremental-field competitor under paired starts and
random streams. Its identical-quality parity is a mandatory baseline for F7.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from experiments.ising_reference import exact_maxcut, trajectory, cut_value

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--restarts",type=int,default=20)
    p.add_argument("--sweeps",type=int,default=12)
    args=p.parse_args()
    if args.out.exists():p.error("Refusing overwrite")
    if not 1 <= args.restarts <= 1000 or not 1 <= args.sweeps <= 200:
        p.error("Out-of-range effort budget")
    records=[]
    for graph_id,(n,density) in enumerate(((12,0.25),(14,0.40),(16,0.60))):
        rng=np.random.default_rng(611040+graph_id)
        x=np.where(rng.random((n,n)) < density, rng.integers(1,4,(n,n)),0)
        a=np.triu(x,1);a=a+a.T
        optimum,_=exact_maxcut(a)
        degree=np.count_nonzero(a,axis=1)
        successes=0
        raw_full=[]
        raw_incremental=[]
        for attempt in range(args.restarts):
            rr=np.random.default_rng(20261104+graph_id*10000+attempt)
            initial=rr.choice([-1,1],n)
            order=np.concatenate([rr.permutation(n) for _ in range(args.sweeps)])
            uniforms=rr.random(len(order))
            betas=np.repeat(np.linspace(0.0,1.5,args.sweeps),n)
            full=trajectory(a,initial,order,uniforms,betas,mode="full_field")
            incr=trajectory(a,initial,order,uniforms,betas,mode="incremental",check_cache=True)
            for key in ("decisions","cuts","spins"):
                np.testing.assert_array_equal(full[key],incr[key])
            successes+=int(cut_value(a,full["spins"])==optimum)
            # Counts of nonzero integer coefficient contributions, not cycles/energy.
            full_ops=int(degree[order].sum())
            incremental_ops=int(degree.sum()) # exact initial fields
            s=initial.copy()
            for k,new in zip(order,full["decisions"]):
                if s[k] != new:
                    incremental_ops+=int(degree[k])
                    s[k]=new
            np.testing.assert_array_equal(s,full["spins"])
            raw_full.append(full_ops)
            raw_incremental.append(incremental_ops)
        records.append({
            "n":n,"edge_density_spec":density,
            "graph_sha256":hashlib.sha256(a.astype("<i8").tobytes()).hexdigest(),
            "edges":int(np.count_nonzero(np.triu(a,1))),
            "max_cut_exact":int(optimum),
            "restarts":args.restarts,"sweeps":args.sweeps,
            "success_count_exact_digital":successes,
            "success_rate_exact_digital":successes/args.restarts,
            "full_recompute_nonzero_terms_total":sum(raw_full),
            "incremental_nonzero_terms_total":sum(raw_incremental),
            "incremental_terms_over_full_terms":sum(raw_incremental)/sum(raw_full),
            "full_vs_incremental_quality_and_trajectory_identical":True,
            "digital_field_cache_size_in_integers":n
        })
    report={
        "experiment":"E09C_new_exact_digital_competitor_screen",
        "evidence_class":"FRESH_EXACT_SOFTWARE_BENCHMARK_ONLY",
        "uses_earlier_read_current_results":False,
        "uses_analog_mram_model":False,
        "new_spectre_data":False,
        "claim":"A fair Ising target must outperform/justify itself against this exact incremental-field competitor at comparable total costs.",
        "caution":"Term counts are not measured runtime/energy; no noisy MRAM solver run was executed.",
        "results":records
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"out":str(args.out),"evidence_class":report["evidence_class"],
                      "results":[{"n":r["n"],"digital_success":r["success_rate_exact_digital"],
                        "cache_term_ratio":r["incremental_terms_over_full_terms"]} for r in records]},indent=2))
if __name__=="__main__":main()
