# Prof Fong — 5 Nov 2026: specific algorithm hypothesis AFTER DIB Algorithm 1 audit

## Working research title
**Latency-bounded joint-operand-conditioned ADC threshold scheduling for MRAM compute-in-memory.**

## Original contribution being proposed — narrow and falsifiable
For each fixed-size B=32 simultaneous binary MAC group, calculate input popcount m and stored weight-bit popcount k. Any actual bit-intersection count is in [max(0,m+k−B),min(m,k)]. The controller uses an operand-conditioned probability model to choose the order of analog comparator thresholds. In contrast to ordinary balanced SAR and input-only resource allocation, it prioritizes likely count values but **never merges two legal integer outputs** in the ideal comparator setting. A depth-constrained dynamic-programming controller caps worst-case comparisons. A limited-bank alternative groups k into only four threshold-tree codebooks (not four reference voltages), to control LUT complexity.

The known hypergeometric distribution and alphabetic optimal decision trees are reused, NOT invented. The proposed research novelty is their operand-conditional, fixed-latency, codebook-resource-constrained co-design for binary MRAM-CIM ADC decoding, assuming full prior-art check confirms distinctness.

## Why not DIB-CIM Algorithm 1?
The supplied Algorithm 1 uses LEBD and I3D effective input-bit/0–1 input distribution to choose **wordline activation block size** B_final and Flag. It does not list stored-weight popcount k as a controller input and does not describe a threshold-comparison tree. Published DIB abstract also lists a dynamic-resolution ADC; **we have NOT accessed its full internal ADC scheme**. Our test is not a replica of DIB, nor an energy/latency comparison with DIB's 12–16% measured/reported latency reductions.

## Executed results (real bitplane workload, ideal comparator)
128 CAL / 256 DEV independent MNIST input parents; complete padded 784-row FC1 dot product groups, 128 channels, all 8 input bits and signed W4 weight bits. All 33,554,432 DEV count events, including deterministic outcomes. Unlike prior E12 signed-ReLU algorithm, no FC1 layer bias is needed because this experiment only exactly decodes individual binary counts.
- CAL-trained optimal input-only threshold search: **41,310,333** comparator decisions (max depth 9).
- Balanced joint input-weight interval search: **45,032,056** (max5).
- Joint hypergeometric optimal tree: **36,558,784** (max9), 11.502% below optimal input-only, independently verified all 6,545 legal leaves, paired parent-bootstrap CI [11.136%,11.868%].
- Joint hypergeometric tree **with max depth 5**: **36,972,994**, saving 17.896% vs joint balanced at equal maximum depth5.
- Hardware-resource-constrained **four k-tree codebooks, max depth6**: **37,477,206**, 9.279% fewer than input-only CAL-optimal, paired parent-bootstrap CI [9.040%,9.509%]; 1,088 tree nodes vs 5,456 for full 33-codebook design. Codebook node count ≠ physical area.
- Eight codebooks: **36,684,387**, max6.

**Rejected parallel algorithm E13:** dynamic, probability-weighted shared wordline ReLU early-stop reordering added only 7,162 skipped logical conversions out of 17,965,231 eligible vs simple static E12—+0.03987 percentage points; reject its complexity/novelty. This failure was logged for CA2.

## Explicit prior art we found
- DIB-CIM (2026), DOI 10.1109/TCSI.2026.3726936.
- Probability-based Single-Slope/SAR hybrid ADC for 9T SRAM CIM (2023), DOI 10.1109/LSSC.2023.3260090 — probability ADC itself is established.
- Entropy-coded successive-approximation tree ADC (2020), WO2020201850A1 — ordered nonuniform threshold tree itself is established.
- Early termination after ReLU in older work — E12 early stopping is NOT the stand-alone originality claim.

## Main technical risk / what supervisor can assess
This is a **MATHEMATICAL ADC CONVERSION-COUNT result**, NOT real MRAM readout, area, energy, latency or proven external novelty. A physically useful implementation requires programmable threshold current references, a monotone and distinguishable `n -> Iread` mapping under GF access NFETs/student MTJs and shared-wire parasitics, and enough independent per-column threshold control to avoid serializing all columns. Four *codebook classes* still need DAC threshold levels, not merely four current sources. Charge metadata, DAC switching, control latency, comparator errors, and calibration. If per-column controls are too expensive or full prior art already conditions ADC thresholds on both operand populations, reject/modify the candidate.

## Discussion ask
“I found a concrete readout-control algorithm after reviewing DIB's block-size algorithm. I've tested a joint input–weight conditional threshold tree with a hard maximum comparison depth and restricted codebook budget; the four-bank version saves 9.28% of ideal comparator decisions against a CAL-optimized input-only controller on held-out real MNIST bitplanes. I know probability-based ADCs and tree search already exist, so my proposed contribution is the MRAM-specific joint-operand and bank-constrained implementation. I'd like your view on whether our available read circuitry can implement selectable per-column thresholds economically and whether this scope is viable for CA2/FYP.”

Evidence package: conversation download `E13_E15_DIB_algorithm_discovery.zip`, SHA256 `64df1bb27a9ba690345413a5f1ef4a4c117de00d1e984870b3fa255feb4e2c4e`. Detailed CA2 record: [E13–E15 discovery](../experiments/2026-11-04-E13-E15-DIB-conditional-ADC-discovery.md).
