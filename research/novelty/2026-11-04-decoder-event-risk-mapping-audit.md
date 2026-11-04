# DIB-CIM audit and a specific mapping/predictor contribution
4 November 2026, Singapore. Research-discovery record.

**Proposed claim:** use the probability mass of the ADC events that a row swap can
change to reject mapping candidates that cannot improve the incumbent reliability.
For remaining candidates, evaluate classification risk only on affected event
intervals. Retain the same persistent physical variation when comparing mappings.

**Status:** a precise algorithm, conditional proof, implemented event estimator,
a resident-mapping prototype and executed mathematical checks. No literature-wide
originality pass, no MNIST result, no GF read-model validation and no demonstrated
total-cost advantage yet.

This is F3 mapping supported by F1 prediction, not a new top-level direction.
The aim is to arrive at the supervisor discussion with an explicit method and
prior-art comparison. The supervisor is not being asked to invent the novelty.

## 1. What DIB-CIM verifiably does

Chen et al., IEEE TCAS-I, online 31 August 2026, DOI
10.1109/TCSI.2026.3726936, 14 pages.

The publisher abstract states:
- SOT-MRAM analog CIM in a 28-nm, 128x128 architecture.
- Dynamic input blocks adjust activated word lines based on effective input-bit
  significance and the 0/1 input distribution.
- Leading effective bit detection (LEBD), input data distribution detection (I3D),
  zero-skipping and a dynamic-resolution ADC are combined.
- The stated goal is an energy/accuracy trade-off without weight retraining.

**Access depth is abstract only.** The IEEE abstract is indexed, but the stamp/PDF
and ielx8 endpoints failed. Searches for an author manuscript and the connected
file collection did not locate the paper itself. The survey PDFs are secondary
project records, not substitutes for the primary method section.

Unknown: exact supported block sizes, decision thresholds, LUT contents, treatment
of spatial order, correlation, calibration and any mapping preprocessing. We cannot
claim DIB-CIM lacks a feature just because its abstract does not mention it.

Consequently, the code in this package is **not a DIB reproduction**, and its
input-count/significance controls are not presented as measured DIB performance.
A copy of the full PDF obtained through university access is needed to complete
the DIB-specific method-equivalence audit.

Primary publisher record:
https://ieeexplore.ieee.org/abstract/document/11672681

## 2. Broad ideas that are already occupied

| Work | Established mechanism | Access used here | Specific issue to compare |
|---|---|---|---|
| DIB-CIM, 2026 | Input-driven WL/block and ADC resource allocation | Publisher abstract | Full control policy still missing; proposed contribution concerns offline candidate evaluation |
| VARA v1, 2026 | Co-zero activation clustering and consistent row/weight permutation | Primary Section 3.3 / Algorithm 1 record | Reordering itself and read skipping are existing; proposed screening objective is class-failure risk |
| Crafton et al., ISLPED 2021 | ADC-code probabilities, significance-weighted arithmetic error and WL-count LUT optimization | Author PDF Section III | Joint persistent decoder events and class failure differ from its marginal/aggregate error approximation |
| Dyn-A-Map, 2026 | VIS/FOW sensitivity and fault-region-guided weight relocation | Primary abstract and previously indexed method passages | Generic sensitivity-aware MRAM mapping is occupied; the proposal targets decoded analog-event changes, not only hard faults |
| U-SWIM, 2024 | Second-derivative-guided selective write verification | Publisher abstract | Generic importance/sensitivity weighting is occupied |
| Awano and Sato, DAC 2016 | Line sampling for transistor-level yield analysis | Author/institutional method record | Conditional probability integration is not claimed as invented here |
| Boetius et al., ICML 2025 | Neural-network probability bounds with branch and bound | Primary PMLR record | Bounding and pruning are established; proposed bound screens design candidates through changed ADC events |
| Small-Noise is All You Need, 2026 | Public description of a fast CIM accuracy-loss estimator | Author project page only | Preprint not public; method-level overlap is unresolved |

The contribution cannot be “use margins,” “preserve correlation,” “apply line
sampling,” or “use branch and bound.” The narrower object to investigate is the
ADC-event influence construction and its safe, cost-effective use inside resident
row-permutation search.

Sources:
- VARA: https://arxiv.org/html/2609.00421v1
- Crafton: https://bpb-us-e1.wpmucdn.com/sites.gatech.edu/dist/e/220/files/2021/08/Crafton_ISLPED_2021.pdf
- Dyn-A-Map: https://www.nature.com/articles/s44335-026-00072-6
- U-SWIM: https://doi.org/10.1109/TCAD.2024.3352496
- Line sampling institutional record: https://www.pass.cce.i.kyoto-u.ac.jp/?lang=en&p=3742
- Probabilistic verification: https://proceedings.mlr.press/v267/boetius25a.html
- Small-Noise project: https://tanner-andrulis.github.io/posts/2026_small_noise/

