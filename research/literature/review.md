# Literature audit and implications for experiment selection

Review date: 3 November 2026. Thirty source records are in `evidence.json`, with exact
URLs, titles, access depth and limitations. This is a targeted decision review, not an
exhaustive systematic review, patent examination or proof that a residual gap is untouched.
No candidate currently has an originality pass.

## 1. What changed in this review

The earlier discussion over-emphasized sector mapping. The new structure keeps seven
families at comparable definition depth. The most consequential additional comparators
are **statistical error compensation for MRAM wiring effects [S29]**, **bidirectional
conversion skipping [S28]**, and **bounded confidence-based early termination [S30]**.
These strengthen the comparison rather than automatically eliminating every narrower idea.

The former repository bibliography already contained relevant leads. Its empirical results
remain archived; its public-paper leads were independently followed where accessible.
The new report does not inherit the former experimental unit, numerical failure regime,
or assumed read-current law as evidence about the target.

## 2. Closest-method matrix

| Family | Closest work already provides | Residual question that must earn a contribution |
|---|---|---|
| F1 estimator | Macro-level hardware calibration [S08]; precision analysis [S09]; semi-analytical fault propagation [S10]; probability-region bounds [S11] | A specific circuit-derived representation that preserves relevant joint errors and wins on total prediction cost |
| F2 encoding | Complement reconstruction disclosure [S20]; activity-based inversion [S21]; mapping/calibration [S06]; fault-aware MRAM remapping [S07] | A cheap electrically justified polarity/encoding rule with useful held-out benefit after overhead |
| F3 mapping | Co-zero clustering/permutation [S01]; adaptive MRAM input blocks [S02]; sparsity-aware conversion [S03,S28]; parallelism/splitting optimization [S05] | A circuit-dependent grouping condition plus a mapper that beats the tuned techniques combined |
| F4 decision refinement | Speculation/recovery arithmetic [S13]; error flags and selective recompute [S14]; mixed precision [S12]; confidence stopping [S30] | A valid inexpensive analog-MRAM decision envelope/refinement implementation with task-level savings |
| F5 crossover | Precision/energy tradeoffs [S05,S15]; ADC architecture models [S16]; digital MRAM [S17] | A predictive validated break-even rule or feasible hybrid implementation rather than another parameter sweep |
| F6 information | Intrinsic analog precision limits [S15]; MRAM calibration [S08,S29]; uncertainty detectors [S14] | A useful target-specific identifiability condition and minimum-cost extra observable |
| F7 Ising | Coupling precision and solver effects [S18]; stochastic-MTJ sampling/precision schedules [S19] | Cheap field refinement preserving the intended update; full exact/lazy-sampling comparison still missing |

## 3. Mapping: the broad idea is occupied; the conflict is conditional

S01's v1 CAR groups rows using pairwise co-zero affinity and marginal zero rate, applying
the permutation consistently to inputs and weights. The supplied comparator implements
that rule independently; it does not reproduce training, pruning or the entire architecture.
A naive marginal zero sort is a separate baseline, not a faithful substitute for CAR.
The newest revision could not be retrieved, so absence of a feature in v1 is not a claim
about every later implementation.

S02 explicitly balances activated word lines and read margin using adaptive block sizes
and ADC resolution. Its full implementation was not accessed. Therefore the general
energy-accuracy tension is established, while the exact relationship between static
co-activation mapping and that adaptive controller remains to be checked.

S28 uses input population information for block and element conversion skipping in a
SAR-based design. S03 supplies a hybrid SRAM/MRAM example. A proposed grouping policy
must allow the baseline to exploit activity in conversion too, rather than charging every
baseline read the same worst-case ADC cost.

The physics hypothesis is sharper than 'high fan-in is worse'. For a fixed input,
sum_g m_g=M is invariant, while the number of nonempty reads C changes. Thus mean
executed-read activity is M/C. With c(0)=0, combining positive loads changes expected
count-error cost by c(a+b)-c(a)-c(b). A linear c leaves the expected total unchanged;
a convex c can penalize concentration. A real circuit's c is also pattern-, weight-,
position-, calibration- and timing-dependent. No toy curve establishes this target cost.
Even an additive expected count-error cost does not determine correlated network failure.

Two useful structural bounds precede any circuit claim: C>=ceil(M/R) for R-row groups,
and C<=min(M,256/R). The lower bound permits input-specific perfect packing and is an
offline diagnostic, not an implementable static mapper. Real traces determine how much
opportunity a fixed permutation retains. Known inactive dimensions must be packed/removed
as a trivial control before crediting a sophisticated mapping.

## 4. Calibration and correction can remove the supposed opportunity

S08 models calibrated MRAM macro nonidealities, including channel effects and input-
dependent behaviour. S06 combines physical mapping and ADC calibration. S29 addresses
column mismatch and wire-induced nonlinear distortion using sensing and statistical
compensation. Together they make a deliberately uncalibrated baseline unsuitable.

For a fair test, each mapping receives the same calibration data/tuning budget and may
choose supported references, precision and sample time. A 'conflict' that exists only
because one mapping's ADC settings are frozen is not an intervention advantage. Full
S29 details are needed before calling a baseline a faithful SEC reproduction; a simpler
gain/offset or fitted nonlinear correction must be labelled as an adaptation.

