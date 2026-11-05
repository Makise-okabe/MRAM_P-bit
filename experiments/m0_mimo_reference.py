#!/usr/bin/env python3
"""M0: independent complex BPSK MIMO-to-Ising reference (E1 software).

No prior experimental data, physical MTJ parameters or format results are used.
Pure Python standard library + fresh M0 Ising exact/Gibbs helper.
"""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import random

import m0_reference as core


def frame(tx=4, rx=4, snr_db=10.0, seed=20261106):
    """Rayleigh H_ri ~ CN(0,1/rx); noise n_r ~ CN(0,sigma2).

    Per-receive-antenna ensemble mean SNR = (tx/rx)/sigma2.
    Define sigma2=(tx/rx)/10**(snr_db/10). BPSK x is real +/-1.
    """
    if not isinstance(tx, int) or not isinstance(rx, int) or tx < 2 or rx < 1 or tx > 16:
        raise ValueError("require 2<=tx<=16 and rx>=1; exact oracle only")
    if not math.isfinite(snr_db) or abs(snr_db) > 100:
        raise ValueError("finite snr_db with |snr_db|<=100 is required")
    rng = random.Random(seed)
    h_std = 1 / math.sqrt(2 * rx)
    H = [[complex(rng.gauss(0, h_std), rng.gauss(0, h_std))
          for _ in range(tx)] for _ in range(rx)]
    transmitted = tuple(rng.choice((-1, 1)) for _ in range(tx))
    signal = [sum(H[r][i] * transmitted[i] for i in range(tx))
              for r in range(rx)]
    sigma2 = (tx / rx) / 10**(snr_db / 10)
    noise_std = math.sqrt(sigma2 / 2)
    noise = [complex(rng.gauss(0, noise_std), rng.gauss(0, noise_std))
             for _ in range(rx)]
    y = [signal[i] + noise[i] for i in range(rx)]
    gram = [[sum((H[r][i].conjugate()*H[r][j]).real
                 for r in range(rx)) for j in range(tx)] for i in range(tx)]
    b = [sum((H[r][i].conjugate()*y[r]).real for r in range(rx))
         for i in range(tx)]
    J = [[0.0] * tx for _ in range(tx)]
    for i in range(tx):
        for j in range(i + 1, tx):
            v = -2 * gram[i][j]
            J[i][j] = J[j][i] = v
    local_h = [2 * v for v in b]
    C = sum(abs(z)**2 for z in y) + sum(gram[i][i] for i in range(tx))
    core.assert_ising(J, local_h)
    def packed(z):
        return [z.real, z.imag]
    return dict(kind="mimo_bpsk", tx=tx, rx=rx, snr_db=snr_db,
                channel_seed=seed, sigma2_complex_noise=sigma2,
                channel_normalization="H_ri iid CN(0,1/rx)",
                snr_convention="E[|Hx|^2] per receive / E[|n|^2] = 10^(snr_db/10)",
                H=[[packed(z) for z in row] for row in H],
                y=[packed(z) for z in y],
                transmitted=list(transmitted),
                J=J, h=local_h, C=C)


def original_residual(instance, state):
    """Independent computation on original H and y, NOT on Ising J,h,C."""
    if len(state) != instance["tx"] or any(v not in (-1, 1) for v in state):
        raise ValueError("state is not a BPSK vector")
    total = 0.0
    for row, target in zip(instance["H"], instance["y"]):
        yh = sum(complex(*z)*state[i] for i, z in enumerate(row))
        error = complex(*target)-yh
        total += abs(error)**2
    return total


def bit_errors(state, truth):
    if len(state) != len(truth):
        raise ValueError("length mismatch")
    return sum(int(a != b) for a, b in zip(state, truth))


def exact_ml(instance):
    """Small Nt only. Exact ML is not necessarily the transmitted sequence."""
    n = instance["tx"]
    if n > 16:
        raise ValueError("exact ML only for tx<=16")
    states = itertools.product((-1, 1), repeat=n)
    best = float("inf")
    best_state = None
    degeneracy = 0
    for s in states:
        residual = original_residual(instance, s)
        if residual < best - 1e-10:
            best, best_state, degeneracy = residual, s, 1
        elif abs(residual-best) <= 1e-10:
            degeneracy += 1
    return dict(state=list(best_state), residual=best,
                degeneracy=degeneracy,
                bit_errors=bit_errors(best_state, instance["transmitted"]))


