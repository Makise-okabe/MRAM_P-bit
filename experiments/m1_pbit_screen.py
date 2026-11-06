#!/usr/bin/env python3
"""M1 software screening: FP4/FP6/FP8 coupling versus scaled INT/BFP.

Nonideal sigmoid variants are ILLUSTRATIVE BEHAVIORAL surrogates (E2),
NOT MRAM device models or foundry/SPICE measurements. This is NOT synthesis.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random

import m0_mimo_reference as mimo
import m0_ising_math as core
import m1_coupling_formats as fmt

RESPONSES = ("ideal", "gain080", "offset015", "contrast090")


def pbit_probability(field, beta, response, offset=0.0):
    if response=="ideal":
        return core.sigmoid(2*beta*field)
    if response=="gain080":
        return core.sigmoid(2*beta*(0.8*field))
    if response=="offset015":
        return core.sigmoid(2*beta*(field+offset))
    if response=="contrast090":
        return 0.05 + 0.9*core.sigmoid(2*beta*field)
    raise ValueError("unknown response")


def simulate_quantized(J,h,*,beta,seed,response,offsets,
                       burnin,records,thin):
    """Choose final state by QUANTIZED Ising energy only.

    The full-precision MIMO original is never consulted for runtime state
    selection. Original residual/BER are computed post hoc externally.
    """
    core.assert_ising(J,h)
    if len(offsets)!=len(h) or beta<=0 or burnin<0 or records<1 or thin<1:
        raise ValueError("invalid solver budget or offsets")
    rng=random.Random(seed)
    n=len(h)
    s=[rng.choice((-1,1)) for _ in range(n)]
    best_state=None
    best_e=float("inf")
    best_at=None
    for t in range(1,burnin+records*thin+1):
        i=rng.randrange(n)
        field=h[i]+sum(J[i][j]*s[j] for j in range(n) if j!=i)
        p=pbit_probability(field,beta,response,offsets[i])
        s[i]=1 if rng.random()<p else -1
        if t>burnin and (t-burnin)%thin==0:
            e=core.energy(J,h,s)
            if best_state is None or e<best_e-1e-12:
                best_state=tuple(s)
                best_e=e
                best_at=t
    return dict(state=best_state,solver_energy=best_e,
                selected_at_update=best_at,
                attempted_updates=burnin+records*thin,
                selection_checkpoints=records)


def run_screen(tx,rx,snrs,frames,channel_seed,solver_seed,device_seed,
               beta,burnin,records,thin,tile,formats,responses):
    if tx<2 or tx>16 or rx<1 or frames<1 or not snrs:
        raise ValueError("invalid benchmark config")
    if not all(math.isfinite(x) for x in snrs) or len(set(snrs))!=len(snrs):
        raise ValueError("invalid SNRs")
    if not formats or not responses or any(x not in fmt.FORMATS for x in formats):
        raise ValueError("invalid coupling formats")
    if any(x not in RESPONSES for x in responses):
        raise ValueError("invalid device response names")
    if not math.isfinite(beta) or beta<=0 or burnin<0 or records<1 or thin<1 or tile<1:
        raise ValueError("invalid solver config")
    # Same fixed per-device offset population in all frames and formats.
    offsets=[random.Random(device_seed+i*7919).gauss(0,0.15)
             for i in range(tx)]
    rows=[]
    frame_defs=[]
    for idx in range(frames):
        ch_seed=channel_seed+idx
        sd=solver_seed+idx
        for snr in snrs:
            instance=mimo.frame(tx=tx,rx=rx,snr_db=snr,seed=ch_seed)
            oracle=mimo.exact_ml(instance)
            frame_defs.append(dict(frame_index=idx,channel_seed=ch_seed,
                                   snr_db=snr,instance=instance))
            quantized={name:fmt.quantize_couplings(instance["J"],instance["h"],
                                                  name,tile=tile)
                       for name in formats}
            for response in responses:
                for name in formats:
                    q=quantized[name]
                    result=simulate_quantized(q["J"],q["h"],beta=beta,
                            seed=sd,response=response,offsets=offsets,
                            burnin=burnin,records=records,thin=thin)
                    state=result["state"]
                    residual=mimo.original_residual(instance,state)
                    bit_errors=mimo.bit_errors(state,instance["transmitted"])
                    rows.append(dict(
                        frame_index=idx,channel_seed=ch_seed,solver_seed=sd,
                        device_seed=device_seed,tx=tx,rx=rx,snr_db=snr,
                        response=response,format=name,
                        selected_state="".join("1" if v>0 else "0" for v in state),
                        selected_at_update=result["selected_at_update"],
                        attempted_spin_updates=result["attempted_updates"],
                        selection_checkpoints=result["selection_checkpoints"],
                        quantized_selection_energy=result["solver_energy"],
                        original_residual=residual,
                        original_ml_residual=oracle["residual"],
                        original_residual_gap=max(0.,residual-oracle["residual"]),
                        ml_hit=int(abs(residual-oracle["residual"])<=1e-8),
                        bit_errors=bit_errors,
                        original_exact_ml_bit_errors=oracle["bit_errors"],
                        coefficient_bits=q["coefficient_bits"],
                        scale_metadata_bits=q["metadata_bits"],
                        total_coefficient_plus_metadata_bits=q["coefficient_bits"]+q["metadata_bits"],
                        mse_J=q["mse_J"],mse_h=q["mse_h"],
                    ))
    summary=[]
    for response in responses:
        for snr in snrs:
            for name in formats:
                sub=[r for r in rows if r["response"]==response and
                     r["snr_db"]==snr and r["format"]==name]
                summary.append(dict(
                    response=response,snr_db=snr,format=name,
                    frames=len(sub),bits_total=len(sub)*tx,
                    bit_errors_total=sum(r["bit_errors"] for r in sub),
                    ber=sum(r["bit_errors"] for r in sub)/(len(sub)*tx),
                    ml_hits=sum(r["ml_hit"] for r in sub),
                    ml_hit_rate=sum(r["ml_hit"] for r in sub)/len(sub),
                    mean_original_ml_gap=sum(r["original_residual_gap"] for r in sub)/len(sub),
                    avg_J_mse=sum(r["mse_J"] for r in sub)/len(sub),
                    avg_h_mse=sum(r["mse_h"] for r in sub)/len(sub),
                    nominal_stored_bits=sub[0]["total_coefficient_plus_metadata_bits"],
                    attempted_updates_per_frame=sub[0]["attempted_spin_updates"],
                ))
    return rows,frame_defs,summary,offsets


def output_evidence(output,rows,frames,summary,offsets,config):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    with (output/"m1_paired_runs.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with (output/"m1_frames.jsonl").open("w",encoding="utf-8") as f:
        for r in frames:
            f.write(json.dumps(r,sort_keys=True,allow_nan=False)+"\n")
    meta=dict(
        evidence_tier="E1 ideal / E2 illustrative nonideal p-bit behavioral models",
        research_caveat="NO physically validated MRAM p-bit model, no FYP H1/H2 novelty proven",
        outcome_caveat="Instance-specific quantizer MSE scale tuning is an optimistic upper-bound; not deployable calibration. "
                       "Formats have different coefficient+scale storage; NOT equal-area/energy. "
                       "No accumulator/exponent-alignment/timing/replica hardware cost implemented. "
                       "Each format selects best state via its own quantized Hamiltonian; "
                       "original H,y used only for post-hoc scoring.",
        config=config,device_offsets=offsets,summary=summary,
        scale_model="FP4/6/8 and INT4/6/8 use instance-optimized global real scalar for J plus h; "
                    "BFP4/6/8 uses power-of-two scale per symmetric tile-pair for J plus h.",
        response_model="ideal; gain0.80; fixed neuron offset std=0.15 field units; contrast0.90 "
                       "all are unvalidated illustrative response curves",
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (Path(__file__),Path(mimo.__file__),
                                 Path(mimo.core.__file__),Path(fmt.__file__))},
    )
    (output/"m1_manifest.json").write_text(json.dumps(meta,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.iterdir() if p.is_file()}
    (output/"SHA256SUMS.json").write_text(json.dumps(hashes,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return meta


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tx",type=int,default=8)
    p.add_argument("--rx",type=int,default=8)
    p.add_argument("--snrs",default="0,5")
    p.add_argument("--frames",type=int,default=12)
    p.add_argument("--channel-seed",type=int,default=2026111600)
    p.add_argument("--solver-seed",type=int,default=2026111700)
    p.add_argument("--device-seed",type=int,default=2026111800)
    p.add_argument("--beta",type=float,default=.8)
    p.add_argument("--burnin",type=int,default=400)
    p.add_argument("--records",type=int,default=120)
    p.add_argument("--thin",type=int,default=5)
    p.add_argument("--tile",type=int,default=4)
    p.add_argument("--formats",default=",".join(fmt.FORMATS))
    p.add_argument("--responses",default=",".join(RESPONSES))
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():
        p.error("output exists; select a NEW evidence directory")
    try:
        snrs=[float(v.strip()) for v in a.snrs.split(",")]
        formats=a.formats.split(",")
        responses=a.responses.split(",")
        rows,frames,summary,offsets=run_screen(
            a.tx,a.rx,snrs,a.frames,a.channel_seed,a.solver_seed,a.device_seed,
            a.beta,a.burnin,a.records,a.thin,a.tile,formats,responses)
        cfg=dict(tx=a.tx,rx=a.rx,snrs=snrs,frames=a.frames,
                 channel_seed=a.channel_seed,solver_seed=a.solver_seed,
                 device_seed=a.device_seed,beta=a.beta,burnin=a.burnin,
                 records=a.records,thin=a.thin,tile=a.tile,formats=formats,
                 responses=responses)
        output_evidence(a.output,rows,frames,summary,offsets,cfg)
    except (ValueError,FileExistsError) as exc:
        p.error(str(exc))
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
