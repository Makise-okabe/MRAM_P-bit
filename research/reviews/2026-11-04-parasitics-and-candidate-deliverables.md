# Parasitics and candidate deliverable contracts

> Later 4 November clarification: [ADR-0005](../decisions/ADR-0005-one-mapping-study-and-supporting-tools.md)
> corrects the presentation below. The original three discussion topics are mapping,
> failure prediction and Ising. Spatial read control is a conditional extension of
> the mapping study; the predictor is its supporting tool. The original numbered
> screens below remain a dated technical discussion, not a replacement shortlist.


Date: 4 November 2026 (Singapore).
Status: proposed outcome contracts for the existing three screens, not a final topic selection, an executed result, or a novelty pass.

## Why this clarification was needed

The user asked whether the original parasitics concern belongs in all three candidates and what each candidate would actually produce. Mechanism observations and parameter sweeps are insufficient for the method/design objective the user has set. Define the intended artifact, discriminating finding, comparison and rejection condition before a large evaluation. The three candidate names remain unchanged.

The exact original proposal is not newly re-read by this note. Its governing scope is taken from the active scope and report: coupled precision, hardware nonidealities and reliable memory-centric inference. No supervisor endorsement of any new method is inferred.

## Common physical foundation

Use the fresh physical 256x256 target with authorized GF access NFETs and the student-owned MTJ model. Include distributed BL/SL/WL resistance and capacitance, relevant drivers, sense loading and neighboring-column connections. Reuse no retired electrical distributions or fitted parameters.

Wire resistance affects local read bias, static current and shared loading. Capacitance affects transients, settling and sample-time dependence; ideal capacitance alone does not create a settled DC current error. Neither deterministic RC nor persistent mismatch establishes a source of fresh random noise.

A declared explicit RC sensitivity model can reject a mechanism early. It must be labelled assumed/model-level. Extracted representative interconnect and checked full-array hierarchy strengthen final physical claims; do not call a software matrix or an RC-free schematic full-macro PEX. Three candidate screens share one physical foundation, not three separately invented array models.

Use paired controls: ideal wiring/nominal cells; RC/nominal cells; ideal wiring/persistent variation; RC/persistent variation. Evaluate common transient windows and a settled reference where meaningful. Include the same realistic ADC and practical calibration. Hold each chip realization fixed across compared operations. Add temporal noise only with separate justified provenance.

## Candidate 1: spatial-footprint read control

Question: does mask arrangement leave useful, predictable read distortion beyond count/activity-based and practical position-aware correction?

Proposed artifact: an implementable policy selecting the lowest-cost supported read operation from a small frozen action set (initially one read versus a specified two-part read). Inputs are bounded activation-mask features and permissible stored metadata. A calibrated LUT or compact rule estimates the error risk of each action. It may not calculate the unknown full dot product digitally for free.

Proposed decision form: choose minimum total cost C(a), subject to a predeclared predicted error budget for action a. This is an operational specification, not a statistical guarantee from an unvalidated predictor. Partitioning reduces concurrent loading; it does not shorten physical wires.

Finding to establish: masks with the same ideal arithmetic and activity can require different actions, and the proposed features predict that difference on new masks and programmed weights after baseline correction. A coactivation residual is only a diagnostic, not the method contribution.

Intended successful outcome: a read controller plus a defensible decision rule, with lower latency/energy at matched task quality, or better task quality at matched total cost. Early read/conversion counts remain proxies until timings/energy are established. Account for feature calculation, extra sensing, accumulation, calibration and storage.

Critical comparisons: tuned ADC/reference placement, longer common sensing time, per-column affine correction, applicable row/SEC-style compensation, count/centroid-only policies, activity-adaptive splitting, and the strongest applicable combined correction/control baseline. DIB-CIM full implementation remains to be inspected.

Reject the method if no consequential conditional dependence survives correction, if mask-only features fail across weights, if simple features/policies match it, or if overhead removes its useful benefit.

## Candidate 2: F3 decoded-covariance-aware mapping

Question: can a legal resident mapping change joint decoded errors across bit cycles in a useful way beyond individual read quality and ordinary randomization?

Proposed artifact: an offline mapper. Inputs are frozen weights, calibration-only workload traces, validated read/decoder behavior and a fixed resource budget. Output is one resident row permutation with corresponding weight placement; retain common mapping across relevant activation and weight planes, signed reconstruction and parent identities. No per-image remapping oracle.

The existing method specification uses reconstructed MSE:
R(P) = E[(b^T e)^2] = (b^T mu)^2 + b^T Sigma b.
Use bounded swaps/exchanges and include offline search/calibration cost. This identity is standard mathematics and is not the novelty claim.

Finding to establish: after practical calibration and decoding, a joint-error score makes better mapping decisions than marginal-error/activity scores, and those decisions matter for independent inputs and chips. Correlation can reinforce or cancel depending on signed coefficients; unconditional decorrelation is not the objective. RC may change the conditional errors without being required for covariance to exist.

Intended successful outcome: a reproducible mapping algorithm and deployment recipe with lower neural failure at the same read/resource budget, or lower total resources at a frozen acceptable failure level. MSE is a search surrogate; task evaluation must check final rankings.

