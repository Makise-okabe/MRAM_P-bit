# Locked FYP ideal-response checkpoint — 20 November 2026

**Decision: the ring selects FP5 / INT6 / FP64, with one certified coupling bit saved; the torus selects FP5 / INT5 / FP64, with zero certified bits saved. The ideal-response campaign is complete. No offset, gain or hardware stage has run.**

The selection applies to the equal-graph mean under the two declared generators, the tested encodings, the fixed best-observed reference procedure and the 50,000-update solver. It does not guarantee preservation on every instance. The previously unopened official ring `_6666` is a particularly important exception: both FP5 and INT6 exceed the added-loss tolerance there, while the FP64 baseline is itself substantially harder than any generated ring case by the recorded mean reference shortfall.

This report interprets the frozen output without altering its inference. All original first-block results remain unchanged. Tables round numerical values to six decimal places unless stated otherwise; linked CSVs retain the full recorded precision.

## 1. Registered choices and scope

| Generator | Lowest tested certified FP | Lowest tested certified INT | Certified-width difference `k_cert` | Selected later offset comparison | Fallback? |
| --- | --- | --- | --- | --- | --- |
| Rounded distance-decaying Gaussian ring | FP5 E2M2 | INT6 | 1 | FP5 / INT6 / matched-response FP64 | No |
| Rounded Gaussian torus | FP5 E2M2 | INT5 | 0 | FP5 / INT5 / matched-response FP64 | No |

For the ring, the registered direct FP5−INT6 contrast is +0.078394 pp with simultaneous bounds [−0.056003,+0.195208]. For the torus, the selected FP5−INT5 comparison is not an additional registered direct contrast: the conservative difference of simultaneous candidate-versus-FP64 bounds is [−0.315799,+0.189308] pp. Both selected-pair bounds lie within ±0.5 pp. The full selection record is [selected_pairs.json](analysis/selected_pairs.json).

These are lowest **tested certified** widths, not an inferred optimum over all possible number formats or widths. No smaller tested FP was included, and no monotonic interpolation or nested-codebook assumption was used. Ring INT5 fails the primary margin; torus INT5 passes. There are no smaller unresolved tested candidates below the selected choices at the primary margin. Neither a positive `k_cert` nor these quality results establishes an area or energy saving once FP decode logic is included.

## 2. Completion, provenance and verification

The executable freeze is **`d217ab54fc41a3a84d6a500f3ab0f3aa433059dd`**. All 144 generated source graphs and their hashes were frozen before solver quality runs; the two official `_6666` files were opened only after that executable freeze. NumPy is pinned to **2.3.5**. Graph generation uses PCG64DXSM and the locked SeedSequence namespaces, including the ring normalization `c_N` and the ×100000 integerization for both models.

The completed, verified record counts are:

| Record set | Count |
| --- | ---: |
| Generated graphs | 144: 72 ring + 72 torus |
| Generated main trajectories | 64,512 = 144 × 64 × 7 |
| Independent generated FP64 reference trajectories | 18,432 = 144 × 128 |
| Official anchor trajectories represented in the archive | 5,376 = 6 × 128 × 7 |
| Total trajectory records | 88,320 |
| Immutable first-block trajectories reused | 768 |
| Newly executed solver trajectories | 87,552 |
| Common-FP64-state fidelity records | 239,616 |
| Complete graph bundles | 150 |

The gate verified frozen hashes, sealed raw and fidelity records, unique registered keys, exact counts, gain 1 and offset 0, the unchanged linear 50,000-update solver, source beta, exact original-weight cut and reference-witness checks, pathwise invariants, and exact reuse of the 768 first-block records. `R_last` is missing exactly on those reused records. See [verification.json](operational/verification.json).

Preflight verification passed **36 synthetic test methods**: six source-generator, five instrumented-solver, twenty analysis and five runner methods. **25 archived controls** covering M5, E0 and the first block reproduced the archived retained states, cuts, represented energies, flips and improvements. The first-block analysis smoke was descriptive and did not rerun its solver trajectories.

The 18 local shards completed with **six workers in 929.38 seconds, or 15.49 minutes**; this is campaign execution wall time, not analysis or packaging time. All shard exit codes were zero. See [execution.json](operational/execution.json). Thirteen deterministic raw archives total approximately **41.5 MB**, preserving 600 scientific bundle files and their hashes. Their membership, verification and extraction procedure is documented in [raw_archives/README.md](raw_archives/README.md).

