#!/usr/bin/env python3
"""M1B: held-out calibrated, scale-granularity-matched coupling audit.

Representation-only E0/E1 diagnostic; no sampled/nonideal p-bit, bit-true
accumulator, physical MTJ, or synthesis. Scale calibration uses ONLY
fresh independent training channel/noise frames (no ML labels).
"""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

import m0_mimo_reference as mimo
import m0_ising_math as core
import m1_coupling_formats as quant

FAMILIES=("fp4","fp4_fn","fp6","fp6_fn","fp8","int4","int6","int8","bfp4","bfp6","bfp8")
GRANULARITIES=("global","tile")
ATOL=1e-8


def groups_for(n, granularity, tile):
    if granularity not in GRANULARITIES or tile<1 or n<2:
        raise ValueError("invalid grouping specification")
    groups={}
    for i in range(n):
        for j in range(i+1,n):
            name=("J_global" if granularity=="global"
                  else f"J_t{i//tile}_{j//tile}")
            groups.setdefault(name,[]).append((i,j))
    return groups


def frames_for(tx, rx, snrs, number, seed):
    if number<1:
        raise ValueError("frame count must be positive")
    # Same frame index/seed across SNRs -> intentionally paired noise draws.
    return [(idx,snr,mimo.frame(tx=tx,rx=rx,snr_db=snr,seed=seed+idx))
            for idx in range(number) for snr in snrs]


def validate_formats(formats, granularities):
    if not formats or len(set(formats))!=len(formats) or any(x not in FAMILIES for x in formats):
        raise ValueError("invalid format selection")
    if not granularities or len(set(granularities))!=len(granularities) or any(x not in GRANULARITIES for x in granularities):
        raise ValueError("invalid granularity selection")


def calibrate(cal_frames, formats, granularities, tile):
    if not cal_frames:
        raise ValueError("empty calibration frames")
    n=cal_frames[0][2]["tx"]
    frozen={}
    for gran in granularities:
        groups=groups_for(n,gran,tile)
        coef={name:[] for name in groups}
        coef["h"]=[]
        for _,_,frame in cal_frames:
            if frame["tx"]!=n:
                raise ValueError("different frame size")
            for name,edges in groups.items():
                coef[name].extend(frame["J"][i][j] for i,j in edges)
            coef["h"].extend(frame["h"])
        for kind in formats:
            # All scales are fixed using coefficient-MSE on TRAIN only.
            # No original ML labels or downstream BER are used to tune scales.
            scales={name:quant.tune_scale(values,kind)[0]
                    for name,values in coef.items()}
            if kind.startswith("bfp"):
                for name,v in scales.items():
                    exponent=round(math.log2(v))
                    if not -128 <= exponent <= 127:
                        raise ValueError("8-bit scale exponent not representable")
            frozen[(kind,gran)] = scales
    return frozen


def quantize_with_frozen(frame, kind, gran, tile, frozen_scales):
    n=frame["tx"]
    groups=groups_for(n,gran,tile)
    required=set(groups)|{"h"}
    if set(frozen_scales)!=required:
        raise ValueError("calibrated scale groups mismatch")
    J=[[0.0]*n for _ in range(n)]
    for name,edges in groups.items():
        scale=frozen_scales[name]
        for i,j in edges:
            J[i][j]=J[j][i]=quant.quantized_level(frame["J"][i][j],scale,kind)
    h=[quant.quantized_level(v,frozen_scales["h"],kind) for v in frame["h"]]
    core.assert_ising(J,h)
    b=quant.format_bits(kind)
    scale_metadata_width=8 if kind.startswith("bfp") else 32
    unique_coefs=n*(n-1)//2+n
    return {
        "J":J,"h":h,
        "coefficient_bits":b*unique_coefs,
        "metadata_bits":scale_metadata_width*(len(groups)+1),
        "total_nominal_bits":b*unique_coefs+scale_metadata_width*(len(groups)+1),
        "J_mse":sum((frame["J"][i][j]-J[i][j])**2
                    for i in range(n) for j in range(i+1,n)),
        "h_mse":sum((a-b)**2 for a,b in zip(frame["h"],h)),
    }


