# E22B / E22P full 17-count decoder audit — NUS user-executed outputs

**Date:** 2026-11-04 user-pasted NUS Singularity log, interpreted 2026-11-05.
**Source:** `E22_GFCURRENT_20261104T162140_178/e22_results.json` under the user's private E22 directory, 1,530 previously executed GF access-NFET + student-static-MTJ DC circuit cases. Assumed line R=0,1,2,3,5Ω/segment; 17 counts at m=k=16, 6 CAL and 12 DEV per count; **204 DEV masks/R**. Mathematically simulated uniform ADC, not physical ADC circuitry. Neither original E22 nor this reanalysis validates actual 256×256 GF PEX, ADC hardware, device mismatch, task inference or energy.

## Execution evidence and data provenance

E22P strong-reference audit and E22B digital-after-ADC audit: both Python selftests PASS, full JSON produced under
`~/mram_private/E02_256x256/E22/FULL_DECODER_AUDIT_20261104T163621_15/`.
The file provided to this chat contains aggregated NUS terminal output; private raw currents are **not** in this repo and have not been independently reprocessed in this environment.

## Full-data 7-bit wrong count / 204 DEV

| Assumed R Ω/segment | Frozen nominal raw | Per-R analog centroid+near (E22P code-centre, optimistic pre-ADC) | E22B digital after-ADC: reprogrammed CAL range + near |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 1 | 143 | 0 | 0 |
| 2 | 192 | 0 | 0 |
| 3 | 192 | 3 | 3 |
| 5 | 192 | 26 | **25** |

E22B additional R5 controls (7b wrong counts/204):
- R-specific **continuous** count centroids without near correction: 57;
- R-specific continuous centroids with near: 26;
- fixed R0 ADC window + CAL code lookup: 87 (24 DEV currents outside frozen window);
- reprogrammed R5 ADC window + CAL lookup: 73 (0 outside);
- fixed window + post-ADC near: 39;
- **reprogrammed ADC window + post-ADC near: 25** (0 outside).

At R5, R-specific CAL near correction reduced DEV adjacent sampled interval overlaps from **14/16** to **9/16** pairs. At R3 raw overlaps were **7/16**, reduced to **0/16** after near; at R2 and below both 0/16. Overlap is a sampled scalar threshold ambiguity, **not** a population BER, universal impossibility theorem, or measured silicon.

## Scientific decision

1. Strong CAL-only calibration and correction reduce much of the apparent R/bit-depth catastrophe; **reject standalone 'more ADC bits make intrinsic fidelity worse' novelty**. Nested higher-bit uniform quantizers can emulate lower bits at identical scale and offset, and frozen-reference decoding was responsible for substantial nonmonotonicity.
2. At high assumed R=5, **25/204 sampled count errors remain** even with reprogrammed CAL window and post-ADC near correction (12.25% descriptive, not silicon BER); similar continuous-near 26/204 shows much of the residual is analogue/position dependent, not ADC resolution.
3. A **diagnostic hypothesis** is that residuals correlate with second-order spatial wire-load moments beyond the cheap near-count feature. Test a small preregistered CAL-only model against strong per-R 17-centroid+near before any new Spectre. This is not yet a novel method; suffix moments and spatial corrections have prior art.
4. No general physical usefulness can be claimed until interconnect R/geometry is grounded in authorized extraction/geometry and a representative multi-column 256×256 target is built or a justified scaling model is validated.
5. DEV was repeatedly inspected in E22/E22P/E22B; future same-dataset result is **development evidence**. Freeze a new independently generated mask/test set and device-chip assignments for final claims. Charge all proposed reprogrammable ADC/reference and feature-extraction costs.

**Next gate:** E23A CAL-feature residual diagnostic on existing E22 private currents (7b code-centre, per-R 5% guarded CAL window, per-R 17 CAL references, near-only baseline, a small spatial-moment candidate with no DEV label leakage). Reject candidate if it cannot improve both CAL cross-validation and previously inspected DEV against near baseline; even positive is only preliminary and requires new masks/actual interconnect range.