No seeds, graphs, candidate formats, schedules or inference contrasts were added after inspection of these outcomes. No offset, gain or hardware work is authorized by this checkpoint.

## 3. Core estimand, uncertainty and all 18 decisions

For generated graph `g`, `B_g` is the largest exactly rescored feasible original cut visited in the fixed pool of 128 independent FP64 reference trajectories plus all seven candidates' 64 main trajectories, with zero as the empty-cut fallback. It is a best-observed feasible reference, **not a certified optimum**. The primary shortfall is `100(B_g − R)/B_g`, where `R` is the original cut of the actually returned state. A contrast `left − right` is `100(mean R_right − mean R_left)/B_g`; negative favors the first representation.

Each graph contributes one complete vector of paired-seed contrast means. The graph, not the seed, is the independent family-inference unit. The frozen analysis resampled whole graph vectors jointly, separately within each family, with **500,000 bootstrap-t resamples**, PCG64DXSM, the registered namespaces and NumPy linear quantiles. There are nine contrasts per family and eighteen total. The per-tail probability is `0.04/(2×18) = 0.0011111111111111111`, giving **nominal 96% simultaneous core coverage**, subject to the bootstrap approximation. The planned device alpha was not used.

PASS requires an upper bound below +0.5 pp; FAIL requires a lower bound above +0.5 pp; otherwise the noninferiority result is unresolved. Practical equivalence requires both bounds strictly inside [−0.5,+0.5]. Statistical superiority requires an upper bound below zero. These are distinct claims. All eighteen core studentizations were finite, with **zero bad resamples**. No unresolved result was relabeled as a pass.


| Family | Contrast | Mean pp | Simultaneous bounds pp | +0.5 pp NI | Within ±0.5 pp? |
| --- | --- | --- | --- | --- | --- |
| ring | FP6-INT6 | -0.169820 | [-0.297938, -0.046931] | PASS | Yes |
| ring | FP5-INT6 | +0.078394 | [-0.056003, +0.195208] | PASS | Yes |
| ring | FP6-INT7 | -0.023524 | [-0.133002, +0.082811] | PASS | Yes |
| ring | FP5-FP64 | +0.312442 | [+0.188834, +0.460736] | PASS | Yes |
| ring | FP6-FP64 | +0.064228 | [-0.021936, +0.149014] | PASS | Yes |
| ring | INT5-FP64 | +0.689623 | [+0.539917, +0.870462] | FAIL | No |
| ring | INT6-FP64 | +0.234048 | [+0.138171, +0.342775] | PASS | Yes |
| ring | INT7-FP64 | +0.087752 | [+0.017487, +0.159911] | PASS | Yes |
| ring | INT8-FP64 | +0.044851 | [+0.007616, +0.090526] | PASS | Yes |
| torus | FP6-INT6 | +0.071585 | [-0.025370, +0.160199] | PASS | Yes |
| torus | FP5-INT6 | +0.079279 | [-0.039044, +0.197670] | PASS | Yes |
| torus | FP6-INT7 | +0.095759 | [+0.001682, +0.201907] | PASS | Yes |
| torus | FP5-FP64 | +0.094937 | [-0.017558, +0.237773] | PASS | Yes |
| torus | FP6-FP64 | +0.087244 | [-0.008214, +0.181476] | PASS | Yes |
| torus | INT5-FP64 | +0.164651 | [+0.048465, +0.298240] | PASS | Yes |
| torus | INT6-FP64 | +0.015659 | [-0.077280, +0.108338] | PASS | Yes |
| torus | INT7-FP64 | -0.008516 | [-0.077853, +0.061356] | PASS | Yes |
| torus | INT8-FP64 | -0.011649 | [-0.080347, +0.059565] | PASS | Yes |


There are **17 PASS labels, one FAIL (ring INT5−FP64), and no unresolved core labels**. All seventeen PASS bounds also satisfy the registered ±0.5 pp practical-equivalence condition. Ring FP6−INT6 is statistically superior, but its improvement is less than a demonstrated 0.5 pp material benefit. Torus FP6−INT7 is statistically inferior while still practically equivalent. Ring FP5, INT6, INT7 and INT8 have statistically positive penalties versus FP64 yet remain within tolerance; torus INT5 does too.

