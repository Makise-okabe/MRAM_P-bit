#!/usr/bin/env python3
"""M4: exact global-scale/gain folding audit of frozen M1 and M3 row vectors.

This is a mathematical integration test, NOT a synthesized controller, finite
precision gain/DAC design, a Gibbs rerun, an MTJ noise or power measurement.
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

FAMILIES = ("fp", "int", "bfp")
FROZEN_ATTEMPTS = 50_000
FROZEN_N = 100


def effective_scale(family: str, source_scale: float) -> float:
    """Convert exact M3 integer row output into M1 represented local field."""
    if family not in FAMILIES or not math.isfinite(source_scale) or source_scale <= 0:
        raise ValueError("invalid family or global scale")
    if family == "bfp":
        # BFP's source_scale must be an exact power of two in the M1 codebook.
        mantissa, exponent = math.frexp(source_scale)
        if mantissa != 0.5 or not -128 <= exponent - 1 <= 127:
            raise ValueError("BFP scale is not an 8-bit signed power of two")
    return source_scale / (16 if family == "fp" else 1)


def folded_gain(family: str, source_scale: float, beta_t: float) -> float:
    """gain * accumulator = frozen ideal Gibbs logit 2*beta(t)*H.

    This factorization is exact as real algebra; Python floating products may
    differ by rounding order from the frozen M1 implementation.
    """
    if not math.isfinite(beta_t) or beta_t <= 0:
        raise ValueError("beta must be positive finite")
    return 2 * beta_t * effective_scale(family, source_scale)


def sigmoid(x: float) -> float:
    """Numerically stable mathematical sigmoid, no device approximation."""
    if x >= 0:
        return 1 / (1 + math.exp(-x))
    z = math.exp(x)
    return z / (1 + z)


def memory_budget(n: int = FROZEN_N, attempts: int = FROZEN_ATTEMPTS) -> dict:
    """Architectural counts ONLY for naive serial 99-term row recomputation."""
    if n != FROZEN_N or attempts != FROZEN_ATTEMPTS:
        raise ValueError("M4 budget frozen to M1 100 spins and 50,000 attempts")
    undirected_edges = n * (n - 1) // 2
    directed_non_diagonal = n * (n - 1)
    payload_bits = 6
    return {
        "status": "ARCHITECTURAL_COUNT_NOT_HARDWARE_MEASUREMENT",
        "n": n, "attempted_updates": attempts,
        "issue_slots_per_attempt": n - 1,
        "coefficient_issue_slots_for_frozen_attempts": (n - 1) * attempts,
        "dense_unique_undirected_entries": undirected_edges,
        "dense_mirrored_directed_entries": directed_non_diagonal,
        "formats": {
            fam: {
                "coefficient_payload_bits_per_entry": payload_bits,
                "shared_scale_metadata_bits": 8 if fam == "bfp" else 32,
                "one_copy_triangular_payload_bits": undirected_edges * payload_bits,
                "one_copy_plus_metadata_bits": undirected_edges * payload_bits + (8 if fam == "bfp" else 32),
                "mirrored_row_addressable_payload_bits": directed_non_diagonal * payload_bits,
                "mirrored_plus_metadata_bits": directed_non_diagonal * payload_bits + (8 if fam == "bfp" else 32),
            }
            for fam in FAMILIES
        },
        "not_included": (
            "SRAM cell/macros and ports, triangular indexing, zero-skip metadata, "
            "dynamic read energy, flip/update traffic, beta/gain delivery, "
            "p-bit/DAC interface, state/controller, best-state retention, "
            "timing/placement/routing, full-system energy"
        ),
        "architecture_assumption": "naive one serial full 99-term row read for every Gibbs attempt",
    }


def audit_official_row(graph_path: Path, vectors_dir: Path) -> dict:
    """Audit all 99 prefix logits using official M3 source-hashed vectors.

    Existing M3 separately checks Jhat from frozen M1 against the row. This
    gate tests that folding source scale into beta(t) does not change the
    Gibbs logit in ideal exact arithmetic for this one row and spin state.
    """
    manifest_path = vectors_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    g = load_rudy(graph_path)
    if g.n != FROZEN_N or manifest.get("graph") != graph_path.name:
        raise ValueError("graph name/dimension mismatch")
    if manifest.get("graph_sha256") != g.sha256:
        raise ValueError("official graph SHA256 mismatch")
    if manifest.get("reference_type") != "PUBLISHED_OPTIMUM":
        raise ValueError("not an M3 official-optimum checked manifest")
    if manifest.get("n_spins") != FROZEN_N:
        raise ValueError("invalid M3 row scope")
    beta_g = beta_from_original_graph(g)
    if not math.isfinite(beta_g) or beta_g <= 0:
        raise ValueError("invalid graph beta")
    rows = {}
    for family in FAMILIES:
        key = family + "6"
        info = manifest["rows"][key]
        source_scale = float(info["source_only_scale"])
        scale = effective_scale(family, source_scale)
        if int(info["scale_metadata_bits"]) != (8 if family == "bfp" else 32):
            raise ValueError("scale metadata width differs from M1 freeze")
        vec_path = vectors_dir / info["vector_file"]
        if hashlib.sha256(vec_path.read_bytes()).hexdigest() != info["vector_sha256"]:
            raise ValueError("vector SHA256 mismatch")
        lines = vec_path.read_text(encoding="ascii").splitlines()
        if len(lines) != FROZEN_N - 1:
            raise ValueError("expected exactly 99 terms")
        acc = 0
        decoded = []
        max_absolute_logit_difference = 0.0
        max_absolute_probability_difference = 0.0
        for step, line in enumerate(lines, 1):
            fields = line.split()
            if len(fields) != 3:
                raise ValueError(f"malformed M3 vector step {step}")
            raw = int(fields[0], 16)
            spin = int(fields[1])
            if spin not in (0, 1):
                raise ValueError("spin must be 0 or 1")
            acc += decode_raw_sixbit(raw, family) * (1 if spin else -1)
            if int(fields[2]) != acc:
                raise ValueError(f"M3 accumulator mismatch step {step}")
            decoded.append(decode_raw_sixbit(raw, family) * (1 if spin else -1))
            # Test frozen schedule at 99 sample times; NOT a solver replay.
            attempted_step = (step - 1) * (FROZEN_ATTEMPTS - 1) // (FROZEN_N - 2)
            beta_t = beta_g * (0.5 + 1.5 * attempted_step / (FROZEN_ATTEMPTS - 1))
            direct_h = math.fsum(x * scale for x in decoded)
            direct_logit = 2 * beta_t * direct_h
            factor_logit = folded_gain(family, source_scale, beta_t) * acc
            discrepancy = abs(direct_logit - factor_logit)
            if not math.isclose(direct_logit, factor_logit, rel_tol=2e-12, abs_tol=1e-9):
                raise AssertionError(f"folded-logit mismatch {key} prefix {step}: {discrepancy}")
            max_absolute_logit_difference = max(max_absolute_logit_difference, discrepancy)
            max_absolute_probability_difference = max(
                max_absolute_probability_difference,
                abs(sigmoid(direct_logit) - sigmoid(factor_logit)))
        if acc != int(info["signed_integer_accum"]):
            raise ValueError("M3 final accumulator mismatch")
        final_h = acc * scale
        if not math.isclose(final_h, float(info["represented_J_local_field_from_M1"]),
                            rel_tol=2e-11, abs_tol=1e-7):
            raise AssertionError("M1 represented local field differs from final M3 integer row")
        rows[key] = {
            "source_only_scale": source_scale,
            "effective_scale": scale,
            "graph_beta_g": beta_g,
            "n_99_term_prefixes_audited": len(lines),
            "final_integer_accumulator": acc,
            "final_ideal_represented_local_field": final_h,
            "max_absolute_logit_difference_python_rounding": max_absolute_logit_difference,
            "max_absolute_ideal_probability_difference_python_rounding": max_absolute_probability_difference,
        }
    return {
        "status": "M4_MATHEMATICAL_GAIN_FOLDING_AUDIT_PASS",
        "scope": "ONE row / ONE state per official graph; 99 prefixes x 3 formats; no solver rerun",
        "graph": graph_path.name,
        "graph_sha256": g.sha256,
        "source_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "rows": rows,
        "memory_budget": memory_budget(),
        "not_demonstrated": "finite precision gain, input dynamic range, DAC/logit hardware, SRAM energy, full p-bit system, physical timing or ASIC area",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--vectors-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError("refuse to overwrite an existing M4 report")
    result = audit_official_row(args.graph, args.vectors_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"M4 GAIN-FOLDING PASS {result['graph']} 3 x 99 prefix logits; {args.out}")


if __name__ == "__main__":
    main()
