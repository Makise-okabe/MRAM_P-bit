# A precise novelty candidate: mapping decoded error covariance

4 November 2026 (Singapore). Development priority within F3; not a selected final topic
or a novelty certification. The new uploaded reassessment is identified by SHA256
`2b74d3605f257f311cd78f69e13b5aa8a6b015ea9c0c918a2bc1fc0c234dd984`.

## The contribution we would try to establish

Develop one deployable row mapping that controls the covariance of decoded errors across
bit-serial reads, subject to a declared read/resource budget. The method should preserve
sparsity savings when available and avoid concentrating error events that reinforce each
other during signed shift-and-add reconstruction.

The narrower hypothesis is: **mappings with equal executed-read counts and equal
per-read error distributions can have different reconstructed arithmetic errors, even
after scalar group calibration; a mapper retaining cross-read covariance can distinguish
them.** This is more specific than adding reliability to a generic energy objective.
The same physical cells being reused across cycles is an established mechanism already
raised in Claude's estimator. We do not claim its discovery. The present development is
a mapping intervention, a calibrated counterexample, and a prospective method specification.

No exact prior-art match was established in the targeted searches, but that is not proof
of absence. Full DIB-CIM implementation access and a broader correlation-aware mapping
check remain necessary. Statistical covariance formulas and local search are established
tools; novelty must be in the useful mechanism, grouping rule and implementation beyond
the closest methods, demonstrated under the target constraints.

## What the closest methods already supply

| Source and checked access | Existing mechanism | Difference to establish |
|---|---|---|
| VARA v1, Section 3.3 and Algorithm 1 | Greedy grouping using zero rates and co-zero affinity across input dimensions | A decoder-error cross-cycle score can rank mappings differently from that affinity; correlation in inputs and correlation in decoded errors are distinct objects |
| DIB-CIM, publisher abstract only | Dynamic WL block sizes, effective input-bit significance, input 0/1 distribution, zero-skipping and ADC resolution | Does its full controller or grouping already exploit joint decoded-error events across bit cycles? Unresolved; do not infer absence from its abstract |
| Crafton et al., ISLPED 2021, Sections II-III | Device-calibrated ADC-code PMFs, per-binary-VMM MAE, bit-significance-weighted aggregate MAE approximation, optimized WL-count LUT | Pairwise decoded-error terms under fixed mismatch enter an exact second-moment objective; its existing MAE approximation remains a legitimate comparator and can be conservative |
| Dyn-A-Map, publisher method passages | VIS/FOW fault sensitivity and relocation away from injected-bit-flip regions | The proposed score concerns joint analog-decoder events from reused cells, rather than merely assigning important weights to less faulty regions |
| Zhang/Deaville/Verma, DAC 2022, Section 3.2 | Macro-level calibrated statistics and channel shuffling of partial computations to randomize deterministic column errors | Decorrelation itself is already a mitigation. Establish a useful decoder/overlap-dependent grouping rule at the same capacity, routing and read budget beyond ordinary randomized shuffling |

