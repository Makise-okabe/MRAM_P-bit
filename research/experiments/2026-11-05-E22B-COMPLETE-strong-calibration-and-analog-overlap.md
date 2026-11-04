# E22B — completed NUS real GF-current postprocessing: strong CAL ADC recalibration and sampled analog count ambiguity

**Run origin:** student pasted NUS Singularity output on 2026-11-05. **Status: E22B execution COMPLETE**; no new Spectre run; reanalysis of 1,530 prior E22 GF access-NFET + student nominal static-MTJ DC simulations. **Physical limits:** 32-row constructed shared BL, R=0/1/2/3/5 Ω/segment chosen as assumptions (NOT GF PEX), no physical ADC/comparator, no device mismatch, no actual MNIST classification.

**Data:** same E22 306 mask identities per R, 102 CAL (6/count) and 204 untouched DEV masks (12/count), m=k=16, 17 count classes 0..16. R-cases are paired on the *same masks*, not independent device/chip samples. Source private:
`~/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162140_178/e22_results.json`;
E22B output `~/mram_private/E02_256x256/E22/E22B_decoder_calibration.json`.

## Empirical NUS result — 204 DEV cases per assumed R

### Reprogrammed ADC fullscale with CAL near/far post-ADC correction
| Assumed R (Ω/segment) | 4 bit | 5 bit | 6 bit | 7 bit |
|---|---:|---:|---:|---:|
| 0 | 12 | 0 | 0 | 0 |
| 1 | 11 | 0 | 0 | 0 |
| 2 | 27 | 2 | **0** | **0** |
| 3 | 41 | 6 | 6 | **3** |
| 5 | 47 | 31 | **25** | **25** |

7bit error at assumed R5 is **25/204=12.255%**, vs old frozen-R0 decoder **192/204=94.118%** (decoding/reference artifact mostly corrected; NOT a genuine 82pp hardware improvement or measured energy).

### Continuous CAL-only count-centroid, no ADC quantization
| Assumed R | R0 fixed nominal decoder | CAL per-R 17-count centroid | CAL per-R centroid + near-position |
|---|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 1 | 140 | **0** | **0** |
| 2 | 192 | 6 | **0** |
| 3 | 192 | 19 | **3** |
| 5 | 192 | 57 | **26** |

This distinguishes reference misalignment from remaining position variation. The naive R0 decoder is not a strong baseline once current gain/range shift.

### Matched ADC controls at 5Ω
- Original frozen-R0 nominal rule: 4/5/6/7-bit errors **192/192/192/192**.
- CAL code-to-count lookup at fixed ADC window: **96/89/88/87**.
- CAL code-to-count lookup with CAL-reprogrammed ADC fullscale: **95/81/65/73**.
- CAL near/far correction post-ADC, fixed fullscale: **86/46/41/39**.
- CAL near/far correction post-ADC, reprogrammed fullscale: **47/31/25/25**.
- Continuous scalar current CAL per-R centroid+near: **26** errors.
Reprogramming current fullscale is hardware-costly and optimistic; the code-to-count lookup calibrates a different digital decision rule. Cases outside the nominal fixed ADC window: 0,0,12,12,24 for R0,1,2,3,5; outside CAL-reprogrammed window: 0 for every R in this DEV sample.

### DEV current-level separability, 16 adjacent count boundaries
| Assumed R | Nonseparable ordered scalar boundaries RAW | After CAL near-position correction |
|---|---:|---:|
| 0 | 0/16 | 0/16 |
| 1 | 0/16 | 0/16 |
| 2 | 0/16 | 0/16 |
| 3 | **7/16** | **0/16** |
| 5 | **14/16** | **9/16** |

The 9/16 at R5 are *sampled* interval overlaps after **this particular near/far correction**, not a theorem that all mappings using the full activation/weight mask cannot distinguish counts. Need test spatial controls such as centroid and suffixQ, and true count-level effects across more occupancy regimes.

## Critical interpretation
1. **Do not claim higher ADC precision intrinsically worsens accuracy.** With the same fixed fullscale, fine uniform quantization contains all coarse bits (the higher-resolution converter can discard LSBs). E22's nonmonotonic errors came from a *specific mismatched decoding policy*, and some residual shifts in a CAL-sparse decoder.
2. **Do not call all 5Ω errors irreversible:** near-position CAL correction is deliberately simple; a richer input-position function may mitigate the residual. Even samples with overlapping levels under near-only cannot be separated by a single *near-corrected scalar threshold*, but this does NOT preclude using the known input mask differently or other ADC models.
3. R2 corrected 7bit=0/204; R3 corrected 7bit=3/204; R5 corrected 7bit=25/204. This supports a *model-specific boundary under these ASSUMED resistor values*, not GF 22FDX+ physical interconnect threshold.
4. 4bit has 16 codes for 17 distinct count classes, so some information loss is cardinality-unavoidable in this specific single-code architecture. ADC energy/area/time not measured.
5. 102 CAL (6/count) is a small calibration set, and exact crossover probabilities are not established. DEV errors within an R are samples of spatial masks; R repeats are paired on the same masks, not independent chip samples.

## Next strong-control gate: E22C (pending actual user execution)
[Committed E22C script](../../experiments/e22c_spatial_feature_ablation.py) compares **raw, near-count, activation centroid and input suffix-load Q** correction trained solely on CAL, under the same reprogrammed ADC range and same independent DEV masks. It reports continuous and 4/5/6/7bit error and adjacent count separability, plus per-mask near-vs-centroid/suffixQ discordance.

**Decision rule:** If plain centroid or other cheap geometry removes most R5 residual count errors, the near-only failure boundary was *not* a new fundamental nonideality limit; do not promote a complex predictor. If count overlaps and held-out errors remain even under strong cheap geometrical controls, E23 can test a physical-margin failure-boundary predictor against those same controls; do not presume novelty from the existence of errors.

Source evidence: student terminal results copied verbatim into this report. No licensed GF PDK or private deck committed.
