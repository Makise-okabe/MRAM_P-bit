# E01 exploratory workload screen — 4 November 2026

**Evidence class:** independent real-dataset activation trace / software-only structural screen.
**Status:** completed as *exploratory alternative workload*; the frozen FYP workload E01 and physical E02 remain open.
**Not a target macro, calibrated MTJ readout, energy result, or evidence of originality.**

## Why this pilot
The 16-page CA2 working draft (revision 15) calls for E01 real activation traces and disjoint calibration/evaluation IDs before E03 mapping development. A fresh exploratory digit-network workload lets us exercise the structural question without using retired eight-cell/column experiments or assuming new GF data.

## Workload and reproducibility
- Public scikit-learn digits (8x8 handwritten digits); fresh PyTorch 64-256-256-10 MLP, seed 20261104; **not** the user's frozen FYP MNIST pipeline.
- Stratified train 1257 / calibration 270 / evaluation 270 images. Train only fits the MLP.
- Layer-1 ReLU activations are linearly quantized to unsigned A8 using training-set scale. Pool all eight activation bit planes, maintaining a single row permutation for all.
- Next layer has 256 inputs and 256 outputs; output 256x256 binary W4 LSB plane from independently trained weights. No padding, no "8-row physical macro" claim.
- Exact integer (int64) matrix-product invariance checked for every static permutation; unique per-image per-plane IDs and cal/eval disjointness checked.
- 2160 calibration and 2160 evaluation bit-plane vectors; separate train/cal/eval partitions.
- Floating-point network accuracy on the evaluation subset: 98.148% (not an MRAM inference result).
- Exactly 21 of 256 pooled input dimensions were always zero in calibration **and** evaluation.

The executable Python source, binary NPZ input, trained model arrays, full JSON outcome, and provenance metadata are bundled in the current ChatGPT result as `MRAM_E01_20261104_experiment.zip`; this GitHub note records the outcome rather than attaching the binary data to the repository.

### Data integrity hashes
- Source script SHA256 `8f4fa9e0014534137f962c83080b188fbbb1db2a7538582411120111e4324077`
- Input NPZ SHA256 `31958438d8446b2079e5c2b6c509cbcf6d0adde8e1d141c6b011bbf447493d9d`
- Result JSON SHA256 `adcbbc7e0de7c98d13d8dcabd3dd170023a75cc0082aff91a1d062d65c9e9a2f`

## Evaluated read counts
All are **nonempty logical group reads** across 270 evaluation images and eight planes. They are **not** ADC-energy measurements; group size is a software schedule, not a validated parallelism.

| Proposed rows/group | Original | Dead-feature packed | Zero-rate sorted | CAR-style alpha=0 | CAR improvement vs original | CAR improvement vs zero-rate sort |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | 32245 | 30367 | 29060 | 28652 | 11.14% | 1.40% |
| 32 | 16668 | 16585 | 15510 | 15450 | 7.31% | 0.39% |
| 64 | 8533 | 8518 | 8314 | 8309 | 2.63% | 0.06% |
| 128 | 4299 | 4301 | 4227 | 4225 | 1.72% | 0.05% |
| 256 | 2158 | 2158 | 2158 | 2158 | 0% | 0% |

CAR is an adaptation of the grouping rule, not all of VARA's training or microarchitecture. Each mapping is fit on calibration vectors only, with evaluation trace structure inspected once. The mapping is shared across eight bit planes.

## Interpretation and decision
1. **Structural opportunity exists**, especially for smaller groups, but 21 permanently inactive input dimensions account for part of the apparent savings. Simple zero-rate sorting explains almost all the remaining gap on this workload.
2. The incremental CAR advantage over zero-rate sorting is modest: 1.40% fewer conversions at 16-row groups and 0.39% at 32. No inference correctness or hardware-energy conclusion follows.
3. Consequently, this pilot does not justify inventing a "reliability-aware" mapper yet. It reinforces the CA2 requirement for an inactive-feature packing control and a physical E02 test.
4. No old eight-cell trial is imported. No new target-array device calibration, target netlist, PEX, ADC or chip-variation result exists.

## Next experimental gates
- **E01 primary:** obtain the user's frozen representative quantized neural-network layer with 256-wide per-plane traces and parent IDs, then rerun the repository's `experiments.run trace-screen` with its approved metadata and untouched evaluation roles.
- **E02:** in the authorized university environment, fix cell/access topology and load/sensing interface; test 12–24 nominal read patterns and held-out target responses before transferring any error law.
- **E03 paired covariance check:** only after E02, hold group read count and marginal read-error laws comparable, measure *decoded* cross-plane covariance after equal calibration; compare CAR, balanced, shuffling and covariance-ablated mapping at the same search/read budget.
- **E09:** retain Ising persistence / cache-control work separately; do not treat E09A verification as noisy solver evidence.

**Gate disposition:** E01 exploratory example documented; E01 on the frozen FYP network and E02 remain blocked on source data, with final F3 novelty undecided.
