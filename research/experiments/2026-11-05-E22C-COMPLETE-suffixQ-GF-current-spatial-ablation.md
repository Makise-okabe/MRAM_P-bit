# E22C — COMPLETED NUS GF-current spatial feature ablation: suffix-load Q wins the tested full-count screen

**Date:** 2026-11-05 (student pasted NUS Singularity output). **Evidence:** actual pre-existing E22 GF `hvtnfet` transistor-level + custom static MTJ currents, mathematically simulated ideal uniform ADC, offline CAL-only fitting. NO new Spectre run in E22C. **No extracted GF 256x256 PEX, no device variability, no physical ADC, no measured energy, no full MNIST classification or verified novelty.**

## Run integrity and provenance
- E22C script `experiments/e22c_spatial_feature_ablation.py`, selftest PASS. Python3.6 on NUS. Student output `~/mram_private/E02_256x256/E22/E22C_spatial_correction_ablation.json`; E22 source `~/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162140_178/e22_results.json`.
- Reused exactly 102 CAL + 204 DEV masks **per assumed R** from the 1530-case E22 Spectre experiment; 17 count classes n=0..16, 6 CAL and 12 DEV masks each, fixed **m=k=16**; R per segment in {0,1,2,3,5} Ω. **DEV was already inspected** through E22, E22B: results are retrospective/development evidence, not a pristine independent final validation.
- Per assumed R, R-specific 17 CAL centroids and one CAL-fitted spatial coefficient per feature; ADC input full-scale set using 102 CAL currents per R, 5% extra current-span range. The operational cost of per-R training, programming, converting and computing Q remains unmeasured.
- Input feature uses only known activation positions: `near=` active number in first 16 rows; `centroid=sum(row_index+1)`; `suffixQ=sum_l (sum_{j>=l} x_j)^2`; raw control. Actual DEV true count n used to SCORE ONLY, not as feature.

## Actual held-out count-decoding errors /204 with 7-bit mathematical ADC

| Assumed segment R (Ω) | RAW | near-count | centroid | suffixQ |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 0 | 0 |
| 2 | 6 | 0 | 0 | 0 |
| 3 | 17 | 3 | 0 | 0 |
| **5** | **60** | **25** | **5** | **0** |

At assumed R=5, **sampled adjacent-count nonseparable boundaries out of 16**: raw 14, near 9, centroid 1, **suffixQ 0**. Zero sampled overlap is not a theoretical guarantee; 204 DEV observations are small and stratified, 12 per n. At R3 all spatial corrections near/centroid/Q eliminated 7 raw range-overlap boundaries, but near still made 3 errors because of CAL centroid fit.

At assumed R=5 full quantized Q errors (continuous/4/5/6/7 bits): **0/41/1/0/0** out of 204, respectively. At R3 **0/19/1/0/0**. Four bits cannot separately encode 17 true count classes in 16 ADC bins.

**Paired R5 7-bit near vs Q**: Q corrects all 25 near-wrong DEV cases and introduces **zero** new errors (25 improvements, zero regressions). Near vs centroid: centroid fixes 22 errors but introduces two new errors, three both-wrong. Exact paired counts alone do not establish confirmatory significance because DEV has been inspected across prior studies and this candidate was motivated by the E22 outcomes.

**Fitted CAL suffixQ coefficient** (A per unit Q, assumed R):
| R Ω | slope A/Q | abs(slope)/R, A/(Q·Ω) |
|---:|---:|---:|
| 1 | -3.67763e-10 | 3.67763e-10 |
| 2 | -7.12203e-10 | 3.56102e-10 |
| 3 | -1.0351e-9 | 3.45033e-10 |
| 5 | -1.62262e-9 | 3.24524e-10 |

These are approximately proportional to assumed wire R, with ~12% fall in normalized slope from R1 to R5, consistent with first-order wire-drop mechanism but NOT proof of it. Note per-R fitting is allowed in the current experiment, so the scaling relation is a **post-hoc observation** until tested on new held-out R and activation patterns.

## Interpretative decision
- **Positive physical-model method evidence:** The simple input-only suffix-load moment predicts systematic spatial current shift more faithfully than near-count and centroid in these GF-NFET DC simulations under assumed 5Ω wire resistance. A CAL-fitted 7-bit decoder has 0/204 wrong counts versus near 25/204 and centroid 5/204, for fixed m=k16 and 17 counts.
- **Do not retire Q as “no incremental improvement” anymore:** E20 n7/8 gave a near/centroid tie; E22C expanded to 17 count levels and now Q decisively improves *the observed developer test*. The previously negative E20 claim was valid for its limited n7/8 data, not for this broader sample.
- **Do not claim this is original:** a quadratic spatial load moment and compensation of wire drop are physically natural and related to established IR-drop prediction. Novel contribution must be a physically justified **generalizing failure-boundary predictor**, ideally calibrated at low cost and compared against strong margin, centroid, near and ordinary recalibration baselines.
- **Critical limitations:** assumed line R≠foundry measured R, 32-row partial topology≠256x256 physical extracted macro; MTJ static/no mismatch; per-R CAL with true 17-level n known; 6 CAL masks/count; no actual comparator nonidealities; runtime overhead of Q/17 refs not measured; original DEV already influenced development.
- **Next independent gate:** freeze a pre-registered new-mask experiment varying activation m (e.g. m=8,16,24) and read count n, with R0/3/5 and possibly new unseen intermediate R; train a simple R-scaled Q correction from original E22 CAL alone, then test on fresh masks/m without re-fitting Q to the new DEV. Include equally calibrated centroid, near, original, and nonphysical ideal count-quantizer controls. Then add **fixed-per-chip** device spread and real extracted wire geometry before chip/technology claim.

**Research direction:** stay with submitted FYP “Characterizing Reliability and Failure Regimes of Memory-Centric Neural Inference Under Coupled Precision and Hardware Non-Idealities”. E22C supports this mechanism-focused direction; it does not by itself deliver paper novelty or end-to-end inference validation.
