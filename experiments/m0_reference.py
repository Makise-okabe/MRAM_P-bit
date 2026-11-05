#!/usr/bin/env python3
"""M0 clean-room ideal Ising mathematical baseline. No legacy device/results used."""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import random

def assert_ising(J,h):
    n=len(h)
    if n < 2 or len(J)!=n or any(len(r)!=n for r in J):
        raise ValueError("invalid Ising matrix dimensions")
    if not all(math.isfinite(x) for x in h) or not all(math.isfinite(v) for r in J for v in r):
        raise ValueError("nonfinite coefficients")
    for i in range(n):
        if abs(J[i][i]) > 1e-12:
            raise ValueError("nonzero diagonal")
        for j in range(i+1,n):
            if abs(J[i][j]-J[j][i]) > 1e-12:
                raise ValueError("non-symmetric coupling")

def energy(J,h,s,C=0.0):
    return C-sum(h[i]*s[i] for i in range(len(h)))-sum(
        J[i][j]*s[i]*s[j] for i in range(len(h)) for j in range(i+1,len(h)))

def exact(J,h,beta,C=0.0):
    assert_ising(J,h)
    if len(h)>16 or beta<=0:
        raise ValueError("exact requires N<=16 and beta>0")
    states=list(itertools.product((-1,1),repeat=len(h)))
    energies=[energy(J,h,s,C) for s in states]
    best=min(energies)
    logs=[-beta*(v-best) for v in energies]
    z=sum(math.exp(x) for x in logs)
    return dict(states=states,energies=energies,
                probabilities=[math.exp(x)/z for x in logs],
                ground_energy=best,ground_degeneracy=sum(abs(v-best)<1e-9 for v in energies))

def sigmoid(x):
    if x>=0:
        z=math.exp(-x)
        return 1/(1+z)
    z=math.exp(x)
    return z/(1+z)

def update(J,h,s,beta,rng):
    i=rng.randrange(len(h))
    field=h[i]+sum(J[i][j]*s[j] for j in range(len(h)) if i!=j)
    s[i]=1 if rng.random()<sigmoid(2*beta*field) else -1

def sample(J,h,beta,seed,burnin,records,thin):
    assert_ising(J,h)
    if beta<=0 or burnin<0 or records<1 or thin<1:
        raise ValueError("invalid sample budget")
    rng=random.Random(seed)
    s=[rng.choice((-1,1)) for _ in h]
    for _ in range(burnin):
        update(J,h,s,beta,rng)
    draws=[]
    for _ in range(records):
        for _ in range(thin):
            update(J,h,s,beta,rng)
        draws.append(tuple(s))
    return draws

