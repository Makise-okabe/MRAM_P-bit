# E22 — completed NUS GF Spectre 17-count ADC-precision × assumed-line-R study
**Student executed:** 2026-11-04 16:21–16:26 timestamps; user's pasted terminal log, recorded after original E22 preregistration. **Physical evidence tier:** foundry GF hvtnfet compact transistor simulation + custom static MTJ, 32-row constructed shunt readout with assumed distributed BL resistances, **not** GF-extracted 256x256 PEX, no physical ADC, read-energy measurement, device mismatch, or whole-network inference.

## Executed reproducibility
- E22 Python selftest PASS; GF Spectre all chunks completed. R/segment **ASSUMED** 0,1,2,3,5Ω. All **17 feasible counts** n0..16 at m=k=16; 6 CAL and 12 independent DEV spatial masks/count; **306 masks per R, 1,530 Spectre DC cases**, 204 DEV masks per R. Identical masks across all five Rs (five repeated observations for same 306 patterns, not five independent chips).
- Private NUS results: `~/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162140_178/e22_results.json`; ADC analysis `.../E22_ADC_REGIME.json`. Model operator historical VREAD=.05V, VWL=.8V, nominal static MTJs; no MTJ variability or real comparator offsets.
- ANALYZE stage uses 17 *R0-CAL* centroid currents and frozen mathematical uniform ADC current window, no readjustment of fullscale as R increases. ADC codes are classified by nearest **quantized R0 centroid**; this is not a CAL-optimized bin-to-count classifier for each R. `b=0` in output labels means **continuous ideal scalar-current nearest nominal centroid**, not 0-bit physical ADC. Correction policies: raw, R-CAL global offset, and R-CAL offset+near/far input-position regression.

## Actual student-run DEV wrong-count numbers (out of 204 independent mask identities per R)
Each cell `continuous / 4-bit / 5-bit / 6-bit / 7-bit`:
| Assumed R Ω/segment | RAW | OFFSET ONLY | OFFSET + NEAR |
|---|---|---|---|
| 0 | 0 / 12 / 0 / 0 / 0 | 0 / 12 / 0 / 0 / 0 | 0 / 12 / 0 / 0 / 0 |
| 1 | 140 / 122 / 172 / 159 / 143 | 1 / 15 / 35 / 9 / 2 | **0 / 13 / 33 / 4 / 0** |
| 2 | 192 / 192 / 192 / 192 / 192 | 23 / 24 / 57 / 34 / 25 | **17 / 20 / 59 / 32 / 19** |
| 3 | 192 / 192 / 192 / 192 / 192 | 70 / 50 / 77 / 71 / 77 | **57 / 45 / 78 / 64 / 62** |
| 5 | 192 / 192 / 192 / 192 / 192 | 115 / 95 / 117 / 124 / 118 | **124 / 91 / 111 / 122 / 123** |

CAL global current offset: R0 0, R1 -1.093µA, R2 -2.145µA, R3 -3.16µA, R5 -5.083µA. Near/far fitted current slope: R1 +0.1014µA/count, R2 +0.1961µA/count, R3 +0.2846µA/count, R5 +0.4450µA/count.

## Immediate interpretation / audit caveats
1. **Raw R2, R3, R5 has exactly 192/204 wrong**, i.e. 16 count classes ×12 errors and a remaining class's 12 successes. This strongly suggests ADC/reference saturation or systematic nominal-current misalignment, NOT that 94.12% error is irreducible device noise. Confirm decoded output histogram and ADC saturation before declaring a failure regime.
2. **Non-monotone bit-depth accuracy in this particular nominal-centroid decoder** is NOT proof that higher precision physically harms accuracy. With a shared fullscale, a higher-bit nested uniform quantizer contains the lower-bit code; an *optimal* decoder could always recover the lower-bit decision by ignoring extra LSBs. Therefore any degradation under higher b is caused by the specific imperfect nominal codebook/rule (or fitting/test uncertainty), not an intrinsic loss of information.
3. At R0, 4bit cannot encode 17 distinct count levels through only 16 uniform bins. 12/204 errors observed; 5+ bits succeed in this nominal noiseless setting.
4. CAL-offset+near improves continuous counts to 0/204 at R1, 17/204 at R2, 57/204 at R3, but makes R5 *worse* than offset-only (124/204 vs115/204). This defeats blanket claims that spatial correction always helps at stronger parasitic.
5. **First promising scientific phenomenon:** a fixed nominal converter and naive calibration can cross a rapid breakdown when wire drop is applied, and the cheap input-position correction's effectiveness is regime-limited. Need stronger per-R CAL affine/range and multi-level decision-threshold calibration before treating it as non-recoverable count ambiguity.
6. Distinguish per-R CAL-fitting of spatial/offset from deployable global calibration: the experiment's CAL oracle knows R condition, which may not be directly available at runtime. No task-level accuracy result/novelty yet.

## Required E22B no-new-Spectre falsifier
From private `e22_results.json`, compare:
- frozen R0 nominal codebook (existing);
- R-calibrated gain+offset normalizer and R-calibrated 17-count centroid decoder;
- fixed ADC reference window versus recalibrated (per-R) ADC fullscale, charging reprogrammable reference overhead;
- continuous no-quantization baseline and direct sampled adjacent-count current overlaps;
- same-bit-depth fair controls on exactly the same held-out DEV masks and CAL-only fitted parameters.

**GO** only if a nontrivial residual physical-count ambiguity/boundary persists after strong conventional CAL-only recalibration and can be predicted on independent DEV patterns better than simple margin/near-count controls. **NO-GO** for a claim of 'more bits intrinsically worsen decoding' or a claim of R>=2 physical catastrophe based only on frozen R0 reference and nearest-centroid rule.

**CA2 status:** actual 1,530 NUS GF-model Spectre cases COMPLETE; decoder interpretation under audit. Keep all negative and positive results.
