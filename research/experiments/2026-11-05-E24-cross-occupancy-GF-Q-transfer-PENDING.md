# E24 preregistered: cross-activity transfer of GF-current suffix-load correction
**Date:** 2026-11-05. **Status: SCRIPT PREPARED AND MOCK-TESTED, BUT NUS GF SPECTRE E24 NOT RUN.** Current script is supplied in the ChatGPT conversation as `e24_activity_transfer_gf.py` and `E24_activity_transfer_package.zip` (archive SHA256 `55e30b372c22eed815d24f6fe03f435f3ff73d45eaf50cf40e18238d15f7c548`); the script is **not** yet a tracked file in this GitHub repo. Source SHA256: `da8925f9c59162b157ebd1270832c27ef7d67bdac4b7260d86669bba2b60ce3b`. Source passed Python3.6 grammar parsing, local module selftest and separately generated end-to-end mock complete-data analysis; these are **NOT** NUS Spectre results.

## Motivation from independently confirmed E23D
[The actual fresh GF Spectre E23D record](2026-11-05-E23D-COMPLETE-fresh-mask-GF-Q-validation.md) shows 2,448 actual GF NFET compact-model and student-static-MTJ DC cases. At assumed R5Ω/segment 7bit wrong/408: raw 111, near 55, centroid 9, input-only suffixQ 0, coefficients frozen from old m=k16 CAL; unseen R4 interpolated old R3/5: raw79, near34, centroid2, Q0. This is a real positive **spatial-mask** and **within-range resistance interpolation** result, but all tests use m=k16.

**E24 next gate:** Does the **same m16-trained spatial correction slope β_Q(R)** generalize to other input activity populations when baseline ideal current/count-reference calibration is fairly shared across methods?

## Frozen E24 protocol
- GF `hvtnfet` compact model + student-owned static `mtj_read_v0` with the E19 constructed 32-branch shared BL (single NFET per branch), historical 50mV read and .8V WL, no PEX or actual ADC. **Series wire segment R values are ASSUMED**, not extracted: 0,3,4,5Ω.
- Fresh disjoint mask scenarios: `m=8,12,20,24`, all `k=16`. Legal count ranges `n=0..8,0..12,4..16,8..16` = **44 class pairs**; six new CAL and twelve new DEV masks per class, each mask unique and excluded from **all old E22 CAL and DEV masks**. Thus **792 independent fresh mask identities and 3,168 GF DC circuits** across four R settings, same masks reused at each R (R repeat does not multiply independent samples).
- Correction slopes `β_near(R), β_centroid(R), β_Q(R)` learned **only from original E22 m=k16 CAL** (6 old CAL per n), with **R4 interpolated** from old R3 and R5 slopes.
- Importantly, changing m changes total ideal sensing current and the feasible n set, so **each new (m,k,R) has its own six-CAL-per-count ADC window and class-reference centroids**, shared by EVERY competitor, **including transfer arms**. Thus E24 tests **spatial coefficient transfer**, not zero-reference-calibration transfer or hardware ADC energy.
- Equal-reference-budget arms: RAW, near_transfer, centroid_transfer, suffixQ_transfer. Each uses identical NEW CAL count-reference and window budget, but NO new feature-slope fitting; the transfer slope remains OLD E22 CAL only.
- Stronger adaptive controls: near_refit, centroid_refit, suffixQ_refit on same new CAL, but ALSO fit a new spatial coefficient; label their additional calibration cost and avoid calling these identical resource competitors.
- ADC: raw-current mathematical 6/7bit converter using CAL-defined 5%-guard fullscale; apply feature correction digitally **AFTER** ADC; continuous ideal-current diagnostic. No hidden DEV n/weight overlap used in runtime feature. Report decoded count wrong/DEV, MAE, adjacent sampled count gaps, and paired Q-transfer wins/regressions vs centroid-transfer, near-transfer, Q-refit.
- **Optional later k control**: `--include-k-check` adds (m,k)=(16,8),(16,24), +1,296 assumed-GF circuits; not included in default.

## Decision gates and falsification
1. If Q-transfer benefits persist at m8,12,20,24 across R3/R4/R5 and beat centroid-transfer at matched CAL refs, the learned geometry slope has **cross-occupancy generalization evidence** beyond E23D.
2. If simple centroid **refitted on same new CAL** catches up or Q-transfer degrades, the result is at best **calibration-specific**; still useful for physical design guidance but weak as distinct algorithm.
3. If Q only works by per-condition new Q slope fitting, do not report calibration-free transfer; describe the limited new-m calibration needed and quantify its per-count overhead.
4. If zero errors are observed, cite finite-sample precision, not zero intrinsic BER. Reports must preserve signed count-level errors, assumed R not PEX, and absence of device mismatch.
5. After this bounded gate, prioritize authorized 2T1MTJ actual geometry/extraction, fixed-chip MTJ spread, and real W4A8 inference rather than more nominal synthetic sweep extensions. Publication novelty still requires a full prior-art comparison to wire-load compensation and alternative predictors.

## User installation
The user downloads `E24_activity_transfer_package.zip` from the current ChatGPT turn and copies `e24_activity_transfer_gf.py` to `~/MRAM_Path_Finding/experiments/` (via VS Code Remote SSH or other chosen transfer). The source is not tracked remotely yet. The archive README supplies full NUS command, or:
```bash
cd ~/MRAM_Path_Finding
python3 -m py_compile experiments/e24_activity_transfer_gf.py
python3 experiments/e24_activity_transfer_gf.py selftest
mkdir -p ~/mram_private/E02_256x256/E24
LOG=~/mram_private/E02_256x256/E24/run_$(date +%Y%m%d_%H%M%S).log
python3 -u experiments/e24_activity_transfer_gf.py run --seed 20261107 --cal-per-count 6 --dev-per-count 12 --chunk-size 16 --vread .05 --vwl .8 | tee "$LOG"
RESULT=$(awk '/^E24_RESULTS /{print $2}' "$LOG" | tail -1)
test -f "$RESULT"
python3 -u experiments/e24_activity_transfer_gf.py analyze --fresh "$RESULT" --out ~/mram_private/E02_256x256/E24/E24_cross_activity_$(date +%Y%m%d_%H%M%S).json
```
No PDK, licensed decks, raw current traces or private per-mask arrays should be committed publicly.
