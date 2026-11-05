# E30P NUS VERIFIED — 2026-11-05 11:27 SGT; NEXT = E31 FROZEN-CAL NEW-MASK TEST

User executed [`e30p_offline_strong_baselines.py`](../../experiments/e30p_offline_strong_baselines.py), no new Spectre, on actual E30 GF-current private source SHA256 `f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52`. E30P private result `~/mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30P_baselines_20261105_112745.json`. E30P printed **global 0/9, 6/9, 6/9** for ideal, assumed BL, assumed BL+SL. **All three stronger CAL-only references (area offset, per-area count bank, input-mask Q) produced 0/9 DEV for every arm**. Input-Q direction chosen on CAL only: prefix for ideal, suffix for assumed BL arms. No extra run has been made to validate recovery/cross-bitplane errors.

Same-count n12 low-row vs high-row current delta `9.485555790824165µA`, 5.1687402993 nominal ideal count-step equivalents; shared-SL extra C0 current max shift `230.88539148437803nA`. CAL shared-SL area offsets (µA): ROW_LO `+4.244794550775694`, ROW_HI `-5.215347147225979`, DISTRIBUTED `+0.9705525964502945`. These are **user-run, physically constructed GF-transistor simulated currents at assumed 0.25Ω/BL segment and 0.25Ω shared return, NOT 1T1 extracted PEX**. One CAL and one DEV pattern per (area,count), a single nominal device map; 0/9 does not certify a BER. Naive 6/9 is NOT a residual that N2 selective digital recomputation must fix. **Decision:** keep physical-array scope 1T1; freeze all E30 CAL and run [E31](2026-11-05-E31-frozen-cal-256row-generalization-PENDING.md) on fresh same-state 256-row masks including unseen spatial families; do not re-use DEV to retune Q.

---

# E30 — ACTUAL NUS GF RESULT: LARGE SPATIAL READ DISTORTION; GLOBAL CAL 6/9 WRONG, SIMPLE SPATIAL CAL 0/9 (2026-11-05)

**USER-RUN COMPLETE:** E30 256 rows ×4 jointly simulated columns, 24 active rows/column, 18 scenarios. 3 electrical arms ×9 chunks (each chunk 2 scenarios×4 columns), all 27 Spectre arm/chunks finished. Actual user-pasted log and private NUS JSON:
`~/mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30_RESULTS.json`. Commit executed `b3669959e41b2eb570d0660d04e779bd553f2736`. Models: GF access NFET and student-owned static 2-terminal MTJ, **NOT physically extracted 1T1MTJ PEX**. Assumed BL R=0.25 Ω **per one of 256 row segments** and shared-return SL R=0.25 Ω for 4 columns. This is an **illustrative and potentially unrealistic** wire model; no external/intertile geometry justification. The physical 1T1 array is not built.

**User's printed C0 CAL-mean current centroids (µA):**

| arm | n=11 | n=12 | n=13 | Global-centroid DEV errors |
|---|---:|---:|---:|---:|
| ideal independent | 103.7021897605 | 105.5373672392 | 107.3725447180 | **0/9** |
| distributed 0.25Ω BL, independent SL | 98.4242217964 | 100.0857531608 | 101.8269034114 | **6/9** |
| distributed 0.25Ω BL, shared 0.25Ω return SL | 98.2203891120 | 99.8818957677 | 101.6192408179 | **6/9** |

