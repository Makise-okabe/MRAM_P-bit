#!/usr/bin/env python3
"""M1 exploratory low-order floating-point coupling quantization.

Value-level mathematical encoding only; not RTL/bit-true arithmetic, device
physics, physical area or complete optimized scale-architecture results.
"""
import bisect
import math
from collections import defaultdict

FP_FORMATS = {"fp4": (2, 1), "fp6": (3, 2), "fp8": (4, 3)}
INT_FORMATS = {"int4": 4, "int6": 6, "int8": 8}
BFP_FORMATS = {"bfp4": 4, "bfp6": 6, "bfp8": 8}
FORMATS = ("fp32", "fp4", "fp6", "fp8",
           "int4", "int6", "int8", "bfp4", "bfp6", "bfp8")


def fp_positive_levels(exponent_bits, mantissa_bits):
    """Finite E(e)M(m) format: exp field all ones reserved, no Inf/NaN used.

    exp=0: signed zero and subnormal fractions; exp=1..2**e-2 normal;
    bias=2**(e-1)-1. Overflow saturates at largest finite number.
    At this stage signed negative zero is decoded as zero (not stored as code).
    """
    if exponent_bits < 2 or mantissa_bits < 1:
        raise ValueError("need e>=2,m>=1")
    bias = (1 << (exponent_bits - 1)) - 1
    levels = [0.0]
    for frac in range(1, 1 << mantissa_bits):
        levels.append((frac / (1 << mantissa_bits)) * 2.0**(1-bias))
    for exponent in range(1, (1 << exponent_bits) - 1):
        for frac in range(1 << mantissa_bits):
            levels.append((1 + frac/(1 << mantissa_bits)) * 2.0**(exponent-bias))
    return sorted(set(levels))


def quantized_level(x, scale, kind):
    """Symmetric round-to-nearest/ties-to-smaller magnitude; saturating."""
    if not math.isfinite(x) or not math.isfinite(scale) or scale <= 0:
        raise ValueError("need finite coefficient and positive scale")
    if kind.startswith("fp"):
        positive = fp_positive_levels(*FP_FORMATS[kind])
        a = abs(x)/scale
        j = bisect.bisect_left(positive, a)
        if j == len(positive):
            q = positive[-1]
        elif j == 0:
            q = positive[0]
        else:
            lo, hi = positive[j-1], positive[j]
            q = lo if a-lo <= hi-a else hi
        return math.copysign(q * scale, x) if q else 0.0
    bits = INT_FORMATS.get(kind, BFP_FORMATS.get(kind))
    if bits is None:
        raise ValueError("unknown format")
    qmax = (1 << (bits-1)) - 1
    # all formats use symmetric range [-qmax,qmax]; minimum negative code unused
    a = abs(x)/scale
    q = min(qmax, int(math.floor(a + 0.5)))
    return math.copysign(q*scale, x) if q else 0.0


def tune_scale(values, kind):
    """Instance-local optimistic coefficient MSE scale tuning.

    This is an upper-bound diagnostic, not a calibrated deployable rule.
    Each represented scale and tuning overhead must be accounted for later.
    """
    if not values or not all(math.isfinite(x) for x in values):
        raise ValueError("nonempty finite group required")
    if kind == "fp32":
        return 1.0, list(values)
    vmax = max(abs(v) for v in values)
    if vmax == 0:
        return 1.0, [0.0]*len(values)
    if kind.startswith("fp"):
        upper = fp_positive_levels(*FP_FORMATS[kind])[-1]
    else:
        bits = INT_FORMATS.get(kind, BFP_FORMATS.get(kind))
        if bits is None:
            raise ValueError("unsupported format")
        upper = (1 << (bits-1)) - 1
    nominal = vmax/upper
    # Float + fixed INT use arbitrary real scales; BFP uses powers of two.
    if kind.startswith("bfp"):
        k0 = math.floor(math.log2(nominal))
        candidates = [2.0**k for k in range(k0-5,k0+6)]
    else:
        candidates = [nominal * 2.0**(k/4) for k in range(-12,9)]
    best = None
    for scale in candidates:
        if scale <= 0 or not math.isfinite(scale):
            continue
        q = [quantized_level(v,scale,kind) for v in values]
        mse = sum((v-r)**2 for v,r in zip(values,q))
        if best is None or mse < best[0]-1e-15:
            best = (mse,scale,q)
    if best is None:
        raise ValueError("no valid scale candidate")
    return best[1],best[2]


def quantize_couplings(J,h,kind,tile=4):
    """Symmetry-safe J quantization with groups of undirected edges.

    Global group for fp/int, symmetric tile-pair groups for BFP. h always
    uses its own group. A future architecture will compare tile FP/INT too.
    """
    if kind not in FORMATS:
        raise ValueError("unknown format")
    if not isinstance(tile,int) or tile < 1:
        raise ValueError("invalid tile")
    n=len(h)
    if len(J)!=n or n<2 or any(len(row)!=n for row in J):
        raise ValueError("invalid matrix dimensions")
    if not all(math.isfinite(v) for v in h):
        raise ValueError("nonfinite h")
    for i in range(n):
        if abs(J[i][i])>1e-12:
            raise ValueError("diagonal must be zero")
        for j in range(i+1,n):
            if not math.isfinite(J[i][j]) or abs(J[i][j]-J[j][i])>1e-12:
                raise ValueError("nonfinite or asymmetric J")
    if kind=="fp32":
        return dict(J=[row[:] for row in J],h=h[:],format=kind,
                    scales={"J":[1.0],"h":[1.0]},coefficient_bits=32*(n*(n-1)//2+n),
                    metadata_bits=0,mse_J=0.0,mse_h=0.0)
    groups=defaultdict(list)
    for i in range(n):
        for j in range(i+1,n):
            key=(i//tile,j//tile) if kind.startswith("bfp") else ("global",)
            groups[key].append((i,j,J[i][j]))
    qJ=[[0.0]*n for _ in range(n)]
    group_scales=[]
    for key in sorted(groups,key=str):
        elements=groups[key]
        scale,q=tune_scale([v for _,_,v in elements],kind)
        group_scales.append({"group":list(key),"scale":scale})
        for (i,j,_),value in zip(elements,q):
            qJ[i][j]=qJ[j][i]=value
    h_scale,qh=tune_scale(h,kind)
    bits=int(kind[-1]) if kind != "fp32" else 32
    # 32-bit real scales for FP/INT per J group, plus h.
    # BFP scale is assumed a signed 8-bit exponent for PoT scale; bounds
    # and encoding must be validated in later macro work.
    scale_bits=8 if kind.startswith("bfp") else 32
    metadata_bits=scale_bits*(len(groups)+1)
    jmse=sum((J[i][j]-qJ[i][j])**2 for i in range(n) for j in range(i+1,n))
    hmse=sum((a-b)**2 for a,b in zip(h,qh))
    return dict(J=qJ,h=qh,format=kind,
                scales={"J":group_scales,"h":[h_scale]},
                coefficient_bits=bits*(n*(n-1)//2+n),
                metadata_bits=metadata_bits,
                mse_J=jmse,mse_h=hmse)
