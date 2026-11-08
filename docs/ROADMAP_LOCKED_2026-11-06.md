# Locked FYP roadmap — coupling precision × STT-MRAM p-bit nonidealities

**Locked by user instruction on 8 November 2026.** This is the authoritative current research scope on both main and the active research branch. It supersedes older execution instructions that prioritize further RTL/toolchain expansion, park device response indefinitely, or expand the benchmark/format/solver search. Completed evidence remains valid within its original scope.

## One research question

**Under non-ideal STT-MRAM p-bit responses, what precision and representation (FP or INT, how many bits) should the coupling matrix J use to keep weighted-Max-Cut quality acceptable, and is its hardware cost reasonable?**

The original proposal's structure is retained: precision × hardware nonidealities → acceptable/degraded/failure regimes → design guidance. The computing platform is now STT-MRAM p-bit Ising computing. FP coupling is the design focus; device nonideality is a core physical condition, and existing RTL is supporting cost evidence.

Candidate originality is an evidenced conditional precision-selection rule. Do not claim that numerical precision, p-bit variability, calibration, or their broad combination is unexplored. Neither an FP win nor a format-ranking reversal is required.

## User-confirmed direction and execution lock — 8 November 2026

The user has reconfirmed this direction and asked to stay with it. This section controls the remaining sequence; dated experimental designs below preserve their original meaning.

**Matrix-coupling invariant:** original graph weights define a symmetric, zero-diagonal J with J_ij=-w_ij. Quantise its entries once per undirected edge to obtain Jhat. Local fields are H=Jhat*s. Adjacency lists and incremental field updates implement the same matrix operation; they do not change the research object. A new dense-matrix software rewrite, physical crossbar or full matrix accelerator is not a prerequisite for the numerical study. The existing row RTL remains supporting evidence.

**One pipeline:** J → low-order FP/INT encoded Jhat → H=Jhat*s → non-ideal p-bit response (gain or offset, separately) → original-weight Max-Cut quality → conditional precision guidance and bounded cost evidence.

**Remaining order:**
1. Finish and analyse the current conditional FP8/INT8 extension. Its current implementation prepares 192 new runs for the triggered CAL cells; the existing raw-primary trigger audit determines the required cells. Keep both formats and reuse completed primary, scout and ideal references. Do not restart completed experiments.
2. Credit the FP64-only offset response scout as COMPLETE: 240 new runs plus 48 reused ideal rows already identified informative d=0.8 and 1.6 logit conditions. The response-sensitive-region step has therefore been performed. Its finite-budget deterioration is not a measured physical device-failure boundary. Further offset escalation and larger-gain scouting are deferred from this campaign.
3. Close the existing precision × offset analysis at those two levels on both CAL graphs: FP/INT4/5/6 plus the required FP8/INT8 controls. The primary design is 576 new low-bit runs with 96 FP64 scout and 336 ideal reference rows reused. Evaluate absolute quality, matched-response quantisation loss and paired format–response interaction.
4. Freeze the conditional selection rule and a bounded validation comparison before reading the two held-out graphs. Then validate on those graphs without changing solver, scales, stress levels or quality thresholds.
5. Assemble the final regime maps, conditional precision rule, counterexamples and existing hardware/storage cost table. Extra RTL, synthesis or physical processor work is not a prerequisite.

**Scientific interpretation stays open:** extra coupling bits may help, cease to help, or have unresolved benefit. Eight-bit quality is measured rather than assumed monotonic. Interaction is tested through continuous paired gaps; crossing an absolute failure threshold is not required. A stable precision threshold is a valid bounded result. No stress range will be extended to manufacture a failure, an interaction or an FP win.

**Change control:** stay with this research question, weighted Max-Cut, the existing format pool and separate gain/offset mechanisms. A benchmark switch, new device axis, solver search or new hardware project requires a new explicit user instruction. Correct implementation errors and qualify claims when evidence changes; do not treat such corrections or a related paper as automatic permission to restart the project. Future batch budgets are declared before execution, and completed compatible data are reused. This documentation update launches no runs.

## Locked scope

| Axis / component | Core | Outside this campaign |
|---|---|---|
| Coupling representation | Existing FP and INT codebooks at 4/5/6 bits, FP64 reference; existing 8-bit variants under the rule below | New codebooks, exponent/mantissa searches, logarithmic formats |
| Shared-exponent control | Preserve all existing BFP results; optional BFP6 supporting control, with scope declared before runs | New BFP group-size searches, independently rounded asymmetric rows |
| Device response | Separate gain and offset slices; retain completed gain pilots and the scout-selected offset comparison d=0/0.8/1.6 | Gain × offset cross-product, new mechanisms, further stress escalation in this campaign |
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

