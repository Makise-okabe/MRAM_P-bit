# E01 frozen MNIST read-packing audit — 2026-11-04

**Status:** USER-EXECUTED workload run verified against uploaded `review_packet.zip`. This is **software workload structure only**, not a new electrical or PEX measurement of the 256×256 MRAM target. No eight-cell/single-column currents, ADC fits or error models used.

## Provenance and reproducibility

- NUS run: `E01_MNIST_20261104T085558Z_038af9`
- Packet SHA-256: `400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a`
- Packet integrity audit: 26 files in `packet_manifest.json`, all reported SHA-256 and byte sizes match the received ZIP.
- Frozen original MNIST-trained W4A8 model, 128 calibration parents, 256 development parents; **original held-out test split not evaluated**.
- Torch golden-vs-NumPy logits identical on 384 parents (reported absolute logit difference 0.0); 251/256 development images correct *without electrical noise*. This accuracy is **not** evidence of MRAM reliability.
- FC1 784 input positions split as four 256-row blocks, packed into eight 256×256 binary weight-plane arrays (last block 16 real rows, 240 padding rows).
- CAL-always-zero real features per row block: 112, 53, 80, 11.
- Every array was verified to reconstruct the same ideal binary/integer dot products under the tested resident permutations.

## Nonempty vector-read totals on development data

Totals across all eight packed arrays; do not interpret as joules or completed operations at any particular ADC precision.

| Group rows | Original | Dead-packed | Zero-rate sorted | CAR alpha 0 | CAR vs original | CAR vs zero-rate sorted |
|---|---:|---:|---:|---:|---:|---:|
| 32 | 70,938 | 59,024 | 45,942 | 45,542 | 35.80% lower | 400 fewer (0.87%) |
| 64 | 37,790 | 34,980 | 25,984 | 25,952 | 31.33% lower | 32 fewer (0.12%) |
| 128 | 21,108 | 22,468 | 15,748 | 15,744 | 25.41% lower | 4 fewer (0.025%) |
| 256 | 12,316 | 12,316 | 12,316 | 12,316 | 0% | tie |

**Interpretation:** sorting dominates much of the opportunity. CAR barely beats ordinary zero-rate sorting in this run. The group-256 tie follows from full-block aggregation: mere row reordering cannot alter whether the entire block has a nonempty read.

## Important countervailing fan-in cost

Derived by aggregating all eight arrays' actual per-group occupancy histograms from the packet's `screen.json` files:

| Group rows | Mapping | Nonempty reads | Active rows per nonempty read (mean) | Maximum observed active rows | Reads with >=16 active rows |
|---|---|---:|---:|---:|---:|
| 32 | Original | 70,938 | 5.591 | 23 | 1,124 |
| 32 | Dead-feature packed | 59,024 | 6.719 | 31 | 3,420 |
| 32 | CAR alpha 0 | 45,542 | 8.708 | 32 | 7,850 |
| 32 | Activity-balanced | 93,830 | 4.227 | 20 | 76 |
| 64 | Original | 37,790 | 10.495 | 43 | 7,896 |
| 64 | CAR alpha 0 | 25,952 | 15.282 | 63 | 11,276 |
| 128 | Original | 21,108 | 18.789 | 71 | 11,130 |
| 128 | CAR alpha 0 | 15,744 | 25.190 | 110 | 10,402 |

The minimum read count mapping packs high fan-in into fewer reads. This is *a hardware-risk hypothesis*, **not** demonstrated sensing error, energy, or read disturb. The local-floating SL 2T1MTJ layout, fan-in support, driver loads, ADC range, sample time, and read-current collapse must be physically validated on E02 before proposing any controller.

## F3 novelty gate

This experiment is a **workload screen**, not a covariance-of-decoded-errors screen. It provides zero error samples, no new 256×256 circuit readout, no cross-cycle hardware covariance, and no held-out test inference with noise.

Moreover, for ideal additive per-device persistent errors with identical variance `sigma^2` and fixed activation masks, a pure permutation of physical row indices does not change the full-group covariance `sigma^2 * sum_i a[i,b]*a[i,b2]`. F3 requires **a specific mechanism that breaks that invariance**, e.g. spatially varying row sensitivity, groupwise nonlinear ADC, shared source-line loading, or an implementable correction that genuinely changes decoded pair covariance. A covariance-only improvement should be shown against tuned no-mapping, zero-rate sorting, CAR, activity balancing, per-column calibrated sensing and equal-budget random search, using newly measured E02 error kernels on independent held-out data.

## Three-path decision

- **H1 spatial mechanism:** continue to the fresh 256×256 Spectre electrical gate, not only interface/mask checks.
- **F3 covariance-aware mapping:** conditionally open; workload shows available grouping trade-offs but no independent novelty beyond sorting and no covariance outcome.
- **F7 Ising:** exact digital incremental-field baseline is strong; in independent pure software checks (12, 14, 16 spins, 20 restarts), incremental/full nonzero-term ratios were 0.23494, 0.25718, 0.22620 with paired identical field-update trajectories. This is not actual hardware energy or speed and supplies **no** MRAM noise kernel. Do not claim an Ising improvement.

**Action:** prioritize new PDK-native whole-array sensing and interconnect validity; evaluate F3/F7 only after a physically supported readout/error model exists. Do not substitute historical 8-cell data.
