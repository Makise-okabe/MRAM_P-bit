# E13–E15 — DIB prior-art differentiation, rejected dynamic scheduler, and operand-conditioned ADC candidate
**Experiment date:** 2026-11-04 (Singapore). **Evidence type:** user-origin E01 frozen MNIST bitplanes + assistant-executed exact mathematical/software comparison model. **No new NUS Spectre, physical ADC, energy, latency, silicon data or publication-novelty certification.**

## Source-method audit: DIB-CIM Algorithm 1 (user-provided figure)
DIB outputs `B_final, Flag` and takes input bit width `X`, bit position `i`, fed input CIM block size `B_F`, subblocks `Z`, basic block `B_b`, imbalance `K,L`, LEBD threshold, Criterion1 and Criterion2.
- Initialize current paired-input-bit block size to 8.
- LEBD computes an effective input count from basic blocks; when `Count >= V_th,LEBD` sets `B_tmp=2*B_curr`, otherwise `B_tmp=B_curr`.
- I3D tests input distribution imbalance and, if a criterion is true, outputs `Flag=1, B_final=B_tmp/2`; else `Flag=0, B_final=B_tmp`.
- The paper's public abstract also describes zero-skip and DR-ADC. User's figure is the **WL block-size algorithm**, not enough to audit the actual DR-ADC circuitry. Full 14-page paper novelty paragraph and ADC details have **NOT** been accessed.

DIB source: https://doi.org/10.1109/TCSI.2026.3726936 (Chen et al., IEEE TCAS-I 2026).

## Hypothesis that is NOT equivalent to DIB's shown algorithm
Rather than choose block-size from input-only LEBD/I3D, use **both operand popcounts** (dynamic active input m and stored-weight-bit k) to choose an ordered ADC comparator-threshold tree for the unknown binary inner-product count n, at FIXED group size B=32:
- Exact support L=max(0,m+k−32), U=min(m,k).
- Analytic prior `P(n|m,k)=C(k,n)C(32-k,m-n)/C(32,m)` is a hypergeometric *prediction* under exchangeable activation masks, not a theorem about actual trained weight/activation correlations.
- The converter chooses a comparator threshold t to split the legal ordered counts, recursively minimizing *expected comparison count* (standard optimal alphabetic search-tree DP). Every integer count is still decoded **exactly under an ideal monotone, noiseless analog count and threshold comparator**.
- Hardware-facing constraint: max comparison depth D=5 for full (m,k) tree or D=6 for a limited k-codebook bank architecture; metadata/ref DAC overhead still unmeasured.
- Feasibility hypothesis for original algorithm research: **joint-count-conditioned, latency-capped, limited-reference-bank readout control** for MRAM CIM. The hypergeometric law and optimal decision trees are established mathematics; no blanket originality claim.

## E13 negative / CA2 rejection record (do NOT delete)
Tried dynamic on-the-fly shared-wordline signed-bitplane read scheduling for ReLU-negative certification. Reordered every 32 logical group/bitplane tasks using already measured counts, CAL-only tuning. 128 CAL and 256 held-out DEV MNIST input parents, zero-bias FC1 (actual model bias missing), exact binary counts.
- E12 static shared joint schedule: **14,942,396** DEV logical ADC-like conversions = 16.8260% saved.
- E13 best CAL-selected dynamic progress policy: **14,935,234** conversions = 16.8659% saved.
- Extra advantage: **7,162** conversions across 256 parents, just **0.03987 percentage points**. Control/priority recomputation makes the benefit implausible as a standalone contribution.
**Decision: REJECT E13 as a new thesis algorithm.** ReLU-sign early termination also has prior art. Neither of these numbers measures actual shared-WL activations or real energy.

## E14 positive — joint input/weight conditioned exact ADC threshold tree
Hash-verified frozen E01 input packet SHA256 `400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a`; all 784 FC1 input rows (padded into 1024 positions), 128 output channels, 8 activation bitplanes, 4 signed weight bitplanes, 128 CAL and 256 DEV parents. **No actual trained layer bias needed** for this bit-count decoding-only task.
- 33,554,432 DEV binary count opportunities, including deterministic ones that need zero comparisons under a joint-count controller.
- Balanced input-only (m): **48,544,050** comparisons.
- CAL-trained optimal **input-only**: **41,310,333** comparisons (strong baseline).
- Balanced **joint (m,k)**: **45,032,056** comparisons, worst depth 5.
- Joint hypergeometric unconstrained: **36,558,784** comparisons, worst depth 9.
- Joint CAL-smoothed optimal: **36,233,566** comparisons, worst depth 9.
- Independent leaf/path audit: all **6,545 legal outcome leaves** across m,k decoded correctly by a separately implemented ordered threshold tree; every path uniquely determines n (ideal comparator).
- Joint hypergeometric vs CAL-trained optimal input-only: **11.502% fewer comparisons**, 256-parent paired bootstrap CI **[11.136%,11.868%]**, all 256 parents positive. Vs balanced joint: **18.816% fewer** CI **[18.687%,18.943%]**.