**Important CAL-only reanalysis from the exact numbers in the pasted NUS run log, independently recomputed in the chat (NOT a new NUS simulation):**
- Under shared-SL condition, **the nine held-out DEV cases are all classified correctly (0/9) if using per-spatial-group CAL references**, with groups `ROW_LO`, `ROW_HI`, `DISTRIBUTED`. This uses 9 CAL points for 9 area×count centres (one per stratum); **overfit risk**.
- Also **0/9 for simpler CAL-only additive area-offset correction**, using shared global count centres plus three CAL-learned offsets; each area offset is averaged across its three count classes. On the same user-pasted currents, the offsets are: `ROW_LO:+4.24479455 µA`, `ROW_HI:-5.21534715 µA`, `DISTRIBUTED:+0.97055260 µA`. Same 0/9 for distributed BL and independent return (`+4.26204, -5.23655, +0.97450 µA`).
- The six global mistakes under shared-SL arise in known positions: `ROW_LO n11→n13, n12→n13; ROW_HI n12→n11, n13→n11; DISTRIBUTED n11→n12, n12→n13`. These are dominant **input-position bias** failures, rather than evidence of intrinsic bitplane covariances or recovery novelty.
- Same *ideal count n12* CAL current `ROW_LO=104.04971794µA` versus `ROW_HI=94.56416215µA`, a difference **9.48555579µA**. The no-R ideal one-count step from `n11→n12` is ~**1.83517748µA**; thus the spatial shift equals about **5.17 ideal count steps**. This strong position-dependence is a result of the **assumed** 256-stage 0.25Ω ladder; cannot claim realistic geometry without extraction.
- The shared-return increment is ~0.18–0.23µA per printed C0 case, **much smaller than the ~9.49µA near/far same-count BL effect**; adding that return did not change 6/9 global decoder mistakes on the tested samples. Does not rule out a common-mode effect at other fan-ins/columns.

**Critical inference:** 6/9 is a **global-current decoder mismatch across spatial groups in this constructed model**, NOT a 66.7% MRAM physical BER, NOT an independently drawn-chip trial and NOT a sign-aware four-plane recovery use case. Only 1 CAL and 1 DEV mask per spatial group×count class, from a single nominal chip/weight map. We should not now apply a recovery algorithm to those mistakes without comparing simple position/Q correction, much stronger baselines and actual geometry.

**Next immediate work: zero-new-Spectre OFFLINE E30P analysis of the already existing JSON**, code [`experiments/e30p_offline_strong_baselines.py`](../../experiments/e30p_offline_strong_baselines.py). It compares global vs CAL additive area offsets vs per-area count reference bank vs a continuous CAL-trained `Q` input-mask position statistic (two possible row orientations selected by CAL SSE only). Run on NUS private E30 JSON to validate the independently calculated 0/9, and report whether a lower-complexity input-Q correction can remove errors. **E30P was not run on NUS when this note was written.** No additional GF Spectre simulations or artificial R increases are justified before this benchmark.

**Next larger physical gate:** User wants 256-row and eventually 256×256; E30 achieved the 256-row length, but only 4 columns. A follow-on 256×16 control could test column-loading scale, but would still require assumed resistor values; preferably obtain real BL/SL geometry from a new 1T1 layout and validate wiring/ADC before large run. Need statistically adequate CAL/DEV mask repetitions and eventually fixed-chip mismatch for reliability estimates; four signed bitplanes are not automatically four simultaneously coupled columns or a full W4A8 result.

---

# E30 — Scale 1T1MTJ CIM to 256 rows before judging recovery

**Created 2026-11-05. Status: executable code committed; NUS user has NOT yet executed E30.** The user correctly noted that four-row, m=2 ideal/low-impedance tests are inappropriate for rejecting large-array count errors, especially when the intended CIM hardware has 256 physical rows. Small arrays *can* have read/ADC/mismatch errors, but E28S's 0/28 errors cannot be extrapolated to a 256×256 target.

## Experimental objective
**Can position and shared return loading cause digitally consequential count errors when an actual GF-transistor 1T1-like network has 256 physical rows, even with only 24 activated rows?**

The immediate **real NUS Spectre test** is 256 physical rows × 4 physical/conceptual columns = **1,024 access NFET + 1,024 student static MTJ elements per scenario**, with all **unselected rows still present**. This is the 256-row target **depth**, not the full 256×256 array **width**. The shared SL coupling is constructed in the same circuit across all four columns. The WL sources use the same logical row mask but are separately ideal-driven: **there is not yet a shared WL R/C network or a qualified physical read driver.** One user-selected 1T1 architecture; no legacy 2T1 PEX.

