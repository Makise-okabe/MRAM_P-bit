# Locked study — low-order FP coupling matrices for STT-MRAM p-bits

Locked by Yanzhang on 20 November 2026, following Round 2 and the six amendments. This is the current working research plan on main and the research branch. It supersedes older next-step instructions and routine supervisor-approval requirements in dated planning notes. Completed M1/M5/M6/E0/EX1 evidence keeps its original conditions and labels.

## Research question and purpose

How do low-order floating-point representations of the symmetric coupling matrix J affect local fields, stochastic p-bit responses and weighted Max-Cut solution quality under specified STT-MRAM nonidealities, and when do those effects justify their implementation cost?

FP representation is the design subject. Integer encodings are the comparison. Outcomes include better quality at equal width, comparable quality at fewer bits, and a supported finding that integer encoding is sufficient. Bits saved is one engineering outcome. A reversal on two viewed graphs is a diagnostic example.

In plain language, we put the same problem into several small-number encodings, let the same p-bit solver use each one, and check how much answer quality we lose or gain. We then check the chosen encodings with imperfect p-bit responses and count the storage and logic they require.

## Completed evidence and present status

M5 dense validation, M6 sparse validation, E0 schedule comparison and EX1 FP5/INT8 exploration are completed. They justify this prospective study, with their existing limitations. The historical CAL campaign has report/console summaries whose complete original raw archive was not located in the public branch.

The research sources inspected for this lock were main 41d586844bfd4f04167276127d4366851d71c279 and research 915a107e40ed7db74659c84b39364ae27708ad44. The new ensemble and offset campaign have not run. This commit locks the study choices. Runner and analysis verification are the next implementation work before freezing their executable source hashes.

## Fixed computation

Use J_ij = J_ji = -w_ij, J_ii = 0 and h = 0. Quantize each undirected edge once and mirror it. Retain the source-MSE global scale policy, nearest-even rounding, finite saturation and the existing custom FP semantics. Keep the binary32 scale metadata and high-precision behavioral local-field accumulation.

Use the existing random-site sequential Gibbs solver, linear beta schedule and 50,000 attempted updates at N = 100. Retain the earliest strict minimum of represented energy and score its state on the original weights. Initialization, site choices and uniforms are paired across conditions within each graph/seed. This is a finite-budget controller.

Candidates are FP5 E2M2, FP6 E3M2, INT5, INT6, INT7, INT8 and FP64. INT7 uses symmetric codes -63 through +63, with -64 unused, and the same integer scale search. The old 4/5/6/8 campaign roster remains unchanged. INT7 is added for the new study only. FP7 and BFP7 are outside this candidate set.

## Independent instances and official anchors

Generate 72 independent N = 100 instances of each model, with 64 paired main solver seeds each. Use the six official Biq Mac anchors separately, at 128 paired seeds per candidate. Keep the two official _6666 weight files unread until the executable protocol is frozen.

### Rounded distance-decaying Gaussian ring

For i < j, use r_ij = (N/pi) sin(pi abs(i-j)/N), independent z_ij drawn from a standard Gaussian, and

    c_N = [sum over j != i of r_ij^(-5)]^(-1/2)
    w_ij = round_even(100000 * c_N * z_ij / r_ij^2.5).

At N = 100, c_N is approximately 0.69407031. It is the mean-field normalization in the primary ring model. The exponent describes spatial decay. It is not an iid Pareto-magnitude model.

### Rounded Gaussian torus

Use a periodic 10 by 10 grid with right/down neighbors, 200 unique undirected edges, and w_e = round_even(100000 * z_e). Preserve signed weights.

Use PCG64DXSM with graph SeedSequence([20261120, 910, family, index]), family 0 ring or 1 torus and index 0 through 71. Pin NumPy 2.3.5, verified in the source-only check, and record the runtime version. Save every source graph and hash before quality runs. Retain every sampled graph. These are declared generators from documented models, rather than exact reproductions of the historical RNG and integerization.

### Source-scale verification completed on 20 November

The following original files were downloaded directly from the official Mac/ising directory, with no solver runs.

