#!/usr/bin/env python3
"""Read-only M1 exact-ground decomposition of original vs quantized Ising.

Use ORIGINAL user-run M1 m1_frames.jsonl + m1_paired_runs.csv.
No simulator sampling or device data is generated. This is E0/E1/E2 analysis.
Historical 'fp32' in the 2026-11-06 pilot meant UNROUNDED reference.
The current exact binary32 coefficient format must NOT be substituted for it.
"""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

import m0_ising_math as core
import m0_mimo_reference as mimo
import m1_coupling_formats as fmt

ATOL = 1e-8


def read_inputs(csv_path, frames_path):
    with Path(csv_path).open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    with Path(frames_path).open(encoding="utf-8") as f:
        frames=[json.loads(line) for line in f if line.strip()]
    if not rows or not frames:
        raise ValueError("pilot files must be non-empty")
    required={"frame_index","snr_db","format","response","selected_state",
              "ml_hit","quantized_selection_energy","original_residual_gap"}
    if not required.issubset(rows[0]):
        raise ValueError("required M1 columns missing")
    frame_dict={}
    for f in frames:
        key=(int(f["frame_index"]),float(f["snr_db"]))
        if key in frame_dict:
            raise ValueError("duplicate saved frame")
        frame_dict[key]=f["instance"]
    if not frame_dict:
        raise ValueError("no saved frames")
    return rows,frame_dict


def quantized_minima(instance, label, tile):
    kind="fp64_ref" if label=="fp32" else label
    # The original pilot mislabeled UNROUNDED coefficients as fp32.
    if kind not in fmt.FORMATS:
        raise ValueError("unknown original format label: "+label)
    quant=fmt.quantize_couplings(instance["J"],instance["h"],kind,tile=tile)
    states=itertools.product((-1,1),repeat=instance["tx"])
    best=float("inf")
    minimizers=[]
    for state in states:
        e=core.energy(quant["J"],quant["h"],state)
        if e<best-ATOL:
            best=e
            minimizers=[state]
        elif abs(e-best)<=ATOL:
            minimizers.append(state)
    return dict(minima=set(minimizers),ground_energy=best,quant=quant)


def audit(rows,frame_dict,tile=4):
    # Only small-N exact check; these datasets are 8-spin MIMO.
    if any(int(frame["tx"])>16 for frame in frame_dict.values()):
        raise ValueError("exact oracle restricted to Nt<=16")
    labels=sorted(set(r["format"] for r in rows))
    cache={}
    unique=[]
    evaluated=[]
    for row in rows:
        key=(int(row["frame_index"]),float(row["snr_db"]))
        if key not in frame_dict:
            raise ValueError("missing matching original frame")
        frame=frame_dict[key]
        label=row["format"]
        ckey=(key,label)
        if ckey not in cache:
            oracle=mimo.exact_ml(frame)
            quant=quantized_minima(frame,label,tile)
            source_min=tuple(oracle["state"])
            in_min=source_min in quant["minima"]
            min_original_gap=min(
                mimo.original_residual(frame,s)-oracle["residual"]
                for s in quant["minima"])
            cache[ckey]=(quant,oracle,in_min,max(0.0,min_original_gap))
            unique.append(dict(
                frame_index=key[0],snr_db=key[1],format=label,
                original_ml_is_quantized_minimizer=int(in_min),
                quantized_ground_degeneracy=len(quant["minima"]),
                best_original_gap_within_quantized_minima=max(0.0,min_original_gap)
            ))
        quant,oracle,in_min,min_gap=cache[ckey]
        bitstr=row["selected_state"]
        state=tuple(1 if c=="1" else -1 if c=="0" else None for c in bitstr)
        if len(state)!=frame["tx"] or any(x is None for x in state):
            raise ValueError("invalid selected state bitstring")
        local_e=core.energy(quant["quant"]["J"],quant["quant"]["h"],state)
        logged_e=float(row["quantized_selection_energy"])
        # Validate reconstruction BEFORE inferring failure mechanisms.
        if not math.isclose(local_e,logged_e,rel_tol=1e-9,abs_tol=1e-8):
            raise ValueError("saved pilot energy disagrees with reconstructed Hamiltonian: "+
                             str((key,label,local_e,logged_e)))
        original_gap=max(0.0,mimo.original_residual(frame,state)-oracle["residual"])
        if not math.isclose(original_gap,float(row["original_residual_gap"]),
                            rel_tol=1e-8,abs_tol=1e-8):
            raise ValueError("saved original residual gap mismatch")
        selected_quant_ground=state in quant["minima"]
        selected_original_ml=original_gap<=ATOL
        if selected_original_ml!=(int(row["ml_hit"])==1):
            raise ValueError("saved ML-hit label mismatch")
        evaluated.append(dict(
            frame_index=key[0],snr_db=key[1],format=label,
            response=row["response"],
            original_ml_in_quantized_minima=int(in_min),
            selected_is_quantized_minimum=int(selected_quant_ground),
            selected_is_original_ml=int(selected_original_ml),
            selected_original_gap=original_gap,
            best_possible_gap_among_quantized_minima=min_gap,
            quantized_energy_gap=max(0.0,local_e-quant["ground_energy"])
        ))
    summary=[]
    responses=sorted(set(r["response"] for r in evaluated))
    snrs=sorted(set(r["snr_db"] for r in evaluated))
    for response in responses:
        for snr in snrs:
            for label in labels:
                group=[r for r in evaluated
                       if r["response"]==response and r["snr_db"]==snr
                       and r["format"]==label]
                if not group:
                    continue
                n=len(group)
                summary.append(dict(
                    response=response,snr_db=snr,format=label,frames=n,
                    original_ml_preserved_as_quantized_minimum=sum(
                        r["original_ml_in_quantized_minima"] for r in group),
                    found_quantized_minimum=sum(
                        r["selected_is_quantized_minimum"] for r in group),
                    original_ml_hits=sum(r["selected_is_original_ml"] for r in group),
                    failed_sampling_even_when_orig_ml_is_quant_min=sum(
                        r["original_ml_in_quantized_minima"] and
                        not r["selected_is_original_ml"] for r in group),
                    mean_selected_quantized_gap=sum(
                        r["quantized_energy_gap"] for r in group)/n,
                    mean_original_residual_gap=sum(
                        r["selected_original_gap"] for r in group)/n
                ))
    return unique,evaluated,summary


