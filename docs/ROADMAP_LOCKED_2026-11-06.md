# Locked FYP roadmap — coupling precision × STT-MRAM p-bit nonidealities

**Locked by user instruction on 8 November 2026.** This is the authoritative current research scope on both main and the active research branch. It supersedes older execution instructions that prioritize further RTL/toolchain expansion, park device response indefinitely, or expand the benchmark/format/solver search. Completed evidence remains valid within its original scope.

## One research question

**Which low-order coupling representation preserves useful weighted-Max-Cut solution quality under specified STT-MRAM p-bit switching nonidealities, and is its implementation cost worthwhile?**

The original proposal's structure is retained: precision × hardware nonidealities → acceptable/degraded/failure regimes → design guidance. The computing platform is now STT-MRAM p-bit Ising computing. FP coupling is the design focus; device nonideality is a core physical condition, and existing RTL is supporting cost evidence.

Candidate originality is an evidenced conditional precision-selection rule. Do not claim that numerical precision, p-bit variability, calibration, or their broad combination is unexplored. Neither an FP win nor a format-ranking reversal is required.

## Locked scope

| Axis / component | Core | Outside this campaign |
|---|---|---|
| Coupling representation | Existing FP and INT codebooks at 4/5/6 bits, FP64 reference; existing 8-bit variants under the rule below | New codebooks, exponent/mantissa searches, logarithmic formats |
| Shared-exponent control | Preserve all existing BFP results; optional BFP6 supporting control, with scope declared before runs | New BFP group-size searches, independently rounded asymmetric rows |
| Device response | Gain and offset, each at ideal + three predeclared stress levels, studied in SEPARATE slices | Gain × offset cross-product, contrast, branch asymmetry, temporal correlation |
| Graphs | Two CAL and two untouched held-out 100-spin original Biq Mac Mac instances | Larger suites, other applications, 10^4-spin scale-up |
| Solver | Frozen 50,000 attempted updates, original-graph beta normalization, linear 0.5→2.0 schedule, 24 paired trials per cell | New solvers, temperature/schedule tuning, outcome-based scales |
| Cost | Existing matched six-bit RTL/Sky130 results plus explicitly labelled storage/access counts | Genus repair, new RTL/processor, analog interface or ADC design, new power claims |

The format pool remains the already implemented 4/5/6/8-bit FP/INT/BFP definitions. The primary campaign starts with seven configurations: FP64 + FP4/5/6 + INT4/5/6. If either six-bit format does not clearly meet the common absolute-quality and +1pp numerical-loss screens at a cell, evaluate BOTH FP8 and INT8 there. Mark cells not run as unmeasured. This predeclared extension is not permission to search additional formats. The existing all-width BFP pilot is retained; optional status must never be used to hide an unfavorable BFP result or claim comparison against an untested best BFP architecture.

## Graphs and pairing

| Role | Original instance | Seed placement |
|---|---|---|
| CAL, wide dense | ising2.5-100_5555 | Preserve M1 graph index 2 |
| CAL, wide sparse | t2g10_5555 | Preserve M1 graph index 1 |
| Held-out, wide dense | ising2.5-100_7777 | New fixed graph index 4 |
| Held-out, wide sparse | t2g10_7777 | New fixed graph index 3 |

Use the existing M1 solver seed rule, base 20261201 + 100000 × graph_index + k, k=0..23. Never reclassify the already inspected 5555 instances as held-out. Existing w01 integer-control evidence is preserved, but no new large integer-control campaign is required. Source hashes and official reference conventions must be verified by existing utilities before scoring the new files.

All future decisions use CAL only. Models, scales, formats and thresholds are fixed before evaluating held-out instances. Two held-out instances validate only this bounded test set, not universal graph-population behavior.

## Device model and calibration assumptions

Use the already implemented behavioral form:
P_i(+1) = sigmoid(alpha_i × 2 beta(t) H_i_quantized + delta_i).

Gain alpha is dimensionless. Offset delta is in LOGIT units, not volts. Parameters persist for each device/spin throughout a run. The same normalized device population is paired across formats, levels and solver trials, using a separate device RNG. State how many device populations are used; seed confidence intervals for one fixed array do not establish manufacturing/yield robustness.

The full planned E2 slices are:
- Gain-only: alpha_i = 1 + a u_i, delta_i = 0; a = 0, 0.025, 0.05, 0.10.
- Offset-only: alpha_i = 1, delta_i = d v_i; d = 0, 0.05, 0.10, 0.20.
- u_i and v_i are the existing fixed uniform [-1,+1] population draws, shared across levels. Start with the already frozen gain pilot; offset follows its scientific review.