Sensitivity labels reuse the same bounds. At +0.25 pp, ring FP5−FP64 and INT6−FP64 are unresolved, and torus INT5−FP64 is unresolved. Ring INT5 remains a failure at +0.25 pp but passes at +1.0 pp. These sensitivity results do not change the registered +0.5 pp selection.

Sources: [core_contrasts.csv](analysis/core_contrasts.csv), [core contrast figure](analysis/core_contrasts.svg), [graph-level contrasts](analysis/graph_contrasts.csv), and [analysis registry](analysis/analysis_registry.json).

## 4. Absolute returned cuts and reference shortfalls

These are equal-graph averages over 72 instances per family, with 64 paired main seeds per graph. Each percentage is averaged after normalization by its own graph's `B_g`; it is not calculated by normalizing an aggregate cut. The shortfalls below are not optimum gaps.


| Family | Candidate | Mean returned original cut | Mean B_g shortfall % | Extra vs FP64 pp |
| --- | --- | --- | --- | --- |
| ring | FP5 | 2,631,138.52 | 5.064960 | +0.312442 |
| ring | FP6 | 2,637,785.33 | 4.816746 | +0.064228 |
| ring | INT5 | 2,620,722.05 | 5.442141 | +0.689623 |
| ring | INT6 | 2,633,284.04 | 4.986566 | +0.234048 |
| ring | INT7 | 2,637,190.10 | 4.840270 | +0.087752 |
| ring | INT8 | 2,638,347.16 | 4.797369 | +0.044851 |
| ring | FP64 | 2,639,580.90 | 4.752518 | +0.000000 |
| torus | FP5 | 6,139,590.59 | 2.996888 | +0.094937 |
| torus | FP6 | 6,139,664.25 | 2.989195 | +0.087244 |
| torus | INT5 | 6,134,816.11 | 3.066602 | +0.164651 |
| torus | INT6 | 6,144,120.17 | 2.917610 | +0.015659 |
| torus | INT7 | 6,145,293.72 | 2.893435 | -0.008516 |
| torus | INT8 | 6,145,690.16 | 2.890302 | -0.011649 |
| torus | FP64 | 6,144,810.56 | 2.901951 | +0.000000 |


FP64 itself remains approximately 4.75% below the ring best-observed reference and 2.90% below the torus reference. The precision claim is therefore about preserving a fixed finite-budget controller's useful quality, not convergence or near-optimality. Sources: [family_quality_mechanism.csv](analysis/family_quality_mechanism.csv) and [graph_quality_mechanism.csv](analysis/graph_quality_mechanism.csv).

## 5. Descriptive trajectory accounting

For each run, `V` is the best original cut visited, `M` is the best original cut among states attaining the minimum represented energy, and `R` is the cut of the earliest strict minimum actually returned. Use `C = B_g` for generated graphs and the published optimum for official anchors. Define:

- Access difference against the matched FP64 run: `A = 100(V_FP64 − V_candidate)/C`.
- **Total selection loss:** `Rz = 100(V − R)/C = 100(V − M)/C + 100(M − R)/C`.
- `100(V − M)/C` is represented-objective selection loss; `100(M − R)/C` is earliest-tie loss.

`Rz` includes **both** components. It must not be interpreted as represented-objective selection alone. Its nonnegative sign is true by definition and is not evidence for a mechanism. `A` can have either sign. The per-run identity is:

`extra gap(candidate − FP64) = A + Rz_candidate − Rz_FP64`.

Matched FP64 has zero recorded `Rz` in this campaign, but the analysis retains the full identity rather than relying on that special case. All following mechanism intervals and correlations are **descriptive**, consume **no alpha from the 18 core contrasts**, and do not identify a unique energetic-barrier mechanism.

### 5.1 Candidate component means

All entries are equal-graph means in percentage points, using each generated graph's `B_g`. These are the existing recorded components, not additional inferential endpoints.


