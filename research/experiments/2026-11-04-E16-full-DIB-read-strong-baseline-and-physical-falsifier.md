# E16 — Full 14-page DIB-CIM paper audit and E15 strong-baseline/physical falsification
**2026-11-04. Executed by assistant with user-provided DIB PDF and frozen user E01 bitplanes.** Source PDF remains privately attached; the IEEE/NUS-licensed article is NOT uploaded to GitHub. E16 software and constructed passive-network results are NOT GF/Spectre physical measurements, NeuroSim, area/power or novel-technology certification.

## Full DIB-CIM method (actual paper, not just Algorithm 1 screenshot)
Source: W. Chen et al., *DIB-CIM: An Energy-Accuracy Balanced Analog Compute-in-Memory MRAM Using Dynamic-Input-Block Size Arithmetic With Dynamic-Resolution ADC*, IEEE TCAS-I 2026, DOI 10.1109/TCSI.2026.3726936, 14 pages. User-provided NUS-licensed PDF inspected and figure/architecture checked.

- p. 3 Section II-B frames novelty as three cooperating elements: LEBD+zero-skip, I3D for input spatial imbalance, and DR-ADC linked to parallelism.
- pp. 4–6 Section III / Algorithm 1: 8-bit input grouped into four 2-bit-significance bands; LEBD starts B=8 and increases subsequent band B to 16/32/64 when active-input count passes its preset threshold; zero-skip bypasses all-zero basic 8-row blocks. I3D aggregates four or two spatial subblocks and halves B when input imbalance criteria hold, with K=1,L=0 for implementation. Algorithm 1 emits `B_final`, `Flag`; it does not use stored weight-bit popcount k as an input.
- pp. 6–8 Section IV/Fig. 11: physical **2-bit coarse flash ADC + dynamic voltage-to-time module + flash TDC**, controlled for output resolutions 4,5,6 bits at B=8,16,32/64. Coarse output DOES select a VREF MUX threshold for fine conversion; it would be incorrect to claim DIB never selects references. This is NOT the E15 recursive conditional binary threshold-search tree.
- pp. 9–12 Section V: circuit-calibrated NeuroSim and 28nm 128x128 series SOT-MTJ; 5% MTJ variation and multiple PVT corners; Table I R_P=10k, R_AP=20k nominal and TMR=100%; control unit 1608um^2, 0.026 mW/25 MHz; Fig. 15 ADC 47.9% system power. DIB's published 12–16% latency gain is versus fixed B8 excluding zero skip, **not comparable** with our hypothetical count-comparison gain.

**Paper novelty audit conclusion:** E15's output action (per-column ADC comparison threshold selection based jointly on m,k, fixed B) is distinct from DIB's shown LEBD/I3D block-size action and also from the actual flash/V2T/TDC conversion sequence. This is a DIFFERENT architecture, not a DIB-algorithm modification validated on identical hardware. Prior probability-conditioned CIM ADC (Jo et al., IEEE SSCL 2023, DOI 10.1109/LSSC.2023.3260090) and pre-existing decision-tree/SAR ADC designs (WO2020190340A1 and WO2020201850A1, both 2020) are serious originality obstacles; novelty NOT certified.

## E16-A: new, stronger same-hardware-model software test (EXECUTED)
Same E01 frozen real-MNIST 128 CAL and 256 held-out DEV inputs; full 784 FC1 rows padded to 1024 physical positions; 128 outputs; B32, 8 activation and 4 stored signed W4 bit planes. **33,554,432** count-decoding events, ideal scalar ADC with free programmable threshold and exact integers, no wire/noise/energy.

New comparator baseline: train an *input-only*, hard-depth-6 ordered threshold tree on CAL m-conditioned count distribution. At runtime it is **allowed the same exact k metadata and tight joint [L,U] support as E15**, and logically prunes every comparison whose branch is predetermined by the k-range; no separate per-k probability-aware tree tuning. This is significantly stronger than the previous input-only baseline and isolates the new conditional probability-order contribution.

