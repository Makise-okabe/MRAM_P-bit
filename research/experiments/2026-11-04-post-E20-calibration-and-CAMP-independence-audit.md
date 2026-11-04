# Post-E20: calibration and independence-baseline audit

**Executed software research, 4 November 2026. No new Spectre, GF target, PEX,
full-network accuracy, hardware cost or novelty result.** E15/E20 remain retired
as principal novelty claims. CAMP-light remains a conditional investigation.

## Decision

1. Do not promote the proposed decoded-error mapping selector. In the completed
   finite-ADC screen, selecting a mapping by CAL decoded W4A8 block MSE failed
   to beat selection by CAL continuous W4A8 block MSE on DEV.
2. Correct the E22 independent-activation ablation: its Bernoulli diagonal must
   be `C_ii=p_i`, not `p_i^2`. A new matched implementation retains the E22
   CAMP-light advantage in zero-rate and CAR grouping under the original
   constructed passive kernel. Original grouping remains a negative condition.
3. CAMP-light is the most concrete remaining mapping hypothesis, not a selected
   or novelty-certified final contribution. Its advantage is sensitive to the
   electrical/readout/calibration protocol. Keep one small physical falsifier;
   do not authorize a large sweep from these software results.

## Data and separation

Verified frozen E01 private packet SHA256
`400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a`.
Only the first 256 FC1 input rows and first eight complete signed W4 output
channels are used. Eight activation planes retain parent and bit identities.
The 256 evaluation parents were previously inspected and remain **DEV**, not
an untouched final test. CAL and DEV parents are disjoint.

All comparisons hold each 32-row group's membership fixed. One common resident
ordering serves all selected activation/weight planes and columns. Ideal
counts, signed W4A8 arithmetic and nonempty group reads are preserved. Groupings
have different read budgets, so compare policies **within each grouping**.

## Audit A: independent Bernoulli second moments

For binary activations, independence gives `C_ij=p_i p_j` only off the diagonal;
`C_ii=E[x_i^2]=p_i`. The previous outer-product-only ablation omitted the
diagonal contribution `sum_i pos_i p_i(1-p_i) gbar_i^2`. It therefore was not a
clean experiment isolating inter-row correlation.

The correction was verified by enumerating all 32 activation patterns of a
five-row independent Bernoulli example: expected Q=81.6, corrected formula=81.6,
old formula=74.5875, missing diagonal term=7.0125.

The new audit first reproduces **all six frozen E22D baseline/CAMP MSE and
wrong-count results exactly** for zero-rate, CAR and original grouping. It then
uses matched deterministic seven-swap optimizers and corrected independent
moments. This is the same **assumed isolated 32-shunt passive ladder** as E22D:
gAP=36.704 microSiemens, gP=73.408 microSiemens, r=5 ohm/segment, exact passive
Kirchhoff recursion, no access transistor or finite ADC. Each mapping receives
the same two global CAL-fitted coefficients on active count and centroid,
followed by the same legal-count clipping and integer decoding.

DEV signed W4A8 first-block MSE, lower is better:

| Fixed grouping | Joint activity/conductance sort | Correct independent light | CAMP-light | CAMP vs corrected independent |
|---|---:|---:|---:|---:|
| Zero-rate | 28,332.48 | 28,440.44 | 25,508.23 | 10.31% lower |
| CAR | 28,100.37 | 28,601.66 | 25,316.25 | 11.49% lower |
| Original | 514.69 | 489.24 | 537.80 | 9.93% higher |

The corrected full conductance-product independent baseline gives 28,879.96,
28,405.49 and 516.52, respectively. No new full-covariance variant is proposed.
Small differences between matched and frozen sorting on CAR/original arise
from deterministic tie ordering; frozen results remain unchanged and are
separately reproduced.

Exploratory paired-parent bootstrap intervals for absolute CAMP-light benefit
over corrected independent light are [1219.7,4756.1] for zero-rate,
[1682.2,5056.3] for CAR, and [-108.0,-5.0] for original grouping. These are
descriptive intervals on previously inspected DEV data, not prospective
confirmation. Individual count errors and end-to-end neural decisions are
different endpoints; the original E22 limitations remain.

## Audit B: finite-ADC, stronger calibration and objective selection

A separately declared **assumed monolithic 256-node passive column** was tested
at r=0/1/5 ohm/segment, with 32-row scheduled groups, AP=100 and P=200
microSiemens, a noiseless ideal 8-bit ADC with 10% range headroom, and exact
assumed upstream-wire deembedding given to every comparator. Inactive rows
are ideal disconnected. No GF transfer characteristic is inferred.

Each mapping fits a bounded residual around the nominal count estimate using
five ridge coefficients plus one residual bound per group/weight-bit column.
Use 64 CAL parents to fit and 64 different CAL parents to select mappings;
DEV uses all 256 parents and all eight outputs. This calibration has more
parameters than E22's two shared coefficients; its hardware cost is unmeasured.
All methods receive identical calibration capacity and the same 32-map pool:
base/reverse, weight-density sorts, joint activity/conductance sort, CAMP-light,
corrected independent optimizer, explicitly labelled old independence control,
and 24 seeded random within-group orders.