| Family | Candidate | A vs FP64 | 100(V−M)/C | 100(M−R)/C | Total Rz=100(V−R)/C |
| --- | --- | --- | --- | --- | --- |
| ring | FP5 | +0.117617 | +0.070411 | +0.124414 | +0.194825 |
| ring | FP6 | +0.046764 | +0.014731 | +0.002734 | +0.017464 |
| ring | INT5 | +0.242845 | +0.122725 | +0.324053 | +0.446778 |
| ring | INT6 | +0.082842 | +0.056901 | +0.094305 | +0.151206 |
| ring | INT7 | +0.027713 | +0.030215 | +0.029824 | +0.060039 |
| ring | INT8 | +0.025057 | +0.011737 | +0.008057 | +0.019794 |
| ring | FP64 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| torus | FP5 | +0.052090 | +0.020135 | +0.022712 | +0.042847 |
| torus | FP6 | +0.063142 | +0.021766 | +0.002336 | +0.024102 |
| torus | INT5 | +0.073809 | +0.036160 | +0.054682 | +0.090842 |
| torus | INT6 | -0.005544 | +0.008200 | +0.013002 | +0.021203 |
| torus | INT7 | -0.014057 | +0.001988 | +0.003554 | +0.005542 |
| torus | INT8 | -0.012873 | +0.000561 | +0.000663 | +0.001224 |
| torus | FP64 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |


For example, ring FP5 total `Rz = 0.194825` pp comprises 0.070411 pp represented-objective selection and 0.124414 pp earliest-tie loss. Ring INT6 total `Rz = 0.151206` pp comprises 0.056901 and 0.094305 pp. Ring FP6 has much smaller earliest-tie loss, 0.002734 pp, and total `Rz = 0.017464` pp. The earliest-tie term compares the actual return with the best original cut among visited minimum-energy states. It does not imply that a cheap tie policy can identify that best state. The passive `R_last` endpoint measures one concrete alternative on the unchanged trajectory; its signed results appear below.

### 5.2 Registered descriptive contrast endpoints

Negative FP−INT `A` favors FP access; negative FP−INT `Rz` means less total selection loss with FP. Sign counts are positive / negative / exactly zero graph means. The final two columns distinguish the SD of 72 graph means from the median paired-seed standard error within a graph. Bounds are ordinary 95% graph-resampled bootstrap-t intervals.


| Family | Contrast | Endpoint | Mean pp | Descriptive 95% bounds | Graph signs +/−/0 | Graph-mean SD | Median within-graph SE |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ring | FP5-INT6 | Rz | +0.043619 | [+0.023825, +0.071644] | 49/23/0 | 0.098033 | 0.030338 |
| ring | FP5-INT6 | A | +0.034775 | [-0.045756, +0.108569] | 41/31/0 | 0.327122 | 0.186721 |
| ring | FP6-INT7 | Rz | -0.042574 | [-0.054813, -0.033697] | 5/67/0 | 0.043385 | 0.011047 |
| ring | FP6-INT7 | A | +0.019051 | [-0.047719, +0.086170] | 38/34/0 | 0.284871 | 0.171488 |
| ring | FP6-INT6 | Rz | -0.133742 | [-0.155928, -0.115382] | 0/72/0 | 0.084794 | 0.020634 |
| ring | FP6-INT6 | A | -0.036078 | [-0.112341, +0.038903] | 31/41/0 | 0.322375 | 0.180126 |
| torus | FP5-INT6 | Rz | +0.021644 | [+0.017027, +0.026717] | 66/6/0 | 0.020571 | 0.014443 |
| torus | FP5-INT6 | A | +0.057634 | [-0.016372, +0.131288] | 43/29/0 | 0.314625 | 0.263396 |
| torus | FP6-INT7 | Rz | +0.018560 | [+0.015819, +0.022361] | 70/2/0 | 0.013335 | 0.008777 |
| torus | FP6-INT7 | A | +0.077199 | [+0.017176, +0.142663] | 42/30/0 | 0.265427 | 0.253953 |
| torus | FP6-INT6 | Rz | +0.002899 | [-0.001285, +0.007281] | 42/30/0 | 0.018269 | 0.011502 |
| torus | FP6-INT6 | A | +0.068686 | [+0.009723, +0.124027] | 50/22/0 | 0.242309 | 0.255950 |


**The tentative prediction `Rz(FP5) > Rz(INT6)` is consistent with both families. The tentative prediction `Rz(FP6) > Rz(INT7)` fails on the ring:** the difference is −0.042574 pp [−0.054813,−0.033697], opposite in 67/72 graph means. It is positive on the torus, in 70/72 graphs. The equal-positive-level-count FP6/INT6 comparison had **no directional prediction**; its ring `Rz` difference is negative in all 72 graphs, whereas its torus interval crosses zero.

The failure constrains a simple cardinality explanation: fewer positive representable levels do not necessarily produce greater total selection loss. It does not, by itself, isolate whether code placement, scale choice, ties, visited-state composition or another landscape feature is causal. FP6 and INT6 each have 31 positive levels, so their ring result shows that level count alone cannot determine the observed total selection loss.

