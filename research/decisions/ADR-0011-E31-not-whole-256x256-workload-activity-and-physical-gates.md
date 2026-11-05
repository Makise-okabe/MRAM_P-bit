# ADR-0011 — E31 is not a whole-macro low-error result: workload, width and physical operating-point gates

**Date:** 2026-11-05 (Singapore). **Status:** active clarification / supersedes any implication that E31 0/36 means the target 256×256 MRAM-CIM has too few errors to justify reliable-computation research. This is an evidence-scope correction, **not a new simulated result**. Original F1 inference-failure prediction remains primary; F3 reliability-aware mapping is an optional intervention, F7 Ising is paused (ADR-0010).

## Narrow E31 fact, not broad conclusion

The NUS E31 **actual GF compact NFET + student static MTJ DC-current solve** had 256 physical rows ×4 jointly modeled columns, **24 active rows** (~9.375% of the 256-row depth), fixed nominal resident MTJ P/AP states, C0 evaluated only for **n=11,12,13**, a hypothetical 0.25 Ω **per-row** BL ladder, hypothetical 0.25 Ω shared return, ideal row-gate sources, no physical ADC/mismatch/noise/dynamic MTJ or 1T1 layout PEX, and 36 new input masks from one nominal model. Global CAL decoder **15/36 wrong** in the two assumed-wire arms; input Q frozen from nine earlier CAL patterns **0/36 wrong**, including 0/18 new spatial-family masks.

**Correct inference:** A particular position-informed read correction generalizes in this restricted *nominal, constructed* circuit and evaluated count range. **Incorrect inferences:** 256×256 target has few hardware errors; calibrated actual hardware has zero residual; MRAM has no failure-prediction problem; all 256 read columns are independent; N2 selective digital recomputation has been ruled out; 36 masks = 36 chip samples.

**The untested variables have separate physical roles.** Physical depth = 256 row/device/BL locations. Simultaneously ON WLs = m, determines active current/fan-in/sensing range; n = ON rows with P-state MTJs is the dot-product count. Array width = number of columns, which affects per-column reliability only if shared WL/SL/supply/sense/reference/coupling load is modeled. 256 columns behind independent ideal sources does not establish width-dependent error. ADC usable range, clipping, effective number of bits, speed and calibration overhead matter. PEX R and C from legal GF geometry, cell device/mismatch, WL driver and real read timing must anchor these effects.

## Frozen E01 W4A8 network shows m=24 is not representative of every read

The *executed* E01 frozen MNIST W4A8 workload report (software-only, not electrical): [E01 audit](../experiments/2026-11-04-E01-frozen-MNIST-workload-audit.md), packet SHA256 `400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a` and E01 reported 128 CAL /256 DEV parents. This gives actual **logical read-group activity**:

| Scheduling group | Mapping | Mean m among nonempty reads | Max m observed |
|---|---|---:|---:|
| 32 | Original | 5.591 | 23 |
| 32 | CAR alpha 0 | 8.708 | **32** |
| 64 | Original | 10.495 | 43 |
| 64 | CAR alpha 0 | 15.282 | **63** |
| 128 | Original | 18.789 | 71 |
| 128 | CAR alpha 0 | 25.190 | **110** |

These are per-group software activity statistics, not physical simultaneous WL configurations; the mapping/sensing implementation must justify actual parallel read group size. The 256-group summary in the earlier public E01 audit only records nonempty-read totals, **NOT** a detailed per-plane m histogram; do not invent its tail. Still, m up to 110 in a *candidate* 128-row logical read group already demonstrates that a fixed 24-active-row test cannot settle target operating-range reliability. Real A8 planes have different activity distributions, and the signed W4 planes use physically distinct resident weights, not identical C0 count classes.

## Literature / closest correction methods — no premature novelty

