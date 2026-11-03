# Review of the Claude/Yanzhang field survey

Reviewed on 3 November 2026. This is a source review, not a circuit or inference run.
Source identity and access notes are in
[the source record](2026-11-03-claude-field-survey.source.json).
All 46 pages were read; selected tables and algorithm pages were also inspected visually.

## What this document changes

The document supplies a longer research history, a more specific estimator algorithm,
and additional circuit-level alternatives. Its latest mapping recommendation overlaps
the already recorded F3 candidate. It does not establish a target-array benefit or select
a core contribution. The current E01/E02 entry gates remain appropriate.

The document contains successive, partly conflicting recommendations. Page 1 is revision
14; pages 3-5 describe revision 12; pages 23-24 and 30 retain older circuit-first advice.
Treat these as stages of deliberation, not simultaneous decisions or new supervisor
instructions. Its header date does not establish the date of every revision.

The source's reported demonstrations remain external, unreproduced illustrative-model
results. The source code, seeds, raw outcomes and complete tuning protocol were not
provided with this upload. Retired trial measurements are excluded from the fresh
physical 256 x 256 project's calibration, validation and motivation. Their numbers are
not transcribed here or into the report.

## Crosswalk and additional leads

| Source material | Existing place or additional lead | Consequence |
|---|---|---|
| Activity clustering versus read reliability, pp. 1-2 | D12-D14 / F3 / E01-E03 | Concrete hypothesis; repeat on the target architecture with tuned comparators |
| Column-correlated discrete estimator, pp. 3-5 | D01-D03 / F1 / E06 | Audit the actual joint distribution, approximations and cost before a port |
| Calibration under a characterization budget, pp. 20-21 | Narrower D05, supporting F1/F6 | Distinguish limited calibration information from unrestricted per-array fitting |
| Access-transistor size, read bias and sensing co-design, pp. 23-24 | Additional circuit reserve R01, related to F5/F6 | Potential design contribution only with a derived rule or new implementation and a strong comparator |
| Read stress and weight-reload cost, pp. 21-25 | Additional device-operation reserve R02 | Needs credible switching/read-disturb parameters and CIM conditions; no dynamic-model campaign authorized by this review |
| Retention/startup and bursty inference, pp. 22-24 | D15 / F5 / E07, deployment extension | Requires trusted startup, calibration and reload costs |
| Weight-leakage/security and CAM search, pp. 23-24 | Additional out-of-core leads R03 and R04 | Preserve in the idea history; no new experimental branch launched |
| Local-field errors and decision refinement, pp. 25-29 | D17-D18 / F7 / E09 | Separate application choice; do not append it automatically to inference |

R01-R04 are supplemental leads, not selected method cards or additions to the 21 active
idea IDs. Mapping, estimator and circuit alternatives remain competitors. Broad prior
work in security or CAM does not prove every narrower idea impossible; neither area
currently supplies a specific new mechanism for this project's core.

## Audit 1: activity concentration is a mechanism, not the whole proof

With fixed total activity M and C executed nonempty groups, mean activity per executed
read is M/C. Reducing C concentrates activity. It does not alone establish increased
total count error, reconstructed-output error or inference failure.

For an illustrative additive expected error-count cost c(m), merging two nonempty groups
changes that cost by c(a+b)-c(a)-c(b). A linear c leaves total expected error count
unchanged; a convex c with c(0)=0 can penalize concentration. The target cost may also
depend on weights, position, calibration, timing and common variation. Signed bit-plane
reconstruction and the classifier introduce further dependencies.

Consequently E03 must measure the relevant shape and task effect after tuning the
baseline's references and readout. A physical array with row batching is a legitimate
starting architecture. Batching does not remove its wire, driver or shared-line loads,
and a logical collection of smaller reads does not validate that architecture.

## Audit 2: what is exact in the estimator?

The source retains frozen cell variation across input bit cycles, an appropriate physical
mechanism to investigate. However, the proposed algorithm truncates joint events at
pairs. Its downstream convolution can be exact for its approximate input PMF without
making the complete estimator exact.

In a declared linear Gaussian model, let theta be the persistent cell-variation vector
and let Y=A theta be the vector of analog perturbations for one column's reads. Then
Cov(Y)=A Cov(theta) A^T. For decoded errors e_t=d_t(I_nom,t+Y_t)-s_t and signed bit
coefficients beta_t, the needed column variable is S=sum_t beta_t e_t. Its PMF requires
the probabilities of joint decoder regions under Y. Gaussian tails at single boundaries
and bivariate crossing probabilities are ingredients, not a complete description of S
after truncation.

Pairwise event statistics alone do not generally determine a weighted sum's distribution.
For example, independent fair bits B1,B2,B3 and the distribution B3=B1 XOR B2 have
identical one- and two-bit marginals, but different distributions of B1+2B2+4B3. This is
a mathematical counterexample, not an MRAM simulation or a counterexample to a fully
specified multivariate Gaussian model. A full Gaussian covariance matrix does specify
that model; replacing its higher-order decoder events by pairwise terms is the step
requiring validation or a bound.

Before implementation, specify:

1. The physical current law and whether its Gaussian approximation is linearized or exact
   after a monotone change of threshold. Include both decoder boundaries and multi-step
   errors where their probability is material.
2. The construction of a normalized, nonnegative joint/column PMF, with the omitted
   higher-order probability or an empirical truncation error and validity region.