| Method | DEV exact integer comparator decisions | Max comparisons/count |
|---|---:|---:|
| Input-only CAL optimal depth6 | 41,390,328 | 6 |
| Input-only CAL depth6 **plus k-support pruning** | 40,529,665 | 6 |
| E15 four-k-codebook depth6 | **37,477,206** | 6 |
| All 33 k-codebooks depth6 | 36,312,243 | 6 |
| Joint balanced exact-count tree | 45,032,056 | 5 |

**Result:** Four-bank E15 saves **3,052,459** comparisons or **7.5314%** vs the significantly stronger depth6 input-only+k-pruned comparator. E15 fewer decisions for **all 256 independent DEV parents**, paired parent-bootstrap 95% interval **[7.3447%, 7.7055%]**. This holds mathematically for this workload and comparator model. 3.052459M /33.554432M ≈ **0.09097 comparator operations saved per potential count event**; if additional per-event control/codebook/DAC/reference cost exceeds this in *comparator-energy equivalents*, no net energy gain. The four codebook classes DO NOT imply four voltage reference levels.

## E16-B: hard physical-model counterexample (EXECUTED, toy only)
Independent 32-row one-ended passive resistor ladder, Rp=5k/Rap=10k (from verified student behavioral default), read 1mV mathematical diagnostic, 15000 randomized spatial placements **per true count** with m=16, k=16, counts n=7 or8, across r in [0,1,5,10,25,50] Ω **assumed** each segment. Valid exactly-identified n cannot be inferred by a single current scalar if the possible current sets overlap.

- At r=0: sampled current sets separated by 100 nA, best CAL threshold independent DEV classification error **0.0%**.
- At r=1Ω: sampled sets remain separated by ≥22.34 nA, but finite-CAL selected threshold gives **0.01%** DEV error.
- At r=5Ω: sampled sets **overlap by 212.56 nA**, independent DEV error **16.91%** for a CAL-tuned scalar threshold.
- At r=10Ω: overlap by 395.84 nA, DEV error **31.32%**.
- At r=25Ω: overlap by 628.46 nA, DEV error **41.86%**.
- At r=50Ω: overlap by 698.57 nA, DEV error **45.21%**.

The threshold is calibrated on 10000 distinct patterns/class and tested on 5000 distinct patterns/class. These are not measurements or definitive probabilities for physical GF, and do not correspond to DIB's *series* SOT-MRAM architecture. **Counterexample demonstrates the E15 'lossless exact count ADC' guarantee is invalid for an arbitrary shared-resistance array absent a physically distinguishable monotone count channel.** More ADC comparator branches cannot fix overlapping analog input levels.

## Decision / next gate
**Retain E15 as a sharply specified software ADC-selection candidate**, not a confirmed novel MRAM algorithm or energy benefit. The E16-A gain persists after a strong k-aware support-pruning competitor; E16-B identifies the make-or-break hardware risk. For next validation, use NUS local `hvtnfet` W=80nm + verified custom MTJ topology (`cim_c03_dot2.py` and `cim_c04_dot4.py` are known connection examples) to establish conditional current ranges for physically different masks with equal (m,k,n) and adjacent n values; quantify ADC error and DAC/control costs on the exact read operator. Do NOT compare the number 7.53% with DIB 12–16% latency; metrics/architectures are different.

**CA2 negative/evidence ledger:** E13 adaptive ReLU scheduler rejected for +0.04pp logical savings; E15 unrestricted exact ADC oracle now receives **physical-scope warning/failure** under assumed ladder. The old E11E 'wire interaction' was validated only for an artificially parameterized resistor network. Research narrative must preserve both the surviving E16-A method gain and the E16-B impossibility witness.

## Reproducibility
Download ZIP delivered in this conversation: `E16_DIB_full_paper_and_falsification.zip`, SHA256 `057f6da7f8a5fc23c28664c26078ea01c01c8e6fedbe6da937934eb58713e4d0`. Contains E16 Python3-compatible scripts, result JSON, detailed audit README. Original user-origin E01 `review_packet.zip` and prior E12/E14/E15 Python dependencies are **not bundled**; they are in the earlier chat uploads and should not be publicly committed without permission. The NUS-licensed DIB article is not bundled.
