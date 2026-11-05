# E33 — NUS NUMERICAL RESULTS OBSERVED; MARKDOWN EXPORT FAILED UNDER ASCII (2026-11-05)

**Evidence status: E33 numerical experiment COMPLETED in the user-posted NUS terminal output, but one-shot E33+E34 workflow NOT fully completed.** Execution source commit `4232c90e6c5013f610245240b00e7ebb926daeba`. Frozen private E30 source SHA `f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52`, private E31 source SHA `78657894903388fe35bef51002786331e8935c916436eaf58ac28b273c69e023`. First run directory `~/mram_private/E33_E34_OFFLINE/20261105T041013Z_6504/`. All 3 circuit arms × 8 predeclared bit depths produced E33 numeric outputs before the export error. The code writes `E33_ADC_SWEEP.json` **before** trying `E33_FOR_PROF_FONG.md`, so the numeric JSON should remain privately present (verify on NUS; no direct access from this chat). Python 3.6 NUS ASCII default text encoding rejected the Unicode em dash in the Markdown title: `UnicodeEncodeError: 'ascii' codec can't encode character '\\u2014'`. **This is a FILE EXPORT failure, not an ADC/circuit computation failure.** E34 DID NOT BEGIN (bash set -e).

**Actual user-run printed E33 numerical results, 36 new E31 DEV masks, 9 original E30 CAL masks, same `n=11,12,13`, fixed hypothetical fullscale from original ideal E30 CAL and uniform mid-rise ADC. Bit-depth columns below are decoder WRONG counts/36.**

| ADC bits | Ideal wire: Global / Q | Assumed BL, independent SL: Global / Q / mean-row / half-row | Assumed BL + shared SL: Global / Q / mean-row / half-row | LSB µA |
|---:|---|---|---|---:|
| 4 | 12 / 12 | 19 / 19 / 9 / 9 | 19 / 20 / 8 / 8 | 3.303319 |
| 5 | 0 / 0 | 16 / 2 / 9 / 7 | 15 / 3 / 8 / 6 | 1.651660 |
| 6 | 0 / 0 | 16 / 0 / 10 / 12 | 15 / 0 / 10 / 11 | 0.825830 |
| 7 | 0 / 0 | 16 / 0 / 10 / 10 | 15 / 0 / 9 / 10 | 0.412915 |
| 8 | 0 / 0 | 16 / 0 / 9 / 10 | 16 / 0 / 9 / 10 | 0.206457 |
| 9 | 0 / 0 | 15 / 0 / 10 / 10 | 15 / 0 / 10 / 10 | 0.103229 |
| 10 | 0 / 0 | 15 / 0 / 10 / 10 | 15 / 0 / 10 / 11 | 0.051614 |
| 12 | 0 / 0 | 15 / 0 / 10 / 10 | 15 / 0 / 10 / 11 | 0.012904 |

All 24 arm×bit depth cases report **0 clipped DEV observations** under the fixed hypothetical fullscale. Nominal ideal-wire one-step count separation was previously ~1.835 µA. At 4 bits, the 3.303 µA ideal-ADC LSB exceeds one nominal count step, so numerical count aliasing is unsurprising even for ideal wiring (12/36 errors). At 5 bits (LSB ~1.652 µA), assumed BL+SL Q has **3/36** residual count errors and assumed BL independent-SL Q **2/36**; at **6–12 bits Q has 0/36** for both assumed-BL arms. On the same tested data and model, continuous mean-row and far-half spatial feature baselines remain at 8–12 errors/36 for 6–12 bits in assumed-R arms, indicating the calibrated nonlinear position-Q feature does more than those **specific linear** spatial controls. This is not a hardware energy/bit-cost result and does not prove novelty against more advanced low-cost spatial calibration.

