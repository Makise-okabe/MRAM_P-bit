#!/usr/bin/env python3
"""M4B: frozen common digital logit interface, source-linked real-graph vectors.

Finite-precision contract (candidate, distinct from M1 ideal Gibbs):
- A is M3 signed exact integer row accumulator.
- Per attempted update, an EXTERNAL controller supplies gain_q28:
  signed positive 32-bit Q4.28 representation of G(t)=2*beta(t)*S_eff.
- logit output is signed 18-bit Q6.12, round-to-nearest-even in integer
  product and saturate to [-12,+12] in real logit units.
- sigmoid acts on this quantized logit. No p-bit device is characterized.
The gain source/schedule and RAM/memory power are NOT implemented in RTL.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph
from experiments.m3_sixbit_encoding import decode_raw_sixbit
from experiments.m4_gain_folding_audit import effective_scale, sigmoid

GAIN_FRAC = 28
LOGIT_FRAC = 12
LOGIT_LIMIT = 12 << LOGIT_FRAC
MAX_PROBABILITY_ERROR_GATE = 0.00025  # test-vector numerical screen, not solver tolerance
FAMILIES = ("fp", "int", "bfp")
STEPS = (("begin", 0), ("middle", 24999), ("end", 49999))


def encode_gain(gain: float) -> int:
    if not math.isfinite(gain) or not 0 < gain < 8:
        raise ValueError("gain is nonpositive/nonfinite or outside signed Q4.28 range")
    code = round(gain * (1 << GAIN_FRAC))  # Python ties to even
    if not 0 < code < (1 << 31):
        raise ValueError("Q4.28 gain underflow or overflow")
    return code


def round_divide_signed_even(n: int, shift: int) -> int:
    if shift < 0:
        raise ValueError("negative shift")
    mag = abs(n)
    q, rem = divmod(mag, 1 << shift)
    half = 1 << (shift - 1) if shift else 0
    if shift and (rem > half or (rem == half and (q & 1))):
        q += 1
    return q if n >= 0 else -q


def quantized_logit(acc: int, gain_code: int) -> int:
    if not -(1 << 16) <= acc < (1 << 16):
        raise ValueError("M3 17-bit integer row out of range")
    if not 0 < gain_code < (1 << 31):
        raise ValueError("invalid gain code")
    # integer acc * Q4.28 -> signed Q6.12, round-even of /2^16
    rounded = round_divide_signed_even(acc * gain_code, GAIN_FRAC - LOGIT_FRAC)
    return max(-LOGIT_LIMIT, min(LOGIT_LIMIT, rounded))


def beta_at(beta_g: float, step: int) -> float:
    if not 0 <= step < 50000:
        raise ValueError("step out of frozen 50,000 attempts")
    return beta_g * (0.5 + 1.5 * step / 49999)


def generate(graph_path: Path, m3_vectors_dir: Path, out: Path) -> dict:
    if out.exists():
        raise ValueError("refuse to overwrite generated M4B vectors")
    g = load_rudy(graph_path)
    m3_bytes = (m3_vectors_dir / "manifest.json").read_bytes()
    m3 = json.loads(m3_bytes)
    if not (g.n == 100 and m3["graph"] == graph_path.name
            and m3["graph_sha256"] == g.sha256
            and m3["reference_type"] == "PUBLISHED_OPTIMUM"):
        raise ValueError("graph identity or official M3 source hash mismatch")
    beta_g = beta_from_original_graph(g)
    out.mkdir(parents=True, exist_ok=False)
    manifest = dict(
        evidence="M4B candidate common digital interface; NOT M1 ideal solver, complete device, or silicon power",
        contract="signed Q4.28 gain; signed Q6.12 logit; RNE; saturate [-12,+12]",
        graph=g.sha256, graph_name=g.name if hasattr(g,"name") else graph_path.name,
        m3_manifest_sha256=hashlib.sha256(m3_bytes).hexdigest(),
        beta_g=beta_g, probability_error_gate=MAX_PROBABILITY_ERROR_GATE,
        rows={},
    )
    for fam in FAMILIES:
        m3row = m3["rows"][fam + "6"]
        path = m3_vectors_dir / m3row["vector_file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != m3row["vector_sha256"]:
            raise ValueError("M3 source-vector SHA mismatch")
        lines = path.read_text(encoding="ascii").splitlines()
        if len(lines) != 99:
            raise ValueError("missing 99 original graph coefficients")
        s = float(m3row["source_only_scale"])
        eff = effective_scale(fam, s)
        acc = 0
        prefixes = []
        for line in lines:
            raw_s, spin_s, expected_s = line.split()
            spin = int(spin_s)
            if spin not in (0, 1):
                raise ValueError("invalid spin")
            acc += decode_raw_sixbit(int(raw_s, 16), fam) * (1 if spin else -1)
            if acc != int(expected_s):
                raise AssertionError("original M3 prefix integer differs")
            prefixes.append(acc)
        if acc != int(m3row["signed_integer_accum"]):
            raise AssertionError("original M3 final integer differs")
        manifest["rows"][fam + "6"] = {}
        for label, step in STEPS:
            gain = 2 * beta_at(beta_g, step) * eff
            gain_code = encode_gain(gain)
            out_file = out / f"m4_{fam}6_{label}.txt"
            max_p_diff = 0.0
            max_z_diff = 0.0
            clipped_count = 0
            with out_file.open("x", encoding="ascii") as stream:
                final = quantized_logit(acc, gain_code)
                stream.write(f"{gain_code:08x} {final} {acc}\n")
                for a, line in zip(prefixes, lines):
                    ideal_z = 2 * beta_at(beta_g, step) * (a * eff)
                    fixed_z = quantized_logit(a, gain_code) / (1 << LOGIT_FRAC)
                    max_p_diff = max(max_p_diff, abs(sigmoid(ideal_z) - sigmoid(fixed_z)))
                    max_z_diff = max(max_z_diff, abs(ideal_z - fixed_z))
                    clipped_count += (abs(ideal_z) > 12)
                    stream.write(line + "\n")
            if max_p_diff > MAX_PROBABILITY_ERROR_GATE:
                raise AssertionError(f"{fam} {label} max probability error={max_p_diff} exceeds contract gate")
            manifest["rows"][fam + "6"][label] = dict(
                step=step, gain_true=gain, gain_q28=gain_code,
                final_integer=acc, final_logit_q12=final,
                max_abs_probability_difference=max_p_diff,
                max_abs_logit_difference_including_saturation=max_z_diff,
                n_prefixes=99, n_logit_saturation_prefixes=clipped_count,
                vector_file=out_file.name,
                vector_sha256=hashlib.sha256(out_file.read_bytes()).hexdigest(),
            )
    (out / "manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--graph",type=Path,required=True)
    ap.add_argument("--m3-vectors",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args = ap.parse_args()
    data = generate(args.graph,args.m3_vectors,args.out)
    prob = max(float(x["max_abs_probability_difference"])
               for family in data["rows"].values() for x in family.values())
    print(f"M4B NUMERICAL CONTRACT PASS {data['graph_name']} 3 formats x 3 beta points x 99 prefixes max_p_error={prob:.8g}")


if __name__ == "__main__":
    main()
