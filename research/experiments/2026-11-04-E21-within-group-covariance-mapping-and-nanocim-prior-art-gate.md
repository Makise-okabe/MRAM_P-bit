# E21 — Physically informed within-group mapping discovery: software screen and literature gate
**2026-11-04. Executed in model environment; E01 real frozen MNIST activity/weight bitplanes + constructed first-order wire-drop model. NOT NUS GF Spectre, no extracted PEX, no measured ADC or actual neural-network classification.**

## Hypothesis
Change placement *within* each existing 32-row read group; keep the exact row set of each group unchanged. This preserves ideal bit-intersection counts, every ideal reconstructed dot product and all group nonempty-read counts. Only spatially nonuniform sense current can change. Strong conventional controls: CAL-activation-frequency sorting (hot rows near driver), joint input-frequency*weight-state-conductance sorting, original layout, CAR and zero-rate grouping.

For binary 0/1 activation x and binary weight state w, assume normalized shunt conductance a_j=x_j(1+w_j) (AP=1,P=2). First-order line-voltage-drop moment `Q(a)=sum_l (sum_{j>=l} a_j)^2 = sum_(i,j) min(i+1,j+1)a_i a_j`. CAL covariance matrix `C_ij=E[a_i a_j]` aggregated across eight real MNIST activation bitplanes, all four W4 bitplanes and eight output columns. The candidate greedily swaps *within each fixed group* to minimize `sum_(p,q) min(p+1,q+1) C[order[p],order[q]]`; no DEV parameter selection. Each group has 1300 proposals, initialized from the strong joint activity sort.

## E21A executed held-out wire-load screen
128 CAL and 256 disjoint DEV E01 MNIST parents; first 256-row FC1 block; eight output columns. Source frozen packet SHA256 `400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a`.

| Starting group membership | Original DEV mean Q | Simple joint activity sort | Proposed CAL pairwise-Q optimizer | DEV nonempty reads SAME for all intra-group policies |
|---|---:|---:|---:|---:|
| original | 4153.63 | **1335.36** | 1337.63 (LOSSES) | 7919 |
| zero-rate sorted | 5750.76 | 4227.42 | **4177.83** | 5478 |
| CAR alpha0 | 5706.67 | 4174.06 | **4140.05** | 5468 |
| activity-balanced | 439.04 | 436.65 | **431.23** | 14824 |

E21A reveals large nonuniform placement effects but a **negative novelty gate**: pairwise-Q does not consistently outperform an extremely cheap simple sorting control. The cross-group read budgets ARE DIFFERENT, thus compare policies only within a row-grouping. Activity-balanced is not a free winner at 2.7× the CAR reads.

## E21B executed nonlinear ideal count-decoder sensitivity
Under **assumed** analog read current proxy `s=m+n-alpha*Q` with true ideal count n and m input active count, decode `n_hat=clip(round(s-m), L=max(0,m+k-32), U=min(m,k))`, then reconstruct W4A8 signed arithmetic error for 256-row block, eight output channels. Coefficients alpha=0.0002/0.0005/0.001 are entirely hypothetical. They are not fitted to GF E19, no NMOS model, no sense amplifier, no ADC circuit/energy, no wire PEX/mismatch. This mathematical stress test has a deterministic negative droop, not a correct empirical current distribution.

| Grouping | alpha | Simple joint activity sorting held-out reconstructed block MSE | Proposed within-group Q optimizer | Relative difference |
|---|---:|---:|---:|---:|
| original | 0.0005 | **73361.8** | 75707.2 | **-3.20%** (proposed worse) |
| zero-rate sorted | 0.0005 | 505934.9 | **459176.1** | **+9.24%** |
| CAR alpha0 | 0.0005 | 508036.7 | **472462.0** | **+7.00%** |
| activity-balanced | 0.0005 | 161.2 | **104.4** | +35% relative but tiny absolute and 14824 group reads |

