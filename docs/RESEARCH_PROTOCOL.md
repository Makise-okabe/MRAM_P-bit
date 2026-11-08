# Evidence protocol — joint precision × STT-MRAM p-bit response

**Current scope:** [locked roadmap, 8 November 2026](ROADMAP_LOCKED_2026-11-06.md). It controls experiment ordering and supersedes older benchmark-only or hardware-first execution notes.

## Evidence levels and physical interpretation

E0: exact theory/algebra. E1: seeded ideal algorithm simulation. E2: explicitly assumed response sensitivity. E3: sourced/validated device response with documented coverage. E4: authorized circuit simulation. E5: bit-true RTL or synthesis. Never promote a code/CI pass, nominal sigmoid, assumed variability distribution or CMOS area result into measured STT-MTJ evidence.

The present gain/offset levels are E2 assumptions. A published nominal curve establishes a response form, not a measured residual distribution. Digitised fits, pre-calibration spread, post-calibration residuals and manufacturing statistics are distinct. A conventional storage MTJ is not automatically a validated free-running p-bit model. Do not reproduce the unpublished manuscript's calibration contribution or publish restricted material.

## Numerical fairness

Use preserved original signed Biq Mac Mac weights. For E=-sum_(i<j)J_ij*s_i*s_j, use symmetric J=-w, diagonal zero and problem h=0; E=sum w-2 Cut_w. Physical response offset remains separate from problem h.

All representations share source-only scale rules, graph identities, frozen beta normalization/schedule, budgets and solver draws. Preserve metadata/rounding/saturation semantics. Runtime returns the earliest best REPRESENTED-energy state; original cut is scored externally. Any-visit success, final state and retained output are different metrics.

Device parameters persist during a run and are paired across formats/levels. Separate device and solver RNGs. Reuse ideal results only after matching semantics and pairing; do not repeat experiments for a new output layout.

## Quality and uncertainty

Report absolute original-optimum gap against the common target, paired additional gap relative to FP64 under the SAME response, and response degradation relative to the fixed ideal condition. Keep the roadmap's 5%/7.5% absolute regime thresholds and +1pp numerical-loss screen. Label intervals crossing category boundaries uncertain. A poor device-conditioned FP64 reference does not make poor low-bit quality acceptable.

Graph instances, device populations and solver seeds are different statistical levels. Seed CIs for a fixed graph and array are conditional, not graph-population or manufacturing/yield claims. With two held-out graphs report per-instance results and limits; do not pretend that 24 seeds create 24 independent graph instances. A CI crossing zero is not evidence of equivalence. Do not tune on held-out outcomes.

## Cost and claims

Coefficient payload/metadata counts, issue slots, mapped standard-cell area, physical memory area, timing and energy are different quantities. Existing Sky130 six-bit boundaries do not establish full-chip cost, GF22FDX integration, other-width area or energy-to-solution. Preserve hardware as one supporting cost table rather than reopening the toolchain.

FP at six bits has no automatic payload saving over INT6. A useful rule must connect a stated quality target to the actual cost information available. Stable thresholds, negative results and bounded uncertainty are valid outcomes; do not invent an advantage or first-ever claim.

## Decision feedback and records

For each scientific choice briefly identify relevance, evidence, closest prior art, minimum test, opportunity cost and stop condition; close the loop after results. Keep source IDs, original/represented coefficients, model/calibration assumptions, populations/seeds, budgets, output policy and minimal reusable numerical summaries. Preserve earlier results, including BFP controls, without adding a provenance/CI framework or a new document for every command.

Completed M0/M1 and M3/M4B evidence is preserved. A scope update is not a new solver/device run. New claims require actual outputs; the current gain pilot is not complete merely because a runner exists.
