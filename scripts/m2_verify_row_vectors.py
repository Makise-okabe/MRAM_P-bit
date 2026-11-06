#!/usr/bin/env python3
"""M2: deterministic Python oracle versus cycle-serial RTL (Icarus).

Verifies all three fixed H2 formats at N=16,64,128 with stalls, signed
values, zero/subnormals, reserved negative integer codes, and Q16 saturation.
This checks the *specified fixed-point RTL semantics*, NOT numerical
equivalence to floating-scale H2, device physics, or synthesis cost.
Standard library only. Existing Icarus must be installed and on PATH.
"""
import argparse
import hashlib
import json
import random
import shutil
import subprocess
from pathlib import Path


def signed(v, bits):
    v &= (1 << bits) - 1
    return v - (1 << bits) if v & (1 << (bits - 1)) else v


def decode_j(mode, code):
    if mode == 0:
        e = (code >> 1) & 3
        m = code & 1
        magnitude = m if e == 0 else (2 + m) << (e - 1)
        return -magnitude if code & 8 else magnitude
    if mode == 1:
        return max(-7, signed(code, 4))
    return max(-31, signed(code, 6))


def decode_h(mode, code):
    if mode == 0:
        e = (code >> 2) & 7
        m = code & 3
        magnitude = m if e == 0 else (4 + m) << (e - 1)
        return -magnitude if code & 32 else magnitude
    return max(-31, signed(code, 6))


def expected_field(mode, codes, signs, bias, scale_j, scale_h, exp_j, exp_h):
    raw_sum = sum(decode_j(mode, c) * (1 if s else -1)
                  for c, s in zip(codes, signs))
    hraw = decode_h(mode, bias)
    if mode == 0:
        q24 = (raw_sum * scale_j << 3) + hraw * scale_h
    elif mode == 1:
        q24 = ((raw_sum * scale_j) << 4) + ((hraw * scale_h) << 4)
    else:
        def pot(raw, exp):
            shift = exp + 24
            return raw << shift if shift >= 0 else raw >> -shift
        q24 = pot(raw_sum, exp_j) + pot(hraw, exp_h)
    # Deliberately keep test vectors inside signed 64-bit math.
    if not -(1 << 63) <= q24 < (1 << 63):
        raise ValueError("test vector overflows Q40.24")
    shifted = q24 >> 8
    q16 = max(-(1 << 31), min((1 << 31) - 1, shifted))
    return q24, q16


def hex_twos(x, bits):
    return format(x & ((1 << bits) - 1), "x")


def make_case(rng, mode, n, t):
    if mode == 0:
        max_code = 15
    elif mode == 1:
        max_code = 15
    else:
        max_code = 63
    codes = [rng.randint(0, max_code) for _ in range(n - 1)]
    signs = [rng.randrange(2) for _ in range(n - 1)]
    bias = rng.randint(0, 63)
    scale_j = rng.choice([1<<20, 1<<19, 5<<18, 4<<20, 64<<20])
    scale_h = rng.choice([1<<20, 1<<19, 3<<19, 2<<20])
    exp_j = rng.choice([-6, -3, 0, 2, 4])
    exp_h = rng.choice([-4, -1, 0, 2])
    if t == 0:
        codes = [6 if mode == 0 else 7 if mode == 1 else 31] * (n - 1)
        signs = [1] * (n - 1)
        bias = 0
        scale_j = 64 << 20
        exp_j = 4
    if t == 1:
        codes = [14 if mode == 0 else 9 if mode == 1 else 33] * (n - 1)
        signs = [1] * (n - 1)
        bias = 63
        exp_j = 4
    if t == 2:
        codes = [0] * (n - 1)
        bias = 0
    expected_q24,expected_q16=expected_field(
        mode,codes,signs,bias,scale_j,scale_h,exp_j,exp_h)
    return (scale_j,scale_h,exp_j,exp_h,bias,
            expected_q24,expected_q16,codes,signs)


def write_vectors(path, mode, n, count, seed):
    rng = random.Random(seed + 10000 * mode + n)
    with path.open("w", encoding="ascii") as out:
        out.write(f"{count}\n")
        for t in range(count):
            sj,sh,ej,eh,bias,q24,q16,codes,signs=make_case(rng,mode,n,t)
            out.write(" ".join([
                hex_twos(sj,32),hex_twos(sh,32),
                hex_twos(ej,8),hex_twos(eh,8),
                hex_twos(bias,6),hex_twos(q24,64),hex_twos(q16,32)
            ]) + "\n")
            for code,sign in zip(codes,signs):
                out.write(f"{code:x} {sign:x}\n")


def run(args):
    if shutil.which("iverilog") is None or shutil.which("vvp") is None:
        raise RuntimeError("Icarus Verilog and vvp are required on PATH")
    root=Path(__file__).resolve().parents[1]
    source=root/"rtl/pbit_local_field_row.sv"
    bench=root/"rtl/tb_pbit_row_vectors.sv"
    args.output.mkdir(parents=True,exist_ok=False)
    records=[]
    for n in (16,64,128):
        for mode in (0,1,2):
            num_cases=4 if n==16 else 8 if n==64 else 16
            vec=args.output/f"vectors_N{n}_mode{mode}.txt"
            sim=args.output/f"rtl_N{n}_mode{mode}.vvp"
            write_vectors(vec,mode,n,num_cases,args.seed)
            cmd=["iverilog","-g2012","-s","tb_pbit_row_vectors",
                 f"-Ptb_pbit_row_vectors.TOP_TB_N={n}",
                 f"-Ptb_pbit_row_vectors.TOP_TB_MODE={mode}",
                 "-o",str(sim),str(source),str(bench)]
            subprocess.run(cmd,check=True,timeout=60)
            result=subprocess.run(["vvp",str(sim),f"+VECTORS={vec.resolve()}"],
                check=True,capture_output=True,text=True,timeout=60)
            print(result.stdout.strip(),flush=True)
            if f"M2 VECTORS PASS: mode={mode} N={n} cases={num_cases}" not in result.stdout:
                raise RuntimeError("simulator did not confirm vector pass")
            records.append(dict(n=n,mode=mode,cases=num_cases,
                       output=result.stdout.strip()))
    summary=dict(status="PASS",test_count=sum(x["cases"] for x in records),
                 formats=["fp4_j_fp6_h","int4_j_int6_h","bfp6"],
                 read_stalls=True,seed=args.seed,records=records,
                 evidence="bit-true RTL-vs-independent-Python-field arithmetic only; no MRAM or mapped synthesis",
                 source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (source,bench,Path(__file__))})
    (args.output/"m2_vector_results.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(f"M2 ALL 3 MODES x 3 SIZES PASS, {summary['test_count']} row vectors.")
    print(f"Result folder: {args.output}")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--seed",type=int,default=20261106)
    args=p.parse_args()
    if args.output.exists():
        p.error("output exists; use a fresh directory")
    run(args)


if __name__=="__main__":
    main()