The current E2 slices are:
- Gain-only: alpha_i = 1 + a u_i, delta_i = 0. Preserve completed a=0/0.025/0.05 pilots; the earlier proposed a=0.10 extension is deferred.
- Offset-only: alpha_i = 1, delta_i = d v_i. The completed FP64 scout used d=0/0.1/0.2/0.4/0.8/1.6; the current low-bit comparison uses d=0/0.8/1.6.
- The earlier proposed offset d=0/0.05/0.10/0.20 range was explicitly superseded by the scout amendment below.
- u_i and v_i are the existing fixed uniform [-1,+1] population draws, shared across levels.

These nonzero magnitudes are explicitly ASSUMED sensitivity levels. They are NOT measured post-calibration residuals, a validated silicon distribution, or GF22FDX characterization. Do not infer residuals from pre-calibration spread. Document the calibration assumption and any measured or digitised inputs separately. Realistic-device conclusions require appropriate data; unavailable supplementary files do not block clearly labelled E2 research indefinitely. Do not reproduce the unpublished paper's calibration method.

Do not alter levels after seeing format rankings. If thresholds do not move within the locked range, report that bounded result instead of widening stress until FP wins.

## Completed bounded offset-scout amendment — 8 November 2026

The FP64-only reference-response scout was completed **before** any additional gain-only rows. The two completed gain-only CAL pilots are preserved,
without rewriting solver, seeds, response equation or their results.

**Scientific question:** At what assumed persistent LOGIT offset does the frozen
FP64 weighted-Max-Cut response exhibit *noticeable* quality deterioration?
This isolates the response baseline **without examining low-bit rankings**.

- Exactly the two existing CAL graphs: `t2g10_5555` (index 1),
  `ising2.5-100_5555` (index 2).
- `ref64` only, same 50,000-update linear solver, 24 original paired seeds,
  same synthetic 100-device offset population drawn in E2, fixed in each run,
  matched across levels, graphs and solver seeds; gain = 1 exactly.
- Five nonzero offset halfspans: `d={0.1,0.2,0.4,0.8,1.6}` LOGIT,
  where `delta_i=d*v_i`, `v_i~Uniform[-1,1]` is the *existing* fixed E2 draw.
  These values are **E2 diagnostic assumed stresses, NOT measured STT-MRAM
  post-calibration residuals**. ±1.6 logit is intentionally a high stress
  and cannot be called realistic or equated with a measured voltage limit.
- **240 new solver runs** = two graphs × five levels × 24 paired seeds.
  **48 ideal runs reused** from the frozen 936-run original M1 CSV.
- Report absolute original-optimum gap vs the existing 5%/7.5% regimes,
  and paired per-seed deterioration from each graph's matching ideal FP64.
  Declare *clear practical deterioration* only if the **95% seed-bootstrap
  lower confidence limit** of the mean gap increase exceeds **+1.0 percentage
  point**. A CI overlapping +1 pp is inconclusive.
- After reviewing FP64 results, select at most two informative offset
  levels using **FP64 only**, before examining any low-bit response rankings.
  If no noteworthy effect appears within this declared range, report the
  bounded negative finding; do not extend stress to force a result.

This is an explicit amendment to the prior proposed offset grid
`d={0,.05,.10,.20}`, which is deferred rather than silently called
unchanged. The gain × offset cross product remains forbidden; the future
low-bit comparison and held-out policy stay frozen. No additional gain
tests, RTL/toolchain work, or new solvers are part of this scout.

## Scout-informed primary offset design — 8 November 2026

**FP64-only scout has completed (240 new runs, 48 reused ideal).**
Its seed-conditional mean original-gap deterioration (pp) from ideal at
d=0.8/1.6 LOGIT was: t2g10 sparse +0.395 / +2.247; ising2.5 dense
+0.529 / +0.685. Only sparse d=1.6 had paired bootstrap CI lower
bound >+1 pp; no absolute failure regime was established. Results belong
to ONE synthetic 100-device offset population, not measured silicon residuals.

**Decision based only on FP64 scout, frozen before any new low-bit outcomes:**
select both d=0.8 and d=1.6 on BOTH existing CAL graphs, zero gain variation.
These are intentionally diagnostic E2 logit offsets and do not replace a
measured calibrated switching-response distribution.

