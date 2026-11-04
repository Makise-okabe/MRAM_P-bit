# E19 — first COMPLETE student-executed GF-NFET + custom-MTJ read-current screen
Date: 2026-11-04. **Evidence: NUS Singularity Spectre 23.1.0.403.isr6 user-pasted terminal log; GF access-NFET compact-model circuit, NOT GF array PEX.**

## Run integrity
- Prior E19 run failed before simulation because string/Path mismatch. The exact-SHA-guarded repair succeeded: `e19_gf_nfet_mtj_nonideal_count_gate_v2.py`, SHA256 `b6bec40bc234fac406d191229146354a5fe47c6969fb6db6a672e607ddf83e54`. Selftest PASS.
- GF `hvtnfet` from local licensed model includes; model `mtj_read_v0` student two-terminal static P/AP behavioural model SHA256 `1d22984b7be5135c07bb5e392d73aa53e1ad42b7c4bdc6d2fc11bb3f313b9a88`. Historical W=80nm design template, read=50mV, WL-on=.8V. Read operating point not newly safety-qualified. No independently measured wire R; the script adds explicit 0/1/5 Ω *per-segment* resistors as chosen assumptions.
- Nominal 32 parallel NFET+MTJ shunts attached along a 32-segment shared resistor ladder. `m=k=16`; true intersections n=7 vs8, new random but valid CAL/DEV placement combinations, no CAL/DEV mask reuse.
- First run: 4 CAL +4 DEV **per class** = 16 masks per R, 48 Spectre circuit cases.
- Independent confirmation: 12 CAL +12 DEV **per class** = 48 masks per R, 144 circuit cases.
- **Total 192 per-mask per-R circuit cases across the two experiments; 64 unique mask placements before R sweep.** All R chunks completed successfully, no Spectre failure in provided log.
- NUS private output first: `~/mram_private/E02_256x256/E19/E19_GF_NFET_MRAM_20261104T144120_179/e19_results.json`. Confirmation: `~/mram_private/E02_256x256/E19/E19_GF_NFET_MRAM_20261104T144132_384/e19_results.json`. The GitHub note does not contain private PDK decks or mask-level current values.

## Actual NUS Spectre printed results

| Assumed R per shared-BL segment | First CAL mean current separation | First sampled DEV overlap | First DEV threshold errors | Independent CAL separation | Independent sampled DEV overlap | Independent DEV threshold errors |
|---|---:|---:|---:|---:|---:|---:|
| 0 Ω | 1.8352 uA | 0 | 0/8 | 1.8352 uA | 0 | 0/24 |
| 1 Ω | 1.7870 uA | 0 | 0/8 | 1.8691 uA | 0 | 0/24 |
| 5 Ω | 1.6219 uA | 0.31172 uA | 2/8 (25.0%) | 1.9854 uA | 0.20122 uA | 2/24 (8.33%) |

Threshold used: simple midpoint between CAL class-mean currents. This is **not an optimal noisy ADC classifier**. Observed DEV range overlap means no *strictly monotonic single-threshold split* can exactly classify ALL these sampled n=7/8 current values; it does not imply no statistical decoder can have lower error. 2/24 has 95% Wilson interval approximately **2.32%-25.85%** and 0/24 still allows an upper ~13.8% error, so do not cite precise 8.33% as a physical BER. Difference between the two 5Ω runs also illustrates limited sample size.

## Scientific conclusion — partial physical-failure gate, not thesis novelty
1. GF compact access NFET plus student MTJ model successfully generates different nonideal currents under assumed distributed BL resistance. At R=0 the n7/n8 separation is stable, supporting netlist basic consistency.
2. **At assumed 5Ω/segment**, different spatial arrangements of adjacent true counts can have **overlapping sense-current ranges**, and nominal midpoint decoding made errors in both independent tests. This falsifies any unconditional claim of *lossless exact count conversion using a single ordered scalar threshold* for this **constructed model and those masks**.
3. **At assumed 0 and 1Ω/segment**, no errors were observed in small DEV sets; this is NOT proof of universal error-free read.
4. E15's separate E17 mathematical result (8.8838% fewer ideal decisions with bank-only metadata versus matched input-only control) **has not been re-evaluated on E19 measured currents**; no real ADC reference logic, comparator noise, PEX or energy included. Sorting ADC thresholds cannot undo an overlap of the analog information itself. Distinction from DIB's algorithm ≠ publication novelty.
5. GF access NFET compact-model behaviour is real licensed foundry simulation; **the 5Ω wire is not measured PEX** and 32-row network is not an extracted 256x256 physical macro, no PVT or MTJ mismatch.

## Next E19C test — use existing read-current outputs before spending more Spectre time
- On each saved `e19_results.json`, compare **CAL-optimized single threshold** with current naive CAL mean midpoint, using an independent DEV split.
- At fixed CAL-tuned abstention/second-measurement quota, report DEV **coverage-versus-error**; do not claim error is removed until an actual second independent sensing operation is physically modelled. This distinguishes poor threshold calibration from truly ambiguous analog current under placement.
- Confirm the voltage/current sense polarity is consistent across masks and resistance sweep.
- Then obtain representative real BL/SL series resistance from authorized geometry/PEX and measure actual `n -> I` distributions in an appropriate 2T1MTJ structure. Only if it is sufficiently distinguishable should E15 move to matched ADC energy-delay/accuracy comparison.

### Research-gate recommendation
**E19 status: PASS for local transistor-level nonideal failure mechanism / FAIL for unconditional exact-count assumption at 5Ω assumed R / OPEN for actual target physical R and E15 hardware energy.** CA2 should retain both completed positive finding and negative warning. Do not lock an MRAM ADC invention based on these data alone.