def solve_one(instance, *, beta=0.8, sampler_seed=20261107,
              burnin=4000, records=1000, thin=10):
    if not math.isfinite(beta) or beta<=0:
        raise ValueError("beta must be finite and positive")
    if burnin < 0 or records < 1 or thin < 1:
        raise ValueError("invalid Gibbs budget")
    oracle = exact_ml(instance)
    exact_ising = core.exact(instance["J"],instance["h"],beta,instance["C"])
    if abs(oracle["residual"] - exact_ising["ground_energy"]) > 1e-8:
        raise AssertionError("Independent ML and Ising exact minima disagree")
    draws = core.sample(instance["J"],instance["h"],beta,sampler_seed,burnin,records,thin)
    scored = [(s,original_residual(instance,s)) for s in draws]
    best_s,best_r = min(scored,key=lambda z:z[1])
    hits = sum(abs(r-oracle["residual"])<=1e-8 for _,r in scored)
    return dict(
        tier="E1 independent ideal MIMO/Ising software; no MRAM physical evidence",
        transmitted_bits=instance["transmitted"], channel_seed=instance["channel_seed"],
        sampler_seed=sampler_seed, tx=instance["tx"], rx=instance["rx"],
        snr_db=instance["snr_db"], sigma2_complex_noise=instance["sigma2_complex_noise"],
        beta=beta, burnin_spin_updates=burnin, recorded_samples=records,
        thinning_spin_updates=thin, total_spin_update_attempts=burnin+records*thin,
        exact_ml=oracle, exact_ising_ground_energy=exact_ising["ground_energy"],
        exact_ml_ber=oracle["bit_errors"]/instance["tx"],
        sampled_unique_states=len(set(draws)), sampled_ml_hit_fraction=hits/records,
        best_sampled_state=list(best_s), best_sampled_original_residual=best_r,
        best_sampled_gap=best_r-oracle["residual"],
        best_sampled_bit_errors=bit_errors(best_s,instance["transmitted"]),
        best_sampled_ber=bit_errors(best_s,instance["transmitted"])/instance["tx"],
        samples=draws)


def write_output(instance, result, directory):
    directory=Path(directory)
    directory.mkdir(parents=True,exist_ok=False)
    public={key:value for key,value in result.items() if key!="samples"}
    (directory/"mimo_manifest.json").write_text(json.dumps({
        "instance":instance,"result":public},indent=2,sort_keys=True,allow_nan=False)+"\n")
    with (directory/"mimo_samples.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["trial","bits","original_ml_residual","error_bits_vs_transmitted","exact_ml_hit"])
        for i,s in enumerate(result["samples"]):
            obj=original_residual(instance,s)
            w.writerow([i,"".join("1" if x>0 else "0" for x in s),repr(obj),
                       bit_errors(s,instance["transmitted"]),
                       int(abs(obj-result["exact_ml"]["residual"])<=1e-8)])
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.glob("mimo_*")}
    hashes["source_m0_mimo_reference.py"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    hashes["source_m0_reference.py"]=hashlib.sha256(Path(core.__file__).read_bytes()).hexdigest()
    (directory/"SHA256SUMS.json").write_text(json.dumps(hashes,sort_keys=True,indent=2)+"\n")
    return public


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--tx",type=int,default=4)
    ap.add_argument("--rx",type=int,default=4)
    ap.add_argument("--snr-db",type=float,default=10.0)
    ap.add_argument("--channel-seed",type=int,default=20261106)
    ap.add_argument("--sampler-seed",type=int,default=20261107)
    ap.add_argument("--beta",type=float,default=0.8)
    ap.add_argument("--burnin",type=int,default=4000)
    ap.add_argument("--records",type=int,default=1000)
    ap.add_argument("--thin",type=int,default=10)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    if args.output.exists():
        ap.error("output path already exists; use a fresh evidence directory")
    try:
        inst=frame(args.tx,args.rx,args.snr_db,args.channel_seed)
        result=solve_one(inst,beta=args.beta,sampler_seed=args.sampler_seed,
                         burnin=args.burnin,records=args.records,thin=args.thin)
        public=write_output(inst,result,args.output)
    except (ValueError,FileExistsError) as e:
        ap.error(str(e))
    print(json.dumps(public,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