Primary links: [VARA](https://arxiv.org/html/2609.00421v1),
[DIB-CIM](https://ieeexplore.ieee.org/abstract/document/11672681),
[Crafton et al. author PDF](https://bpb-us-e1.wpmucdn.com/sites.gatech.edu/dist/e/220/files/2021/08/Crafton_ISLPED_2021.pdf),
[Dyn-A-Map](https://www.nature.com/articles/s44335-026-00072-6),
[Zhang et al. author PDF](https://www.princeton.edu/~nverma/VermaLabSite/Publications/2022/ZhangDeavilleVerma_DAC2022.pdf).

Consequently, neither persistent correlations nor randomizing deterministic errors is
claimed new. The residual method must outperform simple random shuffling, including the
best map found under an equal offline search budget, while accounting for skip savings
and practical routing/weight placement. The constructed witness alone does not do that.

The literature can defeat this proposal in two ways: a closest method may already make
the same grouping decision for the same reason, or a tuned applicable baseline may reach
the same practical frontier without this score. Neither outcome should be relabelled
as an original method contribution.

## Precise score and mapper specification

Let read r have signed reconstruction coefficient b_r and decoded integer error e_r.
For a fixed input, output column and mapping pi,

    delta_y = sum_r b_r e_r
    R(pi) = E[delta_y^2]
          = (b^T mu_e)^2 + b^T Sigma_e b.

This identity is exact whenever the required second moments exist. It includes bias and
all pairwise covariance terms; it does not require the joint distribution to truncate at
pairs. Second moments suffice for MSE, not for a complete output PMF or neural failure
probability. Signed weight-plane coefficients must retain their negative signs.

For a validated conditional Gaussian current model, represent the persistent variation
as theta and read perturbations as Y=A_pi theta after the declared calibration. The
current covariance is A_pi Cov(theta) A_pi^T. Integrating actual decoder intervals gives
the marginal means and pair moments of e. Shared reference/supply factors must be
conditioned on and integrated, or retained explicitly; they are not assumed independent
columns or groups. An empirical paired-read estimate is an alternative when affordable.

The proposed offline algorithm is:

1. Freeze calibration traces, weight arrays, group hardware, decoder, calibration budget
   and resource limit. Fit one row permutation across all input planes sharing the
   resident array, with the corresponding weight permutation.
2. Initialize from CAR, simple zero-rate sorting and balanced orderings. Retain every
   baseline's tuned operating point and compare total frontiers.
3. Evaluate bounded cross-group swaps and, when useful, two-for-two exchanges. Recompute
   the changed reads' means and pair moments. Cache reusable decoder integrations.
   Under independent groups only their local costs change; with shared factors all
   incident cross-group covariance terms must also be updated.
4. Minimize calibration-averaged reconstructed MSE subject to the frozen resource
   budget, or minimize resources under a frozen MSE constraint. Initially resources are
   executed reads; energy may replace that proxy only with validated costs. Include
   overhead and preprocessing runtime in the comparison. No global-optimum claim.
5. Freeze the mapper and all tuning; evaluate new inputs and independent persistent
   variation assignments. Then check task-level benefit. An MSE improvement alone
   establishes neither an inference benefit nor an energy saving.

The covariance-aware score and two-map ranker are implemented in the mathematical probe.
The general local-search mapper and target response model are not implemented yet.

## A counterexample already checked

**Evidence class: constructed normalized model, not target circuit validation.**
No retired trial measurements, GF parameters, RC model or neural accuracy results enter
this example. Storage bookkeeping uses 256 rows by 256 nonconstant binary weight columns.
There are four prospective 64-row read groups and two active input bit planes with
coefficients 1 and 2. This does not validate physical 64-row parallel reading.

Each 128-row half contains four input categories: A=11 on 16 rows, B=01 on 16 rows,
C=10 on 16 rows and D=00 on 80 rows. Every 8-row construction chunk contains four high-
and four low-conductance weight bits in every column, randomly ordered. This balancing
is a proof fixture, not an optimization or a real trace claim.

The concentrated-overlap arrangement uses groups A16+D48 and B16+C16+D32. The balanced
arrangement uses A8+B8+C8+D40 in each group. Repeat for the other 128 rows. Both policies
therefore have, for every column and every executed read:

- 16 active rows, including eight high-current and eight low-current cells;
- the same ideal count, current mean, current variance and marginal count-error law;
- eight executed vector reads in total, the same capacity and exact ideal output.

Normalized cell means are 1 and 2, with assumed independent 3% Gaussian multiplicative
cell-current variation frozen across reads. These are declared illustration parameters,
not a characterization of the target technology. Each group receives its true full-group
current deviation as calibration information. Subtracting one quarter of that deviation
is the exact Gaussian conditional-mean correction for this balanced fixture. Nominal
count thresholds are centered ideally; there is no extra ADC quantization or deliberately
misplaced reference. The finite decoder clips to feasible counts 0..16.

After this calibration, within-group analog correlations across the two cycles are

    concentrated: [1, -1/3, 1, -1/3]
    balanced:     [1/3, 1/3, 1/3, 1/3].

Let v be the decoded count-error variance and c(rho) its covariance at analog correlation
rho. Independent groups then give

    MSE_concentrated = 28v - 8c(1/3)
    MSE_balanced     = 20v + 16c(1/3)
    difference      = 8[v - 3c(1/3)].

For a centered odd quantizer of jointly Gaussian variables, its normalized Hermite
expansion has only odd orders. Hence c(rho)=sum_n a_n^2 rho^n and
v-3c(1/3)=sum_odd_n a_n^2[1-3^(1-n)]. The first-order term cancels; higher odd terms are
nonnegative and some are positive for this non-linear quantizer. This proves a strict
difference for the constructed case. The expansion and Gaussian moment calculations
are standard mathematics, not an asserted new general theorem.

The continuous-readout control is critical: c(rho)=v*rho makes the difference zero.
Indeed both mappings have continuous reconstructed MSE 0.684 in the probe. The effect
comes from non-linear decoding combined with reuse, not a generic claim that rearranging
iid linear device error always improves arithmetic.

| Quantity | Concentrated overlap | Balanced overlap |
|---|---:|---:|
| Executed vector reads | 8 | 8 |
| Active rows per read | 16 | 16 |
| Marginal decoded count-error probability | 0.2343078% | 0.2343078% |
| Analytic reconstructed MSE, normalized integer units squared | 0.0652216 | 0.0476307 |
| Continuous-readout reconstructed MSE | 0.684 | 0.684 |

The analytic MSE reduction is 26.97%. Analytic identities and moments were checked on
all 256 columns. Monte Carlo checked one predeclared column with three predeclared seeds,
131,072 independent Gaussian variation assignments each. Both mappings share each
assignment, and every bit cycle reuses it. The observed MSE reductions under conditional-
mean calibration were 24.47%, 27.88% and 26.55%. All paired difference intervals exclude
zero using per-assignment standard errors.

A separate full-group multiplicative gain correction also retained reductions of 24.95%,
27.99% and 26.02% across those seeds. The linear-Gaussian closed-form values above apply
to conditional-mean correction; do not label them exact results for the gain ratio.

The configuration was written before the first execution. These results are one
constructed setting, not a representative benchmark, a fitted mapper, a published-
method reproduction or a target reliability rate. The example does not demonstrate that
CAR, adaptive blocks or exhaustive tuned calibration are dominated. In particular an
unlimited lookup table containing this very input could bypass the example entirely;
the information and calibration budget must be fixed in any real comparison.

## Reproduction and evidence

- [Frozen configuration](../../experiments/config/covariance_math_probe.json)
- [Probability calculation and two-map ranker](../../experiments/covariance_math_probe.py)
- [Curated result, full provenance and uncertainty](../../experiments/results/E03M_20261104_covariance.json)

Run from the repository root with numpy and scipy installed:

```sh
OPENBLAS_NUM_THREADS=1 python3 -m experiments.covariance_math_probe \
  --config experiments/config/covariance_math_probe.json \
  --out experiments/runs/E03M_new_name/probe.json
```

The script refuses overwrite. It records code/config/weight hashes, exact command,
environment and UTC timestamps. The raw first run is
`experiments/runs/E03M_20261104_covariance/probe.json`; the curated copy is byte-identical.

## What would earn the remaining passes?

1. **Prior-art difference:** obtain full DIB-CIM; check decoder-correlation-aware mapping,
   calibrated CIM statistical models and related fault-tolerant groupers. Build a
   same-information-budget implementation comparison. A title or abstract cannot close it.
2. **Physical case:** in the declared physical 256x256 topology, compare input-mask pairs
   with matched activity/count and different shared-cell overlap after equal calibration.
   Validate the observed decoded pair covariance, including common drivers/references,
   not merely a current RMSE. E02 still precedes a target E03 claim.
3. **Useful method:** fit one mapping on real pooled bit-plane traces. Compare tuned CAR
   plus adaptive blocks/references, balancing, calibrated direct reading, covariance-
   ablated scoring and a simulation-scored search under matched search budgets. Include
   simple inactive-feature packing, equal-budget random shuffling/channel-shuffling
   adaptations and any per-chip correction with equal calibration cost.
   Evaluate new inputs/chips and the real resource-quality frontier.

Stop if the calibrated covariance is negligible, the strongest baseline removes the
gain, the optimized map overfits, hardware/routing costs dominate or a prior method
already supplies the same mechanism and decision. No large evaluation campaign follows
automatically from this mathematical result.