These nonzero magnitudes are explicitly ASSUMED sensitivity levels: half, equal and double the existing E2 gain/offset stress envelope. They are NOT measured post-calibration residuals, a validated silicon distribution, or GF22FDX characterization. Do not infer residuals from pre-calibration spread. Document the calibration assumption and any measured or digitised inputs separately. Realistic-device conclusions require appropriate data; unavailable supplementary files do not block clearly labelled E2 research indefinitely. Do not reproduce the unpublished paper's calibration method.

Do not alter levels after seeing format rankings. If thresholds do not move within this range, report that bounded result instead of widening noise until FP wins.

## Metrics and regime labels

Let g = 100 × (C_optimum - C_returned) / C_optimum, using the ORIGINAL graph weights and documented positive optimum. Runtime retains the earliest lowest REPRESENTED-energy state; original cut is external evaluation, not a selection oracle. J remains symmetric, J=-w, diagonal zero, and problem h=0.

Retain the already declared gain-pilot ABSOLUTE thresholds for the first campaign:
- Acceptable: the 95% solver-seed CI upper bound on mean g is <=5%.
- Degraded: the CI lies above 5% and at/below 7.5%.
- Failure: the CI lower bound is >7.5%.
- Uncertain: the interval crosses a regime boundary.

These are operational cut-quality categories, not device failure probabilities or guarantees on every individual run. Also report mean original-cut gap and the entire interval, so classification does not hide uncertainty.

Separately report paired quantization penalty g(format, response) - g(FP64, SAME response), retaining the existing +1.0pp upper-CI screen. Report response degradation against the FIXED ideal condition, and paired FP-versus-INT response interaction as a diagnostic. A poor nonideal FP64 reference does not make an equally poor low-bit result acceptable. If no configuration meets the absolute target, say so.

A wide interaction CI crossing zero is inconclusive. A stable threshold supports independence only within tested mechanisms, levels, graphs and populations. More variation does not automatically mean more or fewer useful bits.

## Bounded execution and honest budget

1. **Preserve the already authored E2-GAIN-01 pilot:** one dense CAL graph, all 13 existing FP64/FP/INT/BFP configurations, ideal plus a=0.025/0.05, 24 paired seeds. Reuse 312 matching ideal M1 rows; **624 new solver runs**. Do not restart or relabel completed/running pilot results because of this scope lock.
2. Interpret that plot before expanding. The primary one-mechanism CAL campaign is 2 graphs × 7 configs × 4 response levels × 24 trials = **1344 evaluated rows**, including 336 reusable ideal CAL rows when semantics match: **1008 new primary CAL runs**, before optional BFP/8-bit additions. Credit matching pilot rows; do not rerun them for a new report.
3. Review the gain findings, then study the offset slice using the SAME approved protocol. No combined gain-offset grid.
4. Validate the locked rule on the two held-out instances. A full seven-config, four-level mirror is 1344 rows for one mechanism; a smaller predeclared validation subset is allowed if its inference limits are explicit.
5. Two complete four-graph mechanism slices sharing ideal rows contain **4704 primary evaluated rows**, not approximately 2000. Optional BFP and conditional 8-bit cells add cost. This is an upper-scope count, not authorization to launch everything at once. Before each batch state its exact new/reused run count.

Only minimal changes to the existing Python runner, analysis and plots are in scope. Keep the working environment and existing necessary regression checks; no new CI/provenance framework.

## Deliverables and milestones

| Stage | Deliverable / stopping point |
|---|---|
| Baselines, completed | Preserve 936 ideal CAL runs and the verified six-bit row/interface evidence |
| Next scientific result | One gain × precision regime plot and paired uncertainty on the dense CAL graph |
| Core CAL study | Two graph-specific precision-response maps for gain and offset studied separately |
| Validation | Two untouched held-out instances under frozen choices |
| Final result | Conditional precision-selection rule, counterexamples, one bounded hardware/storage cost table and report |

Use existing cost evidence only for implemented semantics and boundaries. Six-bit Sky130 row/interface area does not establish 4/5/8-bit area, full-chip cost, energy, latency or GF22FDX results. Report other-width payload counts as counts, not measured silicon. Equal six-bit payload does not imply equal decode/accumulator cost.

## Stop conditions and feedback

Before a scientific decision, briefly state relevance, evidence tier, closest prior art, opportunity cost, minimum test and stop condition. After results: prediction → observation → fairness/counterexamples → continue/change/stop. This should be concise feedback, not another infrastructure deliverable.

Stop new hardware/toolchain work, new axes, outcome-based parameter tuning, nominal-sigmoid duplicate runs and repeated report rewrites. Stop unsupported superiority/interaction claims when evidence does not support them; preserve valid negative or stable-threshold findings. The FYP goal is a useful, bounded design rule rather than guaranteed FP superiority.

The dated [decision feedback record](https://github.com/Makise-okabe/MRAM_P-bit/blob/research/m4-gain-fusion-20261107/docs/FYP_DECISION_FEEDBACK_LOOP.md) preserves historical evidence. This locked roadmap controls future execution.
