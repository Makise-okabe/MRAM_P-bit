# IMMEDIATE USER EXECUTION — E33 + E34, WHILE E32 PHYSICAL EXTRACTION REMAINS GATING (2026-11-05)

**Two preregistered offline experiments have been committed but have NOT been executed on NUS:** [E33 ideal ADC precision vs calibrated count errors](experiments/2026-11-05-E33-frozen-GF-ADC-precision-PENDING.md) and [E34 all-four-column generalization](experiments/2026-11-05-E34-four-column-calibration-generalization-PENDING.md). Both reuse actual previously executed E30/E31 GF Spectre 256x4 current vectors with **assumed** BL/SL R and the original frozen nine E30 CAL cases; no new Spectre, physical ADC, PEX, chip variation or signed neural accuracy can be claimed. Run `bash experiments/run_e33_e34_nus.sh` after `git pull --ff-only`, then record actual results in GitHub. [Prof Fong evidence talk track](communications/2026-11-05-prof-fong-evidence-E31-E34-brief.md) aligns mapping (reserved), inference-failure prediction (main) and Ising (paused) without inventing new research directions.

**Separately E32 remains the binding NEXT PHYSICAL step:** create/validate a real 1T1-specific GF metal BL/WL/SL extraction, do not substitute historical 2T1 PEX, and compare actual extracted R/C against E30/E31 hypothetical .25Ω segment. E33/E34 are quick software evidence-gap checks, not substitutes for physical model credibility.

---

# THREE ORIGINAL RESEARCH DIRECTIONS — CURRENT HIERARCHY (2026-11-05)

See [ADR-0010](decisions/ADR-0010-three-direction-hierarchy-after-E31.md). For the selected **1T1MTJ MRAM-CIM research-pathfinding** problem: **F1 inference-failure prediction / failure-boundary characterization is primary; F3 reliability-aware mapping is a conditional mitigation candidate; F7 MRAM Ising is paused as a separate alternative.** Q correction, N2 selective digital recomputation, ADC control and individual experiments are *methods/supporting gates*, not replacement top-level research directions. The user **already completed E31** on actual GF NFET + static MTJ constructed circuitry (frozen CAL-Q 0/36, global 15/36 under assumed BL R; not PEX), so E31 must never be described as pending. [E32 physical 1T1 interconnect](experiments/2026-11-05-E32-1T1-physical-interconnect-extraction-NEXT.md) is the next milestone. Direction selection does not establish algorithm originality, physical failure rates or neural accuracy.

---

# E31 COMPLETED; E32 PHYSICAL INTERCONNECT NOW REQUIRED — 2026-11-05

User-run E31 **actual GF access NFET + student static MTJ, 256-row×4-column Spectre** new-mask test completed (36 DEV, 18 familiar spatial families +18 previously unseen): original E30 CAL fit **frozen**; identical P/AP resident device map. With **ASSUMED** BL 0.25Ω/row-segment and SL common-return 0.25Ω, global C0 count decode made **15/36** errors, categorical CAL-area-offset/reference (global fallback on unfamiliar areas) **6/36**, CAL-only input-position Q **0/36**. Ideal-wire arm all methods **0/36**. Full [E31 executed evidence](experiments/2026-11-05-E31-frozen-cal-256row-generalization-PENDING.md). **No layout-extracted 1T1 physical RC, device/chip mismatch, physical ADC or neural inference, and no N2 recovery evidence.** `0/36` is a positive narrow nominal-model *Q correction generalization*, NOT silicon BER=0; recovery has no demonstrated residual count errors. Do not increase arbitrary R or make synthetic joint errors to force N2 novelty.

**NEXT physical milestone** [E32](experiments/2026-11-05-E32-1T1-physical-interconnect-extraction-NEXT.md): obtain actual 1T1 architecture GF CMOS+BL/WL/SL routing geometry and electrically extracted R/C, using student MTJ model externally if no licensed 1T1 MTJ layout cell (explicitly label hybrid wire PEX). Validate extracted 256-row line and shared four-column topology; compare to prior assumed 0.25Ω/segment, then evaluate calibrated read currents and physically justified residual signed bitplane errors. Historical 2T1 PEX remains unrelated. The selected compute-level N2 recovery is a conditional candidate, not novel or validated.

---

# CURRENT SCALE-UP EXPERIMENT — 2026-11-05

**E30 is now the next NUS run, not another 4×4/ideal-wire selftest.** The user pointed out correctly that E28S 4-row m2 with 0/28 wrong counts cannot falsify 256×256 CIM reliability or N2 recovery. We have committed [E30](experiments/2026-11-05-E30-256row-1T1-CIM-scaling-PENDING.md) to simulate a **256-row ×4-column 1T1-like GF NFET + student MTJ constructed read array** with 1,024 cells per four-column case, matched shared input masks, persistent P/AP maps, 18 CAL/DEV cases and jointly solved shared-SL return. An optional 256×16 extension and 256×256 generate-only gate are defined. **The circuit's BL and shared-return R are ASSUMED, not physical 1T1 PEX**, and output is not full-network inference. E30 has not yet been run by user. Existing E28S deterministic shared-return GF effect observed without count errors; E29A cancellation-aware recovery remains synthetic/algorithm candidate without matched-cost physical advantage. No old 2T1MTJ DSPF is used.

---

# ACTIVE ARCHITECTURE / EVIDENCE OVERRIDE — 2026-11-05

**User chose 1T1MTJ analog CIM as the new physical prototype.** See [ADR-0009](decisions/ADR-0009-architecture-gate-1T1MTJ-vs-legacy-2T1MTJ-PEX.md) and [E27](experiments/2026-11-05-E27-1T1MTJ-physical-CIM-pilot-PENDING.md). Earlier legacy 4×4 local-floating-SL **2T1MTJ PEX is NOT the new 1T1 PEX**. E19–E24 used GF access NFET + static MTJ with **assumed** wire resistors, not physical 1T1 layout. E24 NUS DONE: at assumed 5Ω / mathematical 7bit, Q-transfer 7/528 vs centroid26/528 and raw124/528; it is a mechanism screen, not a novel read-margin method.

**E26A software comparison DONE** on 256 actual E01 development MNIST parents, FC1 reconstructed exactly; synthetic shuffled-vs-joint demonstration only, **no physical error covariance nor full-network accuracy measured**. Current E27A is a student-built new 1T1 PEX prerequisite, not an assertion GF provides a qualified 1T1 macro. **Original research focus:** algorithm-level mitigation of physically justified signed multibit neural computation errors at cost-matched baselines, *not* sensing/read margin optimization. Prof Fong architecture signoff not recorded.

**Supersedes old dated notes below** about E23D pending, 2T1 being the active target, or E22 being the next experiment.

---

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
