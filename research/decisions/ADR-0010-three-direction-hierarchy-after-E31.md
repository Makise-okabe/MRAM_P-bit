# ADR-0010 — Reconcile the three original research directions after E31

**Decision date:** 2026-11-05 (SGT).
**Status:** Adopted working organization for the 1T1MTJ MRAM-CIM *research-pathfinding* study. Not a supervisor-approved final novelty claim. This decision **supersedes the priority ordering** in ADR-0005 (mapping primary, predictor supporting); preserves those earlier documents as dated history. It is consistent with the later ADR-0006 emphasis on computation-failure regimes and ADR-0009's user-selected 1T1MTJ target.

## The original three research questions — not one new direction per experiment

| Original direction | Research question | Working priority | Falsification / strong baseline |
|---|---|---|---|
| **F3 — reliability-aware mapping** | Can resident weights / read groups be arranged to reduce **actual** inference errors or readout cost under the same resources? | **Reserved optional intervention**, not an already demonstrated novelty | Compare CAR/zero-rate sort, optimized simple grouping, static random and matched-budget search, mapping-calibration and channel-shuffling prior art; show benefit on physical errors + held-out DNN rather than a constructed error table |
| **F1 — inference-failure prediction** | Can inexpensive **runtime-observable** information predict when physically nonideal MRAM-CIM currents, quantized counts and signed W4A8 outputs will change an inference decision? | **Primary research question** (physical gate currently blocks evaluation) | Beyond Q/position correction, calibrated ADC threshold/margin, conditional baseline error rates, independent plane scores, and *no intervention*; validate calibration and ranking against actual full-network outcomes |
| **F7 — Ising / probabilistic MRAM computing** | Can a credible MRAM physical field/update operator beat exact digital incremental field maintenance or matched caching quality–cost? | **Paused / separate alternative** | Need verified stochastic operator, meaningful hardware cost and superior matched update/TTS comparison; E09/E10/E11 controls to date insufficient |

The **research direction** is not identical to the **algorithmic intervention**. Under F1, possible interventions include no correction, low-cost CAL-Q/position correction, ADC precision change, N2 cancellation-aware selective *digital* recomputation, and optionally a physically justified F3 weight/row mapper. An intervention is not a fourth overarching project, and the phrase “joint” does not establish novelty.

## Latest real GF Spectre evidence (2026-11-05)

E30/E30P: 256 rows ×4 simultaneously modeled columns, 24 active, GF compact NFET + student static P/AP MTJ. Under **manually assumed** BL 0.25Ω **per row segment** and common SL return 0.25Ω: global-CAL C0 decoder gave **6/9** DEV wrong counts; CAL area offset, area count bank and known-activation-mask Q were **0/9**. No 1T1MTJ physical PEX, physical ADC, mismatch or NN inference.

**E31 already completed**; do not present it as the next experiment. On 36 *fresh* read masks using the original nine E30 CAL samples, same resident MTJ map, no DEV refit:
- Ideal conductor: all methods **0/36**.
- Same assumed BL R, independent return: global 15/36; categorical area-offset and area-bank 6/36; CAL-frozen continuous input-mask **Q 0/36**, including 0/18 previously unseen spatial-mask families.
- Same assumed BL R plus shared return: identical C0 wrong-count summary — global 15/36; categorical area method 6/36; Q 0/36.
- **OOD control caution:** categorical area methods use a predeclared GLOBAL fallback on unseen families; Q success does not establish a general win against all continuous spatial estimators, calibrated centroid/near-far/Q regressions, or hardware-cost-adjusted methods.
- 36 masks are not independent chips. Only one nominal static P/AP distribution, activity m=24, target C0 count n=11/12/13. No physical RC, ADC, noise, dynamic MTJ, nonzero post-Q decoded errors, aligned signed W4 planes or full DNN failure labels. Do NOT label E31 “MRAM reliability measured” or inference-predictor success.

Executed E31 private JSON: `~/mram_private/E31_1T1/E31_256x4_20261105T033721Z_2792/E31_RESULTS.json`. E30 freeze source SHA256 `f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52`. Public executed report: [E31](../experiments/2026-11-05-E31-frozen-cal-256row-generalization-PENDING.md).

## Current claim and scientific gate

**Defensible finding:** In a constructed 256-row circuit using actual GF transistor compact models and explicitly assumed interconnect, position-dependent current bias causes naive pooled count decoding failures. A CAL-only activation-position Q score generalized across these selected familiar and unfamiliar input-mask families and eliminated all discrete C0 errors under these particular nominal operating conditions.

**NOT established:** Hardware 1T1MTJ PEX or physical BER, a probabilistic failure predictor, a useful selective-recovery algorithm, cross-bitplane measured covariance, full W4A8 network failure rates, same-cost superiority over conventional calibration/mapping, or a novel contribution.

Current F1 candidate conditional chain:
```
physical GF 1T1-specific wire/CMOS extraction and appropriate MTJ model
  -> legitimate multirow/multicolumn read + realistic ADC/variation/timing
  -> strong CAL-only spatial/Q/near-far/centroid/ADC calibration
  -> test whether any held-out residual decoded errors remain
  -> align *actual* errors across W4 signed bitplanes and A8 cycles
  -> evaluate full clean-vs-hardware neural outputs and observable risk features
  -> optional cost-bounded N2 joint recovery vs optimal contextual significance
     prefix, independent scoring, no repair and any cheaper calibration
```
At every stage: **no residual errors => no paid digital recovery**. No arbitrary wire-R escalation to force a failure.

## Next milestone: E32 (not E31)

[E32 physical interconnect requirement](../experiments/2026-11-05-E32-1T1-physical-interconnect-extraction-NEXT.md): actual GF 1T1-specific BL/WL/SL layout geometry and extracted R/C, at least a qualified **GF-CMOS/wiring + external static MTJ hybrid** if the licensed PDK does not offer a compatible physical 1T1-MTJ layout cell. Explicitly label that hybrid as *wire PEX*, not foundry-qualified MRAM macro PEX. Historical 2T1MTJ local-floating-SL DSPF must never be used as 1T1 physical evidence. Need the extracted 256-row path R/C and driver/sensing constraints to determine whether 0.25Ω/segment in E30/E31 was physically plausible.

Do not fund a separate Ising branch or declare N2 novelty unless the core F1 physics/compute gap is resolved.

## Prof Fong one-paragraph version

“I began by investigating three ideas: reliability-aware mapping, neural-inference failure prediction, and an MRAM Ising engine. The mapping and Ising controls have yet to beat strong simple and digital baselines, so I am currently prioritizing prediction of computational failure in 1T1MTJ CIM, with mapping kept as a possible intervention and Ising paused. In a constructed 256-row GF-transistor read circuit, explicitly assumed BL resistance caused severe position-dependent current shifts and 15/36 pooled-decoder errors on new masks. But a Q-based correction trained on nine earlier masks eliminated all 36 errors, including unfamiliar spatial patterns. This is a useful nominal-model finding, not evidence of physical PEX, inference failures or a novel predictor. My next step is real 1T1-specific metal/interconnect extraction and a legitimate ADC/read path; only if inexpensive calibration leaves consequential signed-W4A8 inference errors will I assess a joint failure predictor and cost-matched selective digital recomputation.”
