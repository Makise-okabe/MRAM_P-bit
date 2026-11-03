# Experiment programme and decision gates

Start with E00, E01 and the E02 architecture gate. Do not launch seven independent large
campaigns. Use their outcomes and the literature gaps to select one main intervention
and, at most, one backup. The other protocols are retained to make the choice reviewable.

## Common requirements

Before a scientific run freeze the input/model/quantization hashes, target physical
architecture, calibration/evaluation split, chip sampling unit, settings, tuning budget,
primary endpoint, acceptable quality/resource budgets and stopping condition. Record the
exact command, code commit, environment and source/output hashes in a new run directory.
Numerical budget values are deliberately unset until a justified operating point is chosen.

Evidence progression: software identity -> workload opportunity -> target physical model
-> useful local intervention -> task-level comparison -> expanded evaluation. No claim is
promoted automatically between these stages.

## E00 - Exact arithmetic and bookkeeping (implemented)

**Question:** do the new tools preserve the intended computation and evidence boundaries?
**Inputs:** explicit synthetic software fixtures of full 256 x 256 dimensions, seed 20261103.
**Checks:** consistent permutation; group partial sums; signed W4A8 reconstruction;
complement reconstruction; conditional count cardinality; polarity proxy identity;
non-overwriting records, disjoint split IDs and rejection of an unknown physical model.
**Run:** `python3 -m experiments.run verify --out experiments/runs/E00_new/verification.json`.
**Output:** software/mathematical verification only. Unit-test fixtures cannot be cited as
physical validation, model accuracy or a workload saving. Rerun after arithmetic changes.

## E01 - Workload opportunity and fair mapping baselines (implemented; inputs needed)

**Question:** can real traces produce a meaningful difference between skipping and activity
concentration, before assuming any error law?
**Inputs:** frozen integer/bit-plane activations and weights from one representative layer;
separate calibration/evaluation IDs; physical bit-plane padded/mapped explicitly to 256x256.
Fit one resident mapping across all activation planes and inputs sharing that physical
weight array; independently optimized per-plane mappings are not a free deployment option.
Use development data when previously inspected; no new claims of untouched TEST.
**Arms:** original; seeded random; zero-rate sort; greedy activity balancing; faithful VARA
v1 CAR with alpha 0/0.25/1; simple quiet-then-balanced comparators. All mapping choices use
calibration only. Proposed row-group sizes 16/32/64/128/256 are software schedule variables.
**Endpoints:** occupancy distribution, nonempty vector-read counts, invariant total activity,
conditional fan-in and exact output equality. Squared activity is labelled a proxy only.
**Control:** quantify always-zero dimensions and the result after their simple packing/removal;
compare zero-rate-only grouping to co-zero grouping. Describe any padding and unused columns.
**Decision:** no opportunity or only a trivial zero-feature effect -> deprioritize F3. A useful
structural effect -> nominate the smallest physical comparison in E02/E03. It proves neither
reliability loss nor energy saving. See `experiments/README.md` for trace schema and command.

## E02 - Physical 256 x 256 architecture and response model (protocol; not run)

**Question:** is the proposed read schedule electrically meaningful on the target macro?
**Prerequisite:** complete `experiments/config/architecture.template.json` using authorized
source references. Declare cell/access model, BL/SL/WL topology, drivers, sense interface,
read voltage, time, distribution law/correlation, and read parallelism. A monolithic array
with row batches is sufficient; do not assume electrical sector isolation.
**Initial bounded circuit set:** nominate one operating point and two candidate parallelism
settings only after checking bias/current limits. Include all-zero, sparse, half-active and
dense masks; equal-count near/middle/far placements and low/high-conductance weights.
Use 12-24 nominal pattern cases for a connectivity/settling check, with additional held-out
patterns for model validation. These are planned budget ranges, not executed cases.
**First evidence:** KCL and source/current extraction parity; driver headroom; current versus
count; settling at the intended sample time; dependence on pattern/location. Then introduce
persistent chip variation separately from repeat-read noise. Do not fit and validate on the
same patterns. If a reduced model is used, validate decoded decisions near ADC edges, not
only average current. State whether neighboring columns are explicit or represented by
justified equivalent loading.
**Decision:** reject a topology outside device/readout limits; narrow if faithful modelling
is unavailable. A selected small set of circuit cases cannot establish a rare-event rate.
**Code status:** architecture preflight implemented; no target netlist generator or Spectre
execution is claimed. Port/model interfaces must be inspected in NUS before generation.