| Source | Maximum absolute weight | Raw zero entries | Raw entries |
| --- | ---: | ---: | ---: |
| ising2.5-100_5555 | 239752 | 69 | 4950 |
| t2g10_5555 | 294541 | 0 | 200 |
| ising2.5-100_7777 | 220276 | 81 | 4950 |

Their SHA256 values are c8fa3ce4df1997b89aad6199525a66e55699c259680483b62cc5fd3cfc1e316e, c742b78ebdebb47ad7146bffd657d42fab814a7fa82c4a17942b37f2f7fa96cb and 109e1ed2edc71d5f43d623367410d9257a72662d665c7a0c71af4cdd8babaf99 respectively.

After multiplying ring weights by r^2.5/100000, the observed standard deviations are 0.69768 and 0.69328 on the two viewed ring cases. These agree closely with c_N. The torus standard deviation after division by 100000 is 1.01126. This supports the multiplier and the ring normalization. It does not identify the historical RNG. A separate 16-draw source-only check per model, using seed domain [20261120,909,family,index], gave ring maxima 167831-260481 and zero counts 64-101, and torus maxima 261791-370870 with no zeros. No solver quality was inspected and no official _6666 file was opened. This is a scale/spread check, not an instance-selection rule.

## Quality metric and tolerance

For official anchors, use the published optimum and the historical original-weight optimum gap. Prospective precision contrasts use a primary tolerance of +0.5 percentage points, with +0.25 and +1.0 as sensitivities on the same bounds. Historical M5/M6 screens are preserved.

For generated graphs, define B_g as the largest feasible original cut in a predeclared pool consisting of 128 independent FP64 reference trajectories plus all seven candidates' 64 ideal-response trajectories. Include the empty cut as a zero fallback. Exactly rescore and retain the state achieving B_g. If B_g is nonpositive, keep the instance and mark normalized qualification undefined. Freeze B_g after that fixed pool, before selecting encodings or running offsets. Device results reuse this reference. A device run can beat B_g and have a negative signed shortfall.

Report generated reference shortfall as 100(B_g - C)/B_g and paired differences as D_A-B = 100(mean C_B - mean C_A)/B_g. Negative FP-minus-INT favors FP. The tolerance means at most 0.5% of this best-observed feasible cut in mean added loss. The estimand is the equal-graph mean under this explicitly fixed evaluation procedure.

This changes the denominator from an unknown optimum to an auditable best-observed reference. Report that distinction in every generated-results table. No assumption that B_g is within 1% of the optimum is made. Adding later runs does not change B_g. Any later best-known update is a separately labelled descriptive analysis. Compare the reference-normalized and optimum-normalized contrasts on official cases to quantify the difference there.

The sum-of-positive-weights envelope is removed from primary qualification. Exact/bounded solver results are optional descriptive checks, with at most two working days of setup and ten minutes per graph. Keep unsolved instances. Best observed, solver-certified optimal and proof-checked exact are distinct reference labels.

## Decision rules and uncertainty

Use paired per-run differences and average them within each graph. Generated-instance inference resamples complete graph vectors, separately for each family. It includes uncertainty from the finite registered run/reference pool. A family-mean conclusion does not establish success on every graph.

There are nine registered core contrasts per family.

1. FP6 minus INT6.
2. FP5 minus INT6.
3. FP6 minus INT7.
4. Each of FP5, FP6, INT5, INT6, INT7 and INT8 minus matched FP64.

There are 18 core contrasts in total. Allocate alpha_core = 0.04, with each lower/upper tail q = 0.04/(2*18). The three device contrasts per family give six in total, with alpha_device = 0.01 and q = 0.01/(2*6). This replaces the earlier 14-contrast registry. Familywise coverage is nominal and subject to interval approximation.

Use studentized bootstrap-t for confirmatory mean bounds, resampling whole independent graph vectors jointly across contrast columns. Use 500000 resamples, batched computation, fixed RNG and declared quantile convention. For mu = mean(x), se = sd(x)/sqrt(n) and bootstrap T = (mean(x*) - mu)/se*, the bounds are mu - quantile(1-q,T)*se and mu - quantile(q,T)*se. Handle truly deterministic equality explicitly. Report undefined or unstable studentization as unresolved.