Critical comparisons: original order, fixed seeded random, best-of-equal-budget random, applicable channel shuffling, CAR/co-zero grouping, activity balancing, marginal-only/covariance-ablated search, practical calibration and adaptive read policies. Account for mapping metadata, routing, skip savings and setup. Do not turn a lower read count into an energy claim.

Reject the method if the hardware has no legal grouping leverage, the calibrated decoder makes mapping effectively invariant, random/shuffled alternatives match the useful frontier, or arithmetic gains do not yield the claimed task/resource benefit. Constructed E03M/E03Q do not pass this physical/method gate.

## Candidate 3: F7 Ising local-field consistency

Question: does the actual MRAM field-update operator introduce consequential coupling distortion or cache drift, and can a more economical field-maintenance policy control it?

Proposed artifact, still less specified than F3: a refresh/accuracy-control policy using an observable or maintainable estimate of local-field uncertainty. It chooses incremental update versus a declared refresh operation. The controller may not consult exact true local fields for free; an implementable uncertainty monitor and its cost must be defined before this becomes a full method project.

A possible development direction is to relate the estimated field error to the sensitivity of the selected stochastic spin-update rule and its annealing temperature. This is a proposal to specify, not an asserted novel controller. Conventional adaptive precision, error budgeting and refresh must be checked as prior art.

Finding to establish: distinguish consistent fixed-coupling distortion, fresh read error and accumulated cache error. A reversible two-flip check tests whether the cache returns to its starting state; cancellation of a fixed error does not establish accuracy relative to the intended Hamiltonian. Static parasitics need not create stochastic noise or cache drift. Full-field recomputation and incremental updates can have different physical error regimes.

Intended successful outcome: a justified field-maintenance rule with better probability of reaching a declared target solution at equal total cost, or lower time/energy to the same success target, including initialization, matrix/transpose storage, access, cache and refresh overhead. Use true graph objectives and verified small-graph optima before larger graphs.

Critical comparisons: exact digital incremental fields, full recomputation, calibrated reads, tuned periodic refresh, and applicable temperature-aware precision policies. Apply the same annealing/tuning budget and meaningful graph/chip/restart statistics.

Reject the method if accurate single-coupling/digital updates remove the relevant problem, if no practical monitor is available, if ordinary refresh matches it, or if MRAM offers no useful total-cost case. Frozen-versus-fresh plots alone are not the deliverable. F7 remains conditional, with a more substantial scope shift from inference.

## What comparable papers actually deliver

These are author-reported external results, not expected gains for this project or cross-paper performance rankings.

| Work and access used here | Technical artifact | Reported outcome and limit |
|---|---|---|
| Roy et al., JSSC 2025, official abstract | MRAM macro with offset-compensated sensing and statistical error compensation for BL/SL effects | 2.7-6 dB SNDR improvement across stated operating points; paper reports explicit overhead/trade-offs. Full SEC implementation is not newly verified here. |
| DIB-CIM, TCAS-I 2026, publisher abstract | Dynamic input-block control, input-bit/distribution detection and dynamic-resolution ADC | 12-16% latency reduction across four workloads versus fixed B=8, excluding zero-skipping; abstract-level access does not certify fabrication or prove spatial information absent. |
| VARA, 2026 preprint, primary indexed abstract | Voltage-aware training plus co-zero activation reordering | Authors report 60.12% average system-energy reduction for the overall scheme. This is not an isolated CAR gain or measured MRAM result. |
| Snowball v1, 2026 preprint, full HTML | FPGA architecture with bit planes, dual matrix layouts, incremental fields and an MCMC engine | Authors report an 8x time-to-solution improvement on the stated benchmark comparison. Not a universal gain, an MRAM result, or our refresh contribution. |

Primary URLs:
- https://experts.illinois.edu/en/publications/compute-sndr-boosted-22-nm-mram-based-in-memory-computing-macro-u/
- https://ieeexplore.ieee.org/abstract/document/11672681
- https://arxiv.org/abs/2609.00421
- https://arxiv.org/html/2601.21058v1
- https://www.princeton.edu/~nverma/VermaLabSite/Publications/2022/ZhangDeavilleVerma_DAC2022.pdf (channel-shuffling comparator, indexed method passage)

## Choice gate and intended report outcome

Before a large campaign, freeze for each surviving candidate:
1. Inputs, outputs, executable algorithm/control rule and a concrete decision differing from the closest method.
2. A physical residual that remains after strong correction, with ideal-wire and settled/transient controls.
3. A small paired comparison against the strongest cheap applicable alternative, including cost.
4. Task-quality budget and minimum practically worthwhile benefit, chosen before final evaluation; no numerical threshold or gain is invented here.
5. A rejection rule. A failed method is not automatically renamed a successful characterization project.

A successful report would present the new controller, mapper or field-maintenance algorithm, its distinct mechanism and implementation, and the evidence supporting a bounded benefit. Circuit characterization and a validated surrogate are supporting infrastructure. An alternative analytical-only contribution would require a separately agreed, nontrivial derivation with predictive usefulness beyond known laws.

Current prioritization is unchanged: F3 is the primary bounded method investigation, the spatial hypothesis is the first physical mechanism screen, and F7 is conditional. This note neither reruns nor interprets unseen NUS outputs, introduces target-array performance, nor changes LaTeX/report claims.