| Assumed r | Joint sort DEV block MSE | CAMP-light | CAL continuous-MSE selector | Proposed CAL decoded-MSE selector |
|---|---:|---:|---:|---:|
| 0 ohm | 0 | 0 | 0 | 0 |
| 1 ohm | 576.59 | 331.39 | 284.86 | 576.59 |
| 5 ohm | 30,184.68 | 30,021.13 | 30,021.13 | 30,376.41 |

At 5 ohm, CAMP improves only 0.54% over joint sort; the descriptive paired-parent
95% interval for absolute benefit is [-4620.8,5313.8], spanning zero. The new
decoded-MSE selector is 1.18% worse than the continuous-MSE selector. At 1 ohm,
its MSE is 102.4% higher. No advantage is established for the new objective.

**Do not attribute the difference from E22 solely to calibration.** Geometry,
conductance, quantization, CAL allocation and calibration all changed. This
screen demonstrates protocol sensitivity, not a controlled causal decomposition
or a refutation of E22's numerical result.

The initial prototype is explicitly invalid as positive mechanism evidence:
unconstrained direct least squares returned zero for groups unexcited in CAL,
creating artificial DEV errors even at zero wire resistance. It also omitted A8
weighting in the output objective. Its source/results are retained privately;
they are not counted as a successful candidate. Corrected runs use a nominal
physics backbone and bounded residual fit, retain A8 identities, and pass the
zero-wire checks.

Verification includes exact ideal-count/read invariance, zero-wire current
invariance for all 32 maps on all splits, zero-wire exact integer decoding,
signed W4A8 reconstruction versus direct int64 dot products, and independent
dense 256-node KCL versus the recursion (maximum normalized difference
1.42e-11). These are engineering/model checks, not target validation.

## Closest literature and remaining novelty question

| Source | Verified access and overlap | Consequence |
|---|---|---|
| Wang et al., JXCDC 2024, DOI 10.1109/JXCDC.2024.3478360 | Publisher abstract and primary manuscript method: STT-MRAM bit-significance placement plus reference-column output transformation | Combining mapping and calibration is occupied. |
| Matsui et al., NanoCiM, TCASAI 2026, DOI 10.1109/TCASAI.2026.3661436 | Author publication record and abstract; full algorithm unavailable here. Weight-aware row-address scrambling, IR-drop mitigation, TSP method | Generic weight/position-aware scrambling cannot be the novelty. Exact objective/activation-statistics comparison is open. |
| Arapidis et al., DATE 2026, DOI 10.23919/DATE69613.2026.11539412 | Institutional abstract and indexed author excerpt, not a complete paper read: balanced mapping with ADC calibration | Generic calibration-aware mapping is occupied. |
| Rasch et al., Nature Communications 2023, DOI 10.1038/s41467-023-40770-4 | Primary method text on row-order/input-dependent IR drop and correlated inputs | Neither IR drop nor correlated workload dependence is a new physical discovery. |

Links: [Wang](https://ieeexplore.ieee.org/document/10714384/),
[NanoCiM author record](https://co-design.t.u-tokyo.ac.jp/en/news/tcasai2026/),
[NanoCiM abstract](https://www.researchgate.net/publication/400560058_NanoCiM_Nano-ReRAM_Computation-in-Memory_with_Neural_Network_Weight-Aware_X-Address_Scrambling_to_Suppress_IR_Drop-Oriented_Bit-Line_MAC_Current_Variation),
[DATE institutional record](https://research.tudelft.nl/en/publications/analysis-and-mitigation-of-ir-drop-in-memristor-based-ai-hardware/),
[Rasch](https://www.nature.com/articles/s41467-023-40770-4).

The narrower candidate is an explicit CAL pairwise-coactivation placement
objective **within fixed groups**, compared with correct independent moments,
weight-aware scrambling and the same practical calibrator/read schedule.
Its physics is not exclusive to MRAM. A title, abstract or unsuccessful search
cannot establish that NanoCiM lacks the same rule.

## Next bounded decision

Read NanoCiM's full method before asserting originality or launching a large
campaign. Compare its objective, activation dependence, allowed permutation,
calibration and optimized endpoint explicitly.

The existing E23 package is a ready **GF + static student MTJ 32-row microgate**,
not an executed result or a physical 256x256 model. Its R0 invariance and paired
R5 raw-current droop comparison are necessary screens only. A raw-current win
is insufficient: next compare frozen maps after the **same CAL-only decoder**
and ADC settings on held-out patterns, including the corrected independent
baseline. If simple tuned correction removes the advantage, reject the method
claim. If the advantage survives, verify target topology/RC, task-level utility
and cost before scaling. No uncalibrated-droop result substitutes for this gate.

Freeze the new decoded-MSE selector, E15/E20 novelty rescue and an Ising pivot.
Retain failure prediction as the mapping study's supporting tool under ADR-0005.

## Reproduction

Public scripts require the existing private packets, which are not distributed
in this repository. No PDK model, licensed paper, raw current, private trace,
weight matrix or parent-ID list is added.

```bash
python3 experiments/postcal_mapping_audit_v3.py \
  --packet /path/to/review_packet.zip --out /new/private/run_03
python3 experiments/camp_independence_ablation_audit.py \
  --packet /path/to/review_packet.zip \
  --legacy-package /path/to/E21_E23_CAMP_candidate.zip \
  --out /new/private/independence_audit/results.json
```

Private result hashes and aggregate outputs are recorded in
`experiments/results/post_e20_calibration_audit_summary.json` and
`experiments/results/camp_independence_audit_summary.json`.