The existing primary offset experiment is exactly:
- Two CAL graphs with original M1 graph indices 1/2.
- Six core low-bit formats: FP4/5/6 and INT4/5/6 (same M1 global codebooks).
- Two selected offset halfspans d=0.8 and 1.6; identical per-device v_i,
  persistent and reused from the completed FP64 scout (gain exactly one).
- 24 paired solver seeds per cell, unchanged 50k linear schedule and beta.
- **576 new primary solver runs** (2 graphs x 2 levels x 6 formats x 24 seeds).
- Reuse **96 matched FP64 scout rows** (2 graphs x 2 levels x 24 seeds)
  and **336 M1 ideal FP64/FP/INT rows** (2 graphs x 7 formats x 24 seeds).
  Do not rerun either reference dataset.
- Report absolute original-optimum gap + full seed CI, matched-condition
  FP64 added quantization loss + CI, direct FP_b minus INT_b paired differences
  and paired offset-induced difference-in-differences, b in {4,5,6}.
- Apply the existing common acceptable-gap (5% CI upper) AND +1pp
  matched-FP64 numerical-loss (CI upper) screens. If either six-bit
  configuration does not clearly pass in a graph/offset cell, add **both
  FP8 and INT8** at that cell as a separately budgeted conditional extension;
  report unmeasured cells honestly.
- Stop after interpreting primary maps, CIs and required conditional 8-bit
  cells. Then freeze the conditional rule and perform held-out testing.
  No gain expansion, enlarged offsets, new benchmark, solver or RTL work.

This is a **scout-informed CAL design choice** documented *before* FP/INT
offset results, not a revision selected using low-bit rankings. The earlier
unextended gain-only pilots, all M1 and hardware cost evidence remain intact.

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

- Preserve the 936 M1 ideal CAL runs, completed gain pilots and FP64 offset scout. Do not rerun these to refresh a report.
- The current primary offset map contains 2 CAL graphs × 7 configurations × 3 conditions (ideal, d=0.8, d=1.6) × 24 seeds = **1008 evaluated rows**: 576 new low-bit rows, 96 reused nonideal FP64 scout rows and 336 reused ideal M1 rows.
- The conditional FP8/INT8 extension is a separate, currently prepared **192-new-run** batch; retain the raw-primary audit of its four triggering graph/offset cells. Reuse compatible ideal eight-bit and nonideal FP64 rows rather than rerunning them. Do not imply eight bits must pass.
- After CAL closure, predeclare the held-out comparison and its exact new/reused budget. The two untouched graphs test the frozen conclusion; they are not a new parameter-search set.
- The old full gain/offset campaign totals are historical scope estimates, not instructions to launch more grids. No additional gain or offset range is authorised by those estimates.

Only minimal corrections to existing runners, analysis and plots are in scope. Keep existing necessary correctness checks; do not create a new CI/provenance framework.

## Deliverables and milestones

| Stage | Deliverable / stopping point |
|---|---|
| Baselines, completed | Preserve 936 ideal CAL runs and the verified six-bit row/interface evidence |
| Current scientific closure | Complete current conditional FP8/INT8 controls and the existing two-CAL precision × offset analysis |
| Core CAL study | Interpret completed gain evidence and the two graph-specific offset–precision maps, with CIs and counterexamples |
| Validation | Two untouched held-out instances under frozen choices |
| Final result | Conditional precision-selection rule, counterexamples, one bounded hardware/storage cost table and report |

Use existing cost evidence only for implemented semantics and boundaries. Six-bit Sky130 row/interface area does not establish 4/5/8-bit area, full-chip cost, energy, latency or GF22FDX results. Report other-width payload counts as counts, not measured silicon. Equal six-bit payload does not imply equal decode/accumulator cost.

## Stop conditions and feedback

Before a scientific decision, briefly state relevance, evidence tier, closest prior art, opportunity cost, minimum test and stop condition. After results: prediction → observation → fairness/counterexamples → continue/change/stop. This should be concise feedback, not another infrastructure deliverable.

Stop new hardware/toolchain work, new axes, outcome-based parameter tuning, nominal-sigmoid duplicate runs and repeated report rewrites. Stop unsupported superiority/interaction claims when evidence does not support them; preserve valid negative or stable-threshold findings. The FYP goal is a useful, bounded design rule rather than guaranteed FP superiority.

The dated [decision feedback record](https://github.com/Makise-okabe/MRAM_P-bit/blob/research/m4-gain-fusion-20261107/docs/FYP_DECISION_FEEDBACK_LOOP.md) preserves historical evidence. This locked roadmap controls future execution.