def write_output(path,source_csv,source_frames,unique,evaluated,summary):
    p=Path(path)
    p.mkdir(parents=True,exist_ok=False)
    def write_csv(name,rows):
        with (p/name).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    write_csv("format_exact_minima.csv",unique)
    write_csv("frame_exact_audit.csv",evaluated)
    manifest=dict(
        evidence="E0 exact finite-N oracle audit of user-run E1/E2 M1 pilot; no new physical/simulation data",
        sources={
            Path(source_csv).name:hashlib.sha256(Path(source_csv).read_bytes()).hexdigest(),
            Path(source_frames).name:hashlib.sha256(Path(source_frames).read_bytes()).hexdigest()
        },
        reference_erratum="Old M1 fp32 means unchanged Python float64; correctly reconstructed with fp64_ref, NOT new true binary32 format.",
        notes="Quantization ground-state preservation and sampled-solver ground-state arrival are distinct. "
              "Quantized ground tie states may have different original ML residuals. "
              "A candidate can match original ML without minimizing quantized energy, "
              "or can minimize quantized energy without matching original ML. "
              "No time-to-target, hardware energy, device-proven nonideality or format novelty inferred.",
        summary=summary,
        audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    )
    (p/"m1_exact_audit.json").write_text(json.dumps(manifest,indent=2,allow_nan=False)+"\n")
    checks={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file()}
    (p/"SHA256SUMS.json").write_text(json.dumps(checks,indent=2,sort_keys=True)+"\n")
    return manifest


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runs",required=True,type=Path)
    ap.add_argument("--frames",required=True,type=Path)
    ap.add_argument("--tile",type=int,default=4)
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    if a.output.exists():
        ap.error("output already exists; choose a fresh directory")
    try:
        rows,frames=read_inputs(a.runs,a.frames)
        unique,checked,summary=audit(rows,frames,tile=a.tile)
        write_output(a.output,a.runs,a.frames,unique,checked,summary)
    except (ValueError,FileExistsError) as exc:
        ap.error(str(exc))
    print("=== EXACT QUANTIZATION vs SAMPLING GATE ===")
    print("Response SNR Format | ML-in-quant-min | Selected-quant-min | Original-ML-hits")
    for item in summary:
        print(f'{item["response"]:11s} {item["snr_db"]:>4g} '
              f'{item["format"]:7s} | '
              f'{item["original_ml_preserved_as_quantized_minimum"]:2d}/{item["frames"]:2d} | '
              f'{item["found_quantized_minimum"]:2d}/{item["frames"]:2d} | '
              f'{item["original_ml_hits"]:2d}/{item["frames"]:2d}')
    print(f"Evidence folder: {a.output}")


if __name__=="__main__":
    main()