### Fix unacceptable worst-case comparator depth (E14C)
Constrain optimal ordered tree with DP over remaining allowed depth:
- Joint hypergeometric **depth cap 5**: **36,972,994** comparisons; worst depth 5 — **17.896% below balanced joint with identical max depth 5**.
- Joint hypergeometric cap 6: **36,624,114**; max6.
- Joint CAL-smoothed cap 5: **36,604,457**; max5.
- Joint CAL-smoothed cap 6: **36,312,243**; max6.
These remain mathematical counts, not evidence that arbitrary comparator thresholds can be implemented or that a shared physical ADC can choose independent thresholds per column.

## E15 positive — limited-bank joint-operand controller
Rather than require one tree per 33 distinct k-values, cluster the integer k=0..32 into fixed equal-width bins; each bin gets a CAL-trained threshold tree over the union of feasible values for members. Max depth 6. Count comparisons on independent DEV and count total internal tree nodes (a proxy for *logic/LUT* complexity, NOT measured memory area or transistor counts):

| Number of k-codebook banks | DEV comparison decisions | Internal tree nodes | Max depth |
|---|---:|---:|---:|
| 1 | 41,068,446 | 496 | 6 |
| 2 | 39,520,250 | 736 | 6 |
| **4** | **37,477,206** | **1,088** | **6** |
| 8 | 36,684,387 | 1,728 | 6 |
| 16 | 36,442,681 | 2,976 | 6 |
| 33 | 36,312,243 | 5,456 | 6 |

**Four k-codebook banks mean four classes of controller decision trees, NOT four analog reference voltage levels.** A physically variable threshold for each branch may still require a multi-code DAC/reference generator per concurrently converting column, or cause serious shared-reference serialization.\n\n**4-bank** beats CAL-optimal input-only (41,310,333) by **9.279%** on held-out DEV; 256-parent paired bootstrap CI **[9.040%,9.509%]**, all 256 input parents benefit. It needs only 1,088 tree nodes versus 5,456 for unrestricted 33-bank codebooks; this is not a full memory/area count. A 4-bank physical implementation would still require metadata/selection, DAC threshold routing, and possibly parallel comparators; the software uses exact k to bypass deterministically known n, so calling it a pure 2-bit k-metadata controller would be **false**.

## Difficult prior art, and the precise originality claim to investigate
- DIB-CIM 2026: input-driven WL block size and DR-ADC (full ADC method not yet audited).
- **Probability-based SS/SAR hybrid ADC for 9T SRAM CIM (2023)**: https://doi.org/10.1109/LSSC.2023.3260090. Probability-based CIM ADC already exists.
- **Entropy-coded successive-approximation tree ADC (WO2020201850A1; 2020)**: https://patents.google.com/patent/WO2020201850A1/en. Nonuniform decision trees are NOT original.
- Early ReLU signed/quantized-output termination already has prior art (e.g. Compend 2018; BLC-CIM 2025; TEMPO FeFET 2026 is labelled an essay, not silicon verification).

**Novelty is NOT certified.** The more defensible, testable gap is: an **exact, joint m/k-conditioned MAC-count reference tree with provable worst-case comparison depth and resource-constrained reference-bank grouping, instantiated for MRAM CIM**. Must inspect prior exact operand-conditioned ADC before asserting no equivalent work.

## Mandatory next Gate: physical implementation, not another generic synthetic sweep
1. Check whether NUS-accessible intended GF NFET+student-MTJ **multirow** sense read produces monotone and non-overlapping count-current levels across position and mismatch; E11E verified only a constructed passive ladder, not this.
2. Determine real ADC architecture: if every column cannot choose its own threshold independently and a single global reference is shared, per-column E15 tree benefits may incur serialization and disappear. A true matched DIB hardware comparison needs the missing full paper.
3. Charge k popcount metadata, codebook LUT, bank routing, finite reference levels, comparator offset/noise, DAC settling, control latency and calibration. Extract area/energy break-even against **input-only CAL-optimal**, not only binary-search baseline; compare with DIB's real WL/ADC policy after PDF audit.
4. Compare actual bit count / decoded error and downstream task accuracy in one matched read/ADC model; quantify any real energy/time advantage, not just ideal comparison count. No fabricated results.

## Reproducibility / provenance
A private conversation download `E13_E15_DIB_algorithm_discovery.zip` contains complete executable Python3.6-syntax scripts for E13, E14, E14C, E15, independent leaf/path and parent bootstrap audits, JSON results, README and an E12 source dependency. SHA256 `64df1bb27a9ba690345413a5f1ef4a4c117de00d1e984870b3fa255feb4e2c4e`. The previous **private** E12 `review_packet.zip` is required and NOT included or uploaded to GitHub. **This GitHub note is documentation, not a claim that code was committed.** No PDK/vendor model source uploaded.

## Prof Fong brief
“DIB selects wordline block size using LEBD/I3D input significance and imbalance. I explored per-column exact AND-count decoding instead: input population m and stored-weight population k constrain the only possible intersection counts and their approximate hypergeometric probabilities. I constructed an optimal comparator-threshold tree and constrained the maximum depth and number of reference codebooks. On held-out real MNIST bitplane traces, a four-bank, max-six-comparison variant uses 9.28% fewer ideal comparator decisions than a CAL-trained input-only optimal threshold decoder. It remains a software feasibility result; I want to evaluate programmable references, per-column shared hardware, and real read variations. The mathematics is established, and I am checking closest probability-based ADC prior art before asserting technical originality.”