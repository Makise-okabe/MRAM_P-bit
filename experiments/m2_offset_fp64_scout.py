#!/usr/bin/env python3
"""E2-OFFSET-SCOUT-01 — FP64-only, two CAL Biq Mac graphs; 240 new runs.

Explicit 8 Nov amendment to the original offset range (0,.05,.1,.2).
This diagnostic E2 grid is (0,.1,.2,.4,.8,1.6) LOGIT units — NOT measured
STT-MRAM calibration residuals and NOT a production voltage spec.
The published switching sigmoid only motivates the response form.

One persistent 100-spin offset population v_i ~ Uniform[-1,+1], inherited
EXACTLY from existing E2 seed/population. g_i=1 for all i; offset_i=d*v_i.
Same v reused at all levels, across both CAL graphs and all solver seeds.
No low-bit coefficients, no new annealing, no gain cross product, no RTL.

Reuse 48 matching FP64 ideal rows from immutable M1 SHA-verified 936-run
CSV; 2 graph x 5 nonzero halfspans x 24 seeds = EXACTLY 240 new runs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_ideal_pilot import prepare, beta_from_original_graph
from experiments.m1_biqmac_precision_sweep import (
    BASE_SEED_FROZEN, SEEDS_FROZEN, UPDATES_FROZEN, bootstrap_paired_ci
)
from experiments.m1_biqmac_reference_quality_gate import official_reference
from experiments.m2_e2_response_gate import (
    IDEAL_RUNS_SHA256, OFFSET_LOGIT_HALFSPAN, EVIDENCE, MODEL_SEED,
    build_e2_assumption, solve_with_response, validate_device_model,
)

GRAPH_SPECS=(("t2g10_5555",1),("ising2.5-100_5555",2))
LEVELS=(0.1,0.2,0.4,0.8,1.6)
ABS_ACCEPT_GAP=5.0
ABS_FAILURE_GAP=7.5
# DECLARED BEFORE results: 'clear practical deterioration' requires the
# paired seed-bootstrap CI lower bound on deterioration to exceed +1 pp.
NOTICEABLE_DEGRADATION_PP=1.0
IDEAL_CSV=Path("results/m1_precision_global_20261106T195502Z_3314224/precision_paired_runs.csv")
REFS=Path("docs/BIQMAC_OFFICIAL_OPTIMA_2007.json")


def paired_seed(graph_index:int) -> tuple[int,...]:
    return tuple(BASE_SEED_FROZEN+100000*graph_index+k for k in range(SEEDS_FROZEN))


def load_ideal_and_graphs(path: Path):
    if hashlib.sha256(path.read_bytes()).hexdigest()!=IDEAL_RUNS_SHA256:
        raise ValueError("frozen 936-run M1 ideal CSV SHA256 mismatch")
    records=list(csv.DictReader(path.open(newline="",encoding="utf-8")))
    if len(records)!=936:
        raise ValueError("frozen M1 ideal rows must total 936")
    refs=json.loads(REFS.read_text(encoding="utf-8"))
    if refs.get("reference_type")!="PUBLISHED_OPTIMUM":
        raise ValueError("source-matched published references required")
    source={}
    for name,graph_index in GRAPH_SPECS:
        g=load_rudy(Path("data/biqmac/raw/ising")/name)
        if g.n!=100:
            raise ValueError("source graph must have 100 spins")
        optimum=official_reference(g,refs["graphs"][name],refs)
        source[name]=(g,graph_index,optimum)
    seen=set()
    ideal={}
    expected={"w01_100.0":0,"t2g10_5555":1,"ising2.5-100_5555":2}
    allfmts={"ref64"}|{f"{f}{b}" for f in ("fp","int","bfp") for b in (4,5,6,8)}
    for rec in records:
        name=rec["graph"]; fmt=rec["configuration"]; seed=int(rec["seed"])
        if name not in expected or fmt not in allfmts:
            raise ValueError("unexpected M1 graph/format")
        ix=expected[name]
        if seed not in paired_seed(ix):
            raise ValueError("wrong frozen M1 seed placement")
        key=(name,fmt,seed)
        if key in seen:
            raise ValueError("duplicate frozen M1 row")
        seen.add(key)
        if rec["schedule"]!="linear" or int(rec["attempted_updates"])!=UPDATES_FROZEN:
            raise ValueError("frozen solver semantics mismatch")
        if name in source:
            graph,_,optimum=source[name]
            if graph.sha256!=rec["graph_sha256"] or float(rec["official_optimum"])!=optimum:
                raise ValueError("source graph SHA256/optimum mismatch")
            if fmt=="ref64":
                gap=float(rec["optimality_gap_pct"])
                score=float(rec["returned_original_cut"])
                if score>optimum+1e-7 or not math.isclose(gap,100*(optimum-score)/optimum,abs_tol=1e-8):
                    raise ValueError("frozen original-cut gap mismatch")
                if not rec["returned_state_hex"]:
                    raise ValueError("missing original best-state retention")
                ideal[(name,seed)]=gap
    if len(seen)!=936 or len(ideal)!=48:
        raise ValueError("expected 936 frozen rows and 48 paired ideal FP64 records")
    return source,ideal


def models(n:int):
    # Identical offset RNG vector to E2-GAIN-01's original build_e2_assumption.
    base=build_e2_assumption(n)
    v=[z/OFFSET_LOGIT_HALFSPAN for z in base["per_device_offset_logit"]]
    model_by_level={}
    for d in LEVELS:
        model=dict(base)
        model.update(
            source="E2 assumed logit-offset scout; NOT measured STT-MRAM residual",
            calibration_assumption="nominal switching transfer; persistent post-nominal synthetic offset",
            per_device_gain=[1.0]*n,
            per_device_offset_logit=[d*x for x in v],
            offset_logit_halfspan_assumed=d,
            underlying_population_v=v,
            gain_halfspan_assumed=0.0,
        )
        validate_device_model(model,n,offset_limit=d)
        model_by_level[d]=model
    return model_by_level


def ci_mean(values:list[float], seed:int):
    lo,hi=bootstrap_paired_ci(values,seed)
    return statistics.mean(values),lo,hi


def summary_rows(rows, ideal):
    summary=[]
    for gi,(name,graph_index) in enumerate(GRAPH_SPECS):
        seeds=paired_seed(graph_index)
        for li,d in enumerate((0.0,)+LEVELS):
            vals=[ideal[(name,k)] if d==0 else rows[(name,d,k)]["gap_pct"] for k in seeds]
            diffs=[v-ideal[(name,k)] for v,k in zip(vals,seeds)]
            mean,lo,hi=ci_mean(vals,61000+1000*gi+li)
            md,dl,dh=ci_mean(diffs,62000+1000*gi+li)
            regime=("acceptable" if hi<=ABS_ACCEPT_GAP else
                    "failure" if lo>ABS_FAILURE_GAP else
                    "degraded" if lo>ABS_ACCEPT_GAP and hi<=ABS_FAILURE_GAP else
                    "uncertain")
            summary.append(dict(
                graph=name,offset_logit_halfspan=d,n_seeds=SEEDS_FROZEN,
                mean_absolute_gap_pct=mean,ci95_abs_gap_lo_pct=lo,
                ci95_abs_gap_hi_pct=hi,
                mean_paired_deterioration_pp=md,ci95_deterioration_lo_pp=dl,
                ci95_deterioration_hi_pp=dh,
                deterioration_vs_ideal_supported=(dl>0),
                practical_deterioration_above_1pp_supported=(dl>NOTICEABLE_DEGRADATION_PP),
                regime_seed_conditional=regime,
                note="E2 assumed offset; CIs conditional on one graph/one device population"
            ))
    return summary


def write_csv(path: Path, rows: list[dict]):
    with path.open("x",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def run(ideal_csv:Path,output:Path|None, audit_only:bool=False):
    source,ideal=load_ideal_and_graphs(ideal_csv)
    for name,ix in GRAPH_SPECS:
        print(f"OFFSET SCOUT AUDIT {name}: FP64 ideal gap={statistics.mean(ideal[(name,k)] for k in paired_seed(ix)):.4f}% "
              f"24 paired seeds, original optimum={source[name][2]}",flush=True)
    print("OFFSET SCOUT AUDIT PASS: 936-run M1 SHA + two original graphs + 48 ideal rows",flush=True)
    if audit_only:
        return
    if output is None or output.exists():
        raise ValueError("supply new non-existing --out directory")
    m=models(100)
    output.mkdir(parents=True,exist_ok=False)
    sourceinfo={
        "evidence":"E2_ASSUMED_NOT_MEASURED",
        "amendment":"8 Nov 2026 explicit FP64-only offset diagnostic; original 0/.05/.10/.20 planned offset campaign deferred",
        "reason":"characterize FP64 response alone before selecting informative stress levels for fixed low-bit comparison",
        "model":"P(+1)=sigmoid(2*beta(t)*H_ref64 + d*v_i); gain=1",
        "d_halfspans_logit":list(LEVELS),
        "persistence":"one fixed 100-device v population shared levels/graphs/seeds",
        "measured_population":False,
        "source":"published 2026 STT-MTJ sigmoid motivates probability form but does NOT determine residual ranges",
        "device_model_seed":MODEL_SEED,
        "calibration":"nominal mapped switching probability, synthetic post-nominal offset; NOT extracted after physical calibration",
        "graph_roles":list(GRAPH_SPECS),"same_ideal_m1_csv_sha256":IDEAL_RUNS_SHA256,
        "n_ideal_reused":48,"n_new_solver_runs":240,
        "practical_noticeable_degradation_rule":"paired bootstrap 95% CI lower bound > +1.0 pp in original-optimum gap vs matched ideal",
        "quality_thresholds":{"acceptable_gap_pct":ABS_ACCEPT_GAP,"failure_gap_pct":ABS_FAILURE_GAP},
        "model_vectors":m,
        "uncertainty":"solver seeds only; one device population and two named CAL graphs; no silicon/manufacturing generalization",
    }
    (output/"E2_offset_scout_model.json").write_text(json.dumps(sourceinfo,indent=2,sort_keys=True)+"\n")
    rows={}
    with (output/"E2_offset_scout_runs.csv").open("x",newline="",encoding="utf-8") as f:
        cols=["graph","graph_sha256","offset_logit_halfspan","seed","official_optimum",
              "gap_pct","ideal_gap_pct","paired_deterioration_pp",
              "returned_original_cut","returned_state_hex","attempted_updates",
              "actual_flips","returned_represented_energy"]
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for name,ix in GRAPH_SPECS:
            g,_,optimum=source[name]
            beta=beta_from_original_graph(g)
            rep=prepare(g,"ref64","source")
            for d in LEVELS:
                model=m[d]
                for seed in paired_seed(ix):
                    x=solve_with_response(g,rep,beta,UPDATES_FROZEN,seed,model,
                                          offset_limit=d)
                    score=float(x["returned_original_cut"])
                    if score>optimum+1e-7:
                        raise AssertionError("published optimum exceeded")
                    gap=100*(optimum-score)/optimum
                    rec=dict(graph=name,graph_sha256=g.sha256,
                             offset_logit_halfspan=d,seed=seed,official_optimum=optimum,
                             gap_pct=gap,ideal_gap_pct=ideal[(name,seed)],
                             paired_deterioration_pp=gap-ideal[(name,seed)],
                             returned_original_cut=score,
                             returned_state_hex=x["returned_state_hex"],
                             attempted_updates=UPDATES_FROZEN,
                             actual_flips=x["actual_flips"],
                             returned_represented_energy=x["returned_represented_energy"])
                    w.writerow(rec);f.flush()
                    rows[(name,d,seed)]=rec
                print(f"OFFSET SCOUT {name} d=±{d:g} logit: 24/24 completed",flush=True)
    if len(rows)!=240:
        raise AssertionError("not 240 offset-scout new runs")
    summary=summary_rows(rows,ideal)
    write_csv(output/"E2_offset_scout_summary.csv",summary)
    (output/"manifest.json").write_text(json.dumps(dict(
        status="OFFSET_FP64_E2_SCIENTIFIC_COMPLETE",
        n_new_runs=len(rows),n_reused_ideal_rows=len(ideal),
        graphs=[x[0] for x in GRAPH_SPECS],formats=["ref64"],
        offset_halfspans=list(LEVELS),device_populations=1,
        model_evidence=EVIDENCE,
        notes="Do NOT select later low-bit formats/levels by inspecting low-bit quality: this scout is FP64 only",
    ),indent=2,sort_keys=True)+"\n")
    print("\n=== FP64 OFFSET SCOUT: ABS GAP AND PAIRED DETERIORATION ===")
    print("Graph                 offset  gap% [CI]            deterioration pp [CI]   >1pp supported?")
    for r in summary:
        print(f'{r["graph"]:21s} {r["offset_logit_halfspan"]:5.1f} '
              f'{r["mean_absolute_gap_pct"]:6.3f}% [{r["ci95_abs_gap_lo_pct"]:5.2f},{r["ci95_abs_gap_hi_pct"]:5.2f}] '
              f'{r["mean_paired_deterioration_pp"]:+6.3f} [{r["ci95_deterioration_lo_pp"]:+5.2f},{r["ci95_deterioration_hi_pp"]:+5.2f}] '
              f'{r["practical_deterioration_above_1pp_supported"]}')
    print(f"OFFSET SCOUT COMPLETE new=240 ideal_reused=48 summary={output/'E2_offset_scout_summary.csv'}",flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--e1-raw-csv",type=Path,default=IDEAL_CSV)
    p.add_argument("--out",type=Path)
    p.add_argument("--audit-only",action="store_true")
    a=p.parse_args()
    run(a.e1_raw_csv,a.out,a.audit_only)


if __name__=="__main__":
    main()
