# E22C — Pre-registered cheap spatial-calibration control after successful E22B audit
**2026-11-05: Prepared; NUS execution PENDING.** Do NOT invent any E22C GF result.

## Why this gate exists
E22B on 1,530 real NUS GF access-NFET + user static-MTJ current cases (assumed wire resistance) changed the interpretation of E22. Frozen R0 reference produced up to 192/204 wrong; CAL-only programmable reference and near correction yielded 0/204 at R2, 3/204 at R3 and 25/204 at R5 (7bit, 204 held-out mask cases per R). At assumed R5, nine of sixteen adjacent count boundaries still have sampled overlapping scalar currents AFTER near correction. That does **not** show that all input-position corrections fail.

E20 had already found, on smaller n7/n8 GF current sets, that very simple near/far and centroid match more complicated suffixQ, 0/8 and 0/24 errors. Before proposing a new predictor we must test the same strong alternatives on **all 17 count classes**.

## E22C exact experiment contract
- Use saved `~/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162140_178/e22_results.json`; **NO NEW SPECTRE**.
- Python 3.6 executable: [experiments/e22c_spatial_feature_ablation.py](../../experiments/e22c_spatial_feature_ablation.py); code runs a mock selftest but only NUS E22 JSON can produce GF-current results.
- Same 102 CAL/204 DEV spatial masks per assumed R=0,1,2,3,5Ω, exact same masks across R. m=k=16, n0..16. CAL-only fitting of one scalar slope, and 17 CAL count centroids, per R. No DEV labels used to fit.
- Candidate position statistics computed ONLY from known input activation mask (no hidden n, no weight overlap):
  1. RAW no correction.
  2. Near = number of active rows within positions 0–15.
  3. Centroid = sum(active row index+1).
  4. SuffixQ = sum_l (sum_{j>=l} active_j)^2.
- Fair correction: per-count CAL-centered least-square slope `beta = sum[(f-fmean_n)(I-Imean_n)] / sum[(f-fmean_n)^2]`, then `I_corr=I-beta*(f-fmean_all_CAL)`. Fit corrected 17 CAL class centroids, decode DEV by nearest corrected centroids, without changing ideal count.
- ADC: for each R, **the same hypothetical CAL-min/max programmable physical input window with 5% span guard** as E22B, digitize raw current first, then digitally apply position correction to the ADC-code midpoint; compare continuous-no-ADC and 4/5/6/7 bit.
- Report per-R DEV count-error/204, count MAE, and number of sampled adjacent nonseparable corrected-current boundaries. Report paired discordant error masks, near vs centroid and near vs suffixQ at 7bit to prevent hiding tradeoffs under a single aggregate error rate.
- At R0/R1, large new correction errors would falsify the candidate. Reproduce E22B `reprogrammed_CAL_near` errors as code audit: R0 [12,0,0,0], R1 [11,0,0,0], R2 [27,2,0,0], R3 [41,6,6,3], R5 [47,31,25,25] for b4/5/6/7 respectively. If numbers diverge, debug calibration, and DO NOT compare models.

## Go/no-go
- If centroid/suffixQ completely or nearly removes 5Ω ADC errors and overlaps compared with near, near-only boundary is **not robust to a cheap known correction**, do not claim a fundamental failure threshold or invent a complex predictor yet.
- If all simple corrections still fail at 5Ω, test E23 **prediction of residual ADC failure events** from CAL-only physical current-margin + position statistics, against simple threshold-margin, class-conditioned uncertainty and conventional calibration. The predictor must demonstrate held-out benefit at fixed read/ref/control budget and not leak hidden n into runtime.
- No physical interconnect resistance known: all R values are hypothetical. Source remains 32-row constructed read topology with GF nominal MOS compact model and static student MTJ; not 256×256 GF PEX, actual ADC or inference.

## NUS command
```bash
set -euo pipefail
cd "$HOME/MRAM_Path_Finding"
git pull --ff-only
python3 -m py_compile experiments/e22c_spatial_feature_ablation.py
python3 experiments/e22c_spatial_feature_ablation.py --selftest
python3 -u experiments/e22c_spatial_feature_ablation.py \
 "$HOME/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162140_178/e22_results.json" \
 --out "$HOME/mram_private/E02_256x256/E22/E22C_spatial_correction_ablation.json"
```

**CA2 evidence standard:** E22C numerical result remains OPEN until the student executes it and provides terminal output. Independently test any claimed novelty against known position-calibration and DIB I3D methods; full GF PEX, process spread and read-energy remain future gates.
