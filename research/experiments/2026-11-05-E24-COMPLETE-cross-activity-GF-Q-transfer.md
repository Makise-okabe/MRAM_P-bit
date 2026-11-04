# E24 COMPLETED — independent cross-activity GF-current validation of transferred suffix-load coefficient

**User NUS Singularity execution:** 2026-11-04 17:33–17:42 terminal record, analyzed 2026-11-05. **Research status:** SUCCESSFUL CROSS-ACTIVITY TRANSFER WITH AN IDENTIFIED HIGH-OCCUPANCY FAILURE REGIME. This is still nominal GF `hvtnfet` compact transistor plus student-owned static-MTJ model in a constructed 32-row one-access-transistor-per-branch bitline with ASSUMED resistors, **not GF 22FDX 256×256 extracted PEX or intended local-floating 2T1MTJ macro.** Offline mathematical ADC, not a physical ADC circuit; no timing/energy, no device mismatch or trained-neural-network accuracy.

## Verified provenance and validity
- User's full output log: 3168 GF Spectre DC cases all completed, `E24_RUN_COMPLETE`, then `E24_FINISHED`. Exactly 792 unique spatial masks (CAL and DEV combined), explicitly excluding old E22 CAL and old E22 DEV hashes. Same spatial masks repeated across assumed segment Rs 0,3,4,5 Ω (not 3168 independent chips).
- Physical-output file on NUS: `~/mram_private/E02_256x256/E24/E24_ACTIVITY_20261104T173351_53/e24_activity_results.json`; analysis `~/mram_private/E02_256x256/E24/E24_cross_activity_20261105_014145.json`. Training original E22 SHA256 `c79133fa5165be8ba2142e7cea78834f29db6a17446d8bbb13226efbfe4df965`.
- Frozen correction slopes ALL trained on **OLD E22 m=k=16 CAL only**. New scenarios vary **m=8,12,20,24** at fixed **k=16** and use 6 new CAL + 12 new DEV per feasible true count n; legal counts 9,13,13,9 classes respectively. So new CAL per m=54/78/78/54, DEV=108/156/156/108; per R total **264 CAL + 528 DEV**, across 4 Rs =3168 cases.
- Every method receives a separately calibrated per-(m,k,R) ADC current window and per-count CAL reference centroids trained on the same new CAL. The `_transfer` methods freeze their **spatial coefficient**, not the entire ADC transfer function. R4 frozen old slope was interpolated from old R3/R5, but NEW R4 CAL references and ADC full-scale ARE USED. Thus this is **cross-m coefficient transfer, not calibration-free operation or fully unseen-R system transfer**.
- Models: raw per-condition 17-or-fewer CAL count centroids, near-transfer, centroid-transfer, suffixQ-transfer; also same-condition centroid-refit and suffixQ-refit. Q is computed from publicly known input activation positions only; actual unknown MAC count is NOT used at DEV runtime. Fullscale has 5% guard around new CAL current min/max.
- Count outcomes are **balanced within each legal count class**, not samples weighted by real MNIST count distribution. No reported chip-level variation.

## ACTUAL 7-bit count errors on fresh DEV masks

### Strongest assumed wire load: 5Ω/segment

| m | DEV count | Raw | Near transfer | Centroid transfer | **Q transfer** | Centroid refit | Q refit |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 |108|1|0|0|**0**|0|0|
| 12 |156|22|10|0|**0**|1|0|
| 20 |156|56|21|11|**0**|11|1|
| 24 |108|45|28|15|**7**|13|7|
| **TOTAL** |**528**|**124**|**59**|**26**|**7**|**25**|**8**|

Pooled R5 descriptive count-error fractions: raw 23.485%, near 11.174%, centroid 4.924%, **Q transfer 1.326%** (relative 73.077% fewer errors than centroid, 94.355% fewer than raw). Q-refit 8/528=1.515%; the one-error advantage of transfer is a sample observation and not evidence refitting is systematically bad. At m=24,R5 the Q correction still makes 7/108=6.481% errors and **2** adjacent count boundaries remain nonseparable in sampled corrected currents. This is a residual failure *under this correction*, not proof no better readout can work.

### Novel assumed resistance R4 (old slope interpolated R3/5, but fresh CAL ADC/reference settings fitted)

| m | DEV | Raw | Near transfer | Centroid transfer | **Q transfer** |
|---:|---:|---:|---:|---:|---:|
| 8|108|0|0|0|**0**|
| 12|156|15|3|0|**0**|
| 20|156|44|11|5|**0**|
| 24|108|27|19|7|**1**|
| **TOTAL**|**528**|**86**|**33**|**12**|**1**|

At R3 (same distribution), raw 39/528; near 12/528; centroid 3/528; Q-transfer **0/528**. R0 all corrected and raw classes 0/528 (7bit). R4 Q-refit 3/528 (m24), centroid-refit 9/528. R3 Q-refit 0/528.

### Paired per-mask checks at R5
At m=20, centroid wrong 11 while Q right all 11, Q never makes a new error. At m=24, Q fixes 12 centroid-wrong cases but introduces **4 errors where centroid was right**, and both wrong on 3 cases. Thus across m8/12/20/24 at R5, Q improves **23** centroid-wrong cases and worsens **4** centroid-right cases (difference 19 errors). Report this, not only aggregate wins. At R4, improves 11 centroid-wrong cases, adds zero errors, and still has one error shared with centroid.

## Interpretation / decision
**PASS E24 as a restricted scientific transfer gate.** The physically inspired single scalar input suffix-square load correction `Q_x = sum_l (sum_{j>=l} x_j)^2` with coefficient trained only at m16 transfers to m8/m12/m20/m24 better than similarly transferred near/far and centroid corrections. R4 slope interpolation is also supported when per-condition ADC reference calibration is allowed. Stronger within-condition refit controls do not erase the benefit in this sample. E23D's m16 positive result therefore **is not confined to m16**.

**NOT a finished FYP or publication-grade contribution.** The source uses **assumed** ohms/segment; a fixed 32-row single-NFET topology differs from local-floating 2T1MTJ 256×256; student static MTJ has no random spread; per-(m,R) ADC fullscale/count centroids have material hardware/calibration cost; Q extraction and multiplier cost unmeasured; network-level W4A8/MNIST performance not calculated. Quadratic wire-drop compensation has established conceptual prior art; present demonstration does not establish a new algorithm.

**Avoid another broad nominal-R sweep.** Physical credibility now dominates: authorize/recover actual 2T1MTJ geometry or PEX-derived effective BL/SL impedance, verify real 256-row multi-column loading and sense interface, add fixed per-chip resistance spread and report whether Q-transfer survives. Only then connect to exact W4A8 network counts and infer task-level failure boundaries. The observed m24 residual is a good **bounded failure-regime boundary** to investigate; don't call it intrinsically irreversible.

## Decision for Prof Fong / CA2
“Using GF access-transistor DC read currents with an explicit assumed resistive bitline, we confirmed that an input-only suffix-square loading statistic, trained at m16, reduces held-out decoded-count errors more than near/far and centroid correction at m8/12/20/24 without refitting its spatial coefficient. At assumed R5 the 7-bit wrong count is **7/528**, vs centroid **26/528**, raw **124/528**. It still fails for high activity (m24 gives 7/108 errors) and all Rs are assumptions, not extracted GF PEX. Our next priority is validating whether this physics-informed design rule survives actual 2T1MTJ interconnect geometry and MTJ variation, followed by inference-level testing. This is a predictive engineering result, not a claimed novel IR-drop compensation invention.”