3. Which columns are independent. Shared reference, supply, driver and spatial variation
   can require conditioning on common latent variables before convolution.
4. The network boundary. Independent hidden-neuron errors with an ideal final linear
   layer allow each class margin to use differences of output weights directly. Different
   output logits still share hidden errors; deeper perturbed layers need additional joint
   reasoning. The simplified demonstration does not establish that generalization.
5. Whether the output is a point estimate or bounds. For class events E_j, max_j P(E_j)
   <= P(union_j E_j) <= min(1,sum_j P(E_j)). Report the interval width; do not score an
   upper bound as if it were an unbiased point predictor.

These are reasons to audit F1, not reasons to discard it. An inaccessible submission
title does not establish method equivalence. A comparison should include calibrated
sampling methods preserving the same persistent variation, not only independent Gaussian
and independent discrete approximations. Include setup, fitting, memory and requested
numerical precision in total cost.

## Audit 3: statistical evidence in the demonstration

Selecting examples because a pilot observed failures is useful for stress testing, but
does not estimate performance on an ordinary held-out image population. Separate the
stress set from a representative evaluation set. Report the selection mechanism and
independent chip identities, plus uncertainty for every failure-probability comparison.

No observed failures does not establish zero probability or a false alarm by a predictor
returning a small positive probability. Under independent Bernoulli chip trials, the exact
one-sided 95% upper bound after zero failures in N trials is 1-0.05^(1/N). For N=20,000
this is about 1.50e-4 for that individual event. Multiple selected images require the
appropriate additional care. This calculation checks the reported statistical language;
it is not a new target-array result.

The source's rare-event speed comparison is useful preliminary evidence about its own
implementation only. Constant-cost distribution propagation may still depend strongly
on dimensionality, tail accuracy, numerical quadrature and the number of boundary events.
E06 must compare methods at the same event, population and accuracy requirement.

## Audit 4: broad literature verdicts and the circuit alternative

The source is right to require a specific difference from prior art. Statements that an
entire problem family is solved, or that transistor-level work is the only remaining
opening, go beyond the evidence described.

Two primary-source checks were made during this review:

- Jacob et al., JXCDC 2023, DOI 10.1109/JXCDC.2023.3258431: the author PDF's Section II
  derives the familiar row bound using independent zero-mean Gaussian mismatch and a
  half-LSB versus three-sigma criterion. It is a useful conditional dynamic-range baseline,
  not a universal neural-accuracy or physical-array theorem. The paper's proposed
  architecture uses local magnetic-to-digital sensing and capacitor accumulation; that
  implementation boundary matters when comparing with direct current summation.
  [Author PDF](https://nanocad.ee.ucla.edu/wp-content/papercite-data/pdf/j73.pdf).
- Roy and Shanbhag, JXCDC 2024, DOI 10.1109/JXCDC.2024.3381888: the institutional abstract
  describes an SNDR/energy analysis incorporating conductance variation, wire parasitics,
  current-mirror mismatch and ADC noise, with validation against an MRAM prototype. This
  is an essential comparator to any generic energy-accuracy co-design claim. The full
  derivation was not read in this review, so equivalence to R01 is unresolved.
  [Institutional record](https://experts.illinois.edu/en/publications/energy-accuracy-trade-offs-for-resistive-in-memory-computing-arch/).

Counting Cards' arXiv abstract was also checked. It explicitly combines device variance
and weight distributions under an error tolerance. Its full text could not be retrieved
in this pass; do not certify the source's precise comparison table from the abstract.
[Primary abstract](https://arxiv.org/abs/2006.03117).

The access-transistor/read-bias alternative deserves preservation: cell contrast,
variation, charging cost and useful parallelism can trade against each other. But an
optimum found using assumed mismatch coefficients is an illustrative desk result. A
generic parameter sweep in a real PDK does not itself establish novelty. R01 would need
an explicit rule, mechanism or implementation absent from the closest energy-accuracy
and memory-read co-design work, plus legal access to the necessary device statistics.
No numerical improvement or arbitrary minimum saving from the source is adopted as a
project acceptance threshold.

The p-bit discussion also needs a conditional reading: random local-field noise is not
in general exactly equivalent to a changed temperature. Averaging a nonlinear transition
probability over noise need not remain in the same sigmoid family. A frozen effective
coupling represents a conventional Ising energy only under the required symmetry and
update assumptions. These remain F7 questions, not conclusions imported into inference.

## Source quality and CA2 use

The paper register says 121 sources but numbers records through 173, including repeated
versions of some works. Several references supporting the latest recommendation are not
given complete entries in that register. Its reading-depth labels describe the original
reviewer's access; they are not our verification status. Do not present this as 173
independently verified papers or transfer its full-read labels into our literature ledger.

The history is valuable for CA2: broad tolerance characterization led to a search for a
decision-relevant intervention, followed by competing estimator, mapping and circuit
ideas. Preserve those changes honestly. Do not turn a hypothesized target mechanism into
a retrospective account of a measured discovery, and do not use agreement between two
AI reviews as independent scientific corroboration.

## Decision after reading

Keep ADR-0001 and the E00-E09 programme. Add the estimator audit to E06, preserve R01-R04
as supplemental leads, and retain the target-architecture gate. No candidate has gained
a novelty pass, target-physics pass or task-level success from this upload. No new
physical experiment was executed, and no source demonstration is promoted to our results.
