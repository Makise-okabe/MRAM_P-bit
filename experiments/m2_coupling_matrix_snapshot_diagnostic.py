#!/usr/bin/env python3
"""Read-only coupling-matrix J diagnostic on frozen FP64-returned CAL states.

For every original FP64 best-returned state s (24 seeds x 2 CAL graphs x
[ideal, assumed +/-0.8, assumed +/-1.6 LOGIT offset]), evaluate exactly
the SAME s for all existing global FP/INT 4/5/6/8-bit J quantizers:

  J_ij = -w_ij, J_ji = J_ij, J_ii = 0, h_i = 0
  H_ref_i(s) = sum_j J_ij s_j
  H_q_i(s)   = sum_j Jhat_ij s_j
  dH_i       = H_q_i-H_ref_i = sum_j (Jhat_ij-J_ij) s_j
  dp_i       = sigmoid(2*beta_snapshot*H_q_i+offset_i)
             - sigmoid(2*beta_snapshot*H_ref_i+offset_i)

All three beta checkpoints (0.5, 1.0, 2.0 times original graph beta)
are STATIC diagnostics; none are solver observations at a particular time.
Offsets are the same ONE synthetic E2 device vector used in completed runs.
The accumulator and input conversion remain idealized (floating arithmetic
and behavioral sigmoid); these metrics do NOT measure RTL/MTJ hardware.

Inputs are completed M1 SHA-checked 936-run CSV, completed 240-row FP64
scout, 576-row precision batch and 192-row conditional 8-bit extension.
No fresh solver runs; diagnostic DOES NOT select states with low-bit energy.
Returned original-cut quality is read from the corresponding existing
solver run, and is association, not a trajectory/causal explanation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

from experiments.m1_biqmac_ideal_pilot import (
    beta_from_original_graph, original_cut, prepare,
)
from experiments.m1_biqmac_precision_sweep import (
    SEEDS_FROZEN, UPDATES_FROZEN, bootstrap_paired_ci,
)
from experiments.m1_precision_codebooks import build_global
from experiments.m2_stt_pbit_transfer_preflight import logistic
from experiments.m2_e2_response_gate import EVIDENCE, IDEAL_RUNS_SHA256
from experiments.m2_offset_fp64_scout import GRAPH_SPECS, IDEAL_CSV, paired_seed
from experiments.m2_offset_precision_primary import (
    DEFAULT_SCOUT_DIR, DEFAULT_SCOUT_DIR as _SCOUT_CHECK,
    DEFAULT_SCOUT_DIR as SCOUT_DIR,
    DEFAULT_SCOUT_DIR as SCOUT_PATH,
    LEVELS, FORMATS, load_references,
)
from experiments.m2_offset_8bit_extension import (
    DEFAULT_PRIMARY, EXT_FORMATS, audit_primary, load_8bit_ideal,
)

# The deliberately redundant aliases above are not part of the experiment;
# use DEFAULT_SCOUT_DIR in CLI. Do not change the upstream experiment constants.
DEFAULT_EXTENSION=Path("results/m2_offset_8bit_extension_20261108")
PHASES=(0.5,1.0,2.0)
ALL_FORMATS=("ref64",)+FORMATS+EXT_FORMATS
RESPONSE_LEVELS=(0.0,)+LEVELS
EXPECTED_REFERENCE_STATES=len(GRAPH_SPECS)*len(RESPONSE_LEVELS)*SEEDS_FROZEN
EXPECTED_DIAGNOSTIC_ROWS=EXPECTED_REFERENCE_STATES*len(ALL_FORMATS)*len(PHASES)
EXPECTED_EXISTING_GAPS=EXPECTED_REFERENCE_STATES*len(ALL_FORMATS)


def decode_spins(text:str,n:int):
    if not text or n<1:
        raise ValueError("missing frozen returned-state hex")
    v=int(text,16)
    if v<0 or v.bit_length()>n:
        raise ValueError("returned spin state outside frozen graph size")
    return tuple(1 if (v>>i)&1 else -1 for i in range(n))


def csv_records(path:Path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path:Path,rows:list[dict]):
    if not rows:
        raise ValueError("no diagnostic rows")
    with path.open("x",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)


def check_cut(graph,optimum:float,spin_hex:str,reported_cut:float,reported_gap:float):
    spins=decode_spins(spin_hex,graph.n)
    cut=original_cut(graph,spins)
    gap=100*(optimum-cut)/optimum
    if (cut>optimum+1e-7 or
        not math.isclose(cut,reported_cut,rel_tol=0,abs_tol=1e-6) or
        not math.isclose(gap,reported_gap,rel_tol=0,abs_tol=1e-7)):
        raise ValueError("returned-state ORIGINAL cut/optimality gap mismatch")
    return spins


def load_snapshots_and_quality(
    e1_csv:Path,scout_dir:Path,primary_dir:Path,extension_dir:Path
):
    source,ideal7,fp64,models=load_references(e1_csv,scout_dir)
    needed=audit_primary(source,ideal7,fp64,models,primary_dir,scout_dir)
    load_8bit_ideal(e1_csv,source)
    expected_cells={(name,d) for name,_ in GRAPH_SPECS for d in LEVELS}
    if {(x["graph"],x["offset_logit_halfspan"]) for x in needed}!=expected_cells:
        raise ValueError("extension cells do not match the predeclared four")

    extension_manifest=json.loads((extension_dir/"manifest.json").read_text(encoding="utf-8"))
    if (extension_manifest.get("status")!="E2_OFFSET_8BIT_EXTENSION_COMPLETE" or
        extension_manifest.get("n_new_runs")!=192 or
        extension_manifest.get("n_reused_8bit_ideal")!=96 or
        extension_manifest.get("n_completed_cells")!=4 or
        extension_manifest.get("device_populations")!=1):
        raise ValueError("conditional extension not recorded as complete")
    extension_protocol=json.loads((extension_dir/"protocol.json").read_text(encoding="utf-8"))
    checks=(("primary_manifest_sha256",primary_dir/"manifest.json"),
            ("primary_runs_sha256",primary_dir/"E2_offset_primary_runs.csv"),
            ("scout_runs_sha256",scout_dir/"E2_offset_scout_runs.csv"))
    for key,path in checks:
        if extension_protocol.get(key)!=hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"conditional extension provenance differs: {key}")
    if (extension_protocol.get("new_budget")!=192 or
        extension_protocol.get("device_populations")!=1 or
        extension_protocol.get("formats")!=list(EXT_FORMATS)):
        raise ValueError("extension protocol/format mismatch")

    e1=csv_records(e1_csv)
    if len(e1)!=936 or hashlib.sha256(e1_csv.read_bytes()).hexdigest()!=IDEAL_RUNS_SHA256:
        raise ValueError("immutable original 936-run M1 CSV mismatch")
    snapshots={}; gaps={}
    ideal_meta={}
    for r in e1:
        name,fmt,seed=r["graph"],r["configuration"],int(r["seed"])
        if name not in source or fmt not in ALL_FORMATS:
            continue
        graph,index,optimum=source[name]
        if (seed not in paired_seed(index) or r["graph_sha256"]!=graph.sha256 or
            float(r["official_optimum"])!=optimum or
            r["schedule"]!="linear" or
            int(r["attempted_updates"])!=UPDATES_FROZEN):
            raise ValueError("M1 source/schedule pairing mismatch")
        key=(name,0.0,fmt,seed)
        if key in gaps:
            raise ValueError("duplicate M1 reference row")
        spins=check_cut(graph,optimum,r["returned_state_hex"],
                        float(r["returned_original_cut"]),
                        float(r["optimality_gap_pct"]))
        gaps[key]=float(r["optimality_gap_pct"])
        if fmt=="ref64":
            snapshots[(name,0.0,seed)]=spins
        ideal_meta[(name,fmt,seed)]=(float(r["scale"]),float(r["beta"]))
    exp_ideal={(name,0.0,fmt,seed) for name,index in GRAPH_SPECS
               for fmt in ALL_FORMATS for seed in paired_seed(index)}
    if set(gaps)!=exp_ideal:
        raise ValueError("incomplete M1 ideal coupling formats")

    scout=csv_records(scout_dir/"E2_offset_scout_runs.csv")
    if len(scout)!=240:
        raise ValueError("expected completed 240-row FP64 scout")
    seen_scout=set()
    for r in scout:
        name,d,seed=r["graph"],float(r["offset_logit_halfspan"]),int(r["seed"])
        if name not in source or d not in (0.1,0.2,0.4,0.8,1.6):
            raise ValueError("invalid scout condition")
        graph,index,optimum=source[name]
        key=(name,d,seed)
        if key in seen_scout or seed not in paired_seed(index) or r["graph_sha256"]!=graph.sha256:
            raise ValueError("duplicate or mismatched scout row")
        seen_scout.add(key)
        spins=check_cut(graph,optimum,r["returned_state_hex"],
                        float(r["returned_original_cut"]),float(r["gap_pct"]))
        if d in LEVELS:
            snapshots[key]=spins
            gaps[(name,d,"ref64",seed)]=float(r["gap_pct"])
    if len(seen_scout)!=240:
        raise ValueError("scout missing a run")

    for path,allowed,expected in (
        (primary_dir/"E2_offset_primary_runs.csv",set(FORMATS),576),
        (extension_dir/"E2_offset_8bit_new_runs.csv",set(EXT_FORMATS),192),
    ):
        records=csv_records(path)
        if len(records)!=expected:
            raise ValueError(f"wrong number of completed runs in {path}")
        seen=set()
        for r in records:
            name,d,fmt,seed=(r["graph"],float(r["offset_logit_halfspan"]),
                             r["configuration"],int(r["seed"]))
            if name not in source or d not in LEVELS or fmt not in allowed:
                raise ValueError("unexpected numerical result condition")
            graph,index,optimum=source[name]
            key=(name,d,fmt,seed)
            if (key in seen or seed not in paired_seed(index) or
                r["graph_sha256"]!=graph.sha256 or
                float(r["official_optimum"])!=optimum or
                int(r["attempted_updates"])!=UPDATES_FROZEN):
                raise ValueError("duplicate or source mismatch in numerical result")
            seen.add(key)
            check_cut(graph,optimum,r["returned_state_hex"],
                      float(r["returned_original_cut"]),float(r["gap_pct"]))
            if key in gaps:
                raise ValueError("duplicate existing solution-quality result")
            gaps[key]=float(r["gap_pct"])
        if len(seen)!=expected:
            raise ValueError("incomplete numerical-result file")

    exp_states={(name,d,k) for name,index in GRAPH_SPECS
                for d in RESPONSE_LEVELS for k in paired_seed(index)}
    exp_gaps={(name,d,fmt,k) for name,index in GRAPH_SPECS
              for d in RESPONSE_LEVELS for fmt in ALL_FORMATS
              for k in paired_seed(index)}
    if set(snapshots)!=exp_states or len(snapshots)!=EXPECTED_REFERENCE_STATES:
        raise ValueError("not exactly 144 same-condition FP64-returned states")
    if set(gaps)!=exp_gaps or len(gaps)!=EXPECTED_EXISTING_GAPS:
        raise ValueError("not exactly 1296 existing solver quality gaps")
    return source,models,ideal_meta,snapshots,gaps


def build_representations(source,ideal_meta):
    reps={}
    for name,index in GRAPH_SPECS:
        graph,_,_=source[name]
        beta=beta_from_original_graph(graph)
        for fmt in ALL_FORMATS:
            rep=(prepare(graph,"ref64","source") if fmt=="ref64"
                 else build_global(graph,fmt[:-1],int(fmt[-1])))
            if fmt!="ref64":
                for k in paired_seed(index):
                    scale,archived_beta=ideal_meta[(name,fmt,k)]
                    if scale!=rep["scale"] or archived_beta!=beta:
                        raise ValueError("original M1 coupling scale/beta differs")
            if len(rep["edges"])!=len(graph.edges):
                raise ValueError("coupling representation drops source edge positions")
            for (i,j,w),(u,v,q) in zip(graph.edges,rep["edges"]):
                if i!=u or j!=v:
                    raise ValueError("coupling matrix J indices do not match source")
                # J is symmetric: each nonzero edge has mirrored adjacency values.
                if (j,q) not in rep["adjacency"][i] or (i,q) not in rep["adjacency"][j]:
                    raise ValueError("coupling J not mirrored exactly")
            reps[(name,fmt)]=rep
    return reps


def local_fields(rep,spins):
    # Intentionally identical sum order/adjacency semantics as M1 solver.
    return [sum(jij*spins[j] for j,jij in adj) for adj in rep["adjacency"]]


def snapshot_metrics(href,hquant,offset,beta,phase):
    n=len(href)
    if len(hquant)!=n or len(offset)!=n:
        raise ValueError("local-field/device population dimension mismatch")
    dh=[x-y for x,y in zip(hquant,href)]
    rms_ref=math.sqrt(sum(x*x for x in href)/n)
    rms_dh=math.sqrt(sum(x*x for x in dh)/n)
    b=beta*phase
    dp=[]
    d_offset=[]
    for a,q,off in zip(href,hquant,offset):
        p_ref=logistic(2*b*a+off)
        p_quant=logistic(2*b*q+off)
        p_ideal=logistic(2*b*a)
        dp.append(abs(p_quant-p_ref))
        d_offset.append(abs(p_ref-p_ideal))
    delta_logit=[2*b*x for x in dh]
    off_rms=math.sqrt(sum(x*x for x in offset)/n)
    return dict(
        mean_abs_dH=sum(map(abs,dh))/n,
        rms_dH=rms_dh,
        relative_rms_field_error=(rms_dh/rms_ref if rms_ref else 0.0),
        mean_abs_quantization_logit_error=sum(map(abs,delta_logit))/n,
        rms_quantization_logit_error=2*b*rms_dh,
        rms_assumed_offset_logit=off_rms,
        quant_logit_to_offset_rms_ratio=(2*b*rms_dh/off_rms if off_rms else ""),
        mean_abs_switch_prob_distortion=sum(dp)/n,
        max_abs_switch_prob_distortion=max(dp),
        mean_abs_fp64_offset_only_prob_shift=sum(d_offset)/n,
        field_sign_disagreement_fraction=sum(a*q<0 for a,q in zip(href,hquant))/n,
        fraction_spins_prob_distortion_gt_005=sum(z>0.05 for z in dp)/n,
    )


def summarize(rows):
    by={}
    for r in rows:
        key=(r["graph"],r["offset_logit_halfspan"],r["configuration"],
             r["anneal_beta_multiplier"])
        by.setdefault(key,[]).append(r)
    out=[]
    for graph_index,(name,_) in enumerate(GRAPH_SPECS):
        for level_index,d in enumerate(RESPONSE_LEVELS):
            for fmt_index,fmt in enumerate(ALL_FORMATS):
                for phase_index,phase in enumerate(PHASES):
                    key=(name,d,fmt,phase)
                    v=by[key]
                    if len(v)!=SEEDS_FROZEN or len({int(r["seed"]) for r in v})!=SEEDS_FROZEN:
                        raise ValueError("summary requires exactly 24 FP64-returned states")
                    prob=[r["mean_abs_switch_prob_distortion"] for r in v]
                    ci=bootstrap_paired_ci(
                        prob,710000+graph_index*10000+level_index*1000+
                        fmt_index*100+phase_index*17)
                    out.append(dict(
                        graph=name,offset_logit_halfspan=d,configuration=fmt,
                        anneal_beta_multiplier=phase,n_reference_states=len(v),
                        n_device_populations=1,
                        mean_existing_returned_original_gap_pct=statistics.mean(
                            r["existing_returned_original_gap_pct"] for r in v),
                        mean_state_relative_rms_field_error=statistics.mean(
                            r["relative_rms_field_error"] for r in v),
                        mean_state_abs_dH=statistics.mean(r["mean_abs_dH"] for r in v),
                        mean_state_abs_quantization_logit_error=statistics.mean(
                            r["mean_abs_quantization_logit_error"] for r in v),
                        mean_state_abs_switch_prob_distortion=statistics.mean(prob),
                        ci95_prob_distortion_lo=ci[0],ci95_prob_distortion_hi=ci[1],
                        mean_state_field_sign_disagreement=statistics.mean(
                            r["field_sign_disagreement_fraction"] for r in v),
                        mean_state_fp64_offset_only_prob_shift=statistics.mean(
                            r["mean_abs_fp64_offset_only_prob_shift"] for r in v),
                        coeff_source_mse=statistics.mean(r["coupling_source_mse"] for r in v),
                        coupling_scale=statistics.mean(r["coupling_global_scale"] for r in v),
                        interpretation="same FP64-returned states; diagnostic only, not sampled solver trajectories",
                    ))
    return out


def run(e1_csv,scout_dir,primary_dir,extension_dir,out,audit_only):
    source,models,ideal_meta,states,gaps=load_snapshots_and_quality(
        e1_csv,scout_dir,primary_dir,extension_dir)
    reps=build_representations(source,ideal_meta)
    print(f"COUPLING SNAPSHOT AUDIT PASS: {len(states)} immutable FP64-returned states; "
          f"{len(gaps)} existing solver quality records; 9 J representations; "
          f"3 beta checkpoints; new solver runs=0",flush=True)
    if audit_only:
        return
    if out is None or out.exists():
        raise ValueError("provide a NEW non-existing --out directory")
    data=[]
    for name,index in GRAPH_SPECS:
        graph,_,optimum=source[name]
        beta=beta_from_original_graph(graph)
        for d in RESPONSE_LEVELS:
            offset=[0.0]*graph.n if d==0 else models[d]["per_device_offset_logit"]
            for seed in paired_seed(index):
                spins=states[(name,d,seed)]
                fields_ref=local_fields(reps[(name,"ref64")],spins)
                for fmt in ALL_FORMATS:
                    rep=reps[(name,fmt)]
                    fields=local_fields(rep,spins)
                    for phase in PHASES:
                        metrics=snapshot_metrics(fields_ref,fields,offset,beta,phase)
                        data.append(dict(
                            graph=name,graph_sha256=graph.sha256,
                            offset_logit_halfspan=d,configuration=fmt,
                            seed=seed,anneal_beta_multiplier=phase,
                            n_spins=graph.n,
                            coupling_global_scale=rep["scale"],
                            coupling_source_mse=rep.get("coefficient_mse",0.0),
                            n_source_nonzero_couplings=len(graph.edges),
                            n_undirected_matrix_positions=graph.n*(graph.n-1)//2,
                            reference_state_original_gap_pct=gaps[(name,d,"ref64",seed)],
                            existing_returned_original_gap_pct=gaps[(name,d,fmt,seed)],
                            **metrics,
                        ))
            print(f"COUPLING SNAPSHOT {name} offset ±{d:g}: 24 FP64 states × "
                  f"{len(ALL_FORMATS)} formats × {len(PHASES)} betas analysed",flush=True)
    if len(data)!=EXPECTED_DIAGNOSTIC_ROWS:
        raise AssertionError("snapshot result count differs from 3888")
    summary=summarize(data)
    out.mkdir(parents=True,exist_ok=False)
    write_csv(out/"E2_coupling_snapshot_per_seed.csv",data)
    write_csv(out/"E2_coupling_snapshot_summary.csv",summary)
    manifest=dict(
        status="E2_COUPLING_SNAPSHOT_DIAGNOSTIC_COMPLETE",
        n_new_solver_runs=0,n_fp64_reference_states=len(states),
        n_format_condition_phase_seed_rows=len(data),
        n_existing_original_gap_records=len(gaps),
        graphs=list(GRAPH_SPECS),conditions=list(RESPONSE_LEVELS),
        representations=list(ALL_FORMATS),beta_multipliers=list(PHASES),
        physical_evidence=EVIDENCE,
        n_device_populations=1,
        graph_J="J_ij=-w_ij, undirected source edge mirrored; diagonal=0; h=0",
        precision_isolation="quantize J only; full numerical local-field accumulator and idealized sigmoid",
        states="the original ideal/offset FP64 solver-returned best states; same states for every coupling format",
        interpretation="state-conditioned snapshots, NOT state visitation or causes of solver quality",
        note="sum uses existing adjacency matrix-equivalent computation; no new optimization or low-bit state selection",
        provenance_sha256={
            "e1_original":hashlib.sha256(e1_csv.read_bytes()).hexdigest(),
            "fp64_scout_runs":hashlib.sha256((scout_dir/"E2_offset_scout_runs.csv").read_bytes()).hexdigest(),
            "primary_runs":hashlib.sha256((primary_dir/"E2_offset_primary_runs.csv").read_bytes()).hexdigest(),
            "extension_runs":hashlib.sha256((extension_dir/"E2_offset_8bit_new_runs.csv").read_bytes()).hexdigest(),
        },
    )
    (out/"manifest.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print("\n=== COUPLING-MATRIX SNAPSHOT: beta_multiplier=2.0 ===")
    print("Graph                 offset fmt   rel_RMS_dH  mean_abs_dP   source_gap")
    for r in summary:
        if r["anneal_beta_multiplier"]==2.0:
            print(f'{r["graph"]:21s} {r["offset_logit_halfspan"]:5.1f} '
                  f'{r["configuration"]:5s} '
                  f'{r["mean_state_relative_rms_field_error"]:10.4g} '
                  f'{r["mean_state_abs_switch_prob_distortion"]:12.5f} '
                  f'{r["mean_existing_returned_original_gap_pct"]:10.4f}%')
    print(f"\nCOUPLING SNAPSHOT SCIENTIFIC COMPLETE: "
          f"reference_states={len(states)} new_solver_runs=0 rows={len(data)} "
          f"summary={out/'E2_coupling_snapshot_summary.csv'}",flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--e1-raw-csv",type=Path,default=IDEAL_CSV)
    p.add_argument("--scout-dir",type=Path,default=DEFAULT_SCOUT_DIR)
    p.add_argument("--primary-dir",type=Path,default=DEFAULT_PRIMARY)
    p.add_argument("--extension-dir",type=Path,default=DEFAULT_EXTENSION)
    p.add_argument("--out",type=Path)
    p.add_argument("--audit-only",action="store_true")
    a=p.parse_args()
    run(a.e1_raw_csv,a.scout_dir,a.primary_dir,a.extension_dir,a.out,a.audit_only)


if __name__=="__main__":
    main()
