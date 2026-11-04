# E23A — residual spatial mechanism screen (PREPARED, NOT YET RUN)

Context: User NUS full E22B audit on assumed R5 showed a 7-bit, CAL-only reprogrammed current window + post-ADC near/far-corrected decoder at 25/204 wrong counts. Per-R continuous-current near-corrected 17-centroid decoder was 26/204 wrong; the remaining errors are largely analog/reference-limited in this constructed model, rather than insufficient precision. Nine of sixteen adjacent-count pairs had overlapping sampled current intervals after near/far correction.

**Experiment:** run the committed Python 3.6 standard-library script experiments/e23a_residual_spatial_diagnostic.py on the existing full E22 source dataset. It does NOT run new Spectre, read PDK files, claim actual PEX, build hardware ADCs, or assess inference accuracy. All 0/1/2/3/5 ohm/segment line resistances are explicit assumptions.

**Predeclared comparison:** R-specific 17 count-centroids + CAL-fitted near/far correction versus the same centroids with a small physically motivated input-only spatial-suffix-Q feature and a count-hypothesis interaction. Candidate model predicts the current for EACH possible n=0..16, then chooses the closest reference to the 7-bit post-ADC code center. It never computes features from true DEV n: the count-dependent feature is evaluated separately for each hypothetical n.

Both policies use the identical ADC full-scale range derived from CAL extrema with a 5%-span guard and the same physical current samples. Candidate coefficients are CAL-fitted with mild fixed ridge, while near baseline gets unregularized OLS. Three-fold stratified CAL validation (six CAL examples per n => four train, two validate in each fold) screens stability. The 204 DEV samples per R were already inspected by E22/E22P/E22B and are developmental rather than independent final holdout.

The script also reports simpler centroid-only, activation centroid, suffix-Q, near+centroid and near+suffix-Q alternatives, with count MAE and ADC clipping. A first-screen candidate should beat near alone on CAL CV and reduce DEV errors at least 25% relatively without worsening MAE. Passing this diagnostic is NOT a novelty result; the features overlap prior art and hardware-computation costs are unmeasured. Failing means stop that feature extension.

**NUS execution:**

1. cd ~/MRAM_Path_Finding && git pull --ff-only
2. python3 -m py_compile experiments/e23a_residual_spatial_diagnostic.py
3. python3 experiments/e23a_residual_spatial_diagnostic.py --selftest
4. SRC="$HOME/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162140_178/e22_results.json"
5. OUT="$HOME/mram_private/E02_256x256/E22/E23A_$(date -u +%Y%m%dT%H%M%S)_$$.json"
6. python3 -u experiments/e23a_residual_spatial_diagnostic.py "$SRC" --out "$OUT"

Scientific next gate regardless of result: establish physical interconnect resistance with authorized geometry/PEX, then prospective independent masks and fixed per-chip variations. Do not equate a 32-row assumed-R ladder with the required physical 256x256 macro.
