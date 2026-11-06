#!/usr/bin/env python3
"""M2 integrated RTL gate: row -> best-of-represented-energy tracker.

A frozen symmetric Ising code matrix and biases define the Hamiltonian.
For each synthetic single-spin proposal, an independent Python reference
recomputes the COMPLETE represented energy from all pairs, including rejects
and no-flip cases. It also checks the expected pre-update local field.
The SV testbench streams coefficients into the actual row RTL and verifies
the wired tracker output after row_done.

No stochastic-MTJ, MIMO detector, real MRAM, memory bandwidth, or scheduler
is implemented here. Tested update proposals are synthetic, deterministic.
"""
import argparse
import hashlib
import json
import random
import shutil
import subprocess
from pathlib import Path

from m2_verify_row_vectors import (
    decode_j, decode_h, expected_field, hex_twos
)


def state_word(spins):
    return sum((1 << i) if spin else 0 for i, spin in enumerate(spins))


def q24_coupling(mode, raw, scale_j, exp_j):
    return (raw * scale_j << (3 if mode == 0 else 4)) if mode != 2 else raw << (24 + exp_j)


def q24_bias(mode, raw, scale_h, exp_h):
    return (raw * scale_h << (0 if mode == 0 else 4)) if mode != 2 else raw << (24 + exp_h)


def full_energy(spins, weights, biases):
    """E=-sum_(i<j)Jij*s_i*s_j -sum_i h_i*s_i, integer Q24."""
    s = [1 if bit else -1 for bit in spins]
    n = len(spins)
    return -sum(weights[i][j] * s[i] * s[j]
                for i in range(n) for j in range(i+1, n)) \
           - sum(biases[i] * s[i] for i in range(n))


def generate_trace(path, mode, n, nsteps, seed):
    rng = random.Random(seed + 100000 * mode + n)
    max_code = 63 if mode == 2 else 15
    # One scale per entire Hamiltonian; no unphysical rescaling per update.
    sj = (1 << 19) if mode == 0 else (3 << 18) if mode == 1 else 0
    sh = (1 << 19) if mode == 0 else (1 << 19) if mode == 1 else 0
    ej, eh = (-4, -3) if mode == 2 else (0, 0)
    codes = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            code = rng.randint(0, max_code)
            codes[i][j] = codes[j][i] = code
    h_codes = [rng.randrange(64) for _ in range(n)]
    weights = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            w = q24_coupling(mode, decode_j(mode, codes[i][j]), sj, ej)
            weights[i][j] = weights[j][i] = w
    biases = [q24_bias(mode, decode_h(mode, c), sh, eh)
              for c in h_codes]
    spins = [rng.randrange(2) for _ in range(n)]
    init_spins = list(spins)
    origin = full_energy(spins, weights, biases)
    best = list(spins)
    current_rel = best_rel = 0
    accepted = improvements = rejected = no_flips = 0
    with path.open("w", encoding="ascii") as out:
        out.write(" ".join([
            str(nsteps), hex_twos(state_word(spins),n),
            hex_twos(sj,32),hex_twos(sh,32),
            hex_twos(ej,8),hex_twos(eh,8)
        ]) + "\n")
        for t in range(nsteps):
            idx = rng.randrange(n)
            old_bit = spins[idx]
            # Every seventh step is a no-flip; every eleventh is rejected.
            new_bit = old_bit if t % 7 == 0 else (1-old_bit)
            do_apply = int(t % 11 != 10)
            candidate = list(spins)
            candidate[idx] = new_bit
            if new_bit == old_bit: no_flips += 1
            if not do_apply: rejected += 1
            h = biases[idx] + sum(weights[idx][j] *
                    (1 if spins[j] else -1)
                    for j in range(n) if j != idx)
            encoded = [codes[idx][j] for j in range(n) if j != idx]
            signs = [spins[j] for j in range(n) if j != idx]
            field_ref, _ = expected_field(
                mode, encoded, signs, h_codes[idx], sj, sh, ej, eh)
            assert h == field_ref, (mode, n, t, h, field_ref)
            before = full_energy(spins,weights,biases)
            proposed = full_energy(candidate,weights,biases)
            delta = 2 * (1 if old_bit else -1) * h \
                if old_bit != new_bit else 0
            assert proposed-before == delta, (mode,n,t,proposed-before,delta)
            if do_apply:
                spins = candidate
                current_rel = proposed - origin
                accepted += 1
                if current_rel < best_rel:
                    best_rel = current_rel
                    best = list(spins)
                    improvements += 1
            assert current_rel == full_energy(spins,weights,biases) - origin
            out.write(" ".join([
                str(idx),hex_twos(h_codes[idx],6),
                hex_twos(old_bit,1),hex_twos(new_bit,1),
                hex_twos(do_apply,1),hex_twos(state_word(candidate),n),
                hex_twos(h,64),hex_twos(current_rel,64),
                hex_twos(best_rel,64),hex_twos(state_word(best),n),
                hex_twos(accepted,32)
            ]) + "\n")
            for code, spin in zip(encoded,signs):
                out.write(f"{code:x} {spin:x}\n")
    return dict(mode=mode,n=n,steps=nsteps,accepted=accepted,
        improvements=improvements,rejections=rejected,no_flips=no_flips,
        initial_state=hex_twos(state_word(init_spins),n),
        final_best_relative_energy_q24=best_rel)