Access differences have substantially larger graph-mean dispersion than most `Rz` differences. That is not a variance-component decomposition: graph-mean SD also includes finite-seed variability. On the torus, access SD is close to the typical within-graph SE, and sometimes smaller; these data cannot be described as proof that access variation is intrinsic graph heterogeneity. Ring access intervals for all three descriptive comparisons include zero. The recorded access and selection terms account for sign reversals without uniquely proving why the search trajectories diverge.

Sources: [mechanism_contrasts.csv](analysis/mechanism_contrasts.csv), [mechanism figure](analysis/mechanism_contrasts.svg), and [graph_quality_mechanism.csv](analysis/graph_quality_mechanism.csv).

### 5.3 All 72 descriptive Spearman correlations

Each row reports six correlations across 72 independent graphs: `Rz` or `A` against common-FP64-state mean absolute probability error (`P`), field RMS (`H`), and zeroed original absolute weight-mass fraction (`Z`). `Z` is a fraction of weight mass, not the fraction of zeroed edge entries. Tied ranks use average ranks. These are descriptive correlations without p-values, multiplicity claims or a causal interpretation.


| Family | Candidate | ρ(Rz,P) | ρ(Rz,H) | ρ(Rz,Z) | ρ(A,P) | ρ(A,H) | ρ(A,Z) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ring | FP5 | +0.638369 | +0.235932 | +0.428934 | -0.106148 | -0.213711 | +0.005467 |
| ring | FP6 | +0.375201 | +0.147823 | +0.006914 | +0.026047 | -0.012026 | +0.155283 |
| ring | INT5 | +0.690720 | +0.312496 | +0.405267 | -0.002830 | -0.020580 | +0.210174 |
| ring | INT6 | +0.635250 | +0.132935 | +0.301563 | -0.004566 | +0.030131 | +0.011287 |
| ring | INT7 | +0.518040 | +0.204901 | +0.239501 | -0.237700 | -0.090295 | +0.047849 |
| ring | INT8 | +0.455238 | +0.292012 | +0.314039 | -0.039263 | +0.042704 | -0.032124 |
| torus | FP5 | +0.519583 | +0.065310 | +0.383819 | +0.144575 | +0.004856 | +0.229243 |
| torus | FP6 | +0.262107 | -0.212682 | -0.232500 | -0.030870 | +0.102901 | -0.010928 |
| torus | INT5 | +0.719339 | +0.471349 | +0.429931 | +0.165927 | +0.237700 | +0.029809 |
| torus | INT6 | +0.620812 | +0.465432 | +0.305647 | +0.192102 | +0.125346 | +0.095858 |
| torus | INT7 | +0.420850 | +0.486482 | -0.004309 | +0.032864 | +0.025307 | +0.088784 |
| torus | INT8 | +0.330533 | +0.246685 | +0.064630 | +0.017268 | -0.029294 | +0.065308 |


The strongest probability-error associations with `Rz` include INT5 (0.690720 ring, 0.719339 torus), FP5 (0.638369, 0.519583) and INT6 (0.635250, 0.620812). Every absolute access correlation is at most about 0.238. Thus the measured response errors associate more strongly with total selection loss than with finite-budget access. This helps explain why a numerical-error metric need not consistently predict returned-cut quality; it remains an association, with graph normalization and the fixed sampling procedure part of the estimand. Full values: [mechanism_correlations.csv](analysis/mechanism_correlations.csv).

## 6. Passive latest-tie measurement: R_last − R

`R_last` is the original cut of the latest state attaining the minimum represented energy. It was recorded passively; RNG consumption, the trajectory and the actual returned state did not change. Its difference from the earliest returned cut is signed and need not improve quality. All generated rows are observed: 4,608 per candidate per family, zero missing. These are descriptive signed means and sign counts; no confidence interval or equivalence test was added.


