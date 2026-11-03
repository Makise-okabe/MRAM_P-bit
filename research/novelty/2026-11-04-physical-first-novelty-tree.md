# Novelty-screen decision tree — original mechanisms only (not a result)

4 November 2026. No broad scheme below is claimed unpublished.

## The first physical observable is more important than the current algorithm

**New-array test:** same ideal P/AP count + same total active rows, different positions on a **fresh fully populated 256-row MRAM column** and its 256x256 hierarchy. This can distinguish workload occupancy effects from actual interconnect-induced deformation.

### H1 — Spatially conditional readout observability
If equal-count patterns are physically distinguishable by location-dependent current distortion, ask whether a **small number of observable mask moments or reference signals** predicts the distortion sufficiently to correct decoded counts on independent masks. Avoid giving the runtime logic exact weight products that negate CIM. Explicitly compare:
- tuned ADC + per-column affine calibration,
- physically informed row-factor/SEC-style correction (JSSC 2025),
- count/activity-only calibration,
- candidate with bounded metadata and circuit cost.

**Novelty risk:** row-dependent correction/SEC and IR-drop-aware mapping already exist. A new sufficient statistic, proof of when it fails, or cost/quality advantage is needed. Merely mapping near/far or selecting reference voltages is not original.

### H2 — Cross-cycle decoded error cancellation
If independent target read cycles show persistent covariance after real calibration, test a **signed-bit-plane reconstruction-aware assignment or legal code/reference schedule** that changes `b^T Σ_e b` under fixed overall read budget. Compete with:
- tuned CAR, zero-rate sorting, random and equal-budget best-of-random,
- shuffling that randomizes deterministic column errors,
- retuned ADC/SEC and activity-adaptive blocks,
- covariance-ablated scores.

**Novelty risk:** matrix covariance formula is textbook mathematics and correlation/decorrelation already known. E03M/E03Q use an oracle-like calibration and cannot pass this gate. A practical mapper with genuinely different decisions and lower held-out errors is required.

### H3 — Ising local-field update with a controlled sampling kernel
If new target hardware can compute binary-MTJ local fields at useful cost, identify whether a **bounded or verified refresh/control decision** maintains a selected stochastic update law under persistent mismatch and read noise. Compare exact incremental digital fields (Snowball and pipelined p-computers), fixed-coupling theory, ordinary periodic refresh and equal-budget independent sampling.

**Novelty risk:** cache updates, adaptive precision, gauge transforms and conventional error mitigation are already known. A distinct cheaply implementable controller, measured hardware cost and advantage at true-Hamiltonian quality are required. Stable binary eMRAM is not by itself a stochastic p-bit.

### H4 — Subarray organization only if full-array parasitics demand it
If monolithic target arrays exhibit a concrete physical limit, compare physically isolated 16/32/64-row sectors, with explicit local sense/ADC, addressing, partial accumulation, row-driver and area energy costs. Compare to DIB-CIM's dynamic block sizing and VARA's co-zero mapping; smaller logical batches alone do not physically shorten wires.

## Evidence hierarchy and kill rules

1. New licensed target topology and safe nominal read;
2. Physically relevant matched-pattern response on fully populated array;
3. Decoder / calibration baselines;
4. One new *method* with bounded control/metadata and a physically justified advantage;
5. Held-out network or Ising task benefit (not merely MSE); total cost.
Any failed candidate remains failed; do not rescue it by attaching Ising or an estimator chapter.

## Closest paper families to inspect fully

- Roy et al., JSSC 2025, statistical error compensation and BL/SL parasitics, DOI:10.1109/JSSC.2024.3442013.
- VARA, arXiv:2609.00421v2, zero-clustering and row reordering.
- DIB-CIM, IEEE TCAS-I 2026, DOI:10.1109/TCSI.2026.3726936, adaptive WL blocks and ADC.
- Zhang, Deaville & Verma, DAC 2022, macro error statistics and shuffling.
- 'Achieving high precision in analog in-memory computing systems', npj Unconventional Computing (2026), including established slicing, ECC and iterative refinement techniques.
- Snowball and pipelined Ising p-computers (2026) for exact incremental-field baselines.

None is considered defeated without access to the relevant method sections. This document proposes **research hypotheses**, not research results.