## 3. The exact new decision being proposed

Ordinary candidate evaluation:
1. Generate a legal row swap.
2. Re-evaluate its complete noisy inference probability.
3. Compare with the current best mapping.

Proposed candidate evaluation:
1. Determine which read/decoder functions the legal resident swap changes.
2. Construct the physical-variation regions where those decoded results could
   change the reconstructed class margins.
3. Bound how much failure probability can change using only the mass of those
   regions.
4. Skip a candidate if even its maximum possible improvement cannot beat the
   incumbent.
5. For survivors, recompute failure only on those regions.

**This changes an optimizer's evaluation decision.** It does not replace the
network, invent a new spin-update law, or merely rename activity-based splitting.

## 4. Conditional event representation

For a fixed input and a fixed physical-factor slice, let read r be

    I_r(t) = alpha_r + beta_r t,

after declared normalization/calibration. Its integer decoder clips to the exact
logical support [l_r,u_r]. Its only transitions occur at

    t_(r,k) = (k+1/2-alpha_r)/beta_r.

Enumerate and sort those transitions. Between consecutive events, every decoded
count is fixed, so the reconstructed final-layer margin vector is fixed. With
factor CDF F, integrate failure by adding F(b)-F(a) over failing intervals.

No Gaussian approximation is made to the decoded output or class margin. The
same factor t drives all reads; it is not redrawn per bit cycle or output.
This handles negative and zero slopes, repeated events, clipping and multiple
disjoint failure intervals.

The current implementation is exact along the declared scalar factor for a fixed
affine output head. It is not an exact full-network, arbitrary-dimensional device
estimator. A higher-dimensional extension must condition on the remaining
persistent physical factors, preserve the same physical coordinate system across
candidate mappings and charge the outer-sampling cost. Sample-average bounds
would certify that sample-average objective, not automatically population risk.

The elementary CDF integration and conditional Monte Carlo/line-sampling
principles are established mathematics. They are supporting tools.

## 5. The influence bound and proof

Let pi be the current map and pi' a candidate. Couple both on the **same physical
variation realization** xi and input n. Write their class-failure indicators as
f_pi and f_pi'. Define D(pi,pi') as the region where the changed decoded reads
alter any reconstructed class margin.

Outside D, all class margins are identical, so the failure indicators are identical.
Therefore

    |R(pi') - R(pi)| <= P[D(pi,pi')] = B(pi,pi').

This is a direct application of the usual coupling bound, not a claim to have
invented a new probability inequality.

For the scalar event representation, D is a finite union of intervals determined
by the old/new thresholds of the changed reads. Its probability mass can be
computed without evaluating the complete old/new classifier over all intervals.
Signed reconstruction is used: changes that cancel in every class margin are
excluded from D.

If the current best candidate has risk R_best, then

    R(pi') >= max(0, R(pi)-B(pi,pi')).

If that lower bound exceeds R_best, pi' cannot win and can be discarded. Surviving
candidates are scored only inside D using cached original margins.

This pruning is safe for the declared model and search objective when all affected
reads are included, factor coupling is correct, bounds are conservative, and
numerical error is guarded. It is not a certificate that an unvalidated surrogate
matches a real chip.

## 6. Implemented mapper and controls

The supplied code includes:
- a vectorized full event sweep and an independently checked incremental update;
- exact risk and exact margin moments under the same model;
- influence-interval construction, probability bound and localized risk query;
- incumbent-based candidate pruning;
- a resident row-mapping prototype, with one map shared across both outputs;
- an equal-search-size comparison of exact risk, Gaussian exact-margin moments
  and exact output MSE;
- a faster vectorized full-rebuild baseline, not only a Python-loop comparator.

All examples are explicitly constructed, not measured MRAM or MNIST. The model
uses a persistent, bounded scalar row-response mode. Its positive conductances
can be written g_AP=1 and g_P=2 times a row-dependent gain. Replication makes the
largest gain deviation 4.375% across 256 positions. That is a mathematical
construction, not a characterization of the authorized GF access transistor.

The mirrored response mode makes zero/full-column affine calibration insensitive
to this particular residual. Stronger mask-conditioned calibration and target
SEC-style correction remain required competitors.

## 7. Executed results, including the outcomes against us

### A. A necessary distinction from moment scoring

Two resident permutations use identical active-row count, weight popcounts,
ideal counts and read budget. Ideal class margin is 0.5.

| Map | Exact failure probability | Exact margin-error MSE | Gaussian score using exact mean/variance |
|---|---:|---:|---:|
| A | 0.0262338683 | 0.2098709460 | 0.1375429878 |
| B | 0.0747023548 | 0.1494047095 | 0.0979080630 |