**Critical limits:** These ADC errors are **mathematical quantization effects on previously solved GF Spectre currents**, not actual physical ADC or new NUS Spectre simulations. BL/SL resistors remain **ASSUMED**, not 1T1 PEX; only C0 count classes 11/12/13 and m=24; no chip/device variation, noise, settling, ADC circuit, actual full 256×256 or signed W4A8 neural inference. Do not say “actual 5-bit ADC has 3/36 errors” or “actual hardware requires 6 bits”; the ADC range is an extrapolated choice, and converter cost/headroom is unknown. No nonzero post-Q decoded count errors persist beyond 5 bits in this constructed model.

**Fix committed:** `experiments/e33_adc_precision_frozen_gf.py` and `experiments/e34_four_column_gf_generalization.py` explicitly use UTF-8 when writing output JSON and Markdown. No numerical E33 algorithm/baseline altered. Re-run NUS `git pull --ff-only && bash experiments/run_e33_e34_nus.sh` to regenerate clean professor exports and complete E34. NO new Spectre. Mark E34 as pending until actual user log.

---

# E33 — Frozen-CAL ADC precision and failure-boundary screen on E30/E31 GF currents

**Date:** 2026-11-05 SGT. **Status:** CODE COMMITTED, USER NUS RUN PENDING. **Original research direction:** F1 inference-failure prediction; F3 mapping remains a conditional intervention; F7 Ising paused (ADR-0010).

## The question (one testable hypothesis)
E31 reported 0/36 held-out decoded-count errors using E30-trained input-position Q on nominal GF-transistor + student static MTJ currents. That success was evaluated on *continuous-precision simulated current*, without an actual ADC. **Does finite ADC quantization make the Q-corrected counts fail, and does Q predict those failure boundaries better than equally cheap continuous spatial statistics?** This experiment tests a *mathematical uniform-ADC sensitivity model*, not real converter noise/performance and not physical 1T1 PEX.

## Fixed prior measured/simulated evidence
- E30 private `~/mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30_RESULTS.json`; SHA256 `f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52`.
- E31 private `~/mram_private/E31_1T1/E31_256x4_20261105T033721Z_2792/E31_RESULTS.json`; completes 36 new DEV masks (18 seen-area-family, 18 unfamiliar-area-family), 256 GF access NFET + student static MTJ rows ×4 simultaneous columns.
- GF compact transistor currents were **actually solved on NUS Spectre** under **ASSUMED** 0.25 Ω per BL row segment and 0.25 Ω lumped shared return, 50mV read and 0.8V WL historical screening bias. This is **NOT** a new 1T1 layout PEX, foundry-qualified MTJ or measured ADC. E31 nominal continuous-precision Q count error: **0/36**; global error **15/36** (each assumed-R read arm).
- Only one nominal resident weight map, m=24, C0 true n ∈ {11,12,13}; 36 new DEV activation masks are not independent chips or full network data. No MTJ switching/variation, CMOS mismatch, read-disturb, noise, timing, ADC physical schematic or signed-bitplane W4A8 neural task result.

## Predeclared E33 method
Executable [`experiments/e33_adc_precision_frozen_gf.py`](../../experiments/e33_adc_precision_frozen_gf.py), batch [`experiments/run_e33_nus.sh`](../../experiments/run_e33_nus.sh).

