# E23D PRE-REGISTERED fresh GF-mask confirmation of E22C Q correction
**Date:** 2026-11-05. **State:** CODE COMMITTED, no new NUS run or scientific output yet. Please do not report E23D as passed.

**Question:** does the suffix-load `Qx` correction that produced 0/204 previously examined E22 DEV errors at R5 still outperform centroid and near/far when ALL new ADC-reference settings and correction parameters are frozen *solely from OLD E22 CAL* and we test physically simulated NEW masks and a NEW assumed R4?

**Script:** `experiments/e23d_freshmask_q_generalization.py` imports the already NUS-tested `e22_gf_precision_regime.py`, `e22c_spatial_feature_ablation.py`, and user's untracked exact-SHA-verifiable `e19_gf_nfet_mtj_nonideal_count_gate_v2.py`. Python3.6 standard library. Local mock selftest only; actual GF result depends on student-run NUS Spectre.

## Frozen protocol
- 32-row GF access-NFET compact model `hvtnfet` + user static `mtj_read_v0`, read=.05V/WL=.8V historical settings, **not requalified nondisturb**. Explicit **ASSUMED** segment Rs=0,1,2,3,**4**,5Ω (no PEX).
- Exact m=k=16; 17 feasible counts 0..16; 24 **NEW** DEV spatial masks per count = **408 independent mask identities** with seed 20261106; all mask hashes explicitly checked against *every old E22 CAL and previously inspected E22 DEV mask*. Identical new masks across six Rs, so **2,448 Spectre DC cases** (408 patterns × 6 conditions), but not 2,448 independent device/chip samples.
- **NO E23D new-mask calibration at all.** For R0,1,2,3,5, fit RAW/near-count/centroid/Q 1-dimensional per-count-centred current correction coefficient and all 17 count centroids from exactly **102 OLD E22 CAL masks at each R**. Compute same 5% guarded CAL-derived reference window. For **unseen R4**, linearly interpolate coefficients, count reference levels, CAL feature centring and ADC fullscale from OLD R3 and R5 CAL; no R4 CAL source and no DEV tuning.
- Digital correction is applied **AFTER** 5/6/7bit mathematical raw-current ADC, exactly as in E22C. Report continuous-current diagnostic, count wrong/408, count MAE, sampled adjacent count overlaps, and **paired** near/centroid versus Q wins/regressions for each R. If test implementation fails preflight or Spectre, do not interpret as physical null.
- This is a **confirmatory replication of a selected feature** on independently generated mask *placement* samples. It does not vary m/k, device noise, process corner, actual ADC circuit or 256x256 foundry PEX; the 17-centroid and programmable-window overhead is not evaluated.
- It is essential that newly measured currents are never used to choose model/slope, and that the unseen R4 be evaluated with its **interpolated** old-CAL model without peeking.

## Predeclared evaluation gates
1. **Replication:** compare E23D fresh R5 7bit Q to both strong near and centroid with identical old-CAL calibrations. A meaningful out-of-sample win needs Q to correct more cases than it breaks in *paired* comparisons; zero errors is not required and cannot certify population error=0. If Q loses or has many regressions, retire it as a broadly useful mechanism.
2. **Unseen-R transfer:** at R4 (not in old CAL) the Q interpolation must also match or beat centroid on held-out 7bit count decoding, without special re-tuning of R4 models. This tests a narrow physical scaling hypothesis.
3. **Control:** R0 should have clean continuous-current decoding and at least 6/7bit; non-zero R0 errors indicate model/netlist/calibration mismatch or sample drift and require audit.
4. **Novelty caution:** Passing confirms a **physics-informed calibration predictor on a chosen model**; quadratic load-moment correction is not presumed original, and full FYP contribution still needs varying m/k, physically justified/extracted wires, fixed-chip MTJ distribution, a failure-boundary prediction metric and full-network task validation.
5. **Statistical caveat:** 408 stratified masks mean error rates describe this chosen m/k distribution; four Rs are repeated observations on each mask. No silicon bit error rate or chip-level confidence can be inferred.

## Student-run commands
```bash
set -euo pipefail
cd "$HOME/MRAM_Path_Finding"
git pull --ff-only
python3 -m py_compile experiments/e23d_freshmask_q_generalization.py
python3 -u experiments/e23d_freshmask_q_generalization.py selftest
mkdir -p "$HOME/mram_private/E02_256x256/E23D"
LOG="$HOME/mram_private/E02_256x256/E23D/run_$(date +%Y%m%d_%H%M%S).log"
python3 -u experiments/e23d_freshmask_q_generalization.py run \
  --reps 24 --seed 20261106 --chunk-size 16 --vread .05 --vwl .8 | tee "$LOG"
FRESH=$(awk '/^E23D_RESULTS /{print $2}' "$LOG" | tail -1)
test -n "$FRESH" && test -f "$FRESH"
python3 -u experiments/e23d_freshmask_q_generalization.py analyze \
 --fresh "$FRESH" \
 --out "$HOME/mram_private/E02_256x256/E23D/E23D_confirmation_$(date +%Y%m%d_%H%M%S).json"
```
**No private PDK, local generated Spectre decks or per-mask data to public GitHub.** Aggregate evidence and exact E22 input hash can be committed after successful NUS run. Developer status remains pending.
