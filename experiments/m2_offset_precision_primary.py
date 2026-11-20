#!/usr/bin/env python3
"""E2-OFFSET-PRECISION-01: frozen FP/INT 4-6-bit × offset CAL experiment.

8 November post-FP64-scout choice, selected using FP64 only:
    Two original CAL Biq Mac graphs × offsets +/-0.8,+/-1.6 logit
    × FP4/5/6 + INT4/5/6 × original 24 graph-indexed paired solver seeds
    = EXACTLY 576 new runs.
Reuse 96 matched FP64 scout runs and 336 M1 ideal rows (including 48 FP64).
FP8/INT8 are NOT silently run; required conditional cells are listed afterward.

Response sigmoid(2 beta(t) H_i^(quantized) + d v_i) with gain=1, v_i fixed
across graphs/levels/formats/seeds. v_i comes directly from existing E2 model.
E2 *assumed* logit stress, not measured MTJ post-calibration residuals.
No solver, annealing, quantizer, reference-score or hardware redesign.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import statistics
from pathlib import Path

from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph
from experiments.m1_biqmac_precision_sweep import UPDATES_FROZEN, SEEDS_FROZEN, bootstrap_paired_ci
from experiments.m1_precision_codebooks import build_global
from experiments.m2_e2_response_gate import (
    IDEAL_RUNS_SHA256, EVIDENCE, solve_with_response,
)
from experiments.m2_offset_fp64_scout import (
    GRAPH_SPECS, IDEAL_CSV, load_ideal_and_graphs, models, paired_seed
)

LEVELS=(0.8,1.6)  # locked after FP64-only scout, BEFORE low-bit inspection
FORMATS=("fp4","fp5","fp6","int4","int5","int6")
COMPARATORS=("ref64",)+FORMATS
EXPECTED_NEW=2*len(LEVELS)*len(FORMATS)*SEEDS_FROZEN
EXPECTED_SCOUT_REFS=2*len(LEVELS)*SEEDS_FROZEN
EXPECTED_IDEAL=2*len(COMPARATORS)*SEEDS_FROZEN
GAP_ACCEPT=5.0
GAP_FAIL=7.5
QUANT_PENALTY=1.0
DEFAULT_SCOUT_DIR=Path("results/m2_offset_fp64_scout_20261108")


def mean_ci(x:list[float],key:int):
    if len(x)!=SEEDS_FROZEN:
        raise ValueError("must have 24 matched solver seeds")
    lo,hi=bootstrap_paired_ci(x,key)
    return statistics.mean(x),lo,hi


def load_references(e1_csv:Path, scout_dir:Path):
    """Audit original M1 SHA, all scout runs and exact persistent offset vectors."""
    source,fp64_ideal=load_ideal_and_graphs(e1_csv)  # full 936-row SHA and graph audit
    original=list(csv.DictReader(e1_csv.open(newline="",encoding="utf-8")))
    ideal={}
    for r in original:
        name,fmt,seed=r["graph"],r["configuration"],int(r["seed"])
        if name not in source or fmt not in COMPARATORS:
            continue
        g,ix,optimum=source[name]
        if (seed not in paired_seed(ix) or r["graph_sha256"]!=g.sha256 or
                float(r["official_optimum"])!=optimum or
                int(r["attempted_updates"])!=UPDATES_FROZEN or
                r["schedule"]!="linear"):
            raise ValueError("M1 low-bit source/seed/schedule mismatch")
        gap=100*(optimum-float(r["returned_original_cut"]))/optimum
        if not math.isclose(gap,float(r["optimality_gap_pct"]),rel_tol=0,abs_tol=1e-8):
            raise ValueError("M1 low-bit original-gap mismatch")
        key=(name,fmt,seed)
        if key in ideal:
            raise ValueError("duplicate M1 ideal row")
        ideal[key]=dict(gap_pct=gap,seed=seed,configuration=fmt,graph=name)
    expected={(name,fmt,seed) for name,ix in GRAPH_SPECS
              for fmt in COMPARATORS for seed in paired_seed(ix)}
    if set(ideal)!=expected or len(ideal)!=EXPECTED_IDEAL:
        raise ValueError("ideal FP64/FP/INT matched 336-row subset incomplete")
    for (name,seed),gap in fp64_ideal.items():
        if not math.isclose(gap,ideal[(name,"ref64",seed)]["gap_pct"],
                            rel_tol=0,abs_tol=1e-12):
            raise ValueError("M1 FP64 ideal reference mismatch")

    manifest=json.loads((scout_dir/"manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("status")!="OFFSET_FP64_E2_SCIENTIFIC_COMPLETE" or
            manifest.get("n_new_runs")!=240 or
            manifest.get("n_reused_ideal_rows")!=48 or
            manifest.get("device_populations")!=1 or
            sorted(manifest.get("offset_halfspans",[])) != [0.1,0.2,0.4,0.8,1.6]):
        raise ValueError("FP64 scout manifest not frozen/complete")
    frozen=json.loads((scout_dir/"E2_offset_scout_model.json").read_text(encoding="utf-8"))
    if (frozen.get("evidence")!=EVIDENCE or
            frozen.get("same_ideal_m1_csv_sha256")!=IDEAL_RUNS_SHA256 or
            frozen.get("n_new_solver_runs")!=240 or
            frozen.get("device_model_seed")!=20261107 or
            frozen.get("measured_population") is not False):
        raise ValueError("FP64 E2 scout model/provenance mismatch")
    m=models(100)
    for d in LEVELS:
        if frozen["model_vectors"].get(str(d))!=m[d]:
            raise ValueError("persistent device offset vector differs from FP64 scout")

    raw=list(csv.DictReader((scout_dir/"E2_offset_scout_runs.csv").open(
        newline="",encoding="utf-8")))
    if len(raw)!=240:
        raise ValueError("FP64 scout must contain exactly 240 actual runs")
    visited=set()
    refs={}
    for r in raw:
        name,d,seed=r["graph"],float(r["offset_logit_halfspan"]),int(r["seed"])
        key=(name,d,seed)
        if key in visited:
            raise ValueError("duplicate FP64 scout row")
        visited.add(key)
        if name not in source or d not in (0.1,0.2,0.4,0.8,1.6):
            raise ValueError("unexpected FP64 scout graph/offset")
        g,ix,optimum=source[name]
        if (seed not in paired_seed(ix) or r["graph_sha256"]!=g.sha256 or
                not math.isclose(float(r["official_optimum"]),optimum) or
                int(r["attempted_updates"])!=UPDATES_FROZEN or
                not r["returned_state_hex"]):
            raise ValueError("FP64 scout per-run graph/seed/budget mismatch")
        cut=float(r["returned_original_cut"])
        gap=100*(optimum-cut)/optimum
        if (cut>optimum+1e-7 or
                not math.isclose(float(r["gap_pct"]),gap,abs_tol=1e-8) or
                not math.isclose(float(r["ideal_gap_pct"]),
                                 ideal[(name,"ref64",seed)]["gap_pct"],abs_tol=1e-8) or
                not math.isclose(float(r["paired_deterioration_pp"]),
                                 gap-float(r["ideal_gap_pct"]),abs_tol=1e-8)):
            raise ValueError("FP64 scout original-gap/paired arithmetic mismatch")
        if d in LEVELS:
            refs[key]=dict(gap_pct=gap,score=cut,state=r["returned_state_hex"])
    if len(visited)!=240 or len(refs)!=EXPECTED_SCOUT_REFS:
        raise ValueError("FP64 scout missing matching 96 selected references")
    print(f"OFFSET PRECISION AUDIT PASS: {len(ideal)} immutable M1 ideal rows, "
          f"{len(refs)} FP64 scout references, 240-row original scout audit, "
          f"identical device vectors; new budget={EXPECTED_NEW}",flush=True)
    return source,ideal,refs,m


def classify(lo,hi):
    if hi<=GAP_ACCEPT:
        return "acceptable"
    if lo>GAP_FAIL:
        return "failure"
    if lo>GAP_ACCEPT and hi<=GAP_FAIL:
        return "degraded"
    return "uncertain"


def summarize(source,ideal,fp64,low):
    table=[];pairs=[]
    for gi,(name,ix) in enumerate(GRAPH_SPECS):
        seeds=paired_seed(ix)
        for li,d in enumerate((0.0,)+LEVELS):
            def gap(fmt,seed):
                if d==0:
                    return ideal[(name,fmt,seed)]["gap_pct"]
                if fmt=="ref64":
                    return fp64[(name,d,seed)]["gap_pct"]
                return low[(name,d,fmt,seed)]["gap_pct"]
            for fi,fmt in enumerate(COMPARATORS):
                vals=[gap(fmt,k) for k in seeds]
                ref=[gap("ref64",k) for k in seeds]
                idealvals=[gap(fmt,k) if d==0 else ideal[(name,fmt,k)]["gap_pct"]
                           for k in seeds]
                quant=[a-b for a,b in zip(vals,ref)]
                response=[a-b for a,b in zip(vals,idealvals)]
                mm,lo,hi=mean_ci(vals,81000+gi*10000+li*1000+fi*17)
                mq,lq,hq=mean_ci(quant,82000+gi*10000+li*1000+fi*17)
                mr,lr,hr=mean_ci(response,83000+gi*10000+li*1000+fi*17)
                table.append(dict(
                    graph=name,offset_logit_halfspan=d,configuration=fmt,
                    n_paired_seeds=len(seeds),device_populations=1,
                    mean_absolute_gap_pct=mm,ci95_abs_gap_lo_pct=lo,ci95_abs_gap_hi_pct=hi,
                    mean_quantization_loss_pp=mq,
                    ci95_quant_loss_lo_pp=lq,ci95_quant_loss_hi_pp=hq,
                    mean_offset_response_shift_pp=mr,
                    ci95_response_shift_lo_pp=lr,ci95_response_shift_hi_pp=hr,
                    absolute_quality_met=(hi<=GAP_ACCEPT),
                    additional_quantization_screen_met=(hq<=QUANT_PENALTY),
                    eligible=(hi<=GAP_ACCEPT and hq<=QUANT_PENALTY),
                    regime=classify(lo,hi),
                    evidence="E1_IDEAL" if d==0 else EVIDENCE,
                ))
            for bits in (4,5,6):
                delta=[gap(f"fp{bits}",k)-gap(f"int{bits}",k) for k in seeds]
                interaction=[
                    this-(ideal[(name,f"fp{bits}",k)]["gap_pct"]-
                          ideal[(name,f"int{bits}",k)]["gap_pct"])
                    for this,k in zip(delta,seeds)
                ]
                md,ld,hd=mean_ci(delta,84000+gi*10000+li*1000+bits*19)
                mi,il,ih=mean_ci(interaction,85000+gi*10000+li*1000+bits*19)
                pairs.append(dict(
                    graph=name,offset_logit_halfspan=d,width_bits=bits,
                    mean_direct_delta_fp_minus_int_pp=md,
                    ci95_direct_delta_lo_pp=ld,ci95_direct_delta_hi_pp=hd,
                    mean_interaction_D_pp=mi,
                    ci95_interaction_D_lo_pp=il,ci95_interaction_D_hi_pp=ih,
                    n_paired_seeds=SEEDS_FROZEN,device_populations=1,
                    inference="seed-conditional E2 assumed device population",
                ))
    return table,pairs


def extension_cells(summary:list[dict]):
    """Frozen rule: if EITHER six-bit format not established, request BOTH 8-bit."""
    by={(r["graph"],r["offset_logit_halfspan"],r["configuration"]):r
        for r in summary}
    needed=[]
    for name,_ in GRAPH_SPECS:
        for d in LEVELS:
            f=by[(name,d,"fp6")];i=by[(name,d,"int6")]
            if not (f["eligible"] and i["eligible"]):
                needed.append(dict(
                    graph=name,offset_logit_halfspan=d,
                    extension_formats="fp8,int8",
                    additional_solver_runs=2*SEEDS_FROZEN,
                    reason="either FP6 or INT6 failed to clearly meet both frozen CI screens",
                    status="NOT_RUN",
                ))
    return needed


def write_csv(path,rows):
    if not rows:
        raise ValueError("refuse empty output CSV")
    with path.open("x",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)


def write_svg(path,summary):
    """Three response panels per graph, original-gap vs bit width with seed CIs."""
    by={(r["graph"],r["offset_logit_halfspan"],r["configuration"]):r
        for r in summary}
    all_lows=[float(r["ci95_abs_gap_lo_pct"]) for r in summary]
    all_highs=[float(r["ci95_abs_gap_hi_pct"]) for r in summary]
    ymin=math.floor(min([5.0,7.5]+all_lows)-0.4)
    ymax=math.ceil(max([5.0,7.5]+all_highs)+0.4)
    tw,th=1240,1240
    buf=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}" viewBox="0 0 {tw} {th}">',
         '<rect width="100%" height="100%" fill="#ffffff"/>',
         '<text x="32" y="36" font-family="Arial" font-size="21" font-weight="bold">E2 offset-only precision × response: original Max-Cut gap</text>',
         '<text x="32" y="61" font-family="Arial" font-size="13">One assumed device population, 24 paired seeds per cell; error bars are seed-conditional 95% bootstrap CIs</text>',
         '<text x="32" y="83" font-family="Arial" font-size="12">5%/7.5% absolute quality boundaries; additionally require +1 pp matched-FP64 penalty CI upper bound for eligibility</text>']
    for gi,(name,ix) in enumerate(GRAPH_SPECS):
        top=160+gi*540
        bottom=top+390
        buf.append(f'<text x="34" y="{top-39}" font-family="Arial" font-size="17" font-weight="bold">{html.escape(name)}</text>')
        def yy(g):
            return top+(ymax-g)/(ymax-ymin)*(bottom-top)
        for li,d in enumerate((0.0,)+LEVELS):
            lx=55+li*397+48
            rx=lx+255
            def xx(bits):return lx+(bits-4)*(rx-lx)/2
            buf.append(f'<text x="{(lx+rx)/2:.1f}" y="{top-13}" font-family="Arial" font-size="15" text-anchor="middle">{"Ideal" if d==0 else f"±{d:g} logit"}</text>')
            for t in range(ymin,ymax+1):
                y=yy(t)
                buf.append(f'<line x1="{lx}" y1="{y:.1f}" x2="{rx}" y2="{y:.1f}" stroke="#eee"/>')
                buf.append(f'<text x="{lx-9}" y="{y+4:.1f}" font-family="Arial" font-size="11" text-anchor="end">{t}%</text>')
            for bound in (5.0,7.5):
                y=yy(bound)
                buf.append(f'<line x1="{lx}" y1="{y:.1f}" x2="{rx}" y2="{y:.1f}" stroke="#999" stroke-dasharray="4,4"/>')
            ref=by[(name,d,"ref64")]
            y=yy(float(ref["mean_absolute_gap_pct"]))
            buf.append(f'<line x1="{lx}" y1="{y:.1f}" x2="{rx}" y2="{y:.1f}" stroke="#666" stroke-width="2" stroke-dasharray="7,4"/>')
            for fam,color in (("fp","#2763b4"),("int","#c6732d")):
                pts=[]
                for bit in (4,5,6):
                    r=by[(name,d,f"{fam}{bit}")]
                    pts.append(f'{xx(bit):.1f},{yy(float(r["mean_absolute_gap_pct"])):.1f}')
                buf.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
                for bit in (4,5,6):
                    r=by[(name,d,f"{fam}{bit}")]
                    x=xx(bit);y=yy(float(r["mean_absolute_gap_pct"]))
                    ylo=yy(float(r["ci95_abs_gap_hi_pct"]))
                    yhi=yy(float(r["ci95_abs_gap_lo_pct"]))
                    buf.append(f'<line x1="{x:.1f}" y1="{ylo:.1f}" x2="{x:.1f}" y2="{yhi:.1f}" stroke="{color}" stroke-width="1.5"/>')
                    for yc in (ylo,yhi):
                        buf.append(f'<line x1="{x-5:.1f}" y1="{yc:.1f}" x2="{x+5:.1f}" y2="{yc:.1f}" stroke="{color}"/>')
                    buf.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
            for bit in (4,5,6):
                buf.append(f'<text x="{xx(bit):.1f}" y="{bottom+24}" font-family="Arial" font-size="13" text-anchor="middle">{bit}</text>')
            buf.append(f'<text x="{(lx+rx)/2:.1f}" y="{bottom+47}" font-family="Arial" font-size="12" text-anchor="middle">Coupling bits</text>')
    buf.extend([
        '<line x1="58" y1="1190" x2="91" y2="1190" stroke="#2763b4" stroke-width="3"/>',
        '<text x="100" y="1195" font-family="Arial" font-size="14">FP</text>',
        '<line x1="168" y1="1190" x2="201" y2="1190" stroke="#c6732d" stroke-width="3"/>',
        '<text x="210" y="1195" font-family="Arial" font-size="14">INT</text>',
        '<line x1="289" y1="1190" x2="321" y2="1190" stroke="#666" stroke-width="2" stroke-dasharray="7,4"/>',
        '<text x="330" y="1195" font-family="Arial" font-size="14">FP64 (same offset)</text>',
        '<text x="58" y="1222" font-family="Arial" font-size="12">Assumed E2 logit offsets, NOT measured post-calibration residuals. FP8/INT8 are conditional and not included here.</text>',
        '</svg>'
    ])
    path.write_text("\n".join(buf)+"\n",encoding="utf-8")


def run(ideal_csv:Path,scout_dir:Path,out:Path|None,audit_only:bool):
    source,ideal,fp64,model=load_references(ideal_csv,scout_dir)
    if audit_only:
        return
    if out is None or out.exists():
        raise ValueError("provide a NEW non-existing --out directory")
    # Recheck original quantizer scale/beta against immutable M1 metadata.
    e1=list(csv.DictReader(ideal_csv.open(newline="",encoding="utf-8")))
    reps={}
    for name,ix in GRAPH_SPECS:
        g,_,optimum=source[name]
        beta=beta_from_original_graph(g)
        for fmt in FORMATS:
            rep=build_global(g,fmt[:-1],int(fmt[-1]))
            seen=0
            for row in e1:
                if row["graph"]==name and row["configuration"]==fmt:
                    if (float(row["scale"])!=rep["scale"] or
                            float(row["beta"])!=beta):
                        raise ValueError("frozen quantizer scale or beta changed")
                    seen+=1
            if seen!=SEEDS_FROZEN:
                raise ValueError("missing 24 M1 quantizer scales")
            reps[(name,fmt)]=rep
    out.mkdir(parents=True,exist_ok=False)
    (out/"E2_offset_primary_protocol.json").write_text(json.dumps(dict(
        evidence=EVIDENCE,
        experiment="E2-OFFSET-PRECISION-01",
        date="2026-11-08",
        selection_basis="FP64-only preexisting scout at +/-0.8 and +/-1.6",
        graphs=list(GRAPH_SPECS),offset_halfspans=list(LEVELS),
        formats=list(FORMATS),n_new_runs=EXPECTED_NEW,
        references=dict(fp64_scout=EXPECTED_SCOUT_REFS,ideal_m1=EXPECTED_IDEAL),
        source_ideal_sha256=IDEAL_RUNS_SHA256,
        scout_manifest_sha256=hashlib.sha256((scout_dir/"manifest.json").read_bytes()).hexdigest(),
        scout_model_sha256=hashlib.sha256((scout_dir/"E2_offset_scout_model.json").read_bytes()).hexdigest(),
        zero_gain_variation=True,
        device_population_count=1,
        device_model_seed=20261107,
        update_budget=UPDATES_FROZEN,
        anneal="unchanged original-graph beta and 50k linear schedule",
        quality_thresholds=dict(acceptable_gap_ci_upper_pct=GAP_ACCEPT,
                                failure_gap_ci_lower_pct=GAP_FAIL,
                                additional_quant_ci_upper_pp=QUANT_PENALTY),
        physical_evidence="synthetic E2 logit sensitivity; NOT measured MTJ residual",
        model_vectors_selected={str(d):model[d] for d in LEVELS},
    ),indent=2,sort_keys=True)+"\n",encoding="utf-8")

    low={}
    with (out/"E2_offset_primary_runs.csv").open("x",newline="",encoding="utf-8") as f:
        cols=["graph","graph_sha256","offset_logit_halfspan","configuration","seed",
              "official_optimum","returned_original_cut","gap_pct",
              "returned_state_hex","returned_represented_energy",
              "actual_flips","attempted_updates"]
        writer=csv.DictWriter(f,fieldnames=cols)
        writer.writeheader()
        for name,ix in GRAPH_SPECS:
            g,_,optimum=source[name]
            beta=beta_from_original_graph(g)
            for d in LEVELS:
                for fmt in FORMATS:
                    rep=reps[(name,fmt)]
                    for seed in paired_seed(ix):
                        x=solve_with_response(g,rep,beta,UPDATES_FROZEN,seed,
                                              model[d],offset_limit=d)
                        cut=float(x["returned_original_cut"])
                        if cut>optimum+1e-7:
                            raise AssertionError("published optimum exceeded")
                        gap=100*(optimum-cut)/optimum
                        row=dict(
                            graph=name,graph_sha256=g.sha256,
                            offset_logit_halfspan=d,configuration=fmt,seed=seed,
                            official_optimum=optimum,returned_original_cut=cut,
                            gap_pct=gap,returned_state_hex=x["returned_state_hex"],
                            returned_represented_energy=x["returned_represented_energy"],
                            actual_flips=x["actual_flips"],attempted_updates=UPDATES_FROZEN,
                        )
                        writer.writerow(row)
                        f.flush()
                        low[(name,d,fmt,seed)]=row
                    print(f"OFFSET PRECISION {name} ±{d:g} {fmt}: 24/24",flush=True)
    if len(low)!=EXPECTED_NEW:
        raise AssertionError("not exactly 576 new low-bit runs")
    summary,pairs=summarize(source,ideal,fp64,low)
    write_csv(out/"E2_offset_primary_summary.csv",summary)
    write_csv(out/"E2_offset_fp_int_paired.csv",pairs)
    write_svg(out/"E2_offset_gap_vs_bitwidth.svg",summary)
    needed=extension_cells(summary)
    (out/"E2_offset_8bit_extension_required.json").write_text(
        json.dumps(dict(status="NOT_RUN",conditional_rule="both FP8 and INT8 if either FP6 or INT6 not clearly eligible",
                        cells=needed,total_additional_runs=sum(x["additional_solver_runs"] for x in needed)),
                   indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (out/"manifest.json").write_text(json.dumps(dict(
        status="E2_OFFSET_PRECISION_PRIMARY_COMPLETE",
        n_new_runs=len(low),n_reused_ideal=len(ideal),
        n_reused_fp64_scout=len(fp64),n_device_populations=1,
        n_required_8bit_extension_cells=len(needed),
        extension_runs_launched=0,
        evidence=EVIDENCE,
        files=["E2_offset_primary_runs.csv","E2_offset_primary_summary.csv",
               "E2_offset_fp_int_paired.csv","E2_offset_gap_vs_bitwidth.svg",
               "E2_offset_8bit_extension_required.json"],
    ),indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("\n=== PRECISION × OFFSET CAL SUMMARY ===")
    for r in summary:
        if r["offset_logit_halfspan"]==0:
            continue
        print(f'{r["graph"]:21s} d=±{r["offset_logit_halfspan"]:3.1f} '
              f'{r["configuration"]:5s} gap={r["mean_absolute_gap_pct"]:6.3f}% '
              f'[{r["ci95_abs_gap_lo_pct"]:5.2f},{r["ci95_abs_gap_hi_pct"]:5.2f}] '
              f'quant={r["mean_quantization_loss_pp"]:+6.3f}pp '
              f'[{r["ci95_quant_loss_lo_pp"]:+5.2f},{r["ci95_quant_loss_hi_pp"]:+5.2f}] '
              f'eligible={r["eligible"]}')
    print("\n=== DIRECT FP-INT AND DIFFERENCE-IN-DIFFERENCES ===")
    for r in pairs:
        if r["offset_logit_halfspan"]>0:
            print(f'{r["graph"]:21s} d=±{r["offset_logit_halfspan"]:3.1f} '
                  f'{r["width_bits"]}bit Δ={r["mean_direct_delta_fp_minus_int_pp"]:+6.3f} '
                  f'[{r["ci95_direct_delta_lo_pp"]:+5.2f},{r["ci95_direct_delta_hi_pp"]:+5.2f}] '
                  f'D={r["mean_interaction_D_pp"]:+6.3f} '
                  f'[{r["ci95_interaction_D_lo_pp"]:+5.2f},{r["ci95_interaction_D_hi_pp"]:+5.2f}]')
    print(f"\n8-BIT EXTENSION REQUIRED cells={len(needed)} extra_runs="
          f"{sum(x['additional_solver_runs'] for x in needed)} (NOT LAUNCHED)")
    print(f"OFFSET PRECISION SCIENTIFIC COMPLETE new={len(low)} "
          f"reused_fp64={len(fp64)} reused_ideal={len(ideal)} "
          f"output={out}",flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--e1-raw-csv",type=Path,default=IDEAL_CSV)
    ap.add_argument("--scout-dir",type=Path,default=DEFAULT_SCOUT_DIR)
    ap.add_argument("--out",type=Path)
    ap.add_argument("--audit-only",action="store_true")
    args=ap.parse_args()
    run(args.e1_raw_csv,args.scout_dir,args.out,args.audit_only)


if __name__=="__main__":
    main()
