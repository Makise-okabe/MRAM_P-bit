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


## H0 refinement: location-dependent cumulative-current footprint (new *hypothesis*, not new law)

For a \emph{simplified one-ended resistive bitline} with a segment resistance
r_l and positive selected-cell conductance g_i, define the current remaining
downstream of segment l in the ideal (zero-line-resistance) circuit:

    J_l = Vread * sum_{i>=l} a_i g_i.

Linearizing the voltage drop caused by a small BL resistance gives an
approximate reduction in total sensed current:

    DeltaI ~= Vread * sum_l r_l (sum_{i>=l} a_i g_i)^2.

If the g_i were equal, this becomes proportional to a mask-only spatial
footprint Phi(a) = sum_l r_l (sum_{i>=l} a_i)^2.

At *the same* total active count and equal P/AP composition, Phi may differ
substantially. This is a physically motivated variable not captured by
activity count alone. It does NOT capture access-device nonlinearity,
distributed/floating SL parasitics, WL delay, varying bitcell conductance,
sensing feedback or coupled columns. It must be derived/check against the
actual authorized topology, not imposed as its behaviour.

Possible distinct *method* (only if physical evidence supports it):
precompute or cheaply estimate spatial footprint from the activated-row
bitmap and use it, with a small calibrated LUT, to choose between a direct
single read, a dynamically partitioned read, and supported ADC/reference
settings. The controller must not cheaply access the unknown exact dot
product. Optimize across real readout cost, metadata and decoding errors.

**Critical competitors:** DIB-CIM (activity and ADC choices), JSSC 2025
Roy et al. SEC (BL/SL correction), Nature Communications 2023
hardware-aware IR-drop modeling, row-aware calibration, and a joint tuned
SEC+DIB baseline. IR-drop location effects and cumulative-wire-current
models are old physics. Only a new, economical, verified controller or
nontrivial predictive bound that changes a physical decision could earn
novelty.

Falsifier: equal-count spatial effects are negligible, the footprint is a
poor held-out predictor with the actual 2T1MTJ/local-SL topology, the
controller overhead dominates, or the tuned correction/adaptive baseline
matches its quality/cost frontier.

Further reference:
https://www.nature.com/articles/s41467-023-40770-4
