# M1: repair quantization attribution and test finite-only floating point

Scope remains low-order floating-point coupling and nonideal MRAM p-bits,
using BPSK MIMO as the application benchmark. INT and BFP are comparisons.

## What the reported exact-audit excerpt establishes

In the user-shared contrast090, 0 dB rows, the returned state reaches a
quantized minimum in all 12 frames for FP4, INT4 and BFP4. FP4 preserves the
original ML optimum in 10 frames and returns an original ML state in 10;
INT4 preserves and returns it in 11. BFP4 preserves it in 11 but returns
an original ML state in 9. A non-ML state can tie with an ML state at the
quantized minimum. That is different from failing to reach a quantized minimum.

The [latest committed NUS audit log](https://github.com/Makise-okabe/MRAM_P-bit/blob/4a0e3d8ab8145bcf16a67100415db08fa91a5055/docs/M1_FP_NONIDEAL_SCREEN.md)
also records quantized-minimum arrival in all 80 reported grouped rows, and
original ML preservation of 10/12 for FP4 at both SNRs. These are user-reported
results, not a local reproduction of the user's complete data. No new research
results are claimed in this change.

## Audit correction

Original-ML misses are now partitioned by the returned state:

1. Above the quantized minimum: a sampling miss, possibly alongside
   quantization bias.
2. At a quantized minimum with an original ML minimizer also present:
   a non-ML quantized tie.
3. At a quantized minimum with no original ML minimizer present:
   a changed quantized optimum.

An original-ML hit is reported separately, including when it is not a
quantized minimum. Structural preservation checks whether *any* original
ML minimizer survives, so degenerate original optima are handled correctly.

The ambiguous summary key
`failed_sampling_even_when_orig_ml_is_quant_min` is removed. Consumers should
use the three explicitly named `missed_original_ml_*` counters instead.
Existing input CSVs and legacy unrounded-fp32 reconstruction are supported.

## Concrete format candidate

Historical `fp4`, `fp6` and `fp8` names and their values/rounding are unchanged.
They reserve the all-ones exponent; historical FP4 has nonnegative levels
`[0, 0.5, 1, 1.5, 2, 3]` before scaling.

New labels:

| Label | Element layout | Nonnegative range | Rounding |
| --- | --- | --- | --- |
| `fp4_fn` | sign + E2M1, all exponent fields finite | 0 to 6; levels 0, 0.5, 1, 1.5, 2, 3, 4, 6 | nearest, ties to even encoding |
| `fp6_fn` | sign + E3M2, all exponent fields finite | 0 to 28; minimum positive 0.0625 | nearest, ties to even encoding |

These element value sets, rounding and saturation follow the FP4/FP6
definitions in the [OCP MX v1.0 specification, sections 5.3.2-5.3.3](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf).
This code does **not** implement a full MX block format. It retains the existing
optimistic instance-tuned global real scale for J and separate scale for h.
Scale metadata is counted nominally; scale quantization, accumulator arithmetic,
area and energy remain later implementation work.

The new FP4/FP6 candidates have the same nominal coefficient/metadata bit counts
as their historical counterparts. Additional finite levels do not guarantee
better original-objective performance after scale tuning. Test that hypothesis.
The standard element format itself is not the project's novelty.

## Next bounded experiment

1. Reuse the existing saved MIMO frames and seeds. Compare historical FP4,
   `fp4_fn`, FP6/`fp6_fn` and the existing optimized INT/BFP baselines.
   Evaluate original-ML preservation, non-ML ties and original residual gaps
   before interpreting sampler convergence. Never tune using the exact ML answer.
2. If needed, isolate quantization of J and h to locate which coefficients
   change the optimum. Mixed precision is a candidate only if total storage
   and runtime costs are counted for every baseline.
3. Under the same ideal and illustrative nonideal responses, measure quality
   at common update budgets and the first target-reaching update with all costs
   counted. `selected_at_update` is **not** first time-to-target.
4. Use a sourced, validated stochastic MTJ response before claiming a physical
   MRAM precision rule. A uniform gain of 0.8 is equivalent to rescaling beta
   in the current sigmoid model; it is not device-to-device gain variation.

Keep original H and y for external scoring. Do not use a hidden high-precision
rescoring step to select among quantized ties at runtime. If such a step is ever
studied, it is an explicit design with its own storage and arithmetic cost.

## Verification

`python3 -m unittest discover -s tests`

Tests cover ties versus sampling, changed optima, degenerate original ML,
historical reconstruction, standard finite element levels/midpoint rounding,
symmetry and nominal storage. Test fixtures are software correctness checks,
not experimental or physical MRAM evidence.
