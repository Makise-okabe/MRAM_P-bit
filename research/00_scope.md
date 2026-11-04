# CURRENT EXPERIMENT UPDATE — 2026-11-05

**E22–E22C executed on NUS:** 1,530 GF access-NFET/static-MTJ DC circuit cases with assumed (NOT PEX) BL wire resistance; 17 count classes. The E22 frozen-reference failure was mostly a calibration artifact; E22B per-R CAL ADC and near repair left 25/204 errors at assumed 5Ω/segment, 7bit mathematical ADC. **E22C improves this on the same previously inspected DEV data:** per-R CAL suffix-load Q correction leaves **0/204 errors at 5Ω**, versus near **25/204**, centroid **5/204**, raw **60/204**; no adjacent sampled overlaps after Q correction. This is a positive development result, **not independently confirmed or novel yet**.

**Immediate priority: E23D new GF mask confirmation** (code/pre-registration in [E23D](experiments/2026-11-05-E23D-fresh-GF-mask-and-unseen-R-confirmation-PENDING.md)). It freezes all Q/centroid/near coefficients, count centroids and ADC reference calibration on OLD E22 CAL only, uses 24 NEW DEV masks ×17 counts=408 fresh masks across assumed R=0/1/2/3/**4**/5Ω = 2,448 new GF DC cases, including R4 previously unobserved and interpolated without CAL. Requires NUS execution; **not yet a measured E23D result**. Still m=k16; multi-occupancy, fixed-chip variation, geometry/PEX, physical ADC and full-network inference follow after independent screen.

Original research direction remains coupled precision and physical non-idealities. Ising and generic physical mapper remain archived alternatives. Any narrower suffixQ invention claim must survive full prior art and strong physically credible control costs.

---

# ACTIVE PRIORITY OVERRIDE — 2026-11-05 (user decision)
**Primary FYP direction now frozen:** *Characterizing Reliability and Failure Regimes of Memory-Centric Neural Inference Under Coupled Precision and Hardware Non-Idealities*. See [ADR-0006](decisions/ADR-0006-coupled-precision-failure-boundary-primary.md) and [pending E22](experiments/2026-11-05-E22-coupled-precision-17count-GF-PENDING.md).

The older sections below are historic scope/evidence contracts from Nov 3–4. Any statement that F3 mapping is the **current leading algorithm route** is superseded. Physical-aware mapping and Ising are archived alternatives; they are not the present primary FYP. Immediate E22 GF read-current × mathematical ADC precision pilot, then E23 held-out failure-boundary prediction versus strong margin and near/far baselines, then E24 variability/PEX and E25 task-level validation. No E22 physical result exists until user runs it in NUS Singularity.

---

# Active scope and evidence contract

Decision: 3 November 2026, at the user's request. The user authorized archiving the
previous work, starting a fresh report, reviewing all candidate directions, preparing
experiments and maintaining a research-path record for later CA2 writing.

## Research objective

Develop an explicit algorithm, derivation or feasible readout/control design, show a
physically justified case where it matters, and demonstrate useful value against tuned
strong baselines. This phase does not presume a sector-mapping winner.

The original proposal's subject remains precision, hardware nonidealities and reliable
memory-centric inference. New interventions extend that objective; they are proposals
for discussion, not independently confirmed supervisor approvals.

## Current working organization (4 November, ADR-0005)

The three discussion topics remain mapping, failure prediction and Ising. F3 is the
main bounded method investigation; F1 supplies a validated scoring/evaluation tool;
F7 remains optional. Spatial H1/E02-A is a physical mechanism screen. A split-read
controller is a conditional extension of the same mapping study, gated on residual
target effects after calibration and longer sensing. It is not a replacement
top-level candidate. See [ADR-0005](decisions/ADR-0005-one-mapping-study-and-supporting-tools.md).
No novelty, numerical improvement or supervisor endorsement is inferred.

## Physical and computational contract

- Target **physical** storage: 256 rows x 256 columns = 65,536 MTJ positions.
- A binary bit-plane occupies physical positions; signed or multibit weights may need
  several positions/arrays. Do not identify logical network dimensions with cell capacity.
- Read parallelism is unresolved. Proposed software screens cover group sizes 16, 32,
  64, 128 and 256 as schedules only. None is physically validated by this repository reset.
- The first target may be a monolithic array with row batches. Electrically isolated
  sectors are an alternative that requires actual switches/periphery and their cost.
- Include WL/BL/SL wiring, drivers, neighboring-column effects where relevant, and the
  declared sensing interface. Start with defensible parameter ranges; extracted RC is
  stronger subsequent evidence, not a prerequisite for writing an honest initial model.
- Prior repository policy permitted licensed GF access NFET use with the student-owned
  MTJ model and excluded the proprietary GF MTJ implementation. Preserve that source
  boundary unless the user provides a different authorized model. Device parameters,
  variability and correlations still require explicit provenance for the target.
- Reuse general arithmetic, model-export and plotting infrastructure only after audit.
  Prior empirical trial tables are not target-array calibration or validation evidence.

## Filters and gates

Five filters: useful improvement at fixed quality; a distinct contribution; physical
credibility; bounded FYP ownership; and advantage over simpler tuned alternatives.
Three gates before a large campaign: precise method/difference, a physical case, and a
small strong-baseline comparison. Existing work in a broad family does not eliminate
every narrower method. A paper title or inaccessible submission cannot prove equivalence.

The target budgets for acceptable arithmetic error, task degradation, latency and area
are **not set yet**. Set them in a frozen run protocol before comparing methods. This
repository does not invent performance thresholds or a guaranteed publication outcome.

## Evidence classes

| Class | Permitted claim |
|---|---|
| Software mathematical verification | Implementation satisfies tested exact identities |
| Workload structure | A trace/mapping changes occupancy or operation counts |
| Illustrative model | A hypothesis occurs under explicit assumed parameters |
| Target circuit simulation | The declared target circuit produces the simulated outputs |
| Validated surrogate | A reduced model matches held-out target circuit cases to a stated tolerance |
| Task evaluation | A frozen task model behaves as reported under the declared hardware model |
| Measured silicon | Requires actual measurement; none is introduced in this phase |

All papers' results remain external literature, not our results. Claude's pasted toy
outcomes are external, unverified illustrative-model reports and are not entered as
target evidence. At the reset, results contained only explicitly marked engineering checks.

Update, 4 November 2026: E03M adds a separately labelled constructed mathematical/
illustrative-model result. It is not a target circuit, real-workload, energy or inference
result. Its provenance and limits are in the novelty note and claim C011.

Revision-15 consolidation, 4 November: Ising persistence and field organization are a
conditional diagnostic/alternative and may become a companion only after a specific
useful result, common method/mechanism and scope fit survive. E09A adds software controls;
it supplies no target noise, Ising hardware, solver-success or energy result. A stable
storage MTJ, stochastic spin source and incremental field cache are separate components.

## Statistical discipline

Freeze source/quantization/model hashes, calibration and evaluation IDs, chip identities,
and seed roles. Use paired inputs/chips across policies; do not sample a new cell mismatch
for every read. Report classification error, mismatch from the clean quantized reference,
and count error separately. Chip-level uncertainty cannot use repeated reads as new chips.
Zero observed failures is not zero probability: the independent-trial 95% rule of three
is a rough diagnostic, not proof under arbitrary correlation or adaptive selection.
