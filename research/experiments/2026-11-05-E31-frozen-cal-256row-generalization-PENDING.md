# E31 — Frozen CAL, unseen 256-row masks: does strong Q correction actually generalize?
**Date:** 2026-11-05. **Status: executable committed; not yet user-run.**

## Why this is the right next experiment
The user executed E30P (offline processing of actual GF access-NFET + student static MTJ currents, ASSUMED BL and SL interconnect), with these **confirmed** NUS DEV outcomes:

| Decoder on C0 | ideal BL | 0.25Ω/segment BL independent SL | BL +0.25Ω shared SL |
|---|---:|---:|---:|
| Global CAL count reference | 0/9 | **6/9** | **6/9** |
| CAL area-offset | 0/9 | **0/9** | **0/9** |
| CAL area/count bank | 0/9 | **0/9** | **0/9** |
| Input-mask Q correction (CAL chooses suffix) | 0/9 | **0/9** | **0/9** |

Actual E30 source SHA-256: \`f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52\`. E30P output user's NUS:
\`~/mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30P_baselines_20261105_112745.json\`.
The same-count n12 row-low minus row-high effect was 9.485555790824165 µA =5.16874 nominal ideal count steps; shared-SL extra C0 absolute shift up to 230.885391484 nA. This is a spatial bias error under assumed 256-section BL R, not a measured MRAM bit failure probability or aligned signed W4 errors.

**Important conclusion:** The 6/9 pooled global decoder result is not evidence that expensive selective digital recovery is needed: three ordinary CAL-only strategies fixed 9/9 DEV cases. But one CAL and one DEV input pattern per \`(region,count)\` is **inadequate** to claim universal correction or small error rate. Fix the statistical and out-of-distribution evaluation first, and freeze the existing fitted Q coefficient.

## E31 pre-registered test
[Source](../../experiments/e31_frozen_cal_unseen_masks.py) and [one-shot runner](../../experiments/run_e31_frozen_cal_nus.sh).

- Reproduce the exact resident weight-state map from E30 using seed 20261105; assert P-row identities against first 4 E30 source profiles. **Do not change any stored MTJ P/AP states or mismatch draw** between old CAL and fresh DEV.
- Take the original **nine E30 CAL input masks** and fit each of the same four decoders once. Pick suffix/prefix input-position Q direction **by original CAL fit residual only**.
- Generate **36 fresh 256-row input masks**, at \(m=24\), \(n=11,12,13\) for C0. For each (count,region) use 2 independently sampled DEV masks with seed 20261106, never duplicate an E30 CAL/DEV mask. Four real GF-current read columns per scenario (1,024 GF NFET/MTJ cell-pairs in a scenario).
- First 18 DEV: in original \`ROW_LO\`, \`ROW_HI\`, \`DISTRIBUTED\` spatial families, but with **new** row combinations.
- Other 18 DEV: completely **out of CAL** \`UNIFORM_OOD\`, \`DUAL_END_OOD\`, \`CENTER_OOD\` activation-mask families, with the same n classes. CAL-area-offset and CAL-area-bank are **undefined** on these new families; they must fallback to GLOBAL, without post-hoc nearest-bin selection, while input-Q is a continuous mask-derived predictor and can extrapolate.
- Three matched electrical arms per fresh scenario: ideal independent; assumed BL .25Ω/segment independent return; assumed BL .25Ω/segment with shared return .25Ω across four simultaneously simulated columns. The wire values are *the same* as E30, still unextracted/illustrative, not increased to manufacture errors. Ideal row gates, no physically shared WL R/C.
- Freeze 50mV read and 0.8V WL from old circuit screening, still **not** qualified nondisturb read bias for real 1T1MTJ hardware.
- Report C0 held-out wrong counts and MAE by seen/OOD/all groups for global, CAL-area-offset, CAL-area-count-bank, and CAL-only input Q. All current vectors retained private. **No DEV tuning, no new calibration samples, no full DNN, no validated covariance or energy cost.**

## Decision gate
1. **Input-Q 0 errors both seen and OOD:** on this assumed-R model, spatial correction appears robust enough that the N2 exact-digital-recompute motivation is **NOT supported**. Do not increase R until an error appears; go to geometry-justified 1T1 PEX/parasitics, process/mismatch/ADC timing and full network to test a real residual failure.
2. **Q errors in unseen groups but area-offset/bank ties on seen groups:** this is a **spatial model generalization gap**, not evidence of signed four-plane cancellation-aware recovery. Improve calibration/model or characterization before 4-plane policy.
3. **Uncorrectable residual errors in seen cases under frozen CAL:** compare bias, position, Q/centroid, and a stronger CAL model in a **separate properly preregistered** study. Preserve residual GF current traces for downstream complete signed W4A8 evaluation if physically validated.
4. **Large shared-SL effect on C0:** distinguish any new errors from BL spatial distortion; note the return resistor is a **lumped assumed geometry**, not correlated manufacturing variation.
5. **Zero errors does not imply BER=0**: 36 new masks on one nominal model, no chip variation. Future chip-level mismatch needs independent physical chip draws, not independent WL masks as fake chips.
6. **N2 recovery** only after actual corresponding four-plane count errors from one *legal* 1T1MRAM mapping, with runtime-only input features and costed exact replay, prove equal-budget advantage over contextual-prefix/independent selector. E31 does not itself provide such four-plane data.

## Exact NUS execution
\`\`\`bash
cd ~/MRAM_Path_Finding
git pull --ff-only
bash experiments/run_e31_frozen_cal_nus.sh
\`\`\`
The shell runs Python syntax/selftests first, verifies E30 SHA and reconstructs weights before generating or solving circuits. NUS outputs under \`~/mram_private/E31_1T1/\`; logs can be shared, foundry netlists must remain private.