| Family | Candidate | Mean cut difference | Mean difference pp | Positive / negative / zero |
| --- | --- | --- | --- | --- |
| ring | FP5 | +9.1921 | +0.000237 | 1124 / 1114 / 2370 |
| ring | FP6 | -6.7930 | -0.000238 | 114 / 140 / 4354 |
| ring | INT5 | +307.8900 | +0.011784 | 1640 / 1563 / 1405 |
| ring | INT6 | +94.3184 | +0.003507 | 1040 / 1009 / 2559 |
| ring | INT7 | -39.7928 | -0.001741 | 601 / 652 / 3355 |
| ring | INT8 | -4.2589 | -0.000199 | 306 / 313 / 3989 |
| ring | FP64 | +0.0000 | +0.000000 | 0 / 0 / 4608 |
| torus | FP5 | +144.8464 | +0.002337 | 534 / 480 / 3594 |
| torus | FP6 | -32.1031 | -0.000540 | 102 / 111 / 4395 |
| torus | INT5 | -163.8631 | -0.002690 | 773 / 825 / 3010 |
| torus | INT6 | +84.1897 | +0.001371 | 431 / 424 / 3753 |
| torus | INT7 | +29.7053 | +0.000483 | 245 / 235 / 4128 |
| torus | INT8 | +2.8140 | +0.000040 | 104 / 114 / 4390 |
| torus | FP64 | +0.0000 | +0.000000 | 0 / 0 / 4608 |


The signed averages are small and mixed. Even the largest generated-family mean is only +0.011784 pp (ring INT5). Balanced signs and small signed means do not prove that individual tie choices are harmless, but they do not support a substantial general repair by always choosing the latest minimum.

For official anchors, **768 `R_last` values remain missing**, exactly the reused FP5, INT6 and FP64 first-block records on ring 5555 and 7777. They were neither reconstructed nor zero-filled. Available anchor means can also be negative: ring 6666 INT5 is −0.054379 pp and INT6 is −0.034591 pp. Full per-graph values, counts and missingness are in [R_last_differences.csv](analysis/R_last_differences.csv).

## 7. Official anchors: range checks and important exceptions

Anchor optimum gaps use the published optimum `C`. To compare with generated shortfalls, the report additionally uses `B_anchor`, the largest visited original cut in all seven candidates' 128 anchor trajectories. Its pool has **896 trajectories**; generated `B_g` uses **576 trajectories** (448 main plus 128 independent FP64 references). The differing fixed pools can affect the comparisons. Normalized anchor/reference values and optimum-normalized values are both retained.

The full range and empirical 2.5/97.5 percentiles below describe the 72 generated graph means. They are **not confidence intervals or prediction intervals**. All nine core contrast graph means and all seven candidates' reference shortfalls are checked. “Inside” below concerns reference-normalized values.

| Official anchor | Core contrasts outside full generated range | Further contrasts outside central 95% only | Candidate absolute reference shortfalls |
| --- | --- | --- | --- |
| ising2.5-100_5555 | None | INT8−FP64 | All seven inside full and central 95% |
| ising2.5-100_6666 | FP6−INT6; FP5−FP64; INT6−FP64 | None additional | All seven above full generated ranges |
| ising2.5-100_7777 | None | None | All seven inside full and central 95% |
| t2g10_5555 | None | None | All seven inside full and central 95% |
| t2g10_6666 | None | None | All seven inside full and central 95% |
| t2g10_7777 | None | INT7−FP64 | All seven inside full and central 95% |

For ring 6666, the `B_anchor`-normalized FP5−FP64 mean is +1.421672 pp, above the generated maximum +1.349931; INT6−FP64 is +1.177324, above +1.019815; FP6−INT6 is −1.183905, below the generated minimum −0.988146. Its FP5 reference shortfall is 9.598295%, above the generated FP5 maximum 8.078628%. Thus the result is not just a marginal central-percentile exception.

### 7.1 Ring 6666: ordinary paired descriptive intervals

These intervals normalize by the **published optimum**, and use ordinary 95% paired-seed bootstrap-t resampling. They do not consume core alpha or override the generated-family selection.


| Contrast | Mean pp | Ordinary 95% bounds pp | Descriptive +0.5 pp label |
| --- | --- | --- | --- |
| FP6-INT6 | -1.164700 | [-1.599382, -0.783286] | PASS |
| FP5-INT6 | +0.240384 | [-0.074395, +0.530150] | UNRESOLVED |
| FP6-INT7 | -0.394618 | [-0.731600, -0.076165] | PASS |
| FP5-FP64 | +1.398610 | [+1.096757, +1.721114] | FAIL |
| FP6-FP64 | -0.006474 | [-0.319574, +0.287556] | PASS |
| INT5-FP64 | +1.461235 | [+1.015198, +1.909975] | FAIL |
| INT6-FP64 | +1.158226 | [+0.854256, +1.502849] | FAIL |
| INT7-FP64 | +0.388143 | [+0.167231, +0.624054] | UNRESOLVED |
| INT8-FP64 | -0.012171 | [-0.253910, +0.200506] | PASS |


