#!/usr/bin/env python3
"""E1 ideal-Gibbs, represented-energy-retained weighted Max-Cut pilot.

Original Biq Mac graph weights used ONLY for external evaluation and
source-weight-based scale fitting. Controller selection uses represented
energy, never original-cut oracle. Deterministic paired random streams.

This is a first solver/representation comparison, NOT a characterized
STT-MRAM device response, a physically bit-true arithmetic model,
a certified optimality claim, timing, memory-energy or area result.
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
from experiments.m1_coupling_formats import (
    format_bits, format_positive_levels, quantized_level, tune_scale
)

FORMATS = ("fp6_fn", "int6", "bfp6")
SCALE_POLICIES = ("fullscale", "mse")


def select_scale(values, fmt, policy):
    """Coefficient-only adaptation, never optimization-output tuning."""
    if not values:
        return 1.0
    vmax = max(abs(v) for v in values)
    if vmax == 0:
        return 1.0
    if policy == "mse":
        # Essential fair INT control: a shared unit scale represents every
        # small signed INTEGER exactly if all weights fit signed INT range.
        # The historical heuristic grid around maxabs/qmax omitted 1.0.
        # This check uses source coefficients only, not solver/optimum data.
        if fmt == "int6" and vmax <= 31 and all(v == round(v) for v in values):
            return 1.0
        scale, _ = tune_scale(values, fmt)
        return scale
    if policy != "fullscale":
        raise ValueError("unknown scale policy")
    upper = format_positive_levels(fmt)[-1] if fmt.startswith("fp") \
        else (1 << (format_bits(fmt)-1)) - 1
    if fmt.startswith("bfp"):
        exp = math.floor(math.log2(vmax / upper))
        scale = 2.0**exp
        if scale * upper < vmax:
            scale *= 2.0
        return scale
    return vmax / upper


def prepare(graph, fmt, policy):
    """One globally symmetric J=-w; h=0. Count nominal dense storage only."""
    edges = [(i, j, -float(w)) for i, j, w in graph.edges]
    if fmt == "ref64":
        scale = 1.0
        quantized = [v for _, _, v in edges]
    else:
        scale = select_scale([v for _, _, v in edges], fmt, policy)
        quantized = [quantized_level(v, scale, fmt)
                     for _, _, v in edges]
    adj = [[] for _ in range(graph.n)]
    represented_edges = []
    for (i,j,v),q in zip(edges,quantized):
        adj[i].append((j,q))
        adj[j].append((i,q))
        represented_edges.append((i,j,q))
    abs_total = sum(abs(v) for _,_,v in edges)
    abs_err = sum(abs(v-q) for (_,_,v),q in zip(edges,quantized))
    mse = sum((v-q)**2 for (_,_,v),q in zip(edges,quantized)) / max(1,len(edges))
    zeroed = sum(v != 0 and q == 0 for (_,_,v),q in zip(edges,quantized))
    metadata_bits = 0 if fmt=="ref64" else 8 if fmt.startswith("bfp") else 32
    bits_per_edge = 64 if fmt=="ref64" else format_bits(fmt)
    return dict(adjacency=adj,edges=represented_edges,scale=scale,
                zeroed_edges=zeroed,relative_abs_coefficient_error=abs_err/abs_total if abs_total else 0.0,
                coefficient_mse=mse,
                nominal_dense_coefficient_bits=graph.n*(graph.n-1)//2*bits_per_edge,
                scale_metadata_bits=metadata_bits,
                nominal_dense_storage_bits=graph.n*(graph.n-1)//2*bits_per_edge + metadata_bits)


def original_cut(graph, spins):
    """Original source weights, independent of the represented model."""
    return sum((float(w) for i,j,w in graph.edges if spins[i] != spins[j]),0.0)


def represented_energy(edges, spins):
    return -sum(q*spins[i]*spins[j] for i,j,q in edges)


def beta_from_original_graph(graph):
    """Shared across formats: beta=1/(mean_abs_weight*sqrt(mean_degree)).

    This is a deterministic, illustrative dimensionless normalization for
    solver testing, not a calibrated p-bit voltage/gain/temperature relation.
    """
    m=len(graph.edges)
    if m == 0:
        return 1.0
    avg_abs=sum(abs(float(w)) for _,_,w in graph.edges)/m
    mean_degree=2*m/graph.n
    return 1.0/(max(1e-30,avg_abs)*math.sqrt(max(1,mean_degree)))


def solve(graph, representation, beta, updates, seed):
    """One asynchronous Gibbs proposal/step, track lowest REPRESENTED E."""
    rng=random.Random(seed)
    n=graph.n
    spins=[1 if rng.randrange(2) else -1 for _ in range(n)]
    adj=representation["adjacency"]
    fields=[sum(q*spins[j] for j,q in adj[i]) for i in range(n)]
    energy=represented_energy(representation["edges"],spins)
    best_energy=energy
    best_state=tuple(spins)
    flips=0
    improvements=0
    for _ in range(updates):
        i=rng.randrange(n)
        u=rng.random()  # advance RNG identically for every representation
        old=spins[i]
        new=1 if u<sigmoid(2*beta*fields[i]) else -1
        if new != old:
            delta_s=new-old
            energy += 2*old*fields[i]
            spins[i]=new
            flips+=1
            for j,q in adj[i]:
                fields[j]+=q*delta_s
            # H_i has no diagonal term and is unchanged by s_i's flip.
        if energy < best_energy:
            best_energy=energy
            best_state=tuple(spins)
            improvements+=1
    # Check incremental bookkeeping against independent recomputation.
    check=represented_energy(representation["edges"],spins)
    tol=1e-7*max(1,abs(check))
    if not abs(check-energy)<=tol:
        raise AssertionError(f"incremental energy mismatch: {check} != {energy}")
    best_check=represented_energy(representation["edges"],best_state)
    if not abs(best_check-best_energy)<=1e-7*max(1,abs(best_check)):
        raise AssertionError("best-state represented energy mismatch")
    return dict(seed=seed,attempted_updates=updates,actual_flips=flips,
                improvements=improvements,
                returned_original_cut=original_cut(graph,best_state),
                final_original_cut=original_cut(graph,spins),
                returned_represented_energy=best_check,
                final_represented_energy=check,
                returned_state_hex=format(sum((1<<i) for i,s in enumerate(best_state) if s>0),"x"))


def run(graphs, fmts, policies, updates, seeds, base_seed, output):
    if not graphs or not fmts or not policies:
        raise ValueError("missing graphs, formats or policies")
    if updates < 1 or seeds < 1:
        raise ValueError("updates and seeds must be >=1")
    output.mkdir(parents=True,exist_ok=False)
    records=[]
    qrows=[]
    source=[]
    for idx,path in enumerate(graphs):
        graph=load_rudy(path)
        if graph.n>128:
            raise ValueError(f"graph >128 vertices cannot fit the intended HW: {path}")
        beta=beta_from_original_graph(graph)
        source.append(dict(filename=path.name,sha256=graph.sha256,
                           n=graph.n,m=graph.raw_edge_count,beta=beta))
        configs=[("ref64","source")]
        configs.extend((fmt,policy) for fmt in fmts for policy in policies)
        for fmt,policy in configs:
            p=prepare(graph,fmt,policy)
            config=dict(graph=path.name,graph_sha256=graph.sha256,
                        n=graph.n,raw_m=graph.raw_edge_count,format=fmt,
                        scale_policy=policy,scale=p["scale"],
                        zeroed_edges=p["zeroed_edges"],
                        relative_abs_coefficient_error=p["relative_abs_coefficient_error"],
                        coefficient_mse=p["coefficient_mse"],
                        nominal_dense_coefficient_bits=p["nominal_dense_coefficient_bits"],
                        scale_metadata_bits=p["scale_metadata_bits"],
                        nominal_dense_storage_bits=p["nominal_dense_storage_bits"],
                        beta=beta)
            qrows.append(config)
            for run_idx in range(seeds):
                # Identical initial-state, spin-index and uniform draws per
                # graph/seed for all representations and scale policies.
                seed=base_seed+idx*100000+run_idx
                result=solve(graph,p,beta,updates,seed)
                records.append({**config,**result})
            avg=sum(r["returned_original_cut"] for r in records[-seeds:])/seeds
            print(f"{path.name:20s} {fmt:7s} {policy:9s} "
                  f"zeroed={p['zeroed_edges']:5d}/{len(graph.edges):5d} "
                  f"rel_L1={p['relative_abs_coefficient_error']:.5g} "
                  f"returned_Cut_mean={avg:.5f}",flush=True)
    with (output/"paired_returns.csv").open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]))
        writer.writeheader();writer.writerows(records)
    with (output/"representation_audit.csv").open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(qrows[0]))
        writer.writeheader();writer.writerows(qrows)
    manifest=dict(status="E1_IDEAL_SOFTWARE_COMPLETE",
       scope="paired ideal Gibbs/quantization solver PILOT with represented-energy retention, NOT stochastic MTJ, exact ML/Max-Cut optimum, bit-true RTL or ASIC cost",
       source_graphs=source, formats=fmts,scale_policies=policies,
       updates_per_run=updates,paired_seeds_per_graph=seeds,base_seed=base_seed,
       beta_rule="shared beta=1/(mean original nonzero abs weight * sqrt(mean nonzero degree))",
       selection="best visited represented Ising energy (strict improvement, earliest tie)",
       evaluation="original unquantized weighted cut ONLY for external score",
       calibration="per-graph source J coefficient-only scale; no quality/optimum labels",
       limits="single fixed-beta illustrative pilot; independent graph is statistical unit; no confidence interval, physical MTJ, power, timing, optimizer convergence or certified reference gap",
       total_records=len(records),code_sha256={
           str(p.relative_to(Path(__file__).resolve().parents[1])):
              hashlib.sha256(p.read_bytes()).hexdigest()
           for p in (Path(__file__).resolve(),
                     Path(__file__).resolve().parent/"biqmac_maxcut.py",
                     Path(__file__).resolve().parent/"m1_coupling_formats.py",
                     Path(__file__).resolve().parent/"m0_ising_math.py")})
    (output/"e1_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("M1 IDEAL MAXCUT PILOT COMPLETE (not device evidence):",len(records),"paired runs")
    return records


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--graph",type=Path,action="append",required=True)
    ap.add_argument("--formats",default="fp6_fn,int6,bfp6")
    ap.add_argument("--scale-policies",default="fullscale,mse")
    ap.add_argument("--updates",type=int,default=5000)
    ap.add_argument("--seeds",type=int,default=3)
    ap.add_argument("--seed",type=int,default=20261107)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    fmts=tuple(x.strip() for x in a.formats.split(","))
    policies=tuple(x.strip() for x in a.scale_policies.split(","))
    if len(set(fmts))!=len(fmts) or any(x not in FORMATS for x in fmts):
        ap.error("only frozen six-bit fp6_fn,int6,bfp6 supported")
    if len(set(policies))!=len(policies) or any(x not in SCALE_POLICIES for x in policies):
        ap.error("policies must be fullscale or mse")
    if a.output.exists():
        ap.error("output already exists")
    run(a.graph,fmts,policies,a.updates,a.seeds,a.seed,a.output)


if __name__ == "__main__":
    main()