Use ordinary 95% paired intervals for descriptive first-block and individual anchor figures. Their significance labels do not supply the simultaneous width-selection claim. Test the analysis implementation on deterministic synthetic examples and first-block paired data before the ensemble source/analysis freeze. Verify signs, studentization, contrast count and multiplicity. Two fixed first-block graphs are not a family-level sample.

For D = FP minus INT, report these distinct statements.

| Claim | Required result |
| --- | --- |
| Statistical superiority | Upper bound below 0 |
| Estimated benefit exceeds 0.5 pp | Point estimate below -0.5, with uncertainty |
| True mean benefit exceeds 0.5 pp | Upper bound below -0.5 |
| Non-inferiority within 0.5 pp | Upper bound below +0.5 |
| Practical equivalence | Both bounds inside [-0.5,+0.5] |
| Penalty exceeds tolerance | Lower bound above +0.5 |
| Otherwise | Unresolved |

Candidate qualification is a separate candidate-minus-FP64 comparison under the same response. Report absolute returned cuts and reference shortfalls as well as contrasts.

Define the lowest tested certified width for each encoding family. Smaller unresolved candidates prevent a claim of the true required minimum. Report certified-width differences with those qualifications. A named FP6-for-INT7 replacement requires its direct comparison and the relevant qualification evidence. Two candidates separately passing versus FP64 do not automatically establish pairwise equivalence.

## Mechanism measurements

Maintain the original cut with a second original-J field cache, without changing update RNG consumption or retention. Record V, the best original cut visited, M, the best original cut among minimum-represented-energy states, and R, the actual returned cut.

The identity C* - R = (C* - V) + (V - M) + (M - R) accounts for quality not reached, represented-objective selection loss and earliest-tie loss. C* cancels in paired differences of the first component. For generated graphs the stored quantities are exact original cuts, even while C* is unknown.

Verify instrumentation against archived deterministic replays and direct integer rescoring. Record summaries/checkpoints at 5000, 15000, 30000 and 50000 attempts. At common FP64 states, evaluate field RMS, logit RMS and mean absolute probability error for every candidate. Aggregate spins/checkpoints within each run and graph.

Run the beta/a diagnostic only on the two viewed dense cases, with a = <J,Q>/<J,J> from source coefficients. Holding legal codes fixed and replacing beta by beta/a also rescales residual error. It tests global operating-point sensitivity. Trajectory accounting identifies where loss appears without uniquely identifying energetic barriers.

## Bounded device validation

Use gain 1 and persistent delta_i independently uniform on [-0.8,+0.8]. Draw one independent 100-device offset bank per generated graph with SeedSequence([20261120,930,family,index]). Pair that bank across the three tested representations. The independent unit is the graph-bank pair, with 72 units per family. This estimates the joint graph/device-distribution mean. It does not separate fixed-graph device variance or establish manufacturing yield.

After the ideal study, freeze the lowest tested certified FP and INT for each family, then compare those two choices and matched-response FP64 at 64 paired solver seeds per graph-bank pair. Use the corresponding ideal solver seeds again across response conditions, pairing initialization, sites and uniforms. If either encoding family has no certified candidate, use FP6/INT6/FP64 as the declared diagnostic fallback.

Register selected FP-minus-INT, FP-minus-FP64 and INT-minus-FP64 per family. Resample whole graph-bank vectors. Official anchors provide descriptive checks. A format-by-offset interaction is exploratory unless separately registered.

For p_i = sigmoid[alpha_i(V-mu_i)] and V = mu_hat_i + x/alpha_hat_i, g_i = alpha_i/alpha_hat_i and delta_i = alpha_i(mu_hat_i-mu_i). At slope 128.8/V, 0.8 logit is a 6.21 mV centering error. The uniform stress is an assumed sensitivity condition. It is not a measured residual distribution. Gain variation remains an explicit limitation.

## Architecture and costs

The primary architecture is a dense fixed all-to-all N = 100 coupling array with packed coefficient positions. One-copy triangular payload is 4950*b + 32 bits. State whether a physical row-access design duplicates symmetric coefficients and how many datapaths it replicates.

