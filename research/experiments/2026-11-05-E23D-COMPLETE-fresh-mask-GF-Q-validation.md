# E23D — Completed fresh-mask GF Spectre confirmation: suffix-load Q transfers to unseen R4

**Date:** 2026-11-05 Singapore. **State:** COMPLETE, user-provided NUS Singularity terminal evidence, after a preregistered E23D script was committed. This is the strongest independent held-out validation yet of the E22C suffixQ model, but is still a **nominal GF access-transistor compact-model circuit with explicitly assumed BL segment resistors and a student static MTJ**, not a GF 256×256 extracted macro. ADC is mathematical, not transistor-level. **No novelty/energy/MTJ mismatch inference.**

## Provenance / execution integrity
- User NUS path: `~/mram_private/E02_256x256/E23D/E23D_FRESH_20261104T170112_8187/e23d_fresh_results.json`; confirmation: `~/mram_private/E02_256x256/E23D/E23D_confirmation_20261105_010707.json`.
- Frozen E22 OLD training SHA256 `c79133fa5165be8ba2142e7cea78834f29db6a17446d8bbb13226efbfe4df965`. **NO calibration from fresh masks**; generated 408 distinct DEV masks (24 each × 17 n=0..16), explicitly excluded any old CAL and previously inspected DEV mask hash.
- Same fresh masks reused across R0/1/2/3/**4**/5Ω per segment, **2448 successful Spectre DC circuits**; GF `hvtnfet`, student static two-terminal `mtj_read_v0`, 32 shared-bitline NFET/MTJ branches, 50mV read / .8V WL historical voltages, m=k=16 fixed.
- **R4 is unseen in the OLD E22 CAL**; Q/near/centroid coefficient, 17 count centroids and mathematical ADC fullscale linearly interpolated **from OLD R3/R5 CAL**. R4 is an *interpolation* challenge, not out-of-range extrapolation or unseen geometry.
- Source `experiments/e23d_freshmask_q_generalization.py` on main. User log confirms all R chunks successful and full analysis completed. PDK sources and private per-mask currents are not uploaded to public GitHub.

## Actual seven-bit wrong decoded count /408 fresh cases
| Assumed R Ω/segment | Raw | Near-far count | Activation centroid | SuffixQ |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 0 | 0 |
| 2 | 12 | 0 | 0 | 0 |
| 3 | 40 | 9 | 0 | 0 |
| **4, unseen interpolation** | **79** | **34** | **2** | **0** |
| **5** | **111** | **55** | **9** | **0** |

- At R5, Q corrects **55/55** near-wrong events and **9/9** centroid-wrong events without causing any new wrong decisions. At R4, Q corrects **34/34** near and **2/2** centroid errors, no regressions. At R3, Q corrects **9/9** near errors, ties centroid.
- Assumed R5 5bit/6bit/7bit wrong per 408: raw **127/117/111**; near **64/65/55**; centroid **23/8/9**; Q **7/1/0**. Assumed R4 Q 5bit/6bit/7bit **4/0/0**.
- Sampled nonseparable adjacent class boundaries after 7b correction: R5 raw **16/16**, near **14/16**, centroid **2/16**, Q **0/16**; R4 raw 14, near 6, centroid 0, Q 0. Zero sample overlap is *not* a universal physical injectivity guarantee.
- Zero Q error in 408 stratified fresh masks at a single R has rule-of-three bound ~3/408=**0.735%** under independent-mask assumptions at the fixed chosen R, m=k=16, nominal device model; this is NOT a chip/device variation or PEX reliability claim. Testing the same masks at 6 Rs does not multiply independent sample size by six.
- Paired centroid vs Q at assumed R5 had 9 discordant cases all favoring Q (exploratory exact matched-pair two-sided p=0.00390625 if the comparison was fixed before these fresh masks); at R4 only 2 discordant cases (insufficient as standalone inference). P-values may overstate independence if the physical mask generator or trial conditions induce correlation; don't use as silicon-level validation.

## Scientific interpretation
**Positive:** A physics-inspired **input-only suffix-square loading statistic** with correction parameters frozen on an independent prior CAL sample **generalizes across NEW spatial placement masks** and an **interpolated unseen segment-R value**, outperforming both simple near/far and first-position-moment centroid for this one nominal 32-row resistive NFET+MTJ model. This overturns the overly-broad conclusion from earlier E20 n7/n8-only testing that Q has no unique advantage.

**Not yet established:** (i) novelty—quadratic line-current moments and IR-drop compensation have extensive prior art; (ii) generalization to **different input activity m, stored weight population k, 256-row physical lengths or multi-column interactions**; (iii) real GF extracted RC; (iv) fixed per-chip device mismatch or process corners; (v) actual ADC/reference/control area/energy or full trained-network inference success. E23D CAL programs a separate 17-count reference/current window for each assumed R except interpolated R4; this hardware/calibration burden must not be hidden.

**Primary FYP stays:** Characterizing Reliability and Failure Regimes of Memory-Centric Neural Inference Under Coupled Precision and Hardware Non-Idealities. Q may be a simple, physically justified **predictive correction component**, not a standalone proven invention.

## Immediate E24 gate
Next pre-register **cross-occupancy transfer**: vary activation m away from 16, and eventually weight k, with genuine fresh masks and separately identified *CAL reference overhead*. Do not assume the 17-centroid m16 ADC range transfers to m8/m24, since the ideal current itself changes with number of active MTJs. Compare equal-budget CAL current references and coefficients frozen from E22, and test against same-activity re-fitted controls to separate physical transfer from a calibration opportunity. Only after occupancy transfer should claims about broad W4A8 neural workload be advanced.
