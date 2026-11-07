# M4 frozen architecture question — shared-gain folding versus explicit scale (7 Nov 2026)

## Research decision

Keep low-order **floating-point coupling storage** as the main FYP subject. No new device-noise experiments, beta retuning, broader solver sweep, or inference of GF22FDX area. M3 already verified one row x one spin state x 3 official Mac CAL graphs x FP6/INT6/BFP6 in clocked Icarus, and **Sky130 HD row-only mapped area** 1438.8800 / 929.6416 / 929.6416 µm² respectively. Those are not overall machine areas. Source M3: docs/M3_FP6_INT6_BFP6_ROW_RESULT_20261107.md.

**Key M4 distinction:** M1's exact ideal Gibbs conditional is P(s_i=+1)=sigmoid(2 * beta(t) * H_i). M3 outputs integer A_i; M1's represented H from the frozen global codebook is:

- FP6 finite E3M2: H = A * S_FP_f32 / 16, where A is the signed sum of decoded q4 integer coefficients.
- INT6 symmetric: H = A * S_INT_f32.
- GLOBAL BFP6 symmetric: H = A * 2**k, with a global signed 8-bit exponent.

**In exact arithmetic**, define G(t)=2 * beta(t) * S_effective and feed sigmoid(G(t)*A) directly. There is no **mathematical** need to materialize an IEEE-754 local-field FP product every attempted Gibbs update. The distinction matters: **do not charge FP/INT for a per-row multiplier without also evaluating scale folding for INT/BFP and a shared gain generator**. Conversely, do not call the gain generator/controller free: it has dynamic range, precision, scheduling, and interface costs not yet characterized. This is an *architecture option*, not a measured implementation or solution-quality benefit.

## Current M4 gate and stop rule

experiments/m4_gain_folding_audit.py reconstructs official M3 source-SHA-verified 99-term vectors. For each of the 3 formats and for **each 99 cumulative row prefixes** in each of the 3 CAL graphs, it tests the equality of direct represented-field logits 2*beta(t)*sum(q_j*s_j) and factored integer logits G(t)*sum(integer_q_j*s_j), with beta drawn from the original graph and the *frozen* linear anneal schedule. It also validates complete-vector SHA, frozen metadata width, final M3 integer accumulator, and represented local field. The audit reports numeric Python rounding differences, **not silicon numeric error**. No original-cut solution, solver rerun, p-bit device, finite DAC, or switched energy is modeled.

**STOP** any assertion of gain folding readiness if original-graph or M3-vector hashes fail, a row integer differs, or a logit diverges beyond stated Python floating-point tolerance. **PASS**, if achieved by CI, licenses *only mathematical scale/gain reparameterization of the M1 ideal update for one sample row per graph*; not hardware feasibility of a common gain in the STT-MTJ interface.

## Frozen cost-accounting table (counts, NOT mapped hardware)

The baseline architecture is a **single serial 99-term row calculation per attempted spin update**, with N=100, frozen 50,000 attempts per solver run, 6-bit payload, h=0, no diagonal. For all three formats, **99 coefficient issues/attempt** gives **4,950,000 slots/run**. Two clearly different memory organizations must remain separate:

| Memory organization | FP6 | INT6 | BFP6 |
|---|---:|---:|---:|
| One copy of 4,950 undirected 6-bit couplings + one global metadata word | 29,732 bits | 29,732 bits | 29,708 bits |
| Fully mirrored row-addressable 9,900 off-diagonal 6-bit entries + metadata | 59,432 bits | 59,432 bits | 59,408 bits |

These are **payload/storage-word counts**, not an SRAM macro's bit-cell area, mapping circuitry, or read energy. One-copy symmetric edge data needs indexing/addressing to serve any row; mirrored storage favors row-oriented access but doubles the payload. Compressed sparse storage would need actual address/metadata cost and a common skip policy. The serial 99-term row is a **specific naive full-recompute scheduler**; Gibbs incremental field updates can change traffic and must not be conflated with this design. A shared beta(t) generator is required for all formats; whether gain coefficients are precomputed, streamed or calculated changes cost.

## Next silicon-comparable experiment (not done yet)

1. **Freeze one common logit/p-bit interface precision, gain dynamic range, latency and scheduling strategy** for all formats. Explicitly distinguish *ideal real-arithmetic equivalence* from quantized gain / saturation effects.
2. Build an **end-to-end digital interface RTL boundary** with either (A) explicit-scale local field followed by global gain or (B) scale-fused gain. Account for registers, metadata loading, controller and coefficient-port organization. Synthesize the three formats and both architectures with the same pinned std-cell library, actual clock/IO constraints; report area, path delay, and architecture assumptions separately.
3. Only after cost and numeric interface integrity, match against frozen M1 original-cut quality; test independent held-out graphs. No FP superiority conclusion is yet justified.

The mathematical result can remove a **potentially unnecessary multiplier assumption**, but it cannot erase the **observed FP6 exponent/mantissa decode and 17-bit accumulator overhead** in the M3 serial row. Do not report unmeasured system area, DAC energy, number of p-bit units or time-to-solution.
