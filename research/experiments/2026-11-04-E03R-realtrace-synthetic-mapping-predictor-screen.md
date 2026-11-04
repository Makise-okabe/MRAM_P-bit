# E03R — real MNIST activation traces + synthetic covariance/predictor discovery
Date: 2026-11-04 Singapore. **No new MRAM electrical measurements, no full neural inference-failure results.** User's frozen E01 packet was reused and its manifest hashes checked. A standalone code/JSON/reproduction package was supplied in the conversation (ZIP SHA256 `d59090e3e016e5578c520fe32d0874f0b9ff6e44fa6f11dda6a028da15b1b197`; script SHA256 `9c82dab0e42d4421585284af9d4e513399e9f8bac6a359e409fc8b0c682e76db`). This note does **not** claim the script is in this GitHub repo.

## Questions
D1: is the low-read-count mapping also the low-error mapping? D2: does retaining cross-read decoded error covariance give a useful calibration-only selection signal over an otherwise comparable marginal-only score? These are discovery questions; data cannot establish target MRAM outcomes without an E02 valid sensing model.

## Input and protocol
- Real E01 frozen-MNIST activation/weight traces: first 256-row FC1 block, 8 output channels, 128 independent CAL parents, 256 independent DEV parents, all 8 A8 read cycles and four W4 signed bit planes. Validated exact ideal arithmetic/permutation.
- Candidate resident group32 orders from E01: original, zero-rate sorted, CAR alpha 0, dead-feature packed, activity-balanced, random. CAL-tuned E01 mapping orders frozen before DEV.
- Model only: independent Gaussian persistent error per physical cell, standard deviation **0.10, 0.20, or 0.35 normalized single-active-cell read-current units**. Offsets persist across repeated bit cycles; no PDK electrical values used; nearest-integer group-count quantizer clipped to [0,32], no calibration or read periphery. These are arbitrarily chosen hypothesis-screen parameters, **not physically calibrated errors**.
- 48 synthetic CAL chip assignments and 48 independent DEV chip assignments; all policies paired on the SAME chip parameters within each split. Mapping-selected scores are chosen on CAL only.
- Joint score: full reconstructed first-block arithmetic MSE from directly simulated noisy CAL; marginal-only proxy: summed coefficient-weighted individual per-read count-error squares. Neither is an efficient neural failure predictor. Cross-cycle moments are implicit in full reconstructed MSE, but covariance itself is not an original algorithm.

## Results
Full E01 group32 all-eight-array read total is not used here. These per-array first-block read counts are: original 7919; dead-packed 7173; zero sorted 5478; CAR 5468; activity balanced 14824; random 14078. The underlying E01 E01 data, not this synthetic screen, establish the read counts.

Held-out mean squared reconstructed arithmetic error for 8 FC1 output channels in selected block:

| Synthetic sigma | Original | Zero-sort | CAR | Activity-balanced | Random | Dead-packed |
|---|---:|---:|---:|---:|---:|---:|
| 0.10 | 52,230 | 101,150 | 91,074 | 8,569 | 14,803 | 64,697 |
| 0.20 | 769,671 | 813,942 | 891,873 | 546,106 | 650,474 | 783,529 |
| 0.35 | 2,850,411 | 2,909,836 | 2,871,890 | 2,941,395 | 3,437,175 | 2,721,517 |

This illustrates a *possible* quality/read-count tension, not a hardware result. At sigma=0.20 CAR has fewest reads among these policies but greater arithmetic MSE than activity-balanced; at sigma=0.35 dead-packed is best in DEV, so rankings are **strongly parameter-dependent**.

CAL-selected joint-reconstruction-MSE policy versus CAL-selected marginal-only policy:
- sigma .10: both **random**; held-out best is activity-balanced
- sigma .20: both **activity-balanced**; held-out best is activity-balanced
- sigma .35: both **CAR**; held-out best is dead-packed

Thus this first toy test finds **NO independent mapping selection benefit from the joint score over the marginal-only proxy**. The scores require direct noisy calibration simulations, so no efficient failure predictor exists here. The real objective is a validated reduction in independent full-network inference failure at equal total resources.

## Null model and caution
An exactly linear sum of independent identically distributed, persistent per-cell read errors under any row permutation has analytically invariant *population* reconstructed arithmetic variance. The script computes the same analytic variance for all six permutations and asserts equality. The illustrative finite integer decoder breaks this simple invariance; a real MRAM sensing path has not been tested. No energy, latency, read-disturb, ADC accuracy, 256x256 physical noise, p-values, inference outcomes, or novelty are asserted.

**Next:** Freeze one physical read/ADC kernel from new E02 or explicitly assumed alternatives; rank maps at the same read budget/cost and compare cheap marginal vs joint/covariance predictor on independent chips and FULL NEURAL task margins. If marginal scoring and strong calibrations suffice, reject the added F1 complexity.

This is a research-pathfinding log, not a F3 thesis endorsement. Ising remains next priority for novel-method discovery as user requested.