The Gaussian score ranks B above A despite the higher actual failure probability.
Exact event integration agrees with an independent closed-form calculation and
200,000 direct persistent-factor draws.

**Important control:** ordinary output MSE selects A in this particular
counterexample too. It is not evidence that the event mapper defeats every baseline.

### B. A small held-out mapping test

64 synthetic boundary-conditioned CAL masks and 128 independently generated DEV
masks, two greedy iterations, all 28 mirrored atom swaps per iteration, 57
candidate evaluations per method. Read budgets are identical.

| Selection score | DEV exact failure probability |
|---|---:|
| Event risk | 0.0058053862 |
| Gaussian using exact margin moments | 0.0058053862 |
| Exact output MSE | 0.0126409362 |

The event method and Gaussian score select the **same mapping**. This test
supports optimizing task reliability rather than output MSE in this model, but it
does not establish incremental value over the strong moment-based selector.

These inputs were deliberately conditioned to equal ideal class counts. The
numbers are not representative MNIST accuracy or a general failure-rate estimate.

### C. The tempting speed claim that did not survive

A cached full-table update was several times faster than a loop-based full
rebuild. After implementing a vectorized full-score baseline, this advantage
disappeared. In the final recorded run:

- vectorized full score: approximately 0.516 ms;
- cached whole-table update: approximately 0.555 ms.

Do not report the earlier 6x-7x ratio as a useful strong-baseline speedup. The
archive preserves the earlier implementation and its comparison.

### D. The safe-pruning mechanism works, but cost still matters

In a constructed pool containing one alternative initial map and 80 random
distinct-weight mirrored row swaps:
- 71 of 81 candidates were skipped without classification-risk evaluation;
- 10 received localized risk evaluation;
- the selected risk exactly matched exhaustive evaluation;
- every skipped candidate was checked afterward and none could beat the winner.

However, bound calculation plus localized scoring took approximately 20.0 ms,
while vectorized exhaustive scoring took approximately 10.5 ms in this tiny
two-read case. Thus **fewer complete evaluations did not produce a speedup**.

This is a valid mechanism demonstration and a negative total-cost result.
It may become useful when full candidate evaluation is expensive and influence
regions are small, but that condition has not been established on the real workload.

### E. Arithmetic/implementation checks

Sixty signed, multi-margin perturbation cases compare full reconstruction,
cached updates and influence-only evaluation. They include changed means,
supports, coefficients, negative/zero slopes and shared threshold locations.
Reported probability differences are zero at the checked precision, and all
influence bounds contain the actual risk change.

No speculative hardware simulation, training run, or hidden test-set access
was performed.

## 8. Relationship to the complementary-read proposal

The separate complementary-read certificate derives count intervals from
one-sided cell-current limits and column-popcount conservation. Its proof does
not validate the event estimator or establish mapping performance.

For this candidate, do not add a complementary read to every runtime operation.
Use exact feasible-count support in the decoder and treat the physical
certificate as a separate calibration/validation or control comparator where
appropriate.

An unsuccessful complementary **point calibration** is not the same algorithm
as a valid interval construction. Equally, a valid interval construction is not
proof of a novel or economical mapping method. Do not combine unproven gains.

## 9. What can be said to Prof Fong now

Proposed contribution:

    A decision-risk-aware MRAM row mapper that safely eliminates candidate swaps
    using the probability mass of changed ADC decoding events, retaining persistent
    cross-read error coupling, and evaluates surviving candidates only on affected
    class-margin intervals.

Present this as a specific research method under development. We have a
conditional proof and functioning prototype, not a validated final thesis
contribution. The current cost test and strongest selector comparison still
prevent a competitive-performance pass.

The next concrete literature action is to read DIB-CIM's full controller and
compare it line by line. The next implementation objective is to make the bound
cheap enough to justify screening, rather than expanding arbitrary noise sweeps.

The primary missing paper is the DIB-CIM PDF. The local E01 download available
in the connected collection contains an older digits256 example, not the frozen
MNIST packet; the E03S archive contains scripts/results but not its source data.
Neither was silently substituted for the required MNIST workload.

## 10. Reproduction

From the branch root, with NumPy and SciPy installed:

    python research/software/decoder_event_mapping_probe.py \
      --out experiments/results/decoder_event_probe_independent_repeat

The output directory must not already exist. The JSON records source hashes,
fixed synthetic seeds and data hashes, all comparator results and limitations.
No Cadence or licensed model file is required.

Frozen executed source SHA256:
134a85464e530a98663fc5e74cc5100d6d19f12fb98d758a0f15679943b415af

Results:
experiments/results/decoder_event_probe_20261104_influence/results.json