def run(args):
    if not shutil.which("iverilog") or not shutil.which("vvp"):
        raise RuntimeError("iverilog and vvp must be available on PATH")
    root=Path(__file__).resolve().parents[1]
    rtl_files=[root/"rtl/pbit_local_field_row.sv",
        root/"rtl/pbit_best_energy_tracker.sv",
        root/"rtl/pbit_row_best_state_system.sv",
        root/"rtl/tb_pbit_row_best_state_system.sv"]
    args.output.mkdir(parents=True,exist_ok=False)
    records=[]
    for n,nsteps in ((16,32),(128,48)):
        for mode in (0,1,2):
            vec=args.output/f"integrated_N{n}_mode{mode}.txt"
            vvp=args.output/f"integrated_N{n}_mode{mode}.vvp"
            info=generate_trace(vec,mode,n,nsteps,args.seed)
            cmd=["iverilog","-g2012",
                "-s","tb_pbit_row_best_state_system",
                f"-Ptb_pbit_row_best_state_system.TOP_TB_N={n}",
                f"-Ptb_pbit_row_best_state_system.TOP_TB_MODE={mode}",
                "-o",str(vvp)] + list(map(str,rtl_files))
            subprocess.run(cmd,check=True,timeout=60)
            result=subprocess.run(
                ["vvp",str(vvp),f"+VECTORS={vec.resolve()}"],
                check=True,capture_output=True,text=True,timeout=60)
            marker=f"M2 INTEGRATED PASS: mode={mode} N={n} steps={nsteps}"
            if marker not in result.stdout:
                raise RuntimeError("simulation lacked PASS marker")
            print(result.stdout.strip(),flush=True)
            info["sim_output"]=result.stdout.strip()
            records.append(info)
    summary=dict(status="PASS",total_steps=sum(r["steps"] for r in records),
       total_accepted=sum(r["accepted"] for r in records),
       test_type="symmetric represented Ising Hamiltonian; complete O(N^2) Python energy oracle",
       warning="Synthetic updates and external testbench scheduler; no stochastic p-bit or MIMO detection",
       seed=args.seed,records=records,
       source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
           for p in rtl_files+[Path(__file__),
                     root/"scripts/m2_verify_row_vectors.py"]})
    (args.output/"integrated_results.json").write_text(
       json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("M2 INTEGRATED ALL PASS: 3 modes x 2 sizes x "
          f"{summary['total_steps']} proposed updates.")
    print(f"Result folder: {args.output}")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--seed",type=int,default=20261106)
    a=p.parse_args()
    if a.output.exists():
        p.error("output directory exists")
    run(a)


if __name__=="__main__":
    main()