def exact_ground_compare(frame, q):
    """Reference original ML only for EVALUATION, never scale calibration."""
    oracle=mimo.exact_ml(frame)
    n=frame["tx"]
    if n>12:
        raise ValueError("M1B exact ground requires Nt<=12")
    levels=[]
    for state in itertools.product((-1,1),repeat=n):
        levels.append((core.energy(q["J"],q["h"],state), state))
    ground=min(e for e,_ in levels)
    minima=[s for e,s in levels if e<=ground+ATOL]
    original_gaps=[
        max(0.0,mimo.original_residual(frame,s)-oracle["residual"])
        for s in minima
    ]
    higher=[e-ground for e,_ in levels if e>ground+ATOL]
    minimum_energy_gap=min(higher) if higher else None
    return {
        "original_ml_preserved":int(min(original_gaps)<=ATOL),
        "quantized_ground_degeneracy":len(minima),
        "ground_degenerate":int(len(minima)>1),
        "best_possible_original_gap":min(original_gaps),
        "worst_possible_original_gap":max(original_gaps),
        "minimum_positive_quantized_energy_gap":minimum_energy_gap,
        "oracle_ml_bit_errors":oracle["bit_errors"],
        "original_ber_lower_bound_among_qground":min(mimo.bit_errors(s,frame["transmitted"])
                                                       for s in minima)/n,
        "original_ber_upper_bound_among_qground":max(mimo.bit_errors(s,frame["transmitted"])
                                                       for s in minima)/n,
    }


def run(tx,rx,snrs,cal_frames,held_frames,cal_seed,held_seed,
        formats,granularities,tile):
    validate_formats(formats,granularities)
    if not 2<=tx<=12 or rx<1 or cal_frames<1 or held_frames<1 or tile<1:
        raise ValueError("invalid MIMO dimensions or frame count")
    if not snrs or len(set(snrs))!=len(snrs) or not all(math.isfinite(x) for x in snrs):
        raise ValueError("invalid SNR list")
    if set(range(cal_seed,cal_seed+cal_frames)) & set(range(held_seed,held_seed+held_frames)):
        raise ValueError("calibration/heldout frame seeds overlap")
    cal=frames_for(tx,rx,snrs,cal_frames,cal_seed)
    held=frames_for(tx,rx,snrs,held_frames,held_seed)
    scales=calibrate(cal,formats,granularities,tile)
    rows=[]
    for frame_index,snr,instance in held:
        for gran in granularities:
            for kind in formats:
                q=quantize_with_frozen(instance,kind,gran,tile,scales[(kind,gran)])
                exact=exact_ground_compare(instance,q)
                rows.append({
                    "frame_index":frame_index,"channel_seed":held_seed+frame_index,
                    "snr_db":snr,"format":kind,"granularity":gran,
                    "calibration_frames_per_snr":cal_frames,
                    "heldout_frames_per_snr":held_frames,
                    **exact,
                    "coefficient_bits":q["coefficient_bits"],
                    "metadata_bits":q["metadata_bits"],
                    "total_nominal_bits":q["total_nominal_bits"],
                    "J_mse":q["J_mse"],"h_mse":q["h_mse"],
                })
    summary=[]
    for gran in granularities:
        for kind in formats:
            for snr in snrs:
                subset=[r for r in rows if r["granularity"]==gran
                        and r["format"]==kind and r["snr_db"]==snr]
                n=len(subset)
                summary.append({
                    "format":kind,"granularity":gran,"snr_db":snr,
                    "heldout_frames":n,
                    "original_ml_preserved":sum(r["original_ml_preserved"] for r in subset),
                    "degenerate_ground_frames":sum(r["ground_degenerate"] for r in subset),
                    "mean_best_possible_original_gap":sum(r["best_possible_original_gap"] for r in subset)/n,
                    "mean_worst_possible_original_gap":sum(r["worst_possible_original_gap"] for r in subset)/n,
                    "avg_J_mse":sum(r["J_mse"] for r in subset)/n,
                    "avg_h_mse":sum(r["h_mse"] for r in subset)/n,
                    "total_nominal_bits":subset[0]["total_nominal_bits"],
                })
    return rows,summary,scales,cal,held


