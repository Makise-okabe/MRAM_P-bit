# E22B — Frozen CAL-only recalibration falsifier after E22 completed NUS GF simulation
**Date:** 2026-11-05. **Status:** executable committed; **NO actual E22B result until run on the user's NUS E22 JSON**. The previous E22 raw/offset/near results are [recorded separately](2026-11-05-E22-GF-fullcount-ACTUAL-results-and-decoder-audit.md).

## Hypothesis at risk
The preliminary E22 result (e.g. at assumed R=1Ω, near-corrected 5bit 33/204 vs 7bit 0/204) could be a consequence of freezing the nominal R0 ADC transfer and nearest quantized R0 class centroids, not an inherent physical penalty from increasing precision. At R≥2 raw 192/204 wrong likely indicates systematic reference failure. Recalibration is a **strong conventional baseline**, so test it BEFORE pitching a novel cross-layer failure predictor.

## E22B executable
`experiments/e22b_decoder_calibration_falsifier.py` (Python3.6 stdlib) imports `experiments/e22_gf_precision_regime.py` for exact parsing and quantization equivalence. Input: private `e22_results.json` containing ALL 1,530 user-executed GF hvtnfet + student static MTJ DC current cases. **No Spectre replay**.

Training: only R-specific **102 CAL** mask patterns, 6 per true count; evaluate same 204 held-out DEV masks/R, paired across R. All R values remain assumed bitline Ω/segment, not extracted geometry.

Per R, compare:
1. `frozen_r0_b{4,5,6,7}`: EXACT old E22 nominal uniform ADC and nearest quantized R0 count-centroid rule. **Must reproduce original RAW E22 per-bit error table** or stop as a code audit failure.
2. `cal_perR_continuous`: nearest mean of all 17 per-R CAL count levels, continuous-noiseless perfect-current readout limit.
3. `cal_perR_continuous_near`: input near/far count linear correction plus per-R CAL count centroids; no ADC quantizer.
4. `fixed_CAL_lookup_bX`: **same physical R0 ADC fullscale** but learn CAL output-code-to-count lookup after digitization. If the physical ADC saturates this cannot recover its lost bits, but it can correct nominal codebook mismatch without new analog references.
5. `reprogrammed_CAL_lookup_bX`: **hypothetical programmable ADC current fullscale** derived from min/max R-CAL readings with 5% CAL-span guard; CAL code-to-count lookup. This changes physical references, so area/energy/reconfiguration cost MUST be included before making performance claims.
6. `fixed_CAL_near_bX` / `reprogrammed_CAL_near_bX`: perform input near/far correction only **after digitizing the raw physical current**. No access to hidden pre-ADC DEV current; on 5Ω this must not pretend to recover an input that was clipped.
7. Count DEV inputs outside fixed and reprogrammed ADC window; report 16 adjacent true-count sampled-current gaps, and number of nonseparable **ordered threshold** boundaries, with/without near correction.

**Scientific interpretation safeguard:** With a common fixed range and nested 4/5/6/7 bit uniform ADCs, increasing precision never removes information available at lower precision—high-bit code can be truncated. The E22 observation '5 bits worse than 4 or 7 bits' is therefore a **policy/calibration effect, not an intrinsic information loss**. Finite-CAL lookup and per-R calibration can still overfit, so report all policies and note only six CAL samples/count. The 4-bit ADC cannot uniquely label 17 counts. Observed current-level overlap is not proven population BER.

## Run on NUS
```bash
set -euo pipefail
cd "$HOME/MRAM_Path_Finding"
git pull --ff-only
python3 -m py_compile experiments/e22b_decoder_calibration_falsifier.py
python3 experiments/e22b_decoder_calibration_falsifier.py --selftest
python3 -u experiments/e22b_decoder_calibration_falsifier.py \
 "$HOME/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162140_178/e22_results.json" \
 --out "$HOME/mram_private/E02_256x256/E22/E22B_calibration_audit.json"
```
Paste the summary `E22B R=...` lines, not model decks or proprietary PDK contents.

## Gate after independent DEV evaluation
- If R-specific calibrated analog current-decoding/ADC reference LUT makes the large E22 errors nearly disappear, **E22 failure map alone is not a new coupled physics result**. Report E22 as a calibration-ablation finding and design a realistic CAL-limited transfer/generalization experiment before E23.
- If many adjacent true counts remain nonseparable and substantial held-out errors persist after standard per-R CAL calibration, there is an actual **spatial count-current ambiguity** to characterize. Then E23 may target *predicting* the cross-over with a simple, testable feature, not promising an unspecified nonlinear ML predictor.
- If `reprogrammed` appears strong but `fixed` fails, note the required analog reference hardware and its unmeasured cost. If six CAL samples/n overfit, increase CAL only with independent DEV validation and fixed hyperparameters. Continue to acknowledge assumed R and missing PEX.
