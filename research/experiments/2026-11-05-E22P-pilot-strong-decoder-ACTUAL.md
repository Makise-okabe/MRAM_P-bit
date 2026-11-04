# E22P — User-executed 51-DEV-per-R strong-baseline decoder audit

**Run:** NUS Singularity, 2026-11-04, user-pasted log. This is the
**small E22 pilot**, not the separate completed 1,530-circuit full E22 run.
Script `experiments/e22p_pilot_decoder_audit.py` executed and
`E22P_SELFTEST_PASS`. Per-count CAL/DEV=3/3, counts n0..16, same
51 DEV mask identities at R0 and assumed R5. All data are existing
GF hvtnfet + student static MTJ DC simulated currents, **not physical
array PEX**, ADC hardware, measured wire R or inferred BER.

## Per-R5 results (wrong exact-count/51 DEV)

| CAL calibration / reference | Decoder | continuous | 4b | 5b | 6b | 7b |
|---|---|---:|---:|---:|---:|---:|
| R0 nominal + near correction | quantized-reference | 29 | 21 | 26 | 29 | 31 |
| R0 nominal + near correction | code-centre | 29 | **21** | 27 | 29 | 29 |
| R5 per-count centroids, no near | code-centre | **13** | 15 | 15 | 15 | **13** |
| **R5 per-count centroids + CAL near correction** | quantized-reference | **2** | 10 | 10 | 3 | 3 |
| **R5 per-count centroids + CAL near correction** | code-centre | **2** | 8 | 6 | 3 | **2** |

At R0 all policies' continuous and 5–7-bit scores were 0/51;
4-bit = 3/51 due to the 17-count / 16-code bottleneck.

At R5, the per-R near-corrected code-centre decoder's count MAE is
0.0392 for continuous and 7-bit, versus 0.1569 for 4-bit.
No R5 7b ADC saturation was reported under nominal-near or
per-R-near. The original 4-bit advantage (21 versus 29 errors)
**reverses after stronger per-R calibration** (8 versus 2 errors).
This falsifies this particular claimed standalone algorithmic novelty,
but does not prove universal monotonicity across all decoders,
hardware or operating conditions.

### Interpretation and limitations

Strong per-R calibration is an optimistic **17-level** hardware/reference
baseline, with costs (programming/retaining reference codes, calibration
sample count, circuitry) not modeled. Only three CAL points per count
and three DEV points per count; confidence in generalization is limited.
DEV is development-inspected. These results are *actual user-executed
NUS GF-model current postprocessing* with assumed R5, not new Spectre
simulation performed by the audit.

A separate GitHub record,
`research/experiments/2026-11-05-E22-GF-fullcount-ACTUAL-results-and-decoder-audit.md`,
reports a **completed full E22 run** with 6 CAL + 12 DEV / count at
all R0/1/2/3/5 settings. Its private file is
`~/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162140_178/e22_results.json`.
The E22P postprocessor should run on that full dataset before
new GF simulations. Full E22P decoding numbers are currently **unknown**;
do not transfer pilot 2/51 to 204 DEV.

## Gate

ADC nonmonotonicity under a frozen misaligned reference is reproducible
as *decoder behavior*, but **not** a demonstrated new algorithm or
intrinsic higher-bit reliability harm. The 204-DEV full-dataset E22P
comparison should determine whether conventional per-R centroids +
CAL near correction substantially closes the apparent failure regime.
A separate predictor candidate must outperform a cheap calibrated
position model with physical and task-level relevance before claiming novelty.