FP5 and INT6 therefore fail this anchor's descriptive added-loss criterion despite both qualifying for the generated-ring family mean. FP6 and INT8 qualify descriptively; INT7 remains unresolved. The FP5−INT6 direct interval itself remains unresolved at +0.5 pp and is not relabeled as a pass.

The viewed first-block ring 5555 also remains a counterexample to per-instance preservation: FP5−FP64 is **+0.952786 pp [0.687521,1.205706]**, a descriptive failure. Its FP5−INT6 comparison is +0.469706 [0.185661,0.748964], unresolved. On ring 7777, FP5−FP64 is +0.057060 [−0.179050,0.289016]. These results retain the original raw runs; the new report does not replace the archived first-block conclusions.

Torus 6666 lies inside the generated spreads, but individual-anchor uncertainty still matters: FP5, FP6, INT5, INT6 and INT7 versus FP64 are unresolved at +0.5 pp in their ordinary paired intervals; only INT8 qualifies. Being inside an empirical family spread is not a qualification label.

### 7.2 Absolute FP64 anchor quality and normalization


| Anchor | Mean returned cut | Published optimum C | B_anchor | Optimum gap % | B_anchor shortfall % |
| --- | --- | --- | --- | --- | --- |
| ising2.5-100_5555 | 2,342,688.82 | 2,460,049 | 2,436,007 | 4.770644 | 3.830785 |
| ising2.5-100_6666 | 1,834,876.23 | 2,031,217 | 1,998,267 | 9.666164 | 8.176623 |
| ising2.5-100_7777 | 3,230,288.39 | 3,363,230 | 3,346,715 | 3.952796 | 3.478833 |
| t2g10_5555 | 5,854,504.28 | 6,049,461 | 6,049,461 | 3.222712 | 3.222712 |
| t2g10_6666 | 5,570,127.59 | 5,757,868 | 5,757,868 | 3.260589 | 3.260589 |
| t2g10_7777 | 6,295,815.12 | 6,509,837 | 6,509,837 | 3.287669 | 3.287669 |


Ring 6666 FP64 has a **9.666164% optimum gap** and **8.176623% reference shortfall**, versus generated-ring FP64 mean 4.752518% and maximum 7.270968%. All seven candidate reference shortfalls on that anchor exceed their generated full ranges. The model's source scale can overlap while the realized finite-budget difficulty does not.

Sources: [anchor_spread.csv](analysis/anchor_spread.csv), [anchor_quality_spread.csv](analysis/anchor_quality_spread.csv), [anchor_contrasts_descriptive.csv](analysis/anchor_contrasts_descriptive.csv), and [anchor figure](analysis/anchor_contrasts.svg).

### 7.3 Source scale versus solver difficulty

The source-only comparison found all six official anchors inside their generated family's central 95% ranges for maximum absolute weight and raw zero count. The ring generated range is 137,395–290,819 for maximum absolute weight and 59–101 raw zeros; its central 95% ranges are 146,617.05–254,961.075 and 61.325–92.8. The torus generated range is 223,512–385,279 for maximum absolute weight, with central 95% 227,376.775–350,228.975; all 72 torus graphs have zero raw zero entries.

| Source family | Official label | Maximum absolute weight | Raw zero entries |
| --- | --- | ---: | ---: |
| Ring | 5555 | 239,752 | 69 |
| Ring | 6666 | 212,231 | 73 |
| Ring | 7777 | 220,276 | 81 |
| Torus | 5555 | 294,541 | 0 |
| Torus | 6666 | 239,344 | 0 |
| Torus | 7777 | 301,004 | 0 |

**Source-scale overlap is not evidence that solver difficulty or precision sensitivity is fully reproduced.** Ring 6666 demonstrates that distinction within this completed campaign. This does not justify dropping an instance or changing a generator after outcomes are known. See [source_spread.csv](provenance/source_spread.csv), [source_spread.json](provenance/source_spread.json) and [source acquisition provenance](provenance/README.md).

## 8. What this checkpoint establishes, and what remains unresolved