- Saion K. Roy and Naresh R. Shanbhag, **“Energy-Accuracy Trade-Offs for Resistive In-Memory Computing Architectures,”** IEEE JxCDC vol. 10, pp. 22–30 (2024), DOI: [10.1109/JXCDC.2024.3381888](https://doi.org/10.1109/JXCDC.2024.3381888). The measurement-validated resistive-IMC model includes conductance variation, BL/SL parasitics, current-mirror mismatch and ADC thermal/quantization effects. It explicitly addresses dot-product dimension and inference-level accuracy. Do not interpret the reported results as direct measurements of our GF student model.
- S. K. Roy *et al.*, **“Compute SNDR-Boosted 22-nm MRAM-Based In-Memory Computing Macro Using Statistical Error Compensation,”** IEEE JSSC vol. 60, issue 3, pp. 1092–1102 (2025), DOI: [10.1109/JSSC.2024.3442013](https://doi.org/10.1109/JSSC.2024.3442013). This physical macro already uses offset-compensating current sensing to address ADC column mismatch and statistical error compensation for BL/SL-induced nonlinearities, with reported NN accuracy changes. Consequently a generic spatial calibration or Q-inspired wire correction by itself is **not automatically a new contribution**. Compare against their correction principles in a clearly stated equivalent architecture/feature/cost setting before novelty claims.

## New hierarchy of immediate falsification gates

**E33 (code committed, NUS PENDING)**: mathematical fixed-fullscale ideal ADC quantization of existing E30 CAL/E31 DEV GF currents at predeclared bit depths, with no DEV tuning, compare current-Q versus continuous mean-row/near-far baselines; report clipping. **This is not a physical ADC or energy measurement.** [E33 protocol](../experiments/2026-11-05-E33-frozen-GF-ADC-precision-PENDING.md).

**E34 (code committed, NUS PENDING)**: evaluate **all 4** jointly solved GF columns, recover their distinct P/AP weight maps, fit 9 CAL points per column and test 36 E31 new masks×4 columns, with true n ranges and count extrapolation checks. Four columns are **not** four signed bitplanes. [E34 protocol](../experiments/2026-11-05-E34-four-column-calibration-generalization-PENDING.md).

**E35 (pre-registered question only; new GF high-activity simulation NOT executed)**: recover actual E01 A8-plane `m` distributions and cross-link physical read grouping/scheduling to m; verify full per-plane m histogram especially for 256-row grouping, never confuse group-128 m max110 with a measured 256-physical-line instantaneous current. Choose fixed, workload-justified strata including 0 (idle/offset), low, typical, high, heavy-tail near 64/96/110 and possibly extreme activity only where actual workload supports it. For each, test the **full count range supported by the stratum**, not only n≈m/2, and use independent CAL/DEV input masks and resident P/AP patterns. The existing E30 generator only allows m=16,24,32; **do not claim it can execute m=64/96/128 without a new topology/scenario audit and NUS test.** These high-m tests remain conditional on safe read bias, practical current range, model convergence, and credible physically extracted wire network.

**E36 / Width gate (design only)**: preserve identical C0–C3 masks and resident weights when moving 4→16→more columns so changing neighbor activity/shared supply/SL/driver network is the only perturbation. In a 4→16 trial, justify column-addition topology, supply wiring and physical return R/C. A full 256×256 PEX gate cannot be met by a larger ideal-source schematic, synthetic shared ground, or old 2T local-floating-SL DSPF.

**E32 (binding PHYSICAL next task)**: actual 1T1-specific GF CMOS+metal BL/WL/SL geometry and extracted R/C (or qualified hybrid with external student MTJ), read bias, sense speed/ADC budget; compare to arbitrary 0.25Ω/row segment. This is the critical physical justification for scaling any nominal GF result.

**Final downstream F1 question**, only after these conditions: can an inexpensive, deployed feature set predict **post-calibration W4A8 neural inference failures** or select exact-digital substitutions better at equal system cost than no repair, calibrated margin, strong continuous location/near–far controls, independent-plane scores, or optimized significance-first recovery? Budget must include Q-feature extraction (with optimized O(m) algorithm where possible), ADC conversions, and any recomputation, memory, latency and calibration overhead. Q's nominal 0/36 is not an uncosted universal solution; N2 remains conditional, not invalidated.

## Prof Fong bottom line

> The 256 in E31 refers to physical read-row depth, **not** a characterized 256×256 MRAM-CIM macro. We had 24 active rows and four columns with assumed wiring. Global decoding made 15/36 count errors; frozen Q calibration fixed all 36 C0 cases, but this only establishes a nominal operating-point result. Our earlier frozen MNIST traces already contain candidate grouping reads with up to 63 or 110 simultaneously active logical rows, so the observed test point is incomplete. I am now testing ADC precision and four-column calibration generalization while preparing workload-justified activity coverage and, most importantly, physically extracted 1T1 BL/WL/SL parasitics. Prior 22nm MRAM literature also includes compensation for these nonidealities, so the actual novelty needs to be task-level failure prediction/decision gains beyond strong calibration, with matched cost.
