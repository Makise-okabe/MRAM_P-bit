# E22 pre-registration — GF current × ADC precision × assumed wire-R
**Date:** 2026-11-05. **State:** prepared and committed; NOT yet run on NUS. No E22 scientific results to claim.

**Script:** [experiments/e22_gf_precision_regime.py](../../experiments/e22_gf_precision_regime.py). Python3.6 stdlib; depends on the student's already verified locally created `experiments/e19_gf_nfet_mtj_nonideal_count_gate_v2.py`. That E19 v2 is intentionally an untracked user-private executable and is not deleted or replaced by a pull.

## Hypothesis / design
H0: ADC precision and line drop can be modeled independently or conventional fixed nominal calibration/offset-only calibration explains held-out failures sufficiently.
H1: same underlying physical current may cross different integer-code boundaries depending on ADC bit depth and spatial wiring, creating a cross-term that simple precision-only or global-offset-only models miss; a cheap position-aware model may predict which regimes need correction/precision changes. H1 has **not** been proven; the initial goal is to falsify it.

- Existing GF `hvtnfet` l=20nm w=80nm, user-owned static P/AP `mtj_read_v0`, 32 branch shunts connected along a constructed BL with assumed R segment.
- Hold B=32, active m=16, weight-P k=16, **all 17 legal counts n=0..16** (not only E19 n7 vs n8).
- CAL=6 independent spatial masks per n, DEV=12 independent spatial masks per n, exactly **306 current cases per R**, and the **same 306 masks** reused for R∈{0,1,2,3,5}Ω. Thus **1530 Spectre DC circuits**, across **306 distinct mask identities**. The 5 R repeats are not statistically independent.
- Pair each mask's n and bit-array state across all R settings; no random P/AP re-draw per R. MTJ is static and nominal. No variation/PVT.
- Historical read=.05V and WL=.8V not requalified safe nondisturb. No actual GF 256×256 PEX, no current-mode sense amp, physical ADC comparator or energy.
- CAL R0 only defines a **frozen**, nominal ADC current window and 17 reference count centroids. Evaluate the same DEV physically simulated current at 4,5,6,7-bit mathematical uniform quantizers, and continuous nominal-nearest-centroid baseline. In particular, 4 bits may not uniquely represent all 17 levels. The broad R0 window may cause clipping at R>0, so measure global shift correction separately.
- Controls: `raw` no correction; `offset_only` CAL-known R global current offset; `offset_near` CAL-known R global offset plus cheap input-half active-row count. Same quantizer/bit budget. Real circuitry/control costs are not included; per-R CAL calibration is a generous baseline.
- Outputs: `DEV wrong count / 204`, count MAE, sampled adjacent-count current-range overlaps, CAL near-count correction coefficient, CAL global offset for each R and bits. Do **not** claim classification accuracy or energy.

## Mechanical pass requirements
- All 17 count levels are monotonically ordered in CAL R0. If not, stop: examine netlist/read polarity and potential nonlinearity.
- All 306 mask identities must appear at every R and have identical true n and split labels.
- CAL and DEV masks are disjoint, predictions use CAL only.
- Preserve raw JSON under `~/mram_private/E02_256x256/E22/`. No foundry PDK or raw licensed Spectre deck to public GitHub.
- Compare bit-depth effects on identical physical currents; never regenerate independent devices between precision conditions.

## Analysis after actual run
For each policy, compute paired per-mask and per-count errors (4/5/6/7-bit), sample overlap and analog-continuous error. Test interaction `[error(r_high,b_high)-error(r_low,b_high)] - [error(r_high,b_low)-error(r_low,b_low)]`, with uncertainty resampling independent DEV *mask identities*, keeping all paired R/b observations together. Report trivial 4-bit insufficiency explicitly as known cardinality, not physical coupling. Verify that any non-monotonic trend persists after offset calibration and fixed DAC fullscale. Classify thresholds only as **assumed-R experimental boundaries**, not GF material/PEX critical resistances.

**Pilot gate:** If 17 levels and both bit depths show only unremarkable monotonic behaviour adequately explained by offset-only and margins, no novelty established; go to calibration/mismatch boundary rather than reporting a “coupled effect”. If observable interaction survives proper controls, proceed to E23 held-out *predictor* relative to simple threshold-margin/near-far models. Either outcome is retained in CA2.

## User's NUS run
```bash
set -euo pipefail
cd ~/MRAM_Path_Finding
git pull --ff-only
python3 -m py_compile experiments/e22_gf_precision_regime.py
python3 experiments/e22_gf_precision_regime.py selftest

LOG="$HOME/mram_private/E22_run_$(date +%Y%m%d_%H%M%S).log"
python3 -u experiments/e22_gf_precision_regime.py run \
 --cal-per-count 6 --dev-per-count 12 \
 --rs 0,1,2,3,5 --seed 20261105 \
 --vread .05 --vwl .8 --chunk-size 16 | tee "$LOG"

RESULT=$(awk '/^E22_GF_RESULTS /{print $2}' "$LOG" | tail -1)
test -n "$RESULT" && test -f "$RESULT"
python3 -u experiments/e22_gf_precision_regime.py analyze "$RESULT"
```

Source evidence for the E22 experiment proposal: [ADR-0006](../decisions/ADR-0006-coupled-precision-failure-boundary-primary.md), [E19 actual GF results](2026-11-04-E19-NUS-GF-NFET-MTJ-nonideal-RESULTS.md), [E20 completed rescue/retire](2026-11-04-E20-suffix-load-rescue-or-retire-E15.md).
