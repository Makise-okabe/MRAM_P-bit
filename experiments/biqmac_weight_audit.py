#!/usr/bin/env python3
"""M0: original Mac graph weight-range audit (NO solver / precision win).

Accept original Biq Mac Mac graphs from both /rudy and /ising.
Use exact Decimal weights from biqmac_maxcut.load_rudy. Save a JSON
audit with immutable source hash and explicit simple INT6 diagnostic.
All optimization quality and optimum-reference fields remain pending.
"""
import argparse
from decimal import Decimal, ROUND_HALF_EVEN
import json
from pathlib import Path

from experiments.biqmac_maxcut import audit_graph, load_rudy


def weight_statistics(graph):
    weights = [w for _, _, w in graph.edges]  # effective nonzero edges
    abs_weights = sorted(abs(w) for w in weights)
    positives = sum(1 for w in weights if w > 0)
    negatives = sum(1 for w in weights if w < 0)
    density = Decimal(len(graph.edges)) / Decimal(graph.n * (graph.n-1) // 2) if graph.n > 1 else Decimal(0)
    result = {
        "positive_nonzero_edges": positives,
        "negative_nonzero_edges": negatives,
        "effective_edge_density": str(density),
        "distinct_nonzero_edge_weights": len(set(weights)),
        "all_original_nonzero_weights_integral": all(w == w.to_integral_value() for w in weights),
    }
    if not abs_weights:
        result.update(min_nonzero_abs=None, max_nonzero_abs=None,
                      abs_weight_ratio=None, naive_int6_zeroed_edges=0,
                      naive_int6_zeroed_fraction=None,
                      naive_int6_normalized_abs_error=None)
        return result
    lo,hi=abs_weights[0],abs_weights[-1]
    # Purely descriptive full-scale INT6 diagnostic. NOT a calibrated INT6
    # baseline and NOT a claim that FP would preserve all of these edges.
    scale=hi / Decimal(31)
    quantized = [
       min(31,max(-31,int((w / scale).to_integral_value(rounding=ROUND_HALF_EVEN))))
       for w in weights
    ]
    zeroed=sum(w != 0 and code == 0 for w,code in zip(weights,quantized))
    total_abs=sum(abs(w) for w in weights)
    absolute_error=sum(abs(w-Decimal(q)*scale) for w,q in zip(weights,quantized))
    result.update({
       "min_nonzero_abs": str(lo),
       "max_nonzero_abs": str(hi),
       "abs_weight_ratio": str(hi/lo),
       "naive_int6_global_fullscale": str(scale),
       "naive_int6_zeroed_edges": zeroed,
       "naive_int6_zeroed_fraction": str(Decimal(zeroed)/Decimal(len(weights))),
       "naive_int6_normalized_abs_error": str(absolute_error/total_abs),
       "naive_int6_diagnostic_rule": "symmetric signed [-31,31], maxabs/31 scale, ROUND_HALF_EVEN; illustrative only; optimized INT6 baseline not run",
    })
    return result


def collect(file, seed):
    graph=load_rudy(file)
    a=audit_graph(graph, n_random_states=32, seed=seed)
    a["weight_statistics"]=weight_statistics(graph)
    a["source_class"]="official Mac graph; verify exact origin URL in manifest"
    a["quality_status"]="NO_SOLVER_RUN"
    a["format_status"]="NO_FP_INT_BFP_COMPARISON"
    return a


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", action="append", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--seed",type=int,default=20261107)
    a=p.parse_args()
    reports=[collect(f,a.seed) for f in a.file]
    content={"status":"M0_WEIGHT_AUDIT_PASS","graph_count":len(reports),
             "evidence":"Source-weight distribution and exact mapping only, not original-cut solver quality or hardware cost",
             "reports":reports}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x",encoding="utf-8") as out:
        out.write(json.dumps(content,indent=2,sort_keys=True)+"\n")
    for r in reports:
        st=r["weight_statistics"]
        print(f"{Path(r['source']).name}: n={r['n']}, m={r['raw_edge_count']}, "+
              f"min|w|={st['min_nonzero_abs']} max|w|={st['max_nonzero_abs']} "+
              f"ratio={st['abs_weight_ratio']} "+
              f"INT6-global-zeroed={st['naive_int6_zeroed_edges']} "
              f"sha256={r['sha256']}")
    print("M0_WEIGHT_AUDIT_PASS — no solver or device experiment")
    print(f"Report: {a.output}")


if __name__=="__main__":
    main()
