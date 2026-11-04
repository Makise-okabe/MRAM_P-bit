#!/usr/bin/env python3
"""Fresh dependency-free exact-digital Ising/Max-Cut baseline (NOT MRAM hardware).
No PDK values, old read currents, analog models or claimed circuit power/timing.
"""
import argparse
import hashlib
import json
import math
import random
from pathlib import Path

def edge_list(a):
    return [(i,j,a[i][j]) for i in range(len(a))
            for j in range(i+1,len(a)) if a[i][j]]

def cut(edges,s):
    return sum(w for i,j,w in edges if s[i] != s[j])

def exact_maxcut(edges,n):
    best=-1
    for bits in range(1<<(n-1)): # fix s[0]=+1
        s=[1]+[1 if (bits>>i)&1 else -1 for i in range(n-1)]
        best=max(best,cut(edges,s))
    return best

def graph(n,density,seed):
    rng=random.Random(seed)
    a=[[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            if rng.random()<density:
                a[i][j]=a[j][i]=rng.randint(1,3)
    return a

def field(a,s,k):
    return -sum(w*s[j] for j,w in enumerate(a[k]) if w)

def paired_digital_run(a,init,order,uniforms,betas):
    n=len(a)
    full=init.copy()
    cache=init.copy()
    h=[field(a,cache,i) for i in range(n)]
    degree=[sum(bool(w) for w in row) for row in a]
    full_terms=0
    cache_terms=sum(degree)
    flips=0
    for k,u,beta in zip(order,uniforms,betas):
        f=field(a,full,k)
        if f != h[k]:
            raise AssertionError("Cached field does not match exact full field")
        full_terms+=degree[k]
        next_spin=1 if u<0.5*(1+math.tanh(beta*f)) else -1
        delta=next_spin-full[k]
        if delta:
            full[k]=cache[k]=next_spin
            flips+=1
            for j,w in enumerate(a[k]):
                if w:
                    h[j]-=w*delta
                    cache_terms+=1
        if full != cache or h != [field(a,cache,j) for j in range(n)]:
            raise AssertionError("Full and incremental update diverged")
    return full,full_terms,cache_terms,flips

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--restarts",type=int,default=20)
    p.add_argument("--sweeps",type=int,default=12)
    args=p.parse_args()
    if args.out.exists():p.error("Refusing overwrite")
    if not (1<=args.restarts<=1000 and 2<=args.sweeps<=200):
        p.error("Invalid budget")
    records=[]
    for idx,(n,density) in enumerate(((12,0.25),(14,0.40),(16,0.60))):
        a=graph(n,density,611040+idx)
        edges=edge_list(a)
        optimum=exact_maxcut(edges,n)
        successes=full_total=cache_total=flip_total=0
        for attempt in range(args.restarts):
            rng=random.Random(20261104+idx*10000+attempt)
            initial=[rng.choice((-1,1)) for _ in range(n)]
            order=[]
            for sweep in range(args.sweeps):
                perm=list(range(n))
                rng.shuffle(perm)
                order.extend(perm)
            uniforms=[rng.random() for _ in order]
            betas=[1.5*(i//n)/(args.sweeps-1) for i in range(len(order))]
            spins,full,cache,flips=paired_digital_run(
                a,initial,order,uniforms,betas)
            successes+=int(cut(edges,spins)==optimum)
            full_total+=full
            cache_total+=cache
            flip_total+=flips
        records.append({
            "spins":n,"specified_edge_probability":density,
            "edge_count":len(edges),
            "graph_sha256":hashlib.sha256(json.dumps(a).encode()).hexdigest(),
            "exact_max_cut":optimum,"restarts":args.restarts,"sweeps":args.sweeps,
            "successes_exact_digital":successes,
            "success_rate_exact_digital":successes/args.restarts,
            "full_recompute_nonzero_terms":full_total,
            "incremental_nonzero_terms":cache_total,
            "incremental_to_full_nonzero_term_ratio":cache_total/full_total if full_total else None,
            "flips":flip_total,
            "full_vs_incremental_exact_parity_each_update":True})
    out={"experiment":"E09_new_exact_digital_competitor_stdlib",
        "evidence_class":"FRESH_EXACT_DIGITAL_SOFTWARE_ONLY",
        "new_target_spectre_results":False,
        "historical_electrical_results_used":False,
        "analog_error_kernel":False,
        "caution":"Operation counts are abstract nonzero terms, not circuit speed or energy.",
        "results":records}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"out":str(args.out),
        "results":[{"spins":r["spins"],
        "exact_digital_success_rate":r["success_rate_exact_digital"],
        "cache_to_full_term_ratio":r["incremental_to_full_nonzero_term_ratio"]}
        for r in records]},indent=2))

if __name__=="__main__":
    main()