## Evidence strength and caveats
- GF compact transistor with student static MTJ: real Spectre model solve, not arbitrary analytical currents.
- **BL segment R=0.25Ω and shared SL return R=0.25Ω are explicitly ASSUMED sensitivity values, NOT PEX/geometry-derived.** No GF-extracted 1T1 interconnect exists. 50mV read / 0.8V WL historical screening bias not re-qualified for read disturb or ADC headroom. Do not call numerical errors "measured physical 1T1MRAM errors." Do not claim a foundry-qualified 1T1 bitcell.
- Three matched arms, exact same frozen masks, resident P/AP columns and device models: (1) ideal BL wire + independent return, (2) distributed assumed BL resistance + independent return, (3) same distributed BL plus a common assumed SL return for four simultaneously solved columns. All four columns receive the same selected-row mask.
- **18 scenarios** = low row-index / high row-index / distributed row-index pools × target C0 count \(n=m/2-1,m/2,m/2+1\) × independent CAL/DEV masks. Here default \(m=24\), count classes 11,12,13. Same full 256-row resident P/AP map across scenarios; only input WL mask changes. Other three columns carry independent resident weights and act as neighboring loads. One stored-state/weight map is shared between CAL/DEV as the same nominal chip; **CAL and DEV split masks, NOT devices/chips**.
- Low row index vs high row index labels are **not claimed to be physically near/far** until actual electrical terminal position is checked. Spatial issue test deliberately applies different positions under the simulator's resistor ladder.
- Offline nearest CAL mean-current (stronger than a completely raw global fixed threshold) for three C0 count classes, tested on held-out DEV masks. Numerically report any non-monotonic count centroids as a result rather than aborting. No physical ADC, comparator offset/noise, timing or energy; no full signed W4A8 inference. Per-column exact current vectors retained for future legitimate combined-effect modeling.
- E28S had 0/28 decoder errors under four-row/m2 and assumed common SL R≤20Ω; this did not test a long BL or high m. E24 at 32 rows and **assumed BL 5Ω/segment**, m24 had 7/108 residual wrong counts **after** Q correction; again not PEX. No physical-scale reliability extrapolation permitted.

## NUS commands

\`\`\`bash
cd ~/MRAM_Path_Finding
git pull --ff-only
bash experiments/run_e30_256x4_nus.sh
\`\`\`

Private E30 result: \`~/mram_private/E30_1T1/E30_256x4_.../E30_RESULTS.json\`. The real GF source, model and simulator outputs stay private; the public GitHub source is [e30_large_1t1_gf_cim.py](../../experiments/e30_large_1t1_gf_cim.py). Each completed chunk writes partial actual current data to the private manifest; if a later Spectre chunk stops, earlier chunks remain on disk. **No result claimed until the NUS user run completes.**

After the 256×4 physical-behaviour screen succeeds, optionally increase **columns** to 16 (4,096 GF NFET+MTJ cell branches per scenario) by running \`python3 -u experiments/e30_large_1t1_gf_cim.py run --rows 256 --columns 16 --active 24 --chunk-scenarios 1 --timeout-sec 480\`. This is still a constructed model with assumed R. A full 256×256 (65,536 cell instances) **netlist generation only** can be staged with \`python3 experiments/e30_large_1t1_gf_cim.py generate --rows 256 --columns 256 --active 24 --max-scenarios 1 --chunk-scenarios 1\`; **256×256 Spectre execution is blocked in code** until manageable physical/simulator resources and valid array-level periphery are confirmed.

## Decision and novelty gate
- First outcome: whether 256-row current distributions show location-, occupancy- or shared-return-dependent differences, and whether a simple CAL-trained C0 count decoder fails on held-out masks in this constructed GF model.
- Even if errors appear, **do not celebrate an algorithm novelty**: test against Q, centroid, spatial calibration and count thresholds, and check the assumed R against future actual 1T1 layout parasitics.
- If errors are real for actual geometry and can be associated in the **correct** signed W4A8 bitplane mapping (four planes across two packed arrays, A8 cycles), then test the N2/E29A selective replacement against equal total digital compute cost contextual-prefix, bias-aware independent scoring and zero-repair.
- A full 256×256 **physically extracted** array requires actual one-FET cell layout, full shared WL/BL/SL routing, DRC/LVS/xACT and realistic readout drivers, or a validated hierarchical PEX-equivalent with explicit intertile R/C. Constructing 256×4 or generating 256×256 schematic nets does **not** achieve this.
- If physical interconnect yields weak/no computational errors after strong CAL correction, the correct finding may be that higher-level digital recovery is not worthwhile at tested operating conditions.
