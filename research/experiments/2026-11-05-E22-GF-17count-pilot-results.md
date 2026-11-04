# E22 — 17-count GF current / ADC-precision pilot: NUS execution results

**Execution reported:** 2026-11-04 (NUS Singularity; user-pasted terminal output).
**Evidence tier:** user-executed nominal GF hvtnfet compact model +
student-owned static MTJ, 32-branch resistor ladder with **explicit assumed
0 and 5 ohm per segment**, 50 mV read, WL 0.8 V. Not 256x256 PEX,
physical ADC, read settling, energy, real interconnect, device mismatch, or inference.

## Pilot run integrity

- Script \`experiments/e22_gf_precision_regime.py\`, selftest PASS.
- Full legal n=0..16, m=k=16, 32 physical row positions.
- 3 CAL +3 DEV independent placement masks **per count**, 102 case profiles
  per assumed R, 204 completed Spectre circuits across R0 and R5.
- Same mask identities reused across R. Completed all seven chunks per R
  without reported Spectre solver failures.
- Raw user-private source:
  \`~/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162651_7025/e22_results.json\`
- Analysis:
  \`~/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162651_7025/E22_ADC_REGIME.json\`.
- The source JSON was not uploaded in this session; this document records the
  **terminal-reported aggregates**, not independently inspected per-mask values.

## Reported wrong exact-count predictions / 51 DEV

| R [assumed ohm/segment] | Policy | Continuous | 4b | 5b | 6b | 7b |
|---:|---|---:|---:|---:|---:|---:|
| 0 | raw | 0 | 3 | 0 | 0 | 0 |
| 0 | offset-only | 0 | 3 | 0 | 0 | 0 |
| 0 | offset + near | 0 | 3 | 0 | 0 | 0 |
| 5 | raw | 48 | 48 | 48 | 48 | 48 |
| 5 | offset-only | 30 | 26 | 32 | 33 | 32 |
| 5 | offset + near | 29 | **21** | 26 | 29 | 31 |

Nominal R0 calibrated window retained for R5: at R5 raw, 6/51 samples
were clipped **below** range; at R5 offset-only and near correction,
0/51 were saturated. R5 CAL global offset \`-4.97e-6 A\`;
near coefficient \`+2.935e-7 A / near-half active row\`. Neither
coefficient represents measured interconnect properties.

## Interpretation and missing controls

- **Positive diagnostic observation:** with the specific R0-reference
  quantized-centroid decoder, the R5 corrected 4-bit run had 21/51
  wrong exact-count predictions versus 31/51 at 7-bit.
  This is not a physical ADC precision-induced loss of information:
  uniform nested quantizers preserve coarse codes, and the existing
  decoder rounds **reference levels as well as sensed currents**,
  allowing ties/collisions in coarse code space. It is a particular
  fixed-decoder/calibration effect and may reflect a biased nominal
  reference rather than genuinely new coupled physics.
- With a 4-bit ADC only 16 codes exist for 17 legal count classes,
  so even the R0 ideal condition had 3/51 count errors. Cardinality
  is already a known conventional limitation, not novel.
- With R5 continuous R0-reference, near-corrected decoding already
  misses 29/51; most of this pilot's failure is **analogue/reference
  mismatch**, not intrinsic quantization.
- The 51 DEV count labels cover 3 spatial patterns per count: far too
  few for robust generalization or precise BER confidence claims.
  The DEV data are now **development-inspected**, so additional final
  validation needs new frozen independent masks.
- Missing evidence: count MAE from full JSON, paired 4b-vs-7b error
  identities, per-count inversion, 17-level R5 CAL calibration,
  code-centre decode versus rounded-reference decode, ADC noise,
  real PEX and task-level results.

## Immediate next experiment E22P (NO new Spectre)

Script \`experiments/e22p_pilot_decoder_audit.py\`, prepared in repository,
compares two decision rules:
(1) original quantized-reference-nearest-code,
(2) unquantized reference nearest to reconstructed ADC code centre.

For each, test R0 nominal raw/offset/near and strong R-specific **17
CAL-labelled count-centroid references** (raw and near corrected).
Report exact count error, count MAE, ADC clipping, CAL centroid-order
inversions, and **paired 4bit vs 7bit** disagreement counts.

If 4-bit advantage disappears with stronger decoder/reference
calibration or worsens count MAE, narrow the claim to this one
reference-collision effect. If it survives both, still require
prospective independent data and actual interconnect relevance
before novelty. Do not spend 1,530 more Spectre cases on the same
baseline without interpreting this pilot.

### NUS E22P command

\`\`\`bash
set -euo pipefail
cd "$HOME/MRAM_Path_Finding"
git pull --ff-only
python3 -m py_compile experiments/e22p_pilot_decoder_audit.py
python3 experiments/e22p_pilot_decoder_audit.py --selftest

SRC="$HOME/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162651_7025/e22_results.json"
OUT="$HOME/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162651_7025/E22P_decoder_audit.json"
python3 -u experiments/e22p_pilot_decoder_audit.py "$SRC" --out "$OUT"
\`\`\`

**Status:** E22 pilot completed, E22P postprocess script committed but
**not yet executed** on actual E22 currents. Full E22 R0/1/2/3/5
6 CAL+12 DEV is still pending and has no asserted results.