S07's sensitivity-guided relocation targets faults and unreliable regions. It is relevant
mapping prior art, but a fault model is not automatically identical to nominal analog
current-sum distortion. Compare mechanisms instead of rejecting a whole family by title.

## 5. Prediction and decision-directed control remain competitors

S10's single-bit floating-point fault model differs from many simultaneous correlated
bit-plane arithmetic errors. S11 establishes probability-bounding methodology. Neither
alone proves that a particular MRAM estimator is already solved. A new estimator still
needs useful scale and setup/amortization behaviour against a strong sampler on the same
event and hardware model. S22 exposes no public preprint; it is an overlap warning, not
grounds for declaring an unknown algorithm equivalent or eliminating F1.

S13 reshapes arithmetic and uses speculative slices with recovery. S14 flags uncertain
outputs for recomputation. S30 includes a calibrated early-exit controller and a claimed
tail bound in digital SRAM CiM. Its implementation is a close comparison for F4, although
an analog-MRAM error envelope is an additional problem. Check the bound's normalization
and assumptions independently; a preprint theorem is not a certificate for our circuit.
The generic interval-separated argmax rule itself is not the intended invention.

## 6. Array size, physical evidence and fair cost

S23/S24 demonstrate the importance of device contrast, current handling and the readout
architecture in large MRAM computation. A physical 256 x 256 array can legitimately use
row batches, but inactive cells/wires do not disappear. Isolation is an optional circuit
intervention with its own cost. Generic code can be reused; an old small-unit error table
cannot simply become the characterization of the new macro.

S16 provides an architecture-level ADC energy/area estimate and explicitly describes
its trend/lower-envelope limitations. Use it for preliminary sensitivity, then anchor
claims to the actual ADC. S17 establishes digital MRAM as a serious alternative. Compare
useful precision, throughput, capacity, normal sensing and data movement, not incompatible
headline TOPS/W. Repeated conversions, bound logic, control, address permutation, extra
state and offline calibration amortization belong in total cost.

## 7. Information and stochastic-computing branches

S15 establishes an analog-core precision ceiling. A target-specific count-observability
analysis must condition only on economical readout metadata. Providing full inputs and
weights to an unlimited digital computation would already determine the ideal result.
The research opportunity is a useful separation condition and an extra measurement that
beats ordinary calibration or precision increases after its cost is included.

S18/S19 constrain generic Ising precision claims. The same-random-draw field-interval
test is mathematically straightforward; exact and retrospective sampling have wider
precedents. Additional algorithmic reading is a prerequisite to an Ising novelty claim.
Treat this as a separate application choice. S27's expert routing is likewise an
application mechanism, not an independent MRAM sensing contribution.

## 8. Mandatory gaps before a novelty pass

1. Obtain the complete S02 implementation and latest accessible S01 revision.
2. Obtain S29's correction implementation and decide which low-cost adaptation is feasible.
3. Inspect the relevant S03/S04 hardware details before claims about MRAM-specific absence.
4. Verify S20 against the original patent document; no legal novelty conclusion is supplied.
5. For F2, complete position-aware encoding/polarity prior art; ordinary inversion is only a baseline.
6. For F7, complete exact/lazy/refinement sampling comparisons beyond device papers.
7. Define the exact estimator/event model before attempting to compare with S22 or fault-analysis tools.

Full texts unavailable here can be read through legitimate university access. The gap
list is explicit so that an inaccessible method is never treated as if it lacks a feature.

## Search record

The current incremental searches followed combinations of reliability, activation
clustering, mapping, MRAM sparsity, input inversion, conversion skipping, statistical
error compensation and retrospective Gibbs/Bernoulli simulation. Primary publisher,
author and institutional records are retained in `evidence.json`; secondary aggregators
were discovery leads only. Earlier primary-method reads in this conversation are carried
forward with their actual access labels. No paper's reported numerical benefit is adopted
as the benefit of our implementation.

## Focused novelty follow-up, 4 November 2026

The register now includes S31: Crafton et al., ISLPED 2021. Its ADC-code PMFs,
bit-significance-weighted MAE approximation and WL-count LUT were inspected directly.
A renewed S08 Section 3.2 check confirms channel shuffling to randomize deterministic
column errors. The [specific mapping candidate](../novelty/2026-11-04-covariance-mapping.md)
must beat these mechanisms and equal-budget random shuffling; neither correlation nor
bit significance is claimed new. DIB-CIM remains abstract-only, an explicit barrier to
a complete method-equivalence verdict.

## Ising update and persistence follow-up, 4 November

S32 (Snowball IV-B.2) and S33 (pipelined p-computer Sections 3.1-3.2) explicitly maintain initialized local fields incrementally. That identity and row/column access layouts are baselines. S18 was checked through primary indexed introduction/method-summary passages, but direct full text remains blocked. The register now has 33 sources. The [revision-15 review](../reviews/2026-11-04-claude-revision15.md) separates fixed manufacturing variation, actual temporal read noise, a matched-law counterfactual and cache drift. No fresh-versus-frozen target result or corresponding novelty pass is established.
