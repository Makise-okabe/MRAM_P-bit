#!/usr/bin/env python3
"""Frozen GLOBAL 4/5/6/8-bit scalar coupling formats for Biq Mac E1.

Software element codebooks and symmetric-source-only scale fitting.
Not bit-true accumulator, STT-MTJ voltage response, full hardware macro,
or globally optimum scale search.

All FP layouts are *custom finite-only* eXmY; exp=0 subnormals, all
exponent patterns including all-ones are FINITE normal values. No Inf/NaN.
Sign bit; signed zero decodes zero. Nearest-even ties in encoded level index.
INT/BFP signed symmetric magnitudes [-qmax,qmax], min-negative code unused;
nearest integer ties-to-even. INT/FP use a ONE-copy binary32 global scale;
BFP uses an ONE-copy signed 8-bit power-of-two exponent. One undirected
edge is encoded ONCE then mirrored, so J_ij == J_ji exactly.
"""
from __future__ import annotations

import math
import struct
from functools import lru_cache

from experiments.m1_coupling_formats import fp_positive_levels

WIDTHS = (4, 5, 6, 8)
FP_LAYOUTS = {4:(2,1), 5:(2,2), 6:(3,2), 8:(4,3)}
FAMILIES = ("fp", "int", "bfp")
SCALE_POLICY = "source_mse_loggrid_v1"
GLOBAL_ONLY = True


def cast_binary32(x: float) -> float:
    """Finite positive 32-bit metadata; candidate invalidity is explicit."""
    if not math.isfinite(x) or x <= 0:
        raise ValueError("scale must be finite positive")
    try:
        q = struct.unpack(">f", struct.pack(">f", float(x)))[0]
    except (OverflowError, struct.error) as exc:
        raise ValueError("scale cannot be encoded in binary32") from exc
    if not math.isfinite(q) or q <= 0:
        raise ValueError("binary32 scale overflow/underflow")
    return q


@lru_cache(maxsize=None)
def levels(width: int) -> tuple[float, ...]:
    if width not in WIDTHS:
        raise ValueError(f"unsupported FP width {width}")
    e, m = FP_LAYOUTS[width]
    # The old module's finite-only representation is explicitly frozen here.
    return tuple(fp_positive_levels(e, m, finite_only=True))


def scalar_quantize(value: float, family: str, width: int, scale: float) -> float:
    if family not in FAMILIES or width not in WIDTHS:
        raise ValueError("unknown family or width")
    if not math.isfinite(value) or not math.isfinite(scale) or scale <= 0:
        raise ValueError("nonfinite coefficient or invalid scale")
    magnitude = abs(value) / scale
    if family == "fp":
        # Ordered nonnegative finite FP codebook. Nearest with even code on
        # exact ties, covering both signed subnormals and saturated max.
        import bisect
        codebook = levels(width)
        k = bisect.bisect_left(codebook, magnitude)
        if k == 0:
            selected = codebook[0]
        elif k >= len(codebook):
            selected = codebook[-1]
        else:
            lo, hi = codebook[k-1], codebook[k]
            dl, dh = magnitude-lo, hi-magnitude
            if dl < dh:
                selected = lo
            elif dh < dl:
                selected = hi
            else:
                selected = lo if (k-1) % 2 == 0 else hi
        number = selected * scale
    else:
        qmax = (1 << (width-1)) - 1
        # Python round uses ties-to-even for real numbers.
        number = min(qmax, round(magnitude)) * scale
    return math.copysign(number, value) if number else 0.0


def fullscale(values: tuple[float, ...] | list[float], family: str, width: int) -> float:
    if not values or not all(math.isfinite(x) for x in values):
        raise ValueError("expected finite source coefficients")
    vmax = max(map(abs, values))
    if not vmax:
        return 1.0
    upper = levels(width)[-1] if family == "fp" else (1 << (width-1)) - 1
    nominal = vmax / upper
    if family == "bfp":
        k = math.ceil(math.log2(nominal))
        if not -128 <= k <= 127:
            raise ValueError("BFP exponent out of 8-bit metadata bounds")
        return math.ldexp(1.0, k)
    # ceil in binary32 to make sure true fullscale does not saturate.
    s = cast_binary32(nominal)
    if s < nominal:
        try:
            s = cast_binary32(math.nextafter(s, math.inf))
        except ValueError:
            # math.nextafter advances a binary64 step and often re-rounds to
            # same f32; use exact binary32 next representable by integer bits.
            pass
    if s < nominal:
        raw = struct.unpack(">I", struct.pack(">f", s))[0]
        if raw >= 0x7F7FFFFF:
            raise ValueError("32-bit positive scale overflow")
        s = struct.unpack(">f", struct.pack(">I", raw+1))[0]
    return s


