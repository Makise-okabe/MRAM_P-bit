# Complete idea inventory

All entries are candidate questions, known techniques or applications, not 21 promised
contributions. IDs remain stable when status changes. Seven family cards are in
[02_candidate_methods.md](02_candidate_methods.md).

| ID | Idea recalled | Role / current decision | Family |
|---|---|---|---|
| D01 | Compact inference-failure probability estimator | Independent method candidate; require total-cost advantage | F1 |
| D02 | Exact/conditional ADC boundary-map integration and reuse | Candidate mechanism; probability-region methods already exist | F1 |
| D03 | Persistent chip variation and bit-serial error coherence | Physical/statistical mechanism, not a standalone novelty claim | F1 |
| D04 | Selective/mixed ADC precision by sensitivity or activity | Established family; candidate needs a precise new policy | F4 |
| D05 | Calibration, ADC references, HAT/noise-aware training | Cross-cutting tuned comparators; narrower implementations remain possible | All |
| D06 | Confidence detection, guaranteed decisions, selective recomputation | Narrow around a valid cheap detector/decision rule | F4 |
| D07 | Analog overlap versus more ADC bits | Foundation for a circuit-specific limit or intervention | F6 |
| D08 | Signed, error-cancelling or alternative arithmetic encoding | Reserve; compare with RAELLA and account for representation cost | F2/F4 |
| D09 | Same ideal sum, different cell location / weight mapping | Spatial mechanism and strong comparator | F2/F3 |
| D10 | Ordinary input complement / minority-mask read | Baseline; public matching disclosure lead requires original verification | F2 |
| D11 | Spatially informed weighted polarity selection | Independent narrow controller candidate | F2 |
| D12 | Physical segmentation versus logical row batching | Architecture choices, not interchangeable models | F3/F5 |
| D13 | Co-zero / co-activation row grouping | Prior-art comparator (VARA CAR), not our invention | F3 |
| D14 | Reliability-constrained sector/group mapping and readout | Candidate; no measured conflict or advantage yet | F3 |
| D15 | Analog versus digital/hybrid crossover | Independent design-rule/control candidate and essential comparator | F5 |
| D16 | Complementary/multi-read load self-identification | Hold until an identifiable model and cost case exist | F6 |
| D17 | Ising coupling/local-field error characterization | Conditional persistence/operator diagnostic; generic characterization insufficient | F7 |
| D18 | Decision-directed Ising field refinement using one random draw | Separate application candidate; sampling prior art incomplete | F7 |
| D19 | LLM/MoE bank/expert skipping and sparsity | Application opportunity; not an independent readout contribution | F3/F5 |
| D20 | Neural decision-directed refinement with output intervals | Independent controller candidate; begin at final classifier | F4 |
| D21 | Readout identifiability and minimal extra observable | Derivation plus sensing-intervention candidate | F6 |

Earlier A-D discussion maps as follows: equivalent sums / position -> D09; analog-digital
crossover -> D15; guaranteed decisions -> D06/D20; ADC cannot fix physical ambiguity ->
D07/D21. The complement proposal is D10, its electrical extension D11, and the user's
array-sector idea D12-D14. This crosswalk prevents ideas being lost under new names.

## Comparison, without unsupported numerical novelty scores

| Family | Intended output | Value could come from | Main unresolved gate |
|---|---|---|---|
| F1 Probability estimator | Prediction algorithm | Faster reliable operating-point evaluation | Scaling benefit versus calibrated simulation |
| F2 Encoding/polarity | Small controller / representation | Better electrical operating condition | Valid proxy and benefit after overhead |
| F3 Mapping and organization | Mapper plus readout constraints | Skipping without excessive correction/sensing cost | Target circuit conflict and simpler baselines |
| F4 Decision-directed inference | Stopping/refinement policy | Avoiding unnecessary conversions/reads | Cheap valid bounds and task-level gain |
| F5 Analog/digital crossover | Predictive rule plus feasible modes | Choosing the cheaper reliable computation | Matched cost/throughput models |
| F6 Readout information | Identifiability rule and extra measurement | Fixing information loss efficiently | Relevant ambiguity after calibration |
| F7 Ising | Persistence/operator diagnostic; refinement reserve | A distinct field-computation decision or reduced read work | Validated target kernel, strong incremental baseline and specific method gap |

Keep F1-F6 as competing questions. F7 is a supervisor-dependent alternative or conditional
companion after its own gates; it does not rescue an unsuccessful main method. No family currently passes
the method + physical case + strong demonstration gates.

## Supplement from the uploaded field survey

The [3 November source review](reviews/2026-11-03-claude-field-survey.md) crosswalks the
Claude/Yanzhang revisions to these IDs and preserves additional leads R01-R04: transistor/
read-bias co-design, device-operation stress, security and CAM search. These are reserves
or out-of-core leads, not extra promised projects or selected method cards. The same
review audits the newly specified estimator and records the limits of its demonstration.

On 4 November, D14/F3 gained a [specific decoded-covariance mapping candidate](novelty/2026-11-04-covariance-mapping.md).
Its constructed equal-marginal counterexample is complete; the target mapper, physical
case, practical advantage and novelty pass remain unestablished. This is a refinement
of an existing ID, not another independent topic added to the shortlist.

The revision-15 follow-up retains D17/F7a as a [bounded Ising diagnostic](04_screening_queue.md),
with exact software controls E09A complete and target E09B/C pending. Ordinary incremental
field updating is an established comparator. D18/F7b refinement remains a reserve.