def write_output(path,rows,summary,scales,cal,held,configuration):
    path=Path(path)
    path.mkdir(parents=True,exist_ok=False)
    with (path/"heldout_exact_results.csv").open("w",newline="",encoding="utf-8") as file:
        w=csv.DictWriter(file,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with (path/"heldout_frames.jsonl").open("w",encoding="utf-8") as file:
        for i,snr,inst in held:
            file.write(json.dumps({"frame_index":i,"snr_db":snr,"instance":inst},sort_keys=True)+"\n")
    with (path/"calibration_frames.jsonl").open("w",encoding="utf-8") as file:
        for i,snr,inst in cal:
            file.write(json.dumps({"frame_index":i,"snr_db":snr,"instance":inst},sort_keys=True)+"\n")
    serialized_scales={f"{kind}|{gran}":vals for (kind,gran),vals in scales.items()}
    metadata={
        "evidence":"E0/E1 representation-only independent BPSK MIMO M1B, NOT nonideal MRAM",
        "scope":"calibrated coefficient-scale policy, matched global/tile grouping for FP/INT/BFP; no p-bit solver",
        "config":configuration,"frozen_scales":serialized_scales,"summary":summary,
        "statistical_limit":"Paired SNR frames reuse H,x and normalized noise seeds. Original ML of small Nt only. Independent channel/noise frame is unit; no formal confidence intervals are provided by this pilot.",
        "hardware_limit":"Bits include unique symmetric J/h and assumed scale metadata only; not alignment, accumulation, routing, peripheral circuits, p-bit response or synthesized area/power. FP/INT real scales provisionally 32 bit, BFP signed power-of-two exponents 8 bit. These are NOT equal-area results.",
        "scale_fit":"Fixed per-group coefficient-MSE candidate-grid tuning on independent calibration frames ONLY; not globally optimal scale search, no heldout original objective tuning.",
        "ground_limit":"Exact quantized minima found by enumeration with 1e-8 energy tolerance; best/worst original residual gaps and BER are bounds over possible quantized minima, NOT sampled detector performance.",
        "sources_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (Path(__file__),Path(mimo.__file__),Path(core.__file__),Path(quant.__file__))},
    }
    (path/"m1b_manifest.json").write_text(json.dumps(metadata,indent=2,sort_keys=True,allow_nan=False)+"\n")
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in path.iterdir() if p.is_file()}
    (path/"SHA256SUMS.json").write_text(json.dumps(hashes,indent=2,sort_keys=True)+"\n")
    return metadata


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--tx",type=int,default=8)
    ap.add_argument("--rx",type=int,default=8)
    ap.add_argument("--snrs",default="0,5")
    ap.add_argument("--cal-frames",type=int,default=24)
    ap.add_argument("--heldout-frames",type=int,default=24)
    ap.add_argument("--cal-seed",type=int,default=2026112000)
    ap.add_argument("--heldout-seed",type=int,default=2026113000)
    ap.add_argument("--formats",default="fp4,fp4_fn,int4,bfp4,fp6,fp6_fn,int6,bfp6,fp8,int8,bfp8")
    ap.add_argument("--granularities",default="global,tile")
    ap.add_argument("--tile",type=int,default=4)
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    if a.output.exists():
        ap.error("output already exists, choose a fresh evidence folder")
    try:
        snrs=[float(x.strip()) for x in a.snrs.split(",")]
        formats=[x.strip() for x in a.formats.split(",")]
        grans=[x.strip() for x in a.granularities.split(",")]
        rows,summary,scales,cal,held=run(
            a.tx,a.rx,snrs,a.cal_frames,a.heldout_frames,
            a.cal_seed,a.heldout_seed,formats,grans,a.tile)
        conf=dict(tx=a.tx,rx=a.rx,snrs=snrs,cal_frames=a.cal_frames,
                  heldout_frames=a.heldout_frames,cal_seed=a.cal_seed,
                  heldout_seed=a.heldout_seed,formats=formats,granularities=grans,
                  tile=a.tile)
        write_output(a.output,rows,summary,scales,cal,held,conf)
    except (ValueError,FileExistsError) as exc:
        ap.error(str(exc))
    print("=== M1B FROZEN-CAL SCALE x GRANULARITY: HELD-OUT EXACT MIMO ===")
    print(" Format Group   SNR | OriginalMLRetained Degenerate | J-MSE   Metadata+codebits")
    for r in summary:
        print(f'{r["format"]:6s} {r["granularity"]:6s} {r["snr_db"]:4g} | '
              f'{r["original_ml_preserved"]:2d}/{r["heldout_frames"]}  '
              f'{r["degenerate_ground_frames"]:2d}/{r["heldout_frames"]} | '
              f'{r["avg_J_mse"]:.5f}  {r["total_nominal_bits"]}')
    print(f"Results saved to {a.output}")


if __name__=="__main__":
    main()
