# E36 — GF 256-row x 4-column high-activity current screen (actual NUS run)

**Date:** 2026-11-05 Singapore. **Status:** USER-EXECUTED; complete NUS Spectre DC data according to posted run log. Repo source commit `9c8017d687c417bc118963276b59a0d637f60312`. Original logs, source decks and raw current JSON remain PRIVATE on NUS; no foundry decks or model text are published here.

**Private run:** `~/mram_private/E36_activity_GF/E36_256x4_20261105T052633Z_28/E36_RESULTS.json`. Launcher log `~/mram_private/E36_activity_GF/E36_pilot_20261105T052632Z_19.log`. E01 packet SHA256 `400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a`, E30 source SHA256 `f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52` verified by user run.

## Circuit and evidence class

Actual NUS Spectre GF compact access-NFET + *student static MTJ* nominal DC-current solutions, 256 physical rows x 4 simultaneously modelled columns, identical resident weight states recovered from frozen E30. Three read arms per scenario: ideal interconnect; illustrative BL ladder **0.25 ohm per row-segment**; that BL ladder plus illustrative **0.25-ohm shared return**. Gate lines ideal. **No actual 1T1 PEX, MTJ mismatch sampling, physical ADC, read transient, 256-column array, full signed W4 neural bitplanes, or end-to-end inference.** E36 uses synthetic spatial masks with *activity count m* selected from frozen real E01 logical 256-group histogram, NOT actual E01 activation masks.

Pilot design: `m = 24, 56, 128` (24 prior baseline, 56 observed E01 ~P90, 128 observed maximum). Each m: three overlapping spatial sampling pools (indices 0..191, 64..255, 0..255), two independent sampled masks per pool = six scenarios x four columns = 24 column-observations per electrical arm. 18 scenarios total; 9 batches x 3 arms = 27 successful DC Spectre batch runs, solving four columns per scenario. C0 P-state counts differed by sampled mask; do not attribute every difference exclusively to m.

## Actual posted results

| m | Column-observations per arm | Mean absolute BL shift vs ideal (uA) | Maximum absolute BL shift (uA) | Maximum additional shared-return shift vs BL-only (nA) |
|--:|--:|--:|--:|--:|
| 24 | 24 | 5.3430732203 | 7.2461349592 | 233.3512861 |
| 56 | 24 | 24.7196321149 | 35.2196459585 | 1112.0003266 |
| 128 | 24 | 109.7025951714 | 149.2974698427 | 4769.3380364 |

Thus activity m increased 5.33-fold (24->128) while mean absolute assumed-wire BL deviation increased approximately 20.53-fold on these specific sampled masks. This is **activity-associated nominal nonlinear wire loading in a constructed electrical model**, not extracted GF hardware error magnitude or a measured trend with confidence intervals. The extra assumed shared SL shift also grows but is smaller than assumed BL-only shift in this pilot. These outcomes are raw-current deviations, **NOT decoded-count errors, signed MAC error, SNR/SNDR, BER, or inference accuracy**.

C0 true P-state count ranges in pilot masks: m24 -> 9..16; m56 -> 19..32; m128 -> 58..68. These ranges are not representative of all E01 bitplane counts. A previous E31 24-active-row Q decoder had 0/36 errors on C0 n11/12/13; it **has not been validated** at m56 or m128 and cannot simply be reused as though calibrated there.

## E01 activity scope

Frozen E01 software histogram: 12,316 nonempty group-256 reads (all eight stored binary arrays), mean m=32.201, P50=29, P90=56, P99=89, max m=128; 7,354/12,316 (59.7%) exceed m24, 804 have m>=64, 22 m>=110. This describes **logical full-256 grouping**; physically simultaneous WL activity remains conditional on the read scheduler/driver/ADC design. The 256-group histogram is unchanged by row permutation, so 8 equivalent run-index histograms are not independent repeated experiments.

## Interpretation and next decision

- E36 supports the *motivation* for a high-activity read nonlinearity study under stated assumed wires, rather than implying that a narrow nominal m24 Q-success settled 256-row reliability.
- It **does not** establish residual post-Q count errors, neural error, energy-saving intervention or new algorithm novelty. High-m current shifts can still be addressed by proper per-m calibration and ADC design; compare strong baselines first.
- **One research contribution** under investigation: runtime-feature-conditioned prediction of **post-calibration joint signed-MAC risk**, used for cost-constrained selective digital recovery. Models/PEX and W4A8 replay are validation work, not separate algorithm novelty claims.
- Next fastest informative software gate: connect real frozen W4 signed bitplanes and paired activation masks to a model with observable runtime features and CAL-only fitted error distributions; compare joint-risk selection against independent per-plane scores, calibrated margin, significance-prefix, fixed high ADC precision, and no recovery under equal declared total cost. Use literature-anchored sensitivity assumptions only if clearly separate from GF-measured parameters. Without joint signed-plane data, any inferred energy-accuracy frontier is *hypothetical*, not a measured GF inference result.
- Physical credibility gate E32 remains real 1T1 BL/WL/SL geometry and extracted RC; cannot treat 0.25-ohm ladder as PEX. Preserve and hash private netlist and raw current results.
