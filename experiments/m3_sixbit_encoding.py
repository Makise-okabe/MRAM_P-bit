#!/usr/bin/env python3
"""M3 exact six-bit coefficient encoding for the frozen M1 global codebooks.

FP6 finite E3M2 is a VALUE codebook; all exponent patterns are finite.
Storage bits encode one coefficient ONCE, mirrored for symmetric J.
Values are decoded to a small integer then multiplied by the global
source-only scale outside the local-field row. This is a digital row
reference, not a device/DAC or full-precision multiplier implementation.

FP6: represented coupling = (signed integer q4) * f32_scale / 16.
INT6: represented coupling = signed integer * f32_scale.
BFP6: represented coupling = signed integer * 2**shared_exponent.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from experiments.m1_precision_codebooks import levels, scalar_quantize

FP6_POSITIVE_Q4 = tuple(int(round(16 * x)) for x in levels(6))
assert len(FP6_POSITIVE_Q4) == 32
assert all(abs(FP6_POSITIVE_Q4[i]/16-levels(6)[i]) < 1e-12 for i in range(32))
assert FP6_POSITIVE_Q4[-1] == 448


def decode_raw_sixbit(code: int, family: str) -> int:
    """Return integer mantissa or FP6 Q4-mantissa integer, not physical J."""
    if not 0 <= code < 64 or family not in ("fp","int","bfp"):
        raise ValueError("expected six-bit raw code and fp/int/bfp")
    if family == "fp":
        # exponent + mantissa bits are simply ordered positive level indices
        index = code & 31
        q4 = FP6_POSITIVE_Q4[index]
        return -q4 if (code & 32) else q4
    q = code if code < 32 else code-64
    if q == -32:  # frozen symmetric INT/BFP exclude the 0b100000 code
        raise ValueError("reserved -32 is invalid for symmetric INT6/BFP6")
    return q


def encode_quantized_sixbit(q: float, scale: float, family: str) -> int:
    """Encode a coefficient ALREADY quantized under frozen M1 source-MSE scale.

    Reject silent scale/codebook mismatches. The M1 Python double product
    can round slightly, so a tight relative tolerance is used.
    """
    if family not in ("fp","int","bfp") or not all(math.isfinite(z) for z in (q,scale)) or scale <= 0:
        raise ValueError("invalid codebook/scale/coefficient")
    if q == 0:
        return 0
    norm = q / scale
    if family == "fp":
        pos = abs(norm)*16
        idx = min(range(32),key=lambda i:(abs(pos-FP6_POSITIVE_Q4[i]),i))
        raw = idx | (32 if q < 0 else 0)
    else:
        integer = round(norm)
        if integer < -31 or integer > 31:
            raise ValueError("out of range INT6/BFP6")
        raw = integer & 63
    reconstructed = decode_raw_sixbit(raw,family) * scale / (16 if family=="fp" else 1)
    if not math.isclose(reconstructed,q,rel_tol=2e-12,abs_tol=1e-12):
        raise ValueError("coefficient is NOT in frozen six-bit codebook at supplied global scale")
    return raw


def row_accumulator_codes(codes, spin_positive, family: str) -> int:
    if len(codes) != len(spin_positive):
        raise ValueError("mismatched row dimensions")
    if len(codes) == 0:
        raise ValueError("empty test row")
    return sum(decode_raw_sixbit(c,family) * (1 if s else -1)
               for c,s in zip(codes,spin_positive))


def row_coupling_value(raw_accum: int, family: str, scale: float) -> float:
    if family not in ("fp","int","bfp") or not math.isfinite(scale) or scale <= 0:
        raise ValueError("invalid row scaling")
    return raw_accum * scale / (16 if family=="fp" else 1)


def make_vectors(directory: Path, count: int=99, seed: int=20261107) -> dict:
    """One reproducible off-diagonal 100-spin row in each format.

    File record: raw coefficient hex, spin_positive (0/1), cumulative
    integer accumulator, each value evaluated by pure Python oracle.
    RTL tests deliberately exclude shared-scale application: it is
    outside this row's stated hardware scope.
    """
    if count < 64 or count > 127:
        raise ValueError("test 64..127 terms; synthesized row MAX_TERMS=99")
    if not directory.exists():
        directory.mkdir(parents=True)
    rng = random.Random(seed)
    out = {}
    for family in ("fp","int","bfp"):
        code_stream = (
            list(range(64)) + [rng.randrange(64) for _ in range(count-64)]
            if family == "fp" else
            [(i % 63)-31 for i in range(count)]
        )
        raw_codes = code_stream if family == "fp" else [x & 63 for x in code_stream]
        spins = [bool(rng.randrange(2)) for _ in range(count)]
        acc = 0
        path = directory / (f"m3_{family}6_vectors.txt")
        with path.open("w",encoding="ascii") as f:
            for raw, s in zip(raw_codes, spins):
                acc += decode_raw_sixbit(raw,family)*(1 if s else -1)
                f.write(f"{raw:02x} {int(s)} {acc}\n")
        out[family] = str(path)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    result=make_vectors(args.out)
    for family,path in result.items():
        print(f"{family}6: {path}")
