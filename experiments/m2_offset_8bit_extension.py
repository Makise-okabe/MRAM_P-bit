#!/usr/bin/env python3
"""E2-OFFSET-8BIT: strictly conditional, frozen FP8/INT8 follow-up.

The previously completed primary E2 offset CAL study selected exactly
four graph x offset cells by a PREDECLARED rule:
If either FP6 or INT6 fails the two 95%-CI quality screens, evaluate
BOTH FP8 and INT8 in that cell. For the completed primary batch this
requires 4 cells x 2 formats x 24 frozen paired seeds = 192 NEW runs.

Source: original M1 936-row SHA-verified CSV, completed FP64-only scout,
completed 576-run primary batch. This code does not rerun any prior data,
alter the simulator, tuning, device population or 50k annealing protocol.
One fixed synthetic offset device vector; E2 NOT measured MTJ residuals.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph
from experiments.m1_biqmac_precision_sweep import UPDATES_FROZEN, SEEDS_FROZEN
from experiments.m1_precision_codebooks import build_global
from experiments.m2_e2_response_gate import EVIDENCE, IDEAL_RUNS_SHA256, solve_with_response
from experiments.m2_offset_fp64_scout import GRAPH_SPECS, IDEAL_CSV, paired_seed
from experiments.m2_offset_precision_primary import (
    DEFAULT_SCOUT_DIR, LEVELS, FORMATS, COMPARATORS,
    EXPECTED_NEW, EXPECTED_IDEAL, EXPECTED_SCOUT_REFS,
    GAP_ACCEPT, QUANT_PENALTY,
    load_references, summarize, extension_cells, mean_ci, classify, write_csv
)

DEFAULT_PRIMARY=Path("results/m2_offset_precision_primary_20261108")
EXT_FORMATS=("fp8","int8")


def audit_primary(source,ideal,fp64,model,primary:Path,scout:Path):
    """Re-derive ALL six-bit extension triggers from immutable raw run rows."""
    manifest=json.loads((primary/"manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("status")!="E2_OFFSET_PRECISION_PRIMARY_COMPLETE" or
        manifest.get("n_new_runs")!=EXPECTED_NEW or
        manifest.get("n_reused_ideal")!=EXPECTED_IDEAL or
        manifest.get("n_reused_fp64_scout")!=EXPECTED_SCOUT_REFS or
        manifest.get("n_device_populations")!=1 or
        manifest.get("extension_runs_launched")!=0):
        raise ValueError("primary manifest not frozen/complete")
    protocol=json.loads((primary/"E2_offset_primary_protocol.json").read_text(encoding="utf-8"))
    if (protocol.get("experiment")!="E2-OFFSET-PRECISION-01" or
        protocol.get("n_new_runs")!=EXPECTED_NEW or
        protocol.get("source_ideal_sha256")!=IDEAL_RUNS_SHA256 or
        protocol.get("graphs")!=[list(x) for x in GRAPH_SPECS] or
        protocol.get("offset_halfspans")!=list(LEVELS) or
        protocol.get("formats")!=list(FORMATS) or
        protocol.get("device_population_count")!=1 or
        protocol.get("update_budget")!=UPDATES_FROZEN or
        protocol.get("zero_gain_variation") is not True or
        protocol.get("model_vectors_selected")!={str(d):model[d] for d in LEVELS}):
        raise ValueError("primary six-bit protocol mismatch")
    for fname,key in (("manifest.json","scout_manifest_sha256"),
                      ("E2_offset_scout_model.json","scout_model_sha256")):
        sha=hashlib.sha256((scout/fname).read_bytes()).hexdigest()
        if protocol.get(key)!=sha:
            raise ValueError("primary's frozen scout provenance differs")
    low={}
    raw=list(csv.DictReader((primary/"E2_offset_primary_runs.csv").open(newline="",encoding="utf-8")))
    if len(raw)!=EXPECTED_NEW:
        raise ValueError("primary raw CSV must contain exactly 576 records")
    for r in raw:
        name,d,fmt,seed=r["graph"],float(r["offset_logit_halfspan"]),r["configuration"],int(r["seed"])
        if name not in source or d not in LEVELS or fmt not in FORMATS:
            raise ValueError("unexpected primary graph/stress/format")
        graph,index,optimum=source[name]
        if (seed not in paired_seed(index) or r["graph_sha256"]!=graph.sha256 or
            float(r["official_optimum"])!=optimum or
            int(r["attempted_updates"])!=UPDATES_FROZEN or
            not r["returned_state_hex"]):
            raise ValueError("primary raw graph/seed/optimum/budget mismatch")
        cut=float(r["returned_original_cut"])
        gap=100*(optimum-cut)/optimum
        if cut>optimum+1e-7 or not math.isclose(gap,float(r["gap_pct"]),rel_tol=0,abs_tol=1e-8):
            raise ValueError("primary original gap inconsistent")
        key=(name,d,fmt,seed)
        if key in low:
            raise ValueError("duplicate primary solver cell")
        low[key]={"gap_pct":gap}
    if set(low)!={(name,d,fmt,k) for name,index in GRAPH_SPECS
                    for d in LEVELS for fmt in FORMATS for k in paired_seed(index)}:
        raise ValueError("primary missing one of 576 paired records")
    recomputed,_=summarize(source,ideal,fp64,low)
    saved=list(csv.DictReader((primary/"E2_offset_primary_summary.csv").open(
        newline="",encoding="utf-8")))
    a={(x["graph"],x["offset_logit_halfspan"],x["configuration"]):x
       for x in recomputed}
    b={(x["graph"],float(x["offset_logit_halfspan"]),x["configuration"]):x
       for x in saved}
    if set(a)!=set(b) or len(saved)!=len(recomputed):
        raise ValueError("primary summary incomplete")
    for key,rec in a.items():
        old=b[key]
        for field in ("mean_absolute_gap_pct","ci95_abs_gap_lo_pct","ci95_abs_gap_hi_pct",
                      "mean_quantization_loss_pp","ci95_quant_loss_hi_pp"):
            if not math.isclose(float(rec[field]),float(old[field]),rel_tol=0,abs_tol=1e-9):
                raise ValueError(f"primary summary differs from raw results: {key} {field}")
        if str(rec["eligible"])!=old["eligible"]:
            raise ValueError("primary eligibility field differs from raw results")
    needed=extension_cells(recomputed)
    recorded=json.loads((primary/"E2_offset_8bit_extension_required.json").read_text(encoding="utf-8"))
    if (recorded.get("status")!="NOT_RUN" or
        recorded.get("cells")!=needed or
        recorded.get("total_additional_runs")!=sum(x["additional_solver_runs"] for x in needed)):
        raise ValueError("recorded extension rule differs from audited data")
    expected_cells={(name,d) for name,_ in GRAPH_SPECS for d in LEVELS}
    if {(r["graph"],r["offset_logit_halfspan"]) for r in needed}!=expected_cells:
        raise ValueError("expected four locked offset extensions from supplied results")
    if len(needed)!=4 or sum(x["additional_solver_runs"] for x in needed)!=192:
        raise ValueError("not exactly four × 48 extensions")
    return needed


def load_8bit_ideal(ideal_csv:Path,source):
    data={}
    for r in csv.DictReader(ideal_csv.open(newline="",encoding="utf-8")):
        name,fmt,seed=r["graph"],r["configuration"],int(r["seed"])
        if name not in source or fmt not in EXT_FORMATS:
            continue
        graph,index,optimum=source[name]
        if (seed not in paired_seed(index) or
            r["graph_sha256"]!=graph.sha256 or
            float(r["official_optimum"])!=optimum or
            r["schedule"]!="linear" or
            int(r["attempted_updates"])!=UPDATES_FROZEN or
            not r["returned_state_hex"]):
            raise ValueError("M1 8-bit ideal original semantics mismatch")
        score=float(r["returned_original_cut"])
        gap=100*(optimum-score)/optimum
        if score>optimum+1e-7 or not math.isclose(gap,float(r["optimality_gap_pct"]),abs_tol=1e-8):
            raise ValueError("M1 8-bit original gap inconsistent")
        key=(name,fmt,seed)
        if key in data:
            raise ValueError("duplicate 8bit ideal row")
        data[key]={"gap_pct":gap,"scale":float(r["scale"]),"beta":float(r["beta"])}
    if len(data)!=2*2*SEEDS_FROZEN:
        raise ValueError("need all 96 original M1 FP8/INT8 ideal rows")
    return data


def report_8bit(source,ideal8,fp64,new,needed):
    summary=[];pairs=[]
    for ci,cell in enumerate(needed):
        name,d=cell["graph"],cell["offset_logit_halfspan"]
        _,index,_=source[name]
        seeds=paired_seed(index)
        for fi,fmt in enumerate(EXT_FORMATS):
            vals=[new[(name,d,fmt,k)]["gap_pct"] for k in seeds]
            refs=[fp64[(name,d,k)]["gap_pct"] for k in seeds]
            original=[ideal8[(name,fmt,k)]["gap_pct"] for k in seeds]
            penalty=[v-r for v,r in zip(vals,refs)]
            response=[v-r for v,r in zip(vals,original)]
            m,l,h=mean_ci(vals,91000+ci*1000+fi*29)
            mq,lq,hq=mean_ci(penalty,92000+ci*1000+fi*29)
            mr,lr,hr=mean_ci(response,93000+ci*1000+fi*29)
            summary.append(dict(
                graph=name,offset_logit_halfspan=d,configuration=fmt,
                n_paired_seeds=SEEDS_FROZEN,device_populations=1,
                mean_absolute_gap_pct=m,ci95_abs_gap_lo_pct=l,ci95_abs_gap_hi_pct=h,
                mean_quantization_loss_pp=mq,
                ci95_quant_loss_lo_pp=lq,ci95_quant_loss_hi_pp=hq,
                mean_offset_response_shift_pp=mr,
                ci95_response_shift_lo_pp=lr,ci95_response_shift_hi_pp=hr,
                absolute_quality_met=(h<=GAP_ACCEPT),
                additional_quantization_screen_met=(hq<=QUANT_PENALTY),
                eligible=(h<=GAP_ACCEPT and hq<=QUANT_PENALTY),
                regime=classify(l,h),
                evidence=EVIDENCE,
            ))
        diffs=[new[(name,d,"fp8",k)]["gap_pct"]-
               new[(name,d,"int8",k)]["gap_pct"] for k in seeds]
        DD=[a-(ideal8[(name,"fp8",k)]["gap_pct"]-
                ideal8[(name,"int8",k)]["gap_pct"]) for a,k in zip(diffs,seeds)]
        m,l,h=mean_ci(diffs,94000+ci*1000)
        md,ld,hd=mean_ci(DD,95000+ci*1000)
        pairs.append(dict(
            graph=name,offset_logit_halfspan=d,width_bits=8,
            mean_direct_delta_fp_minus_int_pp=m,
            ci95_direct_delta_lo_pp=l,ci95_direct_delta_hi_pp=h,
            mean_interaction_D_pp=md,
            ci95_interaction_D_lo_pp=ld,ci95_interaction_D_hi_pp=hd,
            n_paired_seeds=SEEDS_FROZEN,device_populations=1,
            evidence="E2 assumed offset, seed CIs conditional on one device array",
        ))
    return summary,pairs


def final_knee(primary_summary,added):
    """Lowest TESTED eligible width; no monotonic bit-width assumption."""
    by={(r["graph"],float(r["offset_logit_halfspan"]),r["configuration"]):r
        for r in primary_summary+added}
    result=[]
    for name,_ in GRAPH_SPECS:
        for d in LEVELS:
            for fam in ("fp","int"):
                valid=[b for b in (4,5,6,8) if
                       (name,d,f"{fam}{b}") in by and
                       str(by[(name,d,f"{fam}{b}")]["eligible"])=="True"]
                result.append(dict(
                    graph=name,offset_logit_halfspan=d,family=fam,
                    eligible_tested_widths=",".join(map(str,valid)) if valid else "none",
                    lowest_eligible_tested_width=valid[0] if valid else "not established",
                    physical_scope="one CAL graph; one synthetic device population; seed-conditional CIs",
                ))
    return result


def run(ideal_csv:Path,scout:Path,primary:Path,out:Path|None,audit_only:bool):
    source,ideal,fp64,model=load_references(ideal_csv,scout)
    needed=audit_primary(source,ideal,fp64,model,primary,scout)
    ideal8=load_8bit_ideal(ideal_csv,source)
    reps={}
    for name,index in GRAPH_SPECS:
        graph,_,optimum=source[name]
        beta=beta_from_original_graph(graph)
        for fmt in EXT_FORMATS:
            rep=build_global(graph,fmt[:-1],8)
            for seed in paired_seed(index):
                row=ideal8[(name,fmt,seed)]
                if row["scale"]!=rep["scale"] or row["beta"]!=beta:
                    raise ValueError("eight-bit scale or original beta mismatch")
            reps[(name,fmt)]=rep
    print(f"OFFSET 8BIT AUDIT PASS: required_cells={len(needed)} "
          f"new={len(needed)*2*SEEDS_FROZEN} ideal_8bit_reused={len(ideal8)} "
          "FP64/M1/primary references unchanged",flush=True)
    if audit_only:
        return
    if out is None or out.exists():
        raise ValueError("provide a NEW non-existing --out directory")
    out.mkdir(parents=True,exist_ok=False)
    protocol=dict(evidence=EVIDENCE,device_populations=1,
        graph_cells=needed,formats=list(EXT_FORMATS),
        zero_gain_variation=True,original_solver_updates=UPDATES_FROZEN,
        e1_source_sha256=IDEAL_RUNS_SHA256,
        primary_manifest_sha256=hashlib.sha256((primary/"manifest.json").read_bytes()).hexdigest(),
        primary_runs_sha256=hashlib.sha256((primary/"E2_offset_primary_runs.csv").read_bytes()).hexdigest(),
        scout_runs_sha256=hashlib.sha256((scout/"E2_offset_scout_runs.csv").read_bytes()).hexdigest(),
        predeclared_extension_rule="both 8bit if either six-bit representation not clearly eligible",
        new_budget=len(needed)*2*SEEDS_FROZEN,
        n_m1_8bit_ideal_reused=len(ideal8),
        not_measured="logit offsets are assumed E2 sensitivities, not physical post-calibration spread")
    (out/"protocol.json").write_text(json.dumps(protocol,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    new={}
    with (out/"E2_offset_8bit_new_runs.csv").open("x",newline="",encoding="utf-8") as f:
        cols=["graph","graph_sha256","offset_logit_halfspan","configuration","seed",
              "official_optimum","gap_pct","returned_original_cut","returned_state_hex",
              "returned_represented_energy","actual_flips","attempted_updates"]
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for cell in needed:
            name,d=cell["graph"],cell["offset_logit_halfspan"]
            graph,index,optimum=source[name]
            beta=beta_from_original_graph(graph)
            for fmt in EXT_FORMATS:
                for seed in paired_seed(index):
                    x=solve_with_response(graph,reps[(name,fmt)],beta,UPDATES_FROZEN,
                                          seed,model[d],offset_limit=d)
                    cut=float(x["returned_original_cut"])
                    if cut>optimum+1e-7:
                        raise AssertionError("published optimum exceeded")
                    gap=100*(optimum-cut)/optimum
                    item=dict(graph=name,graph_sha256=graph.sha256,
                        offset_logit_halfspan=d,configuration=fmt,seed=seed,
                        official_optimum=optimum,gap_pct=gap,
                        returned_original_cut=cut,returned_state_hex=x["returned_state_hex"],
                        returned_represented_energy=x["returned_represented_energy"],
                        actual_flips=x["actual_flips"],attempted_updates=UPDATES_FROZEN)
                    w.writerow(item);f.flush()
                    new[(name,d,fmt,seed)]=item
                print(f"OFFSET 8BIT {name} ±{d:g} {fmt}: 24/24",flush=True)
    if len(new)!=192:
        raise AssertionError("not exactly 192 new 8-bit solver runs")
    report,pairs=report_8bit(source,ideal8,fp64,new,needed)
    write_csv(out/"E2_offset_8bit_summary.csv",report)
    write_csv(out/"E2_offset_8bit_paired.csv",pairs)
    old=list(csv.DictReader((primary/"E2_offset_primary_summary.csv").open(newline="",encoding="utf-8")))
    knees=final_knee(old,report)
    write_csv(out/"E2_offset_completed_knees.csv",knees)
    (out/"manifest.json").write_text(json.dumps(dict(
        status="E2_OFFSET_8BIT_EXTENSION_COMPLETE",n_new_runs=len(new),
        n_reused_8bit_ideal=len(ideal8),n_reused_fp64_scout=len(fp64),
        n_completed_cells=len(needed),device_populations=1,
        next_step="inspect CAL quality and interactions, freeze rule BEFORE held-out testing",
    ),indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("\n=== CONDITIONAL FP8/INT8 RESULTS ===")
    for r in report:
        print(f'{r["graph"]:21s} ±{r["offset_logit_halfspan"]:3.1f} '
              f'{r["configuration"]:4s} gap={r["mean_absolute_gap_pct"]:6.3f}% '
              f'CI=[{r["ci95_abs_gap_lo_pct"]:.2f},{r["ci95_abs_gap_hi_pct"]:.2f}] '
              f'penalty={r["mean_quantization_loss_pp"]:+.3f} '
              f'CI=[{r["ci95_quant_loss_lo_pp"]:+.2f},{r["ci95_quant_loss_hi_pp"]:+.2f}] '
              f'eligible={r["eligible"]}')
    print("\n=== UPDATED CONDITIONAL PRECISION RULE (CAL ONLY) ===")
    for r in knees:
        print(f'{r["graph"]:21s} ±{r["offset_logit_halfspan"]:3.1f} '
              f'{r["family"]:3s} lowest_eligible={r["lowest_eligible_tested_width"]}')
    print(f"\nOFFSET 8BIT SCIENTIFIC COMPLETE new={len(new)} "
          f"ideal8_reused={len(ideal8)} fp64_reused={len(fp64)} out={out}",flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--e1-raw-csv",type=Path,default=IDEAL_CSV)
    ap.add_argument("--scout-dir",type=Path,default=DEFAULT_SCOUT_DIR)
    ap.add_argument("--primary-dir",type=Path,default=DEFAULT_PRIMARY)
    ap.add_argument("--out",type=Path)
    ap.add_argument("--audit-only",action="store_true")
    a=ap.parse_args()
    run(a.e1_raw_csv,a.scout_dir,a.primary_dir,a.out,a.audit_only)


if __name__=="__main__":
    main()