def candidate_scales(values: tuple[float, ...] | list[float], family: str, width: int) -> list[float]:
    vmax = max(abs(x) for x in values)
    if vmax == 0:
        return [1.0]
    base = fullscale(values, family, width)
    options = set()
    if family == "bfp":
        k0 = int(round(math.log2(base)))
        for k in range(max(-128, k0-12), min(127, k0+8) + 1):
            options.add(math.ldexp(1.0,k))
    else:
        # A predeclared coefficient-only log grid, not a solver-quality grid:
        # symmetric factor [2^-3,2^2] about no-saturation fullscale.
        for k in range(-48, 33):
            s = base * (2.0 ** (k / 16.0))
            try:
                options.add(cast_binary32(s))
            except ValueError:
                pass
        options.add(base)
    if family == "int":
        qmax=(1 << (width-1))-1
        if vmax <= qmax and all(v == round(v) for v in values):
            options.add(1.0)  # fair EXACT small-integer candidate, EVERY INT width
    if not options:
        raise ValueError("no representable scale candidates")
    return sorted(options)


def fit_global_scale(values: tuple[float, ...] | list[float], family: str, width: int) -> tuple[float, float]:
    """One global source-weight-only coefficient MSE rule for all widths.

    Proactively tie-break candidate MSE ties with lower total absolute
    coefficient error then smaller scale; no Max-Cut objective/optimum
    is consulted. Source graph includes no implicit zero edges.
    """
    if family not in FAMILIES or width not in WIDTHS:
        raise ValueError("invalid format")
    if not values or not all(math.isfinite(v) for v in values):
        raise ValueError("empty/nonfinite source")
    options = candidate_scales(values, family, width)
    best = None
    for scale in options:
        mse = 0.0
        l1 = 0.0
        for v in values:
            d = v - scalar_quantize(v, family, width, scale)
            mse += d*d
            l1 += abs(d)
        key = (mse, l1, scale)
        if best is None or key < best:
            best = key
    return best[2], best[0] / len(values)


def describe_codebook(family: str, width: int) -> dict:
    if family not in FAMILIES or width not in WIDTHS:
        raise ValueError("invalid format")
    data = {
        "family": family, "width": width,
        "rounding": "nearest-even", "saturation": "clamp to representable finite maximum",
        "scale_policy": SCALE_POLICY, "scale_granularity": "one global source-graph coupling scale",
        "one_quantized_edge_shared_both_directions": True,
    }
    if family == "fp":
        e,m = FP_LAYOUTS[width]
        positive = levels(width)
        data.update(layout=f"E{e}M{m}", finite_only=True,
                    subnormals=True, exponential_all_ones_is_finite=True,
                    positive_min_nonzero=positive[1],
                    positive_max=positive[-1],
                    signed_zero_unused=True,
                    scale_metadata="one IEEE binary32 real value (32 bits)",
                    scale_bits=32)
    else:
        qmax=(1 << (width-1))-1
        data.update(layout=f"symmetric signed {width}-bit mantissa",
                    min_code_unused=-(1 << (width-1)),
                    min_represented=-qmax,max_represented=qmax,
                    scale_metadata=("one 8-bit signed base-two exponent"
                        if family=="bfp" else "one IEEE binary32 real value (32 bits)"),
                    scale_bits=8 if family=="bfp" else 32)
    return data


def build_global(graph, family: str, width: int) -> dict:
    """Single signed edge J_ij=-w_ij encoded and mirrored exactly once."""
    if graph.n < 2:
        raise ValueError("requires at least two vertices")
    if any(i==j for i,j,_ in graph.edges):
        raise ValueError("nonzero self-loop")
    values = [-float(w) for _,_,w in graph.edges]
    scale, mse = fit_global_scale(values, family, width)
    adj = [[] for _ in range(graph.n)]
    edges = []
    zeroed = 0
    zeroed_abs_mass = 0.0
    source_abs_mass = sum(map(abs, values))
    absolute_error = 0.0
    for (i,j,_),v in zip(graph.edges,values):
        q=scalar_quantize(v,family,width,scale)
        if not (0<=i<j<graph.n):
            raise ValueError("noncanonical source edge")
        if v and not q:
            zeroed += 1
            zeroed_abs_mass += abs(v)
        absolute_error += abs(v-q)
        edges.append((i,j,q))
        adj[i].append((j,q))
        adj[j].append((i,q))
    # Architectural LOWER-BOUND storage proxy: one unique undirected
    # coefficient per possible pair + one scale; no SRAM/routing/ports.
    bits_per_edge=width
    stored_edges=graph.n*(graph.n-1)//2
    meta=describe_codebook(family,width)["scale_bits"]
    return {
       "adjacency":adj,"edges":edges,"scale":scale,
       "codebook":describe_codebook(family,width),
       "zeroed_edges":zeroed,
       "original_nonzero_edges":len(graph.edges),
       "zeroed_abs_weight_fraction":zeroed_abs_mass/source_abs_mass if source_abs_mass else 0.0,
       "relative_abs_coefficient_error":absolute_error/source_abs_mass if source_abs_mass else 0.0,
       "coefficient_mse":mse,
       "scale_metadata_bits":meta,
       "nominal_one_copy_dense_coefficient_bits":stored_edges*bits_per_edge,
       "nominal_one_copy_dense_total_bits":stored_edges*bits_per_edge+meta
    }