def maxcut_instance(n,seed,density=.75):
    if not 2<=n<=16:
        raise ValueError("M0 MaxCut requires 2<=N<=16")
    rng=random.Random(seed)
    W=[[0.]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            if rng.random()<density:
                w=round(10**rng.uniform(-.4,.6),6)
                W[i][j]=W[j][i]=w
    J=[[-W[i][j]/2 for j in range(n)] for i in range(n)]
    return dict(kind="weighted_maxcut",J=J,h=[0.]*n,C=0.0,
                weights=W,instance_seed=seed)

def cut_value(W,s):
    return sum(W[i][j] for i in range(len(s)) for j in range(i+1,len(s))
               if s[i]!=s[j])

def tsp_instance(n,seed,A=20.,B=1.):
    """n*n binary one-hot variables mapped to Ising; small N exact M0 only."""
    if n not in (3,4) or A<=0 or B<=0:
        raise ValueError("M0 TSP requires 3 or 4 cities, A/B positive")
    rng=random.Random(seed)
    pts=[(rng.random(),rng.random()) for _ in range(n)]
    D=[[0. if i==j else math.dist(pts[i],pts[j]) for j in range(n)] for i in range(n)]
    N=n*n
    a=[0.]*N
    q=[[0.]*N for _ in range(N)]
    Cq=2*n*A
    def idx(city,slot):
        return city*n+slot
    def pair(x,y,w):
        i,j=sorted((x,y))
        if i==j:
            raise ValueError("diagonal QUBO")
        q[i][j]+=w
    for city in range(n):
        group=[idx(city,t) for t in range(n)]
        for k in group:
            a[k]-=A
        for i,j in itertools.combinations(group,2):
            pair(i,j,2*A)
    for t in range(n):
        group=[idx(c,t) for c in range(n)]
        for k in group:
            a[k]-=A
        for i,j in itertools.combinations(group,2):
            pair(i,j,2*A)
    for t in range(n):
        for c in range(n):
            for nxt in range(n):
                if c!=nxt:
                    pair(idx(c,t),idx(nxt,(t+1)%n),B*D[c][nxt])
    h=[-x/2 for x in a]
    J=[[0.]*N for _ in range(N)]
    C=Cq+sum(a)/2
    for i in range(N):
        for j in range(i+1,N):
            w=q[i][j]
            J[i][j]=J[j][i]=-w/4
            h[i]-=w/4
            h[j]-=w/4
            C+=w/4
    assert_ising(J,h)
    return dict(kind="tsp_onehot",J=J,h=h,C=C,instance_seed=seed,
                distance=D,n_cities=n,A=A,B=B,linear_qubo=a,quad_qubo=q,constant_qubo=Cq)

def tsp_qubo_energy(inst,s):
    x=[(v+1)//2 for v in s]
    return inst["constant_qubo"]+sum(a*b for a,b in zip(inst["linear_qubo"],x))+sum(
        inst["quad_qubo"][i][j]*x[i]*x[j] for i in range(len(x))
        for j in range(i+1,len(x)))

def tsp_objective(inst,s):
    n=inst["n_cities"]
    slots=[[c for c in range(n) if s[c*n+t]==1] for t in range(n)]
    if not all(len(z)==1 for z in slots):
        return dict(valid=False,tour_cost=None)
    tour=[v[0] for v in slots]
    if len(set(tour))!=n:
        return dict(valid=False,tour_cost=None)
    return dict(valid=True,tour_cost=sum(inst["distance"][tour[t]][tour[(t+1)%n]] for t in range(n)))

def run(inst,beta,seed,burnin,records,thin,out):
    J,h,C=inst["J"],inst["h"],inst["C"]
    ref=exact(J,h,beta,C)
    draws=sample(J,h,beta,seed,burnin,records,thin)
    count={s:0 for s in ref["states"]}
    for s in draws:
        count[s]+=1
    tv=.5*sum(abs(count[s]/records-p) for s,p in zip(ref["states"],ref["probabilities"]))
    result=dict(tier="E1 independent software M0, not MRAM device evidence",
                kind=inst["kind"],instance_seed=inst["instance_seed"],sampler_seed=seed,
                beta=beta,spin_count=len(h),burnin_updates=burnin,
                sampled_states=records,thin_updates=thin,
                exact_ground_energy=ref["ground_energy"],
                exact_degeneracy=ref["ground_degeneracy"],sampled_tv_distance=tv)
    out.mkdir(parents=True,exist_ok=False)
    (out/"m0_manifest.json").write_text(json.dumps(dict(instance=inst,result=result),
                                    indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    with (out/"m0_samples.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["trial","state_bits","original_energy","ground_hit","valid","tour_cost"])
        for i,s in enumerate(draws):
            obj=tsp_objective(inst,s) if inst["kind"]=="tsp_onehot" else dict(valid=True,tour_cost=None)
            e=energy(J,h,s,C)
            w.writerow([i,"".join("1" if v>0 else "0" for v in s),repr(e),
                        int(abs(e-ref["ground_energy"])<1e-9),int(obj["valid"]),obj["tour_cost"]])
    checks={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob("m0_*")}
    (out/"SHA256SUMS.json").write_text(json.dumps(checks,sort_keys=True,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--family",choices=["maxcut","tsp"],default="maxcut")
    p.add_argument("--size",type=int,default=8)
    p.add_argument("--instance-seed",type=int,default=20261106)
    p.add_argument("--sample-seed",type=int,default=20261107)
    p.add_argument("--beta",type=float,default=.5)
    p.add_argument("--burnin",type=int,default=4000)
    p.add_argument("--records",type=int,default=1000)
    p.add_argument("--thin",type=int,default=10)
    p.add_argument("--output",type=Path,default=Path("results/m0_demo"))
    a=p.parse_args()
    if not math.isfinite(a.beta) or a.beta<=0 or a.burnin<0 or a.records<1 or a.thin<1:
        p.error("invalid beta/update budgets")
    if a.output.exists():
        p.error("output exists: choose a NEW path")
    try:
        inst=maxcut_instance(a.size,a.instance_seed) if a.family=="maxcut" else tsp_instance(a.size,a.instance_seed)
        result=run(inst,a.beta,a.sample_seed,a.burnin,a.records,a.thin,a.output)
    except ValueError as e:
        p.error(str(e))
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