At alpha=0.0002/0.0005/0.001, proposed Q optimizer beats simple joint-activity sort from zero-rate grouping by 10.01/9.24/3.32%, and from CAR by 8.99/7.00/2.46%; **loses in every tested alpha from the original grouping**, proving no blanket optimizer superiority. No multiple independent chip/device samples or confidence intervals; no trained-model layer bias/inference accuracy. The constructed model itself embeds Q as the error term, so improved Q is expected, and Q improvement is NOT independent physics confirmation.

## Critical 2026 prior art found on the same night
1. **NanoCiM**, Matsui et al., *Nano-ReRAM Computation-in-Memory with Neural Network Weight-Aware X-Address Scrambling to Suppress IR Drop-Oriented Bit-Line MAC Current Variation*, IEEE TCASAI 3(3):190–202, 2026, DOI 10.1109/TCASAI.2026.3661436. Its abstract explicitly claims **weight-aware row-address scrambling** for IR-drop mitigation; a TSP-based optimization; digital classification. This overlaps materially with generic `weight-aware spatial row mapping`. https://doi.org/10.1109/TCASAI.2026.3661436 . Full paper not accessed here.
2. **Dyn-A-Map**, *Dynamic AI-Model Mapping for robust and accurate MRAM-based analog edge computing*, npj Unconventional Computing (2026), https://www.nature.com/articles/s44335-026-00072-6 . Its abstract studies SOT-MRAM weight relocation guided by spatial PV-induced local faults. Distinct physical fault model, but prior MRAM-specific physical mapping.
3. **Hardware-aware training in AIMC**, Nature Communications 2023, https://www.nature.com/articles/s41467-023-40770-4 : spatially dependent IR-drop and analog mapping effects known.
4. **Full-stack memristor AIMC**, Nature Communications 2025, https://www.nature.com/articles/s41467-025-57183-0 : software/hardware mapping parameters as an established co-design dimension.

## Decision
**E21: physically coherent candidate/measurable theoretical result, FAIL as a proven novel algorithm.** Existing weight-aware row-address scrambling defeats any unqualified novelty claim. E21 uses **activation-weight covariance, fixed group membership / zero read-count difference, and a different signed bitplane objective**, which may be a narrower difference than NanoCiM, but full prior-art comparison and actual GF/PEX held-out task benefit are required. The current gain of 7–9% in synthetic block MSE must never be described as physical read-error or end-to-end classification improvement.

## Best next falsifier (pre-registered)
1. Read full NanoCiM (method/placement objective and physical measurement) before claiming algorithmic originality.
2. With NUS actual GF + student MTJ 32-row read model, obtain measured `mask -> current` over 3+ representative group occupancy patterns and positions; fit a low-parameter surrogate on CAL **without using holdout**. The E19 `n=7,8,m=k=16` small masks are useful but insufficient for full E01 FC1.
3. Compare frozen maps from original, zero-rate, CAR, joint activity sort, covariance-Q and strong NanoCiM/TSP-inspired controller at matched group membership/read count. Use held-out **decoded count error, signed dot MSE and final classification or Ising metric**, plus mapping CPU and metadata costs.
4. If covariance-Q does not beat the strong activity sort and weight-aware scrambling, **reject** for CA2, not an invention. If it does, determine whether the difference is a specific statistical correlation/ADC decision phenomenon not addressed in NanoCiM or Dyn-A-Map.
5. E21 remains an exploration record even if eventually rejected.

## Reproducibility
Conversation package `E21_mapping_pathfinding.zip` SHA256 `91c5919f32cf8a2d30f99705a7755c00f1f9623fdd0db56ae8d19a463a8eff92` includes script `e21_withingroup_mapping_screen.py` SHA256 `c2cf1168f1d193540a68bf4dc97688a2882ff4e4ee51905359c1786226e6cd21`, script `e21b_quantization_falsifier.py` SHA256 `ed0d1cac1e65f089ed55ca20ae19d78cf8f130f827204221bf22b66a838f1d6e`, the result JSONs and logs. Frozen E01 packet NOT bundled and never to be committed publicly. Scripts currently in download package, not this GitHub repository.
