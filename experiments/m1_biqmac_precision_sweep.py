#!/usr/bin/env python3
"""M1 first global-scale 4/5/6/8-bit FP/INT/BFP precision-quality sweep.

Three ORIGINAL NUS E0-audited Biq Mac Mac calibration graphs (one signed
small-integer control, two wide-range). New paired 24-seed reference
FP64 on the SAME 50,000-update LINEAR beta schedule as every quantized
configuration. No source/cut optimum oracle in runtime output selection.

Only ideal mathematical Gibbs response, not STT-MRAM p-bit device data,
bit-true Q arithmetic, optimizing tile-scale formats or area/energy.
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

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph, prepare
from experiments.m1_biqmac_reference_quality_gate import (
    official_reference, solve_reference
)
from experiments.m1_precision_codebooks import (
    FAMILIES, WIDTHS, FP_LAYOUTS, SCALE_POLICY, build_global,
    describe_codebook
)

GRAPH_NAMES = ("w01_100.0", "t2g10_5555", "ising2.5-100_5555")
UPDATES_FROZEN = 50_000
SEEDS_FROZEN = 24
BASE_SEED_FROZEN = 20261201  # disjoint from 20261107 quality-gate seeds
ADDITIONAL_GAP_TOLERANCE_PP = 1.0
BOOTSTRAP_RESAMPLES = 4000
SCHEDULE = "linear"


def bootstrap_paired_ci(deltas, bootstrap_seed, replicates=BOOTSTRAP_RESAMPLES):
    """Nonparametric paired-seed CI for the MEAN additional gap.

    Confidence intervals describe seed-to-seed Monte Carlo variation
    WITHIN a source graph, NOT graph-population generalization or
    family-wise multiple-comparison-adjusted equivalence.
    """
    if len(deltas) < 2 or replicates < 1:
        raise ValueError("need >=2 paired seeds and positive resamples")
    if max(deltas) == min(deltas):
        return float(deltas[0]), float(deltas[0])
    rng = random.Random(bootstrap_seed)
    n = len(deltas)
    means = sorted(sum(deltas[rng.randrange(n)] for _ in range(n))/n
                   for _ in range(replicates))
    # nearest-rank quantile (predetermined)
    lo = means[max(0, math.ceil(0.025*replicates)-1)]
    hi = means[max(0, math.ceil(0.975*replicates)-1)]
    return lo, hi


def summarize(rows, graph_index):
    """Rows must contain ONE reference and ONE each of 12 configs/seed."""
    by_seed = {}
    by_config = {}
    for row in rows:
        seed = row["seed"]
        config = row["configuration"]
        key = (seed, config)
        if key in by_config:
            raise ValueError(f"duplicate run {key}")
        by_config[key] = row
        if config == "ref64":
            if seed in by_seed:
                raise ValueError("duplicate reference")
            by_seed[seed] = row
    seeds = sorted(by_seed)
    if len(seeds) < 2:
        raise ValueError("at least two fresh paired reference seeds required")
    configs = ["ref64"] + [f"{family}{width}" for family in FAMILIES for width in WIDTHS]
    for config in configs:
        if {seed for seed, tag in by_config if tag == config} != set(seeds):
            raise ValueError(f"missing paired samples for {config}")
    report=[]
    for config in configs:
        values=[by_config[(seed,config)] for seed in seeds]
        deltas=[v["optimality_gap_pct"]-by_seed[v["seed"]]["optimality_gap_pct"] for v in values]
        lower,upper=bootstrap_paired_ci(
            deltas, bootstrap_seed=3000 + graph_index*1000 + configs.index(config))
        mean_delta=statistics.mean(deltas)
        fmt=values[0]
        report.append({
            "graph": fmt["graph"],"graph_sha256":fmt["graph_sha256"],
            "official_optimum":fmt["official_optimum"],
            "configuration":config,
            "family":fmt["family"],"width":fmt["width"],
            "layout":fmt["layout"],"scale":fmt["scale"],
            "paired_seeds":len(seeds),
            "mean_returned_original_cut":statistics.mean(r["returned_original_cut"] for r in values),
            "mean_optimality_gap_pct":statistics.mean(r["optimality_gap_pct"] for r in values),
            "mean_reference_gap_pct":statistics.mean(by_seed[seed]["optimality_gap_pct"] for seed in seeds),
            "mean_additional_gap_pp":mean_delta,
            "bootstrap_95_lo_additional_gap_pp":lower,
            "bootstrap_95_hi_additional_gap_pp":upper,
            "predeclared_useful_precision_gate":(
                "YES_PRELIMINARY_WITHIN_GRAPH" if upper <= ADDITIONAL_GAP_TOLERANCE_PP
                else "NO_OR_UNCERTAIN"),
            "beats_or_ties_ref_seeds":sum(d <= 0 for d in deltas),
            "zeroed_nonzero_edges":fmt["zeroed_nonzero_edges"],
            "zeroed_abs_weight_fraction":fmt["zeroed_abs_weight_fraction"],
            "relative_abs_coefficient_error":fmt["relative_abs_coefficient_error"],
            "nominal_one_copy_dense_total_bits":fmt["nominal_one_copy_dense_total_bits"],
            "mean_flips":statistics.mean(r["actual_flips"] for r in values)
        })
    return report


def run(graph_paths, reference_path, out, *, updates=UPDATES_FROZEN,
        seeds=SEEDS_FROZEN, base_seed=BASE_SEED_FROZEN):
    """Default real experiment is immutable; tests may call short tiny runs."""
    if out.exists():
        raise ValueError("results directory exists; cannot overwrite")
    if updates < 1 or seeds < 2:
        raise ValueError("updates/seeds invalid")
    if tuple(p.name for p in graph_paths) != GRAPH_NAMES:
        raise ValueError("graph names/order must be exactly the preregistered three")
    refs=json.loads(reference_path.read_text(encoding="utf-8"))
    if refs.get("reference_type") != "PUBLISHED_OPTIMUM":
        raise ValueError("source-matched published optimum required")
    out.mkdir(parents=True, exist_ok=False)
    runs=[]
    summary=[]
    source=[]
    configurations=[]
    for fmt in FAMILIES:
        for width in WIDTHS:
            configurations.append((f"{fmt}{width}",fmt,width))
    for graph_index,path in enumerate(graph_paths):
        g=load_rudy(path)
        if g.n != 100:
            raise ValueError("100-spin original graph required")
        refdata=refs["graphs"].get(path.name)
        if refdata is None:
            raise ValueError("no published optimum entry")
        optimum=official_reference(g,refdata,refs)
        beta=beta_from_original_graph(g)
        source.append({"file":path.name,"sha256":g.sha256,"n":g.n,
                       "raw_edge_count":g.raw_edge_count,
                       "nonzero_edge_count":len(g.edges),"published_optimum":optimum,
                       "published_table":refdata["table"],"pdf_page":refdata["pdf_page"],
                       "beta":beta})
        config_reps=[("ref64","ref",64,prepare(g,"ref64","source"))]
        for tag,family,width in configurations:
            config_reps.append((tag,family,width,build_global(g,family,width)))
        # Reuse the SAME seed/initial spin/selected index/uniform random
        # sequence across every representation at each update.
        per_graph=[]
        for config,family,width,representation in config_reps:
            exact_repr=(representation["edges"] == config_reps[0][3]["edges"])
            if family == "ref":
                meta=dict(scale=1.0,layout="FP64 unquantized source",zeroed_nonzero_edges=0,
                          zeroed_abs_weight_fraction=0.0,
                          relative_abs_coefficient_error=0.0,
                          nominal_one_copy_dense_total_bits=64*g.n*(g.n-1)//2)
            else:
                meta=dict(scale=representation["scale"],
                          layout=representation["codebook"]["layout"],
                          zeroed_nonzero_edges=representation["zeroed_edges"],
                          zeroed_abs_weight_fraction=representation["zeroed_abs_weight_fraction"],
                          relative_abs_coefficient_error=representation["relative_abs_coefficient_error"],
                          nominal_one_copy_dense_total_bits=representation["nominal_one_copy_dense_total_bits"])
            for k in range(seeds):
                seed=base_seed + graph_index*100000 + k
                result=solve_reference(g,representation,beta,updates,seed,SCHEDULE)
                score=float(result["returned_original_cut"])
                if score > optimum + 1e-7:
                    raise AssertionError(f"original cut beats published optimum: {path.name} {config} {seed}")
                rec={
                   "graph":path.name,"graph_sha256":g.sha256,
                   "official_optimum":optimum,"configuration":config,
                   "family":family,"width":width,
                   **meta,"beta":beta,"schedule":SCHEDULE,
                   "attempted_updates":updates,"seed":seed,
                   "returned_original_cut":score,
                   "optimality_gap_pct":100*(optimum-score)/optimum,
                   "actual_flips":result["actual_flips"],
                   "improvements":result["improvements"],
                   "returned_represented_energy":result["returned_represented_energy"],
                   "returned_state_hex":result["returned_state_hex"]
                }
                if exact_repr and family!="ref":
                    # Exact INT on small graphs must reproduce bit-identical
                    # reference if RNG, beta and update/retention are fair.
                    baseline=next((r for r in per_graph if r["configuration"]=="ref64" and r["seed"]==seed),None)
                    if baseline is None or (baseline["returned_state_hex"]!=rec["returned_state_hex"]
                            or baseline["returned_original_cut"]!=rec["returned_original_cut"]
                            or baseline["actual_flips"]!=rec["actual_flips"]):
                        raise AssertionError(f"exact representation does not reproduce FP64: {path.name} {config} seed {seed}")
                per_graph.append(rec)
            print(f"{path.name:20s} {config:6s} scale={meta['scale']:.6g} "
                  f"zeroed={meta['zeroed_nonzero_edges']:<5d} "
                  f"gap={statistics.mean(r['optimality_gap_pct'] for r in per_graph[-seeds:]):.4f}%",
                  flush=True)
        runs.extend(per_graph)
        report=summarize(per_graph,graph_index)
        summary.extend(report)
        for r in report:
            if r["configuration"]!="ref64":
                print(f"  paired {r['configuration']:5s} delta={r['mean_additional_gap_pp']:+.3f}pp "
                      f"CI=[{r['bootstrap_95_lo_additional_gap_pp']:+.3f},"
                      f"{r['bootstrap_95_hi_additional_gap_pp']:+.3f}] "
                      f"useful={r['predeclared_useful_precision_gate']}",flush=True)
    for name,records in (("precision_paired_runs.csv",runs),
                         ("precision_summary.csv",summary)):
        with (out/name).open("x",newline="",encoding="utf-8") as stream:
            writer=csv.DictWriter(stream,fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    manifest = {
       "status":"PRECISION_IDEAL_GLOBAL_SOFTWARE_COMPLETE",
       "evidence":"E1 IDEAL Gibbs software only; no measured STT-MRAM physical response, exact hardware, area/energy or general precision knee",
       "freeze":"4/5/6/8 custom finite FP, symmetric INT, BFP global PoT",
       "codebooks":[describe_codebook(family,width) for family in FAMILIES for width in WIDTHS],
       "scale":"one source-coefficient MSE loggrid global scale; one edge encoded once and mirrored (exact J symmetry)",
       "scale_policy":SCALE_POLICY,
       "data_sources":source,
       "reference_json_sha256":hashlib.sha256(reference_path.read_bytes()).hexdigest(),
       "seed_base":base_seed,
       "new_24_seeds_disjoint_from_old_FP64_calibration":base_seed==BASE_SEED_FROZEN,
       "seeds_per_graph":seeds,"updates":updates,"schedule":SCHEDULE,
       "beta":"fixed graph-original beta_G normalization from prior FP64 calibration; linear 0.5beta_G to 2beta_G",
       "selection":"strict best represented Ising E visited; earliest tie; exact unrounded weights never used as runtime oracle",
       "external_score":"original unquantized signed weighted Max-Cut, published original optimum gap",
       "quality_gate":"within-graph one-sided criterion: 95% paired bootstrap two-sided upper endpoint for mean additional gap <= +1.0 percentage point vs paired FP64",
       "bootstrap_resamples":BOOTSTRAP_RESAMPLES,
       "uncertainty_scope":"paired independent solver seeds within ONE graph; 3 graphs all CAL, no independent graph population CI, multiple comparisons exploratory",
       "nominal_storage_scope":"single copy dense undirected-edge bits plus ONE metadata word; NOT total cell/memory/ports/update energy or CMOS mapped area",
       "total_runs":len(runs),
       "code_sha256":{
           str(p.relative_to(Path(__file__).resolve().parents[1])):
               hashlib.sha256(p.read_bytes()).hexdigest()
           for p in (Path(__file__).resolve(),
                     Path(__file__).parent/"m1_precision_codebooks.py",
                     Path(__file__).parent/"m1_biqmac_reference_quality_gate.py",
                     Path(__file__).parent/"m1_biqmac_ideal_pilot.py",
                     Path(__file__).parent/"biqmac_maxcut.py")
       }
    }
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"M1 GLOBAL PRECISION IDEAL COMPLETE {len(runs)} runs, output={out}",flush=True)
    return runs,summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    run(
      [Path("data/biqmac/raw/rudy/w01_100.0"),
       Path("data/biqmac/raw/ising/t2g10_5555"),
       Path("data/biqmac/raw/ising/ising2.5-100_5555")],
      Path("docs/BIQMAC_OFFICIAL_OPTIMA_2007.json"),
      args.out
    )


if __name__ == "__main__":
    main()
