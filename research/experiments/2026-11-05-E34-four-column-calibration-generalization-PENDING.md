# E34 — Four-column generalization of a CAL-only count/position decoder

**Date:** 2026-11-05 SGT.
**Status:** Executable code and preregistered baseline plan committed; NUS execution PENDING.
**Research direction:** F1 inference-failure prediction, supporting electrical feature test. Not a new primary FYP direction.

## Why E34 is necessary

E30/E30P/E31 produced **real Spectre GF access-NFET + student static-MTJ** currents for four simultaneously modeled columns, but almost all previous offline evaluations analyzed **C0 only** (fixed alternating P/AP states at 256 physical rows). E31's **CAL-frozen Q correction obtained 0/36 C0 errors** using n=11/12/13 at m=24 and *assumed* .25 Ω BL resistor per row segment, .25 Ω shared-SL resistor. This result **cannot simply be attributed to all 4 columns**, since C1/C2/C3 have *different independently generated resident P/AP states* and their true selected P count n varies with activity.

**E34 asks:** Can a low-cost, CAL-only spatial readout model correct all four physically distinct resident-weight columns in the *already-solved joint GF-current data*, including count classes not represented in each column's nine calibration samples?

## User-provided frozen electrical evidence
- E30 nominal 256 physical row ×4 column GF model, 18 masks (9 CAL and 9 original DEV). Actual private result SHA256 `f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52`, path `~/mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30_RESULTS.json`.
- E31 36 fresh DEV masks, including 18 familiar families and 18 unfamiliar input-mask families, same P/AP weight map. Private result `~/mram_private/E31_1T1/E31_256x4_20261105T033721Z_2792/E31_RESULTS.json`. Original frozen E30 calibration confirmed.
- Actual device current vectors use GF compact NFET models with the student's **static resistor MTJ** P/AP behavioral state; both BL/SL R values are **ASSUMED**, not physically extracted GF 1T1 wiring. No physical ADC, independent chip variation, timing, signed W4 bitplane mapping, or full neural inference.

## Exact E34 method

Runnable [`experiments/e34_four_column_gf_generalization.py`](../../experiments/e34_four_column_gf_generalization.py), included in [`experiments/run_e33_e34_nus.sh`](../../experiments/run_e33_e34_nus.sh).

1. Recover four distinct **permanently resident P-state row sets** from E30's `source_profiles`. Verify exactly 128 P rows per column and that each set stays identical across every E30 electrical case. Check the reported E30 `true_n` equals `|WL_active ∩ P_rows|` for every physical/conceptual column. Verify E31's 36 new masks do not duplicate the original E30 mask set.
2. Derive **only offline CAL labels** for the four columns from the 9 E30 CAL active masks and known resident P/AP weights. Compute *held-out evaluation labels* for the E31 masks separately; the predictor NEVER sees true n at runtime.
3. Compare (identical 9 CAL per column, per arm):
   - `GLOBAL_LINEAR`: fit `I = a + b*n`, 2 coefficients;
   - `MEAN_ROW_LINEAR`: `I = a + b*n + c*(mean active row index)`, 3 coefficients;
   - `FAR_HALF_LINEAR`: replace spatial feature with fraction of active rows in indices 128–255, 3 coefficients;
   - `Q_CAL_SELECTED`: `I = a+b*n+c*Q`, choose prefix or suffix spatial Q **only on 9 CAL currents** using residual SSE, 3 continuous coefficients plus orientation bit.
4. Runtime decoder observes the sensed current, known active-WL mask (and its low-cost scalar spatial feature) and saved CAL coefficients. It tests integer candidate counts `0..m=24` and takes the closest predicted current; it does **NOT** read the actual count/MTJ state at runtime for free.
5. DEV results by physical column (36 per column), including **true n range, CAL n coverage and n extrapolation frequency**, and across all four columns (144 column-read decisions, **not 144 independent chips**), broken down by seen/OOD mask families. Evaluate all three electrical arms: ideal independent, assumed BL R independent, assumed BL+shared-SL.

## How to interpret
- **If Q is also 0/36 on C1–C3:** the nominal assumed-wire physics exhibits a broad calibratable bias; no N2 exact digital recompute is justified in these particular count-level data. It remains *outside* real 1T1 layout PEX or actual ADC regime.
- **If Q has C1–C3 residual errors but mean-row or half-line also fail:** look at CAL count coverage (9 points), model adequacy and spatial weighting; do not immediately conclude correlated bitplane errors or ML failure. Increase independent calibration evidence only with a preregistered budget once physically credible.
- **If Q loses to simpler feature:** choose the simpler baseline. A stronger 3-parameter model without equal CAL cost comparison would not automatically be novel.
- **If ideal-independent current has count errors:** the 9-CAL global *linear* model may be poorly identified in unrepresented count classes; diagnose before attributing failure to interconnect.
- **Do NOT label four simultaneously read columns as W4 signed planes**. Original frozen E01 W4A8 physical packing spans bit planes/cycles and must be mapped separately before a cancellation-aware N2 recovery claim.
- Only one nominal chip, one resident-weight map and m=24; no 1T1 PEX or ADC; shared-source R hypothetical. E32 new physical 1T1 wire geometry remains necessary.

## Run on NUS
```bash
cd ~/MRAM_Path_Finding
git pull --ff-only
bash experiments/run_e33_e34_nus.sh
```
Results under `~/mram_private/E33_E34_OFFLINE/<timestamp>/E34/`, with `E34_RESULTS.json` (complete private data) and `E34_FOR_PROF_FONG.md` (sanitized experiment summary). Nothing above asserts E34 has already passed or returned numeric results.