## E03 - Grouping versus reliability, then a mapper (F3; protocol)

**Prerequisite:** E01 opportunity and E02 validated response. Fix physical hardware across
mapping comparisons. Independently tune each baseline's calibration, ADC span/precision and
sample time under the same budget and constraints.
**Mechanism test:** paired patterns compare c(a+b) with c(a)+c(b), with c(0)=0, while checking
position/weight dependence. Monotone per-read error alone does not prove aggregate damage.
Preserve common chip identity across reads and reconstruct signed outputs.
**Arms:** E01 mappings; electrical-load-balanced plus gain/reference calibration; a faithful
SEC-style correction or clearly labelled adaptation [S29]; DIB-style adaptive blocking after
full-text inspection [S02]. Original hardware and fixed isolated sectors, if implemented,
are separate architecture controls. Include a restricted offline mapping oracle.
**Candidate:** bounded feasible row swaps using whole-trace total cost and a predeclared
reconstructed-error constraint. Score calibration only; freeze before evaluation.
**Endpoints:** paired reconstructed-output error, count-error distributions and bias; total
energy/latency/area when supported, otherwise explicitly operation counts; then clean-reference
prediction mismatch and ground-truth accuracy separately on one frozen network.
**Kill:** no meaningful conflict after calibration; simple packing/balancing matches the
candidate; full tuning removes gain; overhead dominates; effect fails independent patterns.

**Narrower covariance check (4 November):** E03M is a separate completed mathematical
counterexample, not a completed target E03. Follow the [precise method and proof](novelty/2026-11-04-covariance-mapping.md):
hold per-read activity/count statistics equal, vary within-group mask overlap, and measure
decoded pair covariance after the same scalar calibration. Compare continuous readout as
an invariance control. Fit one covariance-aware static mapper only after the target response
is validated; add covariance-ablated scoring and a simulation-scored search at equal search
budgets, plus combined CAR/adaptive-block/calibration comparators. Second moments justify
an MSE objective; they do not determine a neural failure probability.
S08 already uses channel shuffling to randomize deterministic errors. Include faithful
or explicitly adapted shuffling and best-of-equal-budget random maps before attributing
a gain to the covariance-aware optimizer.

## E04 - Electrical polarity selection (F2; protocol)

**Prerequisite:** E02 pattern/location response. Derive or fit a cheap score on calibration
patterns; keep the true requested dot product unavailable to runtime control.
**Arms:** calibrated direct; ordinary minority inversion; position-weighted selector;
load-balanced mapping plus calibration; per-input offline oracle using both physical reads.
**Endpoints:** selector regret on independent patterns, decoded error and settling, then total
controller/metadata/subtraction/read costs. Paired chips and stimuli across polarities.
**Kill:** little oracle benefit, weak held-out score prediction, or cheaper baseline equivalence.
**Gap:** encoding-specific prior art and official S20 disclosure verification remain required.

## E05 - Decision-directed neural readout (F4; protocol)

**Prerequisite:** exact reference model plus a defensible target read-error envelope. Start
at the final classifier. Build output intervals including omitted terms and hardware error.
Accept only an interval-separated winner; otherwise refine under a frozen schedule.
**Arms:** best fixed precision, per-layer mixed precision, input/activity-aware conversion
[S02,S28], double-reference/detector recompute [S14], and the candidate. S13/S30 are close
method comparisons, not faithful analog-MRAM implementations by name alone.
**Endpoints:** decision agreement/error allowance, bound coverage, refinement frequency,
saved conversions, bound/control state and energy, plus the layer's share of task cost.
**Kill:** invalid/loose bounds, almost universal fallback, or total cost greater than baseline.
Any deterministic guarantee is conditional on a valid deterministic hardware envelope.

## E06 - Failure estimator (F1; protocol)

**Prerequisite:** E02 validated model and a clearly specified probability (read, inference or
chip yield). Compare the same event and input/chip distribution for every estimator.
**Arms:** calibrated brute-force reference with uncertainty; randomized quasi-Monte Carlo;
stratified or importance sampling with correct weights; event-aware conditional estimator;
S11-style probability bounds where applicable; S10 only under a compatible fault model.
**Endpoints:** absolute error/confidence coverage versus total runtime and memory, including
characterization, fitting and boundary construction; amortization over predeclared new settings.
**Kill:** no advantage over a strong sampler, high-dimensional event explosion or no useful
predictive effect of the retained structure. A submission title [S22] does not kill the idea.

