# E24B — CAL-derived ADC-range falsification on completed E19 Spectre currents

**Executed:** NUS Singularity, 2026-11-04 according to user-provided terminal log.  
**Evidence class:** postprocessing of existing NUS GF hvtnfet + student static MTJ
32-shunt current circuits with *explicitly assumed* R=0/1/5 ohm per BL segment;
**not** PEX, actual ADC hardware, variation, energy or 256x256 readout.

## Integrity / settings

- Selftest: `E24B_SELFTEST_PASS` (constructed data, not a Spectre validation).
- Two independent existing E19 result files were processed; 8 CAL + 8 DEV and
  24 CAL + 24 DEV **per R** (n=7 and n=8 only).
- Source input SHA-256:
  - initial: `53f5eee150132654c08823f63053b37f6e63ec2304edd99eb24247552de48901`
  - confirmation: `f0217209427c4b1895cf1e9a8b1cfe40cc99d06f0a4c0bd4cc76ed234c66d714`
- Swept nested 3/4/5/6/7/8-bit ideal uniform ADC, fullscale 1.5/2/3 times
  per-R per-run CAL current range, offsets = CAL min - 0.15/0.25/0.35
  CAL span. Ranges and thresholds never use DEV.
- The initial E24A fixed 28/29 uA input fullscale produced **100% saturation**
  because E19 actual current is around 62–70 uA; E24A is invalid as an
  ADC-precision experiment. E24B corrects the range mismatch.
- Private E24B JSON: `~/mram_private/E02_256x256/E24B/E24B_20261104T162038_15/e24b_results.json`
  (not copied or checked into GitHub).

## E24B observed results

| E19 arm | First-run DEV | Confirmation-run DEV | Observation |
|---|---:|---:|---|
| 0 ohm/segment | 0 errors / 8 across all ADC settings | 0 / 24 across all | No observed count errors |
| 1 ohm/segment | 0 / 8 across all ADC settings | 0 / 24 across all | No observed count errors |
| 5 ohm/segment | CAL-fit varies 1–3 / 8 depending on settings; some 2 / 8 | CAL-fit usually 2 / 24, occasional 4 / 24 at coarse code | Analogue overlap limits ordered scalar decoding; ADC alignment sensitivity not reproducible at large magnitude |

At first-run assumed R5 and `FS=5.88003 uA, offset=61.0089 uA`:
CAL-fitted DEV errors by bits 3..8 = **[2,1,1,3,2,2] / 8**.
Thus 5-bit = 1/8 vs 6-bit = 3/8, but the **6-bit inherited 5-bit
decoder = 1/8**, proving this is decoder/calibration dependent under
nested ideal quantization, not fundamental loss of information.
The similar substantial 5->6 worsening did **not** reappear in the
larger independent 24 DEV study (R5 CAL-fit usually 2/24 across bits).
Some fixed-midpoint code-center outcomes differ by one event at 24 DEV.

On one confirmation R5 configuration `FS=5.03183 uA,
offset=61.342 uA`, **1/24 DEV case saturated**; exclude or separately
flag that setting in any no-clipping comparison. No saturation marks were
printed for other sweep entries.

## Decision and limitations

**E24B protocol PASS; observation of decoder-dependent bit nonmonotonicity
in a small held-out split PASS; robust replication / novelty NOT PASSED.**
There is no demonstrated general physical ADC coupling algorithm and no
proof precision hardware becomes less reliable. Counts are tiny, and the
sampled DEV cases had been used as development evidence in earlier E19/E20
analysis; avoid describing them as a new prospective final holdout.

Do not freeze the FYP around this bit-sweep alone. Use the already prepared
**E22 GF full-count 17-level** experiment to test whether a comparable
phenomenon survives on independent n=0..16 masks, with a continuous-current
baseline and CAL-fitted offset-only and near/far spatial corrections.
Its R0 CAL ADC window may clip at high R, so the analysis MUST report
saturation and separate clipping from bit-alignment effects before
interpreting an interaction. The E22 script must be considered
**prepared but NUS execution unverified** in this record.
