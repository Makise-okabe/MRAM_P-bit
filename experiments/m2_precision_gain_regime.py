#!/usr/bin/env python3
"""E2-GAIN-01: preregistered gain-only STT-MRAM response x coupling precision.

SCIENCE: original dense Biq Mac weighted Max-Cut. This is an E2 *assumed*
post-nominal-transfer gain sensitivity, NOT measured post-calibration silicon
residuals and NOT a new switching physical model. Only source-only global
4/5/6/8-bit FP/INT/BFP and FP64; no solver tuning, hardware or beta changes.

One fixed dimensionless uniform device population u_i in [-1,+1] shared
across levels/formats/seeds. Response sigmoid((1+alpha*u_i)*2*beta(t)*Hq_i).
Alpha=0 uses exact existing M1 raw rows. alpha in {.025,.05} executes the
existing E2 solver with ZERO offsets. No offset x gain grid.

24 solver seeds, one original graph, 13 formats, 2 new stress levels:
624 new x 50,000 attempt runs; 312 ideal rows reused. Statistical CIs
condition on ONE graph and ONE device population.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import statistics

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph, prepare
from experiments.m1_biqmac_precision_sweep import (
    UPDATES_FROZEN, BASE_SEED_FROZEN, SEEDS_FROZEN,
    bootstrap_paired_ci
)
from experiments.m1_biqmac_reference_quality_gate import official_reference
from experiments.m1_precision_codebooks import FAMILIES, WIDTHS, build_global
from experiments.m2_e2_response_gate import (
    IDEAL_RUNS_SHA256, EVIDENCE, GAIN_HALFSPAN,
    build_e2_assumption, solve_with_response, validate_device_model
)

GRAPH_NAME = "ising2.5-100_5555"
GRAPH_INDEX = 2  # existing M1 seed placement is unmodified
GRAPH_PATH = Path("data/biqmac/raw/ising") / GRAPH_NAME
REFERENCE_PATH = Path("docs/BIQMAC_OFFICIAL_OPTIMA_2007.json")
SEEDS = tuple(BASE_SEED_FROZEN + 100_000*GRAPH_INDEX + k
              for k in range(SEEDS_FROZEN))
FORMATS = ("ref64",) + tuple(f"{fam}{bits}" for fam in FAMILIES for bits in WIDTHS)
SPARSE_GRAPH_NAME = "t2g10_5555"
SPARSE_GRAPH_INDEX = 1
SPARSE_FORMATS = ("ref64",) + tuple(
    f"{fam}{bits}" for fam in ("fp","int") for bits in (4,5,6))
STRESSES = (("ideal",0.0), ("gain_025",0.025), ("gain_050",0.05))


def select_cal_graph(name: str):
    if name == GRAPH_NAME:
        return GRAPH_PATH, GRAPH_INDEX, FORMATS, SEEDS
    if name == SPARSE_GRAPH_NAME:
        seeds=tuple(BASE_SEED_FROZEN+100000*SPARSE_GRAPH_INDEX+k
                    for k in range(SEEDS_FROZEN))
        return Path("data/biqmac/raw/ising")/name, SPARSE_GRAPH_INDEX, SPARSE_FORMATS, seeds
    raise ValueError("only the two locked CAL graphs supported")
# Predeclared, E2 sensitivity only. A single seed-conditioned bootstrap
# is not proof of production device/yield or across-graph generality.
ACCEPT_GAP_PCT = 5.0
FAIL_GAP_PCT = 7.5
ADDITIONAL_GAP_PP = 1.0


def load_paired_ideal(path: Path, *, graph_sha: str, optimum: float,
                      graph_name: str = GRAPH_NAME,
                      formats: tuple = FORMATS, seeds: tuple = SEEDS) -> dict:
    """Inspect the ACTUAL 936-run CSV; fail closed on SHA / original semantics."""
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=IDEAL_RUNS_SHA256:
        raise ValueError("M1 original 936-run CSV SHA256 mismatch")
    records=list(csv.DictReader(raw.decode("utf-8").splitlines()))
    if len(records)!=936:
        raise ValueError("M1 original CSV has wrong run count")
    seen=set()
    out={}
    all_configs=set(FORMATS)
    expected_graphs={"w01_100.0",SPARSE_GRAPH_NAME,GRAPH_NAME}
    for r in records:
        name=r["graph"]
        fmt=r["configuration"]
        seed=int(r["seed"])
        if name not in expected_graphs or fmt not in all_configs:
            raise ValueError("unexpected graph/format in 936-run CSV")
        expected_ix={"w01_100.0":0,SPARSE_GRAPH_NAME:1,GRAPH_NAME:2}[name]
        if seed not in {BASE_SEED_FROZEN+100000*expected_ix+k for k in range(SEEDS_FROZEN)}:
            raise ValueError("unmatched M1 paired seed")
        key=(name,fmt,seed)
        if key in seen:
            raise ValueError("duplicate raw M1 row")
        seen.add(key)
        if r["schedule"]!="linear" or int(r["attempted_updates"])!=UPDATES_FROZEN:
            raise ValueError("schedule/updates differ from M1 freeze")
        if name==graph_name:
            if r["graph_sha256"]!=graph_sha:
                raise ValueError("original selected graph hash mismatch")
            if not math.isclose(float(r["official_optimum"]),optimum,rel_tol=0,abs_tol=1e-8):
                raise ValueError("original optimum mismatch")
            score=float(r["returned_original_cut"])
            gap=100*(optimum-score)/optimum
            if not math.isclose(float(r["optimality_gap_pct"]),gap,rel_tol=0,abs_tol=1e-8):
                raise ValueError("raw M1 gap inconsistent with original cut")
            if score > optimum + 1e-7 or not r["returned_state_hex"]:
                raise ValueError("bad ideal original-cut / retained state")
            if fmt in formats:
                out[(fmt,seed)]=dict(
                    condition="ideal",alpha=0.0,configuration=fmt,seed=seed,
                returned_original_cut=score,optimality_gap_pct=gap,
                returned_state_hex=r["returned_state_hex"],
                actual_flips=int(r["actual_flips"]),
                source="FROZEN_M1_IDEAL_CSV")
    if len(seen)!=936 or len(out)!=len(formats)*len(seeds) or set(out)!={(f,s) for f in formats for s in seeds}:
        raise ValueError("M1 ideal pairing lacks complete selected-format/seed coverage")
    return out


def build_gain_models(n: int) -> dict[str,dict]:
    """Use the *existing* E2 gain RNG sample; drop old offset completely."""
    base=build_e2_assumption(n)
    # Reuse exactly the previously preselected one-population 5% gains.
    u=[(g-1.0)/GAIN_HALFSPAN for g in base["per_device_gain"]]
    models={}
    for condition,alpha in STRESSES[1:]:
        model={**base,
               "source":"E2 assumed gain-only sensitivity, not measured device residuals",
               "condition":condition,
               "selected_gain_halfspan":alpha,
               "per_device_gain":[1.0+alpha*v for v in u],
               "per_device_offset_logit":[0.0]*n,
               "underlying_population_u":u,
               "calibration_assumption":"nominal sigmoid transfer; residual gains purely hypothetical"}
        validate_device_model(model,n)
        assert all(abs(o)<1e-30 for o in model["per_device_offset_logit"])
        models[condition]=model
    return models


def classify_gap(lo:float,hi:float) -> str:
    if hi <= ACCEPT_GAP_PCT:
        return "acceptable"
    if lo > FAIL_GAP_PCT:
        return "failure"
    if lo > ACCEPT_GAP_PCT and hi <= FAIL_GAP_PCT:
        return "degraded"
    return "uncertain"


def mean_ci(xs:list[float],seed:int) -> tuple[float,float,float]:
    if len(xs)!=SEEDS_FROZEN:
        raise ValueError("not 24 paired seeds")
    lo,hi=bootstrap_paired_ci(xs,seed)
    return statistics.mean(xs),lo,hi


def summarize(rows:dict, *, graph_name: str = GRAPH_NAME,
              formats: tuple = FORMATS, seeds: tuple = SEEDS) -> list[dict]:
    out=[]
    for cix,(condition,alpha) in enumerate(STRESSES):
        for fix,fmt in enumerate(formats):
            vals=[rows[(condition,fmt,seed)]["optimality_gap_pct"] for seed in seeds]
            ref=[rows[(condition,"ref64",seed)]["optimality_gap_pct"] for seed in seeds]
            ideal=[rows[("ideal",fmt,seed)]["optimality_gap_pct"] for seed in seeds]
            quant=[v-r for v,r in zip(vals,ref)]
            shift=[v-o for v,o in zip(vals,ideal)]
            m,lo,hi=mean_ci(vals,31000+cix*1000+fix*11)
            mq,lq,hq=mean_ci(quant,32000+cix*1000+fix*11)
            ms,ls,hs=mean_ci(shift,33000+cix*1000+fix*11)
            # Paired format-by-response diagnostic vs same-width INT baseline.
            comparator="int"+fmt[2:] if fmt.startswith("fp") else (
                "int"+fmt[3:] if fmt.startswith("bfp") else "int"+fmt[3:] if fmt.startswith("int") else "ref64")
            delta=[
                (rows[(condition,fmt,s)]["optimality_gap_pct"]-
                 rows[(condition,comparator,s)]["optimality_gap_pct"])-
                (rows[("ideal",fmt,s)]["optimality_gap_pct"]-
                 rows[("ideal",comparator,s)]["optimality_gap_pct"])
                for s in seeds
            ]
            md,ld,hd=mean_ci(delta,34000+cix*1000+fix*11)
            out.append(dict(
                graph=graph_name,condition=condition,alpha_gain_halfspan=alpha,
                configuration=fmt,paired_seeds=len(seeds),
                conditional_device_populations=1,
                mean_absolute_gap_pct=m,ci95_abs_gap_lo_pct=lo,ci95_abs_gap_hi_pct=hi,
                mean_quantization_penalty_pp=mq,
                ci95_quant_penalty_lo_pp=lq,ci95_quant_penalty_hi_pp=hq,
                mean_response_degradation_pp=ms,
                ci95_response_shift_lo_pp=ls,ci95_response_shift_hi_pp=hs,
                comparator=comparator,
                mean_interaction_vs_int_pp=md,
                ci95_interaction_lo_pp=ld,ci95_interaction_hi_pp=hd,
                regime_seed_conditional=classify_gap(lo,hi),
                absolute_target_met_seed_conditional=(hi<=ACCEPT_GAP_PCT),
                additional_quantization_gate_met_seed_conditional=(hq<=ADDITIONAL_GAP_PP),
                eligible_at_common_target=(hi<=ACCEPT_GAP_PCT and hq<=ADDITIONAL_GAP_PP),
                evidence="E1_IDEAL" if alpha==0 else EVIDENCE,
            ))
    return out


def write_csv(path:Path,rows:list[dict]) -> None:
    if not rows:
        raise ValueError("empty CSV")
    with path.open("x",newline="",encoding="utf-8") as handle:
        w=csv.DictWriter(handle,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def write_svg(path:Path, summary:list[dict], *, formats: tuple = FORMATS) -> None:
    """Single compact regime plot, no new plotting dependency."""
    by={(x["condition"],x["configuration"]):x for x in summary}
    w=930
    h=140+len(formats)*39+100
    y0=121
    palette={"acceptable":"#cdebdc","degraded":"#ffe6ae",
             "failure":"#ffcaca","uncertain":"#dddded"}
    buf=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
         '<rect width="100%" height="100%" fill="#fff"/>',
         '<text x="22" y="29" font-family="Arial" font-size="20" font-weight="bold">E2 gain-only precision × response: original Max-Cut gap</text>',
         '<text x="22" y="51" font-family="Arial" font-size="12">One CAL graph, 24 paired solver seeds, ONE fixed assumed device population</text>',
         '<text x="22" y="70" font-family="Arial" font-size="12">Accepted only if 95% seed-CI upper bound <= 5% AND quantization penalty upper bound <= 1 pp</text>']
    for j,(name,alpha) in enumerate(STRESSES):
        buf.append(f'<text x="{225+j*228}" y="100" font-family="Arial" font-size="14" font-weight="bold">{html.escape(name)} (±{100*alpha:g}%)</text>')
    for i,fmt in enumerate(formats):
        y=y0+i*39
        buf.append(f'<text x="26" y="{y+24}" font-family="Arial" font-size="14">{html.escape(fmt)}</text>')
        for j,(name,alpha) in enumerate(STRESSES):
            x=220+j*228
            r=by[(name,fmt)]
            mode=r["regime_seed_conditional"]
            buf.append(f'<rect x="{x-8}" y="{y}" width="214" height="34" rx="4" fill="{palette[mode]}" stroke="#eee"/>')
            text=f'{r["mean_absolute_gap_pct"]:.2f}% [{r["ci95_abs_gap_lo_pct"]:.2f},{r["ci95_abs_gap_hi_pct"]:.2f}]'
            buf.append(f'<text x="{x}" y="{y+22}" font-family="Arial" font-size="13">{html.escape(text)}</text>')
    y=y0+len(formats)*39+14
    buf.append(f'<text x="22" y="{y}" font-family="Arial" font-size="12">Legend: green=acceptable, amber=degraded, red=failure, violet=uncertain (seed-CI thresholds).</text>')
    buf.append(f'<text x="22" y="{y+20}" font-family="Arial" font-size="12">E2 assumptions, NOT measured residual spread; no manufacturing or held-out graph inference.</text>')
    buf.append(f'<text x="22" y="{y+40}" font-family="Arial" font-size="12">Companion CSV contains paired FP64 penalties, response shifts and INT interactions.</text>')
    buf.append("</svg>")
    path.write_text("\n".join(buf)+"\n",encoding="utf-8")



def paired_fp_int(rows: dict, *, graph_name: str, formats: tuple,
                  seeds: tuple) -> list[dict]:
    """Direct per-condition gap(FP)-gap(INT) and paired difference-in-differences.

    Independent unit for this CI is a solver seed, conditional on exactly one
    100-device E2 assumed realization and one graph (NOT manufacturing/yield).
    """
    comparisons=[]
    for cidx,(condition,alpha) in enumerate(STRESSES):
        for bits in (4,5,6,8):
            fp,intfmt=f"fp{bits}",f"int{bits}"
            if fp not in formats or intfmt not in formats:
                continue
            delta=[rows[(condition,fp,k)]["optimality_gap_pct"]-
                   rows[(condition,intfmt,k)]["optimality_gap_pct"] for k in seeds]
            interaction=[
                d-(rows[("ideal",fp,k)]["optimality_gap_pct"]-
                   rows[("ideal",intfmt,k)]["optimality_gap_pct"])
                for d,k in zip(delta,seeds)
            ]
            md,ld,hd=mean_ci(delta,51000+1000*cidx+bits)
            mi,li,hi=mean_ci(interaction,52000+1000*cidx+bits)
            comparisons.append(dict(
                graph=graph_name,condition=condition,
                gain_halfspan_assumed=alpha,width_bits=bits,
                fp_format=fp,int_format=intfmt,
                mean_direct_delta_fp_minus_int_pp=md,
                ci95_direct_delta_lo_pp=ld,ci95_direct_delta_hi_pp=hd,
                mean_interaction_D_pp=mi,
                ci95_interaction_lo_pp=li,ci95_interaction_hi_pp=hi,
                n_paired_solver_seeds=len(seeds),
                device_populations=1,
                evidence="E1_IDEAL" if alpha==0 else EVIDENCE,
            ))
    return comparisons


def write_gap_bitwidth_plot(path: Path, summary: list[dict], *,
                            graph_name: str, formats: tuple) -> None:
    """One SVG with THREE original-optimum gap curves and paired-seed 95% CIs.

    This plots FP and INT at the tested bit widths; FP64 mean is shown for
    context. Exact +1pp FP64 penalty CIs are in E2_gain_regime_summary.csv.
    """
    lookup={(r["condition"],r["configuration"]):r for r in summary}
    widths=[b for b in (4,5,6,8) if f"fp{b}" in formats and f"int{b}" in formats]
    if len(widths)<2:
        raise ValueError("bit-width plot needs >=2 matched widths")
    ymin=math.floor(min([5.0,7.5]+[float(r["ci95_abs_gap_lo_pct"]) for r in summary])-0.5)
    ymax=math.ceil(max([5.0,7.5]+[float(r["ci95_abs_gap_hi_pct"]) for r in summary])+0.5)
    top,bottom=150,565
    total_w,total_h=1240,710
    def ycoord(g):
        return top+(ymax-g)*(bottom-top)/(ymax-ymin)
    out=[
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" width="{total_w}" height="{total_h}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="24" y="35" font-family="Arial" font-size="20" font-weight="bold">{html.escape(graph_name)} — gap versus coupling width, assumed gain variation</text>',
        '<text x="24" y="58" font-family="Arial" font-size="13">Original weighted Max-Cut optimality gap (lower better), 24 paired solver seeds; one fixed E2 device population</text>',
        '<text x="24" y="78" font-family="Arial" font-size="12">Error bars are 95% solver-seed bootstrap CIs; 5% and 7.5% gap thresholds are predeclared</text>',
    ]
    for cidx,(condition,alpha) in enumerate(STRESSES):
        base=23+405*cidx
        lx,rx=base+69,base+337
        def xcoord(width):
            return lx+(width-min(widths))*(rx-lx)/(max(widths)-min(widths))
        out.append(f'<text x="{base+192}" y="117" font-family="Arial" font-size="17" font-weight="bold" text-anchor="middle">{html.escape(condition)} (±{100*alpha:g}%)</text>')
        out.append(f'<line x1="{lx}" y1="{top}" x2="{lx}" y2="{bottom}" stroke="#888"/>')
        out.append(f'<line x1="{lx}" y1="{bottom}" x2="{rx}" y2="{bottom}" stroke="#888"/>')
        for tick in range(ymin,ymax+1):
            y=ycoord(tick)
            out.append(f'<line x1="{lx}" y1="{y:.1f}" x2="{rx}" y2="{y:.1f}" stroke="#eeeeee"/>')
            out.append(f'<text x="{lx-9}" y="{y+4:.1f}" font-size="11" font-family="Arial" text-anchor="end">{tick}%</text>')
        for threshold in (5.0,7.5):
            y=ycoord(threshold)
            out.append(f'<line x1="{lx}" y1="{y:.1f}" x2="{rx}" y2="{y:.1f}" stroke="#a0a0a0" stroke-dasharray="4,5"/>')
        ref=lookup[(condition,"ref64")]
        y=ycoord(float(ref["mean_absolute_gap_pct"]))
        out.append(f'<line x1="{lx}" y1="{y:.1f}" x2="{rx}" y2="{y:.1f}" stroke="#666666" stroke-width="2" stroke-dasharray="7,3"/>')
        for family,color in (("fp","#2765b7"),("int","#c87020")):
            coords=[]
            for bits in widths:
                row=lookup[(condition,f"{family}{bits}")]
                xx=xcoord(bits)
                yy=ycoord(float(row["mean_absolute_gap_pct"]))
                coords.append(f"{xx:.1f},{yy:.1f}")
            out.append(f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
            for bits in widths:
                row=lookup[(condition,f"{family}{bits}")]
                xx=xcoord(bits)
                yy=ycoord(float(row["mean_absolute_gap_pct"]))
                ylow=ycoord(float(row["ci95_abs_gap_hi_pct"]))
                yhigh=ycoord(float(row["ci95_abs_gap_lo_pct"]))
                out.append(f'<line x1="{xx:.1f}" y1="{ylow:.1f}" x2="{xx:.1f}" y2="{yhigh:.1f}" stroke="{color}" stroke-width="1.5"/>')
                out.append(f'<line x1="{xx-4:.1f}" y1="{ylow:.1f}" x2="{xx+4:.1f}" y2="{ylow:.1f}" stroke="{color}"/>')
                out.append(f'<line x1="{xx-4:.1f}" y1="{yhigh:.1f}" x2="{xx+4:.1f}" y2="{yhigh:.1f}" stroke="{color}"/>')
                out.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="4" fill="{color}"/>')
        for bits in widths:
            xx=xcoord(bits)
            out.append(f'<text x="{xx:.1f}" y="{bottom+22}" font-size="13" font-family="Arial" text-anchor="middle">{bits}</text>')
        out.append(f'<text x="{base+200}" y="{bottom+47}" font-family="Arial" font-size="13" text-anchor="middle">Coupling bits</text>')
    out.extend([
        '<line x1="45" y1="665" x2="75" y2="665" stroke="#2765b7" stroke-width="3"/>',
        '<text x="82" y="670" font-size="13" font-family="Arial">FP</text>',
        '<line x1="145" y1="665" x2="175" y2="665" stroke="#c87020" stroke-width="3"/>',
        '<text x="182" y="670" font-size="13" font-family="Arial">INT</text>',
        '<line x1="245" y1="665" x2="275" y2="665" stroke="#666" stroke-width="2" stroke-dasharray="7,3"/>',
        '<text x="283" y="670" font-size="13" font-family="Arial">FP64 mean (same response)</text>',
        '<text x="45" y="692" font-size="12" font-family="Arial">E2 sensitivity, not measured post-calibration residuals. Matched-FP64 +1pp eligibility requires the companion CSV.</text>',
        '</svg>',
    ])
    path.write_text("\n".join(out)+"\n",encoding="utf-8")


def audit(graph,refs,ideal_csv:Path, *, graph_name: str = GRAPH_NAME,
          formats: tuple = FORMATS, seeds: tuple = SEEDS) -> dict:
    optimum=official_reference(graph,refs["graphs"][graph_name],refs)
    if graph.n != 100:
        raise ValueError("100-spin locked CAL graph required")
    ideal=load_paired_ideal(ideal_csv,graph_sha=graph.sha256,optimum=optimum,
                            graph_name=graph_name,formats=formats,seeds=seeds)
    for fmt in formats:
        values=[ideal[(fmt,s)]["optimality_gap_pct"] for s in seeds]
        print(f"FROZEN E1 {fmt:6s} gap={statistics.mean(values):.4f}% paired_seeds=24",flush=True)
    print(f"E2-GAIN-01 {graph_name} AUDIT PASS: 936-row source SHA and "
          f"{len(formats)}x{len(seeds)} ideal pairing; original optimum={optimum}",flush=True)
    return ideal


def run(ideal_csv:Path,out:Path,audit_only:bool,graph_name:str=GRAPH_NAME) -> None:
    refs=json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
    if refs.get("reference_type")!="PUBLISHED_OPTIMUM":
        raise ValueError("missing official published optimum")
    graph_path,graph_index,formats,seeds=select_cal_graph(graph_name)
    graph=load_rudy(graph_path)
    optimum=official_reference(graph,refs["graphs"][graph_name],refs)
    ideal=audit(graph,refs,ideal_csv,graph_name=graph_name,formats=formats,seeds=seeds)
    if audit_only:
        return
    if out is None or out.exists():
        raise ValueError("supply a non-existing --out directory")
    beta=beta_from_original_graph(graph)
    reps={"ref64":prepare(graph,"ref64","source")}
    for fmt in formats[1:]:
        family=next(f for f in FAMILIES if fmt.startswith(f))
        bits=int(fmt[len(family):])
        reps[fmt]=build_global(graph,family,bits)
    # Check source-only scales against frozen M1 metadata, including layout.
    with ideal_csv.open(newline="",encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            if rec["graph"]!=graph_name or rec["configuration"] not in formats:
                continue
            fmt=rec["configuration"]
            if not math.isclose(float(rec["scale"]),reps[fmt]["scale"],rel_tol=0,abs_tol=0):
                raise ValueError(f"source scale mismatch for {fmt}")
            if not math.isclose(float(rec["beta"]),beta,rel_tol=0,abs_tol=0):
                raise ValueError("original beta mismatch")
    models=build_gain_models(graph.n)
    out.mkdir(parents=True,exist_ok=False)
    model_payload={
        "evidence":"E2_ASSUMED_NOT_MEASURED",
        "formula":"sigmoid((1+alpha*u_i)*2*beta(t)*Hq_i), offset=0",
        "units":"gain dimensionless multiplier; no voltage model/transfer clipping",
        "source_note":"2026 STT-MTJ published sigmoid motivates response form only; gain spreads assumed, not measured residuals",
        "levels":[dict(name=k,alpha=a) for k,a in STRESSES],
        "model_seed":20261107,
        "device_population_count":1,
        "population_seed_scope":f"one fixed 100-device realization across both levels, all {len(formats)} formats and 24 solver seeds",
        "original_ideal_csv_sha256":IDEAL_RUNS_SHA256,
        "graph":graph_name,"graph_sha256":graph.sha256,
        "original_optimum":optimum,
        "paired_seeds":list(seeds),
        "updates":UPDATES_FROZEN,"schedule":"linear 0.5 to 2 beta from original graph",
        "thresholds":{"acceptable_upper_ci_gap_pct":ACCEPT_GAP_PCT,
                      "failure_lower_ci_gap_pct":FAIL_GAP_PCT,
                      "additional_quant_upper_ci_pp":ADDITIONAL_GAP_PP},
        "model_vectors":models,
        "scope":"one calibration graph; per-seed CIs CONDITIONAL on one assumed population; no E3/device/sample generalization"
    }
    (out/"frozen_E2_gain_model.json").write_text(json.dumps(model_payload,indent=2,sort_keys=True)+"\n")
    results={(rec["condition"],rec["configuration"],rec["seed"]):rec for rec in ideal.values()}
    new_runs=[]
    # Append-only progress; if interrupted directory remains incomplete, never label PASS.
    with (out/"E2_gain_new_runs.csv").open("x",newline="",encoding="utf-8") as f:
        header=["condition","alpha_gain_halfspan","graph","graph_sha256",
                "configuration","seed","official_optimum","optimality_gap_pct",
                "returned_original_cut","returned_state_hex","actual_flips",
                "improvements","returned_represented_energy","attempted_updates"]
        writer=csv.DictWriter(f,fieldnames=header)
        writer.writeheader()
        for condition,alpha in STRESSES[1:]:
            model=models[condition]
            for fmt in formats:
                for seed in seeds:
                    got=solve_with_response(graph,reps[fmt],beta,UPDATES_FROZEN,seed,model)
                    score=float(got["returned_original_cut"])
                    if score>optimum+1e-7:
                        raise AssertionError("original optimum beaten; abort")
                    gap=100*(optimum-score)/optimum
                    item=dict(condition=condition,alpha_gain_halfspan=alpha,
                              graph=graph_name,graph_sha256=graph.sha256,
                              configuration=fmt,seed=seed,official_optimum=optimum,
                              optimality_gap_pct=gap,
                              returned_original_cut=score,
                              returned_state_hex=got["returned_state_hex"],
                              actual_flips=got["actual_flips"],
                              improvements=got["improvements"],
                              returned_represented_energy=got["returned_represented_energy"],
                              attempted_updates=UPDATES_FROZEN)
                    writer.writerow(item)
                    f.flush()
                    new_runs.append(item)
                    results[(condition,fmt,seed)]=item
                print(f"E2-GAIN-01 {condition} {fmt:6s} complete {SEEDS_FROZEN} paired seeds",
                      flush=True)
    if len(new_runs)!=2*len(formats)*len(seeds):
        raise AssertionError("wrong number of new response runs")
    summary=summarize(results,graph_name=graph_name,formats=formats,seeds=seeds)
    write_csv(out/"E2_gain_regime_summary.csv",summary)
    write_svg(out/"E2_gain_regime_map.svg",summary,formats=formats)
    pairs=paired_fp_int(results,graph_name=graph_name,formats=formats,seeds=seeds)
    write_csv(out/"E2_gain_fp_int_paired.csv",pairs)
    write_gap_bitwidth_plot(out/"E2_gain_gap_vs_bitwidth.svg",summary,
                            graph_name=graph_name,formats=formats)
    # The "minimum sufficient width" is SEED-CONDITIONAL on one CAL graph
    # and one assumed device sample, not a universally optimal bit width.
    knee=[]
    for condition,alpha in STRESSES:
        for family in FAMILIES:
            if not any(fmt.startswith(family) for fmt in formats):
                continue
            eligible=[w for w in WIDTHS if f"{family}{w}" in formats and next(
                r["eligible_at_common_target"] for r in summary
                if r["condition"]==condition and r["configuration"]==f"{family}{w}")]
            knee.append(dict(condition=condition,family=family,
                             eligible_widths=eligible,
                             minimum_eligible_width=eligible[0] if eligible else None))
    (out/"E2_gain_precision_rule.json").write_text(json.dumps(
        dict(scope="candidate one-graph one-device E2 sensitivity; not a hardware-optimal rule",
             absolute_gap_threshold_pct=ACCEPT_GAP_PCT,
             matched_fp64_penalty_threshold_pp=ADDITIONAL_GAP_PP,
             tested_formats=list(formats),
             unmeasured_formats=[f"{fam}{w}" for fam in ("fp","int") for w in WIDTHS if f"{fam}{w}" not in formats],
             results=knee),indent=2,sort_keys=True)+"\n")
    manifest={
        "status":"E2_GAIN01_SCIENTIFIC_RUN_COMPLETE",
        "evidence":"E2 assumed sensitivity, NOT measured post-calibration residual",
        "n_new_solver_runs":len(new_runs),"n_reused_ideal_records":len(ideal),
        "original_e1_csv_sha256":IDEAL_RUNS_SHA256,
        "graph":graph_name,"graph_sha256":graph.sha256,
        "device_population_count":1,"gain_stress_levels":[0,0.025,0.05],
        "formats_tested":list(formats),"graph_index":graph_index,"solver_seeds":list(seeds),
        "offset":0,"anneal":"frozen M1 50k linear beta",
        "solver":"existing m2_e2_response_gate.solve_with_response; E1 M1 original returned-state policy",
        "no_retuning":True,
        "precision_rule_scope":"within-calibration graph seed CI, conditional one E2 population",
        "output_files":["E2_gain_new_runs.csv","E2_gain_regime_summary.csv",
                        "E2_gain_regime_map.svg","E2_gain_fp_int_paired.csv",
                        "E2_gain_gap_vs_bitwidth.svg","E2_gain_precision_rule.json",
                        "frozen_E2_gain_model.json"]
    }
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    for item in knee:
        print(f"CONDITIONAL KNEE {item['condition']:8s} {item['family']:3s}: "
              f"{item['minimum_eligible_width']}",flush=True)
    print(f"E2-GAIN-01 {graph_name} SCIENTIFIC COMPLETE new={len(new_runs)} ideal_reused={len(ideal)} "
          f"plot={out/'E2_gain_regime_map.svg'}",flush=True)
    for r in pairs:
        if r["width_bits"] == 6:
            print(f"DIRECT FP6-INT6 {r['condition']} "
                  f"Delta={r['mean_direct_delta_fp_minus_int_pp']:+.3f} pp "
                  f"CI=[{r['ci95_direct_delta_lo_pp']:+.3f},"
                  f"{r['ci95_direct_delta_hi_pp']:+.3f}] "
                  f"D={r['mean_interaction_D_pp']:+.3f} pp "
                  f"CI=[{r['ci95_interaction_lo_pp']:+.3f},"
                  f"{r['ci95_interaction_hi_pp']:+.3f}]",flush=True)


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--e1-raw-csv",type=Path,required=True)
    ap.add_argument("--out",type=Path)
    ap.add_argument("--audit-only",action="store_true")
    ap.add_argument("--graph",choices=(GRAPH_NAME,SPARSE_GRAPH_NAME),default=GRAPH_NAME)
    a=ap.parse_args()
    run(a.e1_raw_csv,a.out,a.audit_only,graph_name=a.graph)


if __name__=="__main__":
    main()