Sparse bitmap and indexed layouts are sensitivity analyses. Include support/index bits, scale metadata and access overhead. FP6 can save dense payload against INT8 while requiring more sparse storage because it retains more edges. Raw coefficient width alone does not establish total area savings.

Use existing Sky130 row evidence as component-level evidence. Cost a quality-qualified named pair under matched assumptions. Additional synthesis is limited to one week when its actual decoder cost can change the engineering choice. Memory, mapped logic area and energy are different outputs.

## Execution order and budget

| Stage | Registered runs | Purpose |
| --- | ---: | --- |
| First viewed-dense block | 1280 | 768 raw FP64/FP5/INT6 runs plus 512 beta/a controls |
| Generated ideal ensemble | 64512 | 144 graphs * 64 seeds * 7 candidates |
| Independent FP64 references | 18432 | 144 graphs * 128 seeds |
| Six official ideal anchors | 5376 | 6 anchors * 128 seeds * 7 candidates |
| Restricted beta/a controls | 512 | Counted separately from anchor raw runs |
| Generated graph-bank offset validation | 27648 | 144 units * 64 seeds * 3 candidates |
| Full unique planned total | 116480 | First block raw runs are reused inside anchors |

The first block is part of this total. Stop it at 128 pairs per viewed graph and continue the ensemble regardless of the reversal's sign. Runtime is expected to be a few hours at the reported replay timings, excluding implementation, bootstrap analysis and optional exact solves. INT7 and the full pipeline need fresh timing checks. These are estimates, not completed campaign measurements.

During late-November exams, prioritize this source lock and the bounded implementation/first block. December covers the ideal ensemble, official anchors and a methods-chapter draft. January covers analysis, frozen encoding choices and offset validation. February covers memory-inclusive cost and results/discussion. March closes figures, limitations, reproducibility and the thesis.

The INT7 quantizer extension is implemented with four passing targeted tests and 600 legacy scalar/scale parity checks. The remaining implementation deliverables are a parity-preserving trajectory logger and a tested analysis script implementing this 18-contrast registry. Freeze executable versions before reading official _6666 weights or collecting the independent main campaign. Research choices are owned by the student and justified in methods. No routine supervisor sign-off is required.

Keep one stable question throughout. Further experiment requests must identify a decision they could change and use a bounded plan. Scientific corrections can amend this document with reasons and dates. Preserve completed raw evidence and report unresolved outcomes at the stated cap.

## Primary sources and provenance

- Official library and source files — https://biqmac.aau.at/biqmaclib.html and https://biqmac.aau.at/library/mac/ising/
- Ring model and mean-field normalization — Frauke Liers, dissertation, Section 3.1, printed pp. 79-80, https://kups.ub.uni-koeln.de/1308/1/Dissertation.pdf
- Round 2 protocol and Yanzhang's six-amendment review, 20 November 2026.
- Closest engineering comparison — Bratenkov et al. (2026), DOI 10.15514/ISPRAS-2026-38(4)-23.
- Mechanism boundary — Hizzani et al. (2026), DOI 10.1038/s44335-026-00082-4.

## Dated amendment — 20 November 2026: descriptive mechanism endpoints

The student's next-stage instruction adds the descriptive endpoints specified in
[FYP_MECHANISM_AMENDMENT_20261120.md](FYP_MECHANISM_AMENDMENT_20261120.md).
It preserves this lock's research question, seven candidates, solver, source
generators, reference procedure, tolerance, nine core contrasts per family
(18 total), alpha allocations, seed namespaces and run caps. It does not reopen
or rerun the completed first block. The decomposition explains the engineering
answer; it is not a separate thesis or an additional confirmatory test family.

The amendment adds a passive `R_last` field and descriptive across-instance
access/selection comparisons. It uses no alpha from the 18 core contrasts.
Missing `R_last` in reused historical records remains explicitly unavailable;
the authorized small parity sample is not a rerun of the first-block campaign.
No distinct-energies-among-the-best-one-percent endpoint is added.