**Source-specific audit before a port:** the uploaded field survey specifies a
column-correlated estimator but truncates joint decoder events at pairs. Following
[the source review](reviews/2026-11-03-claude-field-survey.md), specify the resulting
normalized PMF, omitted-event error, multi-step crossings, common-latent conditioning and
the network independence boundary. Compare point estimates and bounds separately. Use
a representative held-out set in addition to pilot-selected stress examples; zero observed
failures does not make a positive prediction a false alarm. No demonstration in the source
is target-array evidence or an executed E06 run.

## E07 - Analog/digital crossover (F5; protocol)

**Prerequisite:** one feasible analog and one feasible digital implementation. Freeze useful
precision, capacity, throughput and task-quality requirements. Extra dual-mode hardware is
part of the candidate cost, not a free software switch.
**Arms:** tuned analog, tuned digital, static hybrid and a small calibrated mode-selection rule.
**Endpoints:** predictive accuracy of the crossover rule and resource Pareto curves under
uncertainty in ADC/driver/digital costs. S16 can support initial sensitivity modelling; it is
not a measurement of our ADC. S17 provides a digital-MRAM comparator family.
**Kill:** one simple mode dominates or duplicated periphery erases the benefit. A sweep alone
is not the new design contribution; derive and validate the rule.

## E08 - Readout identifiability and an extra observable (F6; protocol)

**Prerequisite:** E02 calibrated class responses conditioned only on practical readout metadata.
Estimate the best one-observable decoding and its residual ambiguity. Derive the unknown
parameters before selecting a second sample/reference/read configuration.
**Arms:** optimized references/decoding; greater ADC precision; simple gain/offset or SEC-style
correction; one added observable with counted sample/ADC/control overhead.
**Endpoints:** held-out count/decision separation and total cost. Check identifiability and
noise amplification; do not choose the best read after observing the evaluation label.
**Kill:** no meaningful ambiguity, non-identifiable nuisance parameters or cheaper correction.

## E09 - Ising persistence, field organization and refinement (F7; conditional)

**E09A, implemented and completed software only:** exact small-graph targets, target-energy
identity, same-random-stream full/incremental trajectories, cache parity and a two-flip
drift diagnostic. `python3 -m experiments.ising_reference verify --out NEW_PATH`.
Its kernel preflight intentionally blocks a scientific noise study until target and
temporal-noise evidence plus the response adapter are available.

**E09B, target diagnostic:** match conditional post-calibration error laws on fixed states.
Distinguish a fixed chip, a deliberately decorrelated counterfactual and physical temporal
noise. Compare full field recomputation, noisy incremental cache updates, initialization
errors and exact refresh. A two-flip/reversal loop separates cache drift from an
instantaneous-field/temperature hypothesis. Read S18 fully before an exact novelty verdict.

**E09C, small solver pilot:** after E09B and a reviewed target adapter, compare exact full
and incremental digital fields, quantized digital couplings and feasible calibrated target
operators on small graphs with enumerated optima. Use paired graph/chip/start identities.
The [queue](04_screening_queue.md) gives arms, effort budget, endpoints and stopping rules.
Count initialization, transpose/duplicate storage, coefficient reads, cache and refresh;
do not infer energy or measured TTS from spin counts. No broad graph campaign is started.

**Refinement reserve:** given a cheap valid interval, compare fixed/scheduled precision,
simple heuristics and same-draw refinement. Stop if bounds consume full work or existing
methods already supply it. A companion chapter is conditional on a distinct useful result,
common mechanism/method and supervisory/scope fit; it is not committed by a common story.

## First working sequence

1. Follow the [bounded screening queue](04_screening_queue.md), read the source gaps and
   settle one target topology/model interface. E09A may run before physics as software only.
2. E00 engineering checks (completed locally in this reset; repeat on NUS if environment differs).
3. Export one real layer's calibration/evaluation traces and run E01. No circuit cost claims.
4. Specify and validate the small E02 circuit set on NUS. Do not launch a large variability sweep.
5. Compare F1-F6 using the resulting evidence. Select one intervention and one backup, write
   the exact closest-work difference and freeze its E03-E08 protocol.
6. Run the smallest strong comparison, record rejection/continuation and update the CA2 draft.
