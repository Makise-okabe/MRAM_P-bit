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