The supported engineering result is a conditional one-bit coupling-storage advantage for FP5 over the lowest tested certified integer on the declared distance-decaying ring, and no certified bit advantage on the declared Gaussian torus. It uses a predeclared tolerance and equal-graph estimand. It does not imply that FP5 is universally adequate, that a lower untested width could not qualify, or that memory-bit savings outweigh implementation cost.

The descriptive decomposition locates the returned-quality difference in access and total selection terms. Response-error metrics associate more strongly with total selection loss than with finite-budget access. One directional prediction fails, and the equal-level-count comparison differs markedly by family. These observations constrain a cardinality-only explanation but do not uniquely establish trap reshaping, barrier changes or another causal mechanism. The graph-mean access variability especially on the torus cannot be assigned to genuine between-instance heterogeneity without accounting for finite-seed noise.

A family-mean certification does not establish acceptable loss for each official anchor. Ring 6666 and viewed ring 5555 show why this distinction matters. The fixed best-observed references are auditable but are not assumed within any known distance of the generated optima. Bootstrap coverage is nominal and approximate. The absolute FP64 shortfalls also show the remaining finite-budget search limitation.

The device model in this stage is **gain 1, offset 0**. No conclusion about measured MTJ variability, offset robustness, gain variation, manufacturing yield, FPGA performance or memory-inclusive area/energy follows from these ideal-only results. These remain outside the completed checkpoint.

The first block was reused exactly where required. No extra seeds or graph instances were added, no unresolved result became a pass, and the actual solver return rule remains the earliest strict represented-energy minimum. The passive latest-tie endpoint did not change that rule.

**Checkpoint commitment:** retain the registered study, archive these results, and stop. The registered choices awaiting confirmation are ring FP5/INT6/FP64 and torus FP5/INT5/FP64. No offset, gain or hardware work begins until the user confirms.

## 9. Audit and deliverables index

- [Executable source/hash freeze](../../docs/FYP_IDEAL_FREEZE_20261120.json), [core registry](../../docs/FYP_IDEAL_CORE_REGISTRY_20261120.json), [descriptive registry](../../docs/FYP_IDEAL_DESCRIPTIVE_REGISTRY_20261120.json), and [dated mechanism amendment](../../docs/FYP_MECHANISM_AMENDMENT_20261120.md).
- [Every generated source hash](../../data/fyp_locked_20261120/source_manifest.json), [the 144 frozen source graphs](../../data/fyp_locked_20261120/sources.tar.gz), [complete seed lists](../../data/fyp_locked_20261120/seed_manifest.json.gz), and [archived parity evidence](../fyp_ideal_preflight_20261120/archived_parity.json).
- [Autogenerated analysis summary](analysis/RESULTS.md) and [analysis output hashes](analysis/analysis_manifest.json).
- [Core contrast PNG](figures/core_contrasts.png), [mechanism PNG](figures/mechanism_contrasts.png), and [presentation input/output hashes](figures/figure_manifest.json); these render the frozen tables without new inference.
- [All core contrasts and sensitivity labels](analysis/core_contrasts.csv), [selected choices](analysis/selected_pairs.json), and [core figure](analysis/core_contrasts.svg).
- [Per-graph quality and trajectory components](analysis/graph_quality_mechanism.csv), [family summaries](analysis/family_quality_mechanism.csv), and [per-graph core contrasts](analysis/graph_contrasts.csv).
- [Descriptive mechanism contrasts](analysis/mechanism_contrasts.csv), [all correlations](analysis/mechanism_correlations.csv), [mechanism figure](analysis/mechanism_contrasts.svg), and [signed latest-tie measurements](analysis/R_last_differences.csv).
- [Anchor contrast intervals](analysis/anchor_contrasts_descriptive.csv), [anchor contrast spread checks](analysis/anchor_spread.csv), [anchor absolute-quality spread checks](analysis/anchor_quality_spread.csv), and [anchor figure](analysis/anchor_contrasts.svg).
- [Frozen registry](analysis/analysis_registry.json), [full campaign verification](operational/verification.json), [local execution record](operational/execution.json), [raw archive instructions](raw_archives/README.md), and [raw archive hashes and membership](raw_archives/archive_registry.json).
- [Official source acquisition and source-spread provenance](provenance/README.md) and [source-spread table](provenance/source_spread.csv).

This human-readable report was written from the completed registered outputs. It does not modify frozen executable sources or autogenerated analysis outputs and adds no solver runs, endpoints or inferential tests.

