#!/usr/bin/env python3
"""M0 independent BPSK MIMO BER-versus-SNR pilot; not FP or MTJ evidence.

Each channel_seed identifies a transmitted frame, its complex Rayleigh H,
and a unit Gaussian noise draw rescaled for each selected SNR.
Frames are independent across seeds; measurements at different SNRs are
paired/NOT independent because the same frame seeds are deliberately reused.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import m0_mimo_reference as mimo


def run_batch(*, tx, rx, snrs, frames, channel_seed, solver_seed,
              beta, burnin, records, thin):
    if not 2 <= tx <= 16 or rx < 1 or frames < 1 or not snrs:
        raise ValueError("invalid MIMO dimensions, frame count, or SNR list")
    if len(set(snrs)) != len(snrs) or not all(math.isfinite(s) for s in snrs):
        raise ValueError("unique finite SNR values required")
    if not math.isfinite(beta) or beta <= 0 or burnin < 0 or records < 1 or thin < 1:
        raise ValueError("invalid Gibbs parameters")
    rows, frame_instances = [], []
    # Loop by frame: independent H,x and Gaussian draw per channel_seed.
    # Repeated SNR points reuse the same frame seed, making SNR curves paired.
    for idx in range(frames):
        fid = channel_seed + idx
        sid = solver_seed + idx
        for snr in snrs:
            instance = mimo.frame(tx=tx, rx=rx, snr_db=snr, seed=fid)
            result = mimo.solve_one(
                instance, beta=beta, sampler_seed=sid,
                burnin=burnin, records=records, thin=thin,
            )
            frame_instances.append({"frame_index":idx,"snr_db":snr,"instance":instance})
            rows.append({
                "frame_index":idx,"channel_seed":fid,"solver_seed":sid,
                "snr_db":snr,"tx":tx,"rx":rx,
                "exact_ml_bit_errors":result["exact_ml"]["bit_errors"],
                "gibbs_best_bit_errors":result["best_sampled_bit_errors"],
                "gibbs_best_ml_hit":int(result["best_sampled_gap"] <= 1e-8),
                "exact_ml_original_residual":result["exact_ml"]["residual"],
                "gibbs_best_original_residual":result["best_sampled_original_residual"],
                "gibbs_best_original_gap":max(0.0,result["best_sampled_gap"]),
                "sampled_ml_state_fraction":result["sampled_ml_hit_fraction"],
                "gibbs_attempted_spin_updates":result["total_spin_update_attempts"],
            })
    summary=[]
    for snr in snrs:
        sub=[r for r in rows if r["snr_db"] == snr]
        denom=frames*tx
        summary.append({
            "snr_db":snr,"independent_frames":frames,"transmitted_bits":denom,
            "exact_ml_bit_errors":sum(r["exact_ml_bit_errors"] for r in sub),
            "gibbs_best_bit_errors":sum(r["gibbs_best_bit_errors"] for r in sub),
            "exact_ml_ber":sum(r["exact_ml_bit_errors"] for r in sub)/denom,
            "gibbs_best_ber":sum(r["gibbs_best_bit_errors"] for r in sub)/denom,
            "gibbs_best_ml_hit_frames":sum(r["gibbs_best_ml_hit"] for r in sub),
            "gibbs_best_ml_hit_rate":sum(r["gibbs_best_ml_hit"] for r in sub)/frames,
            "mean_original_ml_residual_gap":sum(r["gibbs_best_original_gap"] for r in sub)/frames,
            "attempted_spin_updates_total":sum(r["gibbs_attempted_spin_updates"] for r in sub),
        })
    return rows,frame_instances,summary


def write_output(path, rows, frames, summary, configuration):
    path=Path(path)
    path.mkdir(parents=True,exist_ok=False)
    with (path/"paired_frames.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (path/"mimo_frames.jsonl").open("w",encoding="utf-8") as f:
        for record in frames:
            f.write(json.dumps(record,sort_keys=True,allow_nan=False)+"\n")
    meta={
        "tier":"E1 independent software BPSK MIMO; ideal Gibbs only",
        "aim":"M0 BER/ML baseline functionality check, not precision/device results",
        "configuration":configuration,
        "summary":summary,
        "interpretation":(
            "ML hit and BER are distinct; ML may differ from transmitted bits. "
            "Same channel_seed under different SNR yields paired correlated frames. "
            "Reported rates from small frame counts have substantial uncertainty. "
            "No confidence interval, hardware energy/latency, FP advantage or "
            "MRAM nonideality is inferred from this smoke test. "
            "Gibbs returns the best sample after burn-in; no first-hit timing measured."
        ),
        "script_hashes":{
            p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__),Path(mimo.__file__),Path(mimo.core.__file__))
        },
    }
    (path/"summary.json").write_text(json.dumps(meta,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.iterdir() if p.is_file()}
    (path/"SHA256SUMS.json").write_text(json.dumps(hashes,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return meta


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tx",type=int,default=4)
    p.add_argument("--rx",type=int,default=4)
    p.add_argument("--snrs",default="0,5,10,15",help="comma-separated SNR in dB")
    p.add_argument("--frames",type=int,default=32)
    p.add_argument("--channel-seed",type=int,default=2026110600)
    p.add_argument("--solver-seed",type=int,default=2026110700)
    p.add_argument("--beta",type=float,default=.8)
    p.add_argument("--burnin",type=int,default=1000)
    p.add_argument("--records",type=int,default=200)
    p.add_argument("--thin",type=int,default=5)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():
        p.error("output already exists: choose a NEW directory")
    try:
        snrs=[float(v.strip()) for v in a.snrs.split(",")]
        rows,instances,summary=run_batch(
            tx=a.tx,rx=a.rx,snrs=snrs,frames=a.frames,
            channel_seed=a.channel_seed,solver_seed=a.solver_seed,
            beta=a.beta,burnin=a.burnin,records=a.records,thin=a.thin)
        conf=dict(tx=a.tx,rx=a.rx,snrs=snrs,frames=a.frames,
                  channel_seed=a.channel_seed,solver_seed=a.solver_seed,
                  beta=a.beta,burnin=a.burnin,records=a.records,thin=a.thin)
        write_output(a.output,rows,instances,summary,conf)
    except (ValueError,FileExistsError) as exc:
        p.error(str(exc))
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