1. **Frozen current source**: E30 original 9 CAL input masks only; E31 exactly 36 held-out DEV masks, no DEV retraining or selection. Same 3 arms: ideal wire independent, assumed BL independent SL, assumed BL+shared SL.
2. **Fixed ideal ADC fullscale** (CAL-only *design assumption*, shared across ALL bits/arms): use original **E30 ideal-wire CAL** GF currents at n=11,12,13 to calculate ideal adjacent current/count step `dI=(mean(I13)-mean(I11))/2`. Extrapolate nominal endpoints `I(n=0)=I12-12*dI` and `I(n=24)=I12+12*dI`; extend both endpoints by **10% of nominal span** as fixed guard. These endpoints are deliberately **extrapolated**, not a measured 0..24 count sweep; report clipping explicitly.
3. **Ideal mid-rise uniform ADC**: mathematically map every CAL/DEV GF current to one of `2^b` codes, reconstructed at bin center. Fixed bit-depth set **b = 4, 5, 6, 7, 8, 9, 10, 12**. No dither, comparator offset, thermal noise, nonlinearity, aperture jitter, settling time or ADC layout/energy modeled. Do NOT label the resulting nominal count errors as physical MRAM BER.
4. **Strong CAL-only decoders at every b and arm**, using the SAME 9 quantized CAL currents:
   - pooled global 3 count levels;
   - known-area additive offset with predeclared GLOBAL fallback for unseen areas;
   - continuous `MEAN_ROW` input spatial centroid (learn class intercepts plus CAL-only linear slope);
   - continuous `FAR_HALF_FRACTION` input occupancy (comparable near/far spatial indicator);
   - known-input activity **Q** with prefix/suffix orientation chosen by CAL-only residual.
   For each continuous feature, one common slope plus n-class intercepts; true n is used as an *offline calibration label* only, never a runtime feature.
5. **DEV gate**: print wrong-count counts and MAE (ALL 36, seen 18, unseen 18) for each decoder; report ADC LSB, input code clipping, class-code collapse and quantization error. Show whether a failure is caused by ADC resolution versus BL spatial distortion.
6. **No fishing**: report ALL predeclared bits, both Q orientations only via CAL SSE, and all comparisons. No RETUNING ADC fullscale or choosing a bit-depth to manufacture an advantage. If Q ties other continuous features, the simpler baseline wins. A 4-bit or 5-bit information-limit failure does not establish N2 recovery novelty.

## Exact NUS command
```bash
cd ~/MRAM_Path_Finding
git pull --ff-only
bash experiments/run_e33_nus.sh
```
Outputs under `~/mram_private/E33_1T1/E33_<timestamp>/`: `E33_ADC_SWEEP.json`, sanitized `E33_FOR_PROF_FONG.md`, `E33_run.log`. The GitHub repo contains **code + protocol only** until actual user NUS output is returned. Never push licensed netlists, PDK or private full current data to public GitHub. If the script fails, record the blocker, not invented results.

## Interpretation / novelty gate
- **At 7–12 bits Q and near/far/centroid all correct**: ADC precision does not create residual nominal errors at these chosen inputs; N2 selective exact recomputation remains unmotivated. Next = actual 1T1 wire PEX, physical ADC/error and variation.
- **Finite precision creates errors but Q matches simple continuous features**: characterize the failure boundary and information limit; not a new algorithm.
- **Q retains advantage over strong continuous features at the same ADC bit depth**: useful predictor-support result *under this hypothetical ADC model*, NOT physical or NN novelty. Verify across actual interconnect and more representative workload/chip draws before claiming contribution.
- **Failures concentrate at coarse resolutions or clipped codes**: expected quantization effect. Report converter range and cost instead of calling it an MRAM hardware failure. The algorithm cannot recover information absent from the ADC without actually paying for a remeasurement or digital replacement.
- **Final F1 target** remains predicting **actual signed-W4A8 inference failure** *after* cheap correction, and improving decisions at equal system cost against calibrated margins, spatial references, independent-plane scores and zero intervention. E33 only tests a C0 count-level ADC idealization.

## Parallel E32 physical milestone
[Actual 1T1 BL/WL/SL extraction](2026-11-05-E32-1T1-physical-interconnect-extraction-NEXT.md) is the binding physical credibility dependency. It requires a real GF 1T1 CMOS+metal layout/line extraction with externally modeled student MTJ if necessary; old 2T1MTJ DSPF cannot replace it. E33 is short *offline software diagnosis* while E32 layout proceeds, **not** permission for additional arbitrary wire-resistor sweeps.
