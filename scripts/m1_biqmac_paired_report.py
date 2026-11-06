#!/usr/bin/env python3
"""Paired seed-level diagnostic for a completed E1 ideal Max-Cut pilot.

No new solver run. Reads existing paired_returns.csv and checks that each
graph/seed has exactly one ref64 row and unique candidate format/scale rows.
No significance test is asserted from 3 seeds; independent graph is the
proper statistical unit for subsequent cross-graph inference.
"""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def analyze(rows):
    table={}
    base={}
    graph_seeds=defaultdict(set)
    for row in rows:
        graph=row["graph"]
        source=row["graph_sha256"]
        seed=int(row["seed"])
        key=(graph,source,seed,row["format"],row["scale_policy"])
        if key in table:
            raise ValueError(f"duplicate paired result {key}")
        table[key]=row
        graph_seeds[(graph,source)].add(seed)
        if row["format"]=="ref64":
            bkey=(graph,source,seed)
            if bkey in base:
                raise ValueError(f"duplicate ref64 source {bkey}")
            base[bkey]=float(row["returned_original_cut"])
    if not rows:
        raise ValueError("no rows")
    groups=defaultdict(list)
    for key,row in table.items():
        graph,source,seed,fmt,policy=key
        bkey=(graph,source,seed)
        if bkey not in base:
            raise ValueError(f"missing reference {bkey}")
        current=float(row["returned_original_cut"])
        ref=base[bkey]
        groups[(graph,source,fmt,policy)].append({
            "seed":seed,
            "returned_cut":current,
            "reference_returned_cut":ref,
            "paired_delta_cut":current-ref,
            "flips":int(row["actual_flips"]),
            "improvements":int(row["improvements"]),
            "final_cut":float(row["final_original_cut"]),
        })
    records=[]
    for (graph,source,fmt,policy),values in sorted(groups.items()):
        values.sort(key=lambda r:r["seed"])
        seeds=graph_seeds[(graph,source)]
        if {r["seed"] for r in values}!=seeds:
            raise ValueError(f"not all seeds used by {graph} {fmt} {policy}")
        d=[x["paired_delta_cut"] for x in values]
        n=len(d)
        rows_here=[table[(graph,source,r["seed"],fmt,policy)] for r in values]
        rr=dict(graph=graph,graph_sha256=source,format=fmt,scale_policy=policy,
                paired_seed_count=n,
                mean_returned_cut=sum(x["returned_cut"] for x in values)/n,
                mean_reference_cut=sum(x["reference_returned_cut"] for x in values)/n,
                mean_paired_delta_cut=sum(d)/n,
                min_paired_delta_cut=min(d),max_paired_delta_cut=max(d),
                wins_vs_reference=sum(x>0 for x in d),
                ties_vs_reference=sum(x==0 for x in d),
                losses_vs_reference=sum(x<0 for x in d),
                mean_actual_flips=sum(x["flips"] for x in values)/n,
                mean_returned_minus_final_original_cut=sum(
                    x["returned_cut"]-x["final_cut"] for x in values)/n,
                zeroed_edges=int(rows_here[0]["zeroed_edges"]),
                relative_abs_coefficient_error=float(rows_here[0]["relative_abs_coefficient_error"]),
                zeroed_abs_weight_fraction=(
                    float(rows_here[0]["zeroed_abs_weight_fraction"])
                    if "zeroed_abs_weight_fraction" in rows_here[0]
                    else None),
                per_seed=values)
        records.append(rr)
    # Compare the MSE configurations directly seed-for-seed.
    cross=[]
    for (graph,source),seeds in sorted(graph_seeds.items()):
        configs=[("fp6_fn","mse"),("int6","mse"),("bfp6","mse")]
        for fmt,pol in configs:
            if any((graph,source,seed,fmt,pol) not in table for seed in seeds):
                raise ValueError(f"missing {fmt}/{pol} in {graph}")
        for a,b in ((configs[0],configs[1]),(configs[0],configs[2]),
                    (configs[1],configs[2])):
            values=[]
            for seed in sorted(seeds):
                x=float(table[(graph,source,seed,*a)]["returned_original_cut"])
                y=float(table[(graph,source,seed,*b)]["returned_original_cut"])
                values.append(dict(seed=seed,delta_cut=x-y))
            ds=[v["delta_cut"] for v in values]
            cross.append(dict(graph=graph,graph_sha256=source,
                candidate_a=f"{a[0]}:{a[1]}",candidate_b=f"{b[0]}:{b[1]}",
                delta_interpretation="A returned original cut minus B returned original cut",
                paired_seed_count=len(ds),
                mean_delta_cut=sum(ds)/len(ds),
                a_wins=sum(v>0 for v in ds),
                ties=sum(v==0 for v in ds),
                b_wins=sum(v<0 for v in ds),
                per_seed=values))
    return dict(status="PAIRED_DIAGNOSTIC_OK",configuration_summaries=records,
       direct_format_comparisons=cross,
       caveat="Only paired solver seeds within 4 source graphs; seeds are not independent graph instances; no device/circuit/optimum claim.")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    with a.csv.open(newline="",encoding="utf-8") as stream:
        rows=list(csv.DictReader(stream))
    report=analyze(rows)
    report["source_csv_sha256"]=hashlib.sha256(a.csv.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x",encoding="utf-8") as stream:
        stream.write(json.dumps(report,sort_keys=True,indent=2)+"\n")
    for row in report["configuration_summaries"]:
        if row["format"]=="ref64" or row["scale_policy"]=="mse":
            print(f"{row['graph']:20s} {row['format']:7s} {row['scale_policy']:7s} "
                  f"meanCut={row['mean_returned_cut']:.3f} "
                  f"deltaRef={row['mean_paired_delta_cut']:+.3f} "
                  f"win/tie/loss={row['wins_vs_reference']}/"
                  f"{row['ties_vs_reference']}/{row['losses_vs_reference']} "
                  f"zeroMass={row['zeroed_abs_weight_fraction']}")
    print("========== DIRECT 6-BIT PAIRING, MSE SCALES ==========")
    for row in report["direct_format_comparisons"]:
        print(f"{row['graph']:20s} {row['candidate_a']} - {row['candidate_b']}: "
              f"delta={row['mean_delta_cut']:+.3f} "
              f"wins/ties/losses={row['a_wins']}/{row['ties']}/{row['b_wins']}")
    print(f"PAIRED_DIAGNOSTIC_OK: {a.output}")


if __name__=="__main__":
    main()
