# M2 E2 response screening freeze — 7 November 2026

> **Historical six-bit combined-response screen.** The [8 November locked roadmap](ROADMAP_LOCKED_2026-11-06.md) now controls the research campaign. Preserve this source/model record, but do not launch its 288-run command as the precision-regime study. The current first scientific gate is the separately authored gain-only E2-GAIN-01 pilot; it is followed by gain/offset slices under the new lock.

**Decision: GO for one bounded E2 *sensitivity* screen, not an E3 device-performance claim.** The research objective remains the original Biq Mac Mac weighted Max-Cut quality versus full hardware/whole-solution cost of low-order symmetric FP/INT/BFP `J` coefficients. Device-response interaction is a diagnostic, not a prerequisite for FP value or a reason to tune the solver. Benchmark/solver/scale/codebooks are frozen.

## Source/model gate outcome

Yang et al. (2026), Nature Communications **17:5368**, DOI [10.1038/s41467-026-72020-8](https://doi.org/10.1038/s41467-026-72020-8), documents a pulse-driven STT-MTJ p-bit, a representative `sigmoid(128.8*(V-1.852))` curve, device calibration and a proposed chiplet **local-field/FIFO-index quantizer**. This does NOT imply that its local-field quantizer is the numerical `J_ij` storage format. The paper's Supplementary PDF is identified as `41467_2026_72020_MOESM1_ESM.pdf` but still **not successfully retrieved/inspected** in this audit. Therefore its coefficient-word widths, individual *post*-calibration residual parameters, and precise chiplet implementation limitations are NOT independently verified. Do not claim these are absent; do not promote pre-calibration spread to measured post-calibration residual.

A **clearly stated E2** envelope is scientifically permissible without asserting that it reproduces measured STT-MTJ calibration residuals. Source-backed nominal sigmoid establishes an interface *form*, NOT the numerical magnitude of the following model.

## E2 model: explicitly artificial, one fixed device realization

For represented local field `H_i^q = sum_j Jhat_ij * s_j` and frozen `beta(t)`, use

```
P(s_i=+1 | H_i^q) = sigmoid(g_i * [2 beta(t) H_i^q] + d_i)
```

`g_i` is a dimensionless per-spin gain multiplier; `d_i` is a dimensionless additive **logit** offset. They are not volts. They are held fixed for each spin for the entire run, and the *same indexed population* is reused for FP64/FP6/INT6/BFP6, every paired seed and all three calibration graphs (all N=100).

**Chosen assumptions (NOT physical measurements, NOT inferred from figures):**
- Generate 100 independent gain deviates and 100 independent offset deviates with Python `random.Random(20261107)`.
- `g_i = 1 + 0.05 * Uniform[-1,1]`; `d_i = 0.10 * Uniform[-1,1]`. One fixed deterministic 100-spin realization.
- These envelopes were selected purely as a bounded, nonzero software stress for a first sensitivity screen. **No evidence presently shows that ±5% gain or ±0.10 logit is representative of the paper's *post*-calibration devices**.
- No clipping, DAC quantization, colored temporal noise, stochastic gain drift, device aging, actual pulse energy or voltage operating-window constraints are represented. No fabricated claims of GF22FDX-PDK consistency.
- If the illustrative model strongly changes rankings, that is a conditional E2 observation and a reason to prioritize physical parameter validation, not evidence such changes exist on silicon.

This is a **one-population conditional test**, not statistical sampling over a 100-device manufacturing distribution. The 24 seeds estimate software stochasticity *within each of three calibration graphs*, not graph or device-population generalization.

## Frozen numerical experiment

- **Original graphs:** `w01_100.0` (control), `t2g10_5555` (wide sparse), `ising2.5-100_5555` (wide dense); original files/hash-validated against Biq Mac official references.
- **Formats:** FP64 original; custom finite FP6 E3M2, symmetric INT6, global BFP6. Same `J=-w`, `h=0`, exact mirror symmetry `J_ij=J_ji`, and prior source-MSE global scales.
- **Frozen solver:** 50,000 attempted single-spin updates; linear `0.5 beta_G → 2 beta_G` based on original graph; initial state, spin proposal and sampling uniform stream exactly match E1; `seed=20261201 + 100000*graph_index + k`, `k=0..23`.
- **State selection:** retain earliest *lowest represented Ising energy* visited; inspect original-weight Max-Cut and published original optimum only after return.
- **Integrity gate:** original E1 `precision_paired_runs.csv` **SHA256** must equal `27556b10bc9d2a778af28b2d007f28e34dedd47b14c0701fc444b5285e466b97`. Do not re-run all ideal jobs for a new presentation. Verify zero-residual model reproduces M1 bit-for-bit on tiny regression graphs.
- **Budget:** exactly **3 graphs × 4 formats × 24 paired seeds = 288 new E2 solver runs**, conditional on one fixed device model. No beta tune, extra formats, alternate benchmark or parameter grid.

### Evaluation and interpretation

Report separately:
1. **Absolute gap to ORIGINAL optimum** for each configuration; a degraded E2 FP64 reference does not excuse poor quality.
2. E2 paired additional original-gap vs E2 FP64, seed-bootstrap 95% CI, and preexisting +1.0-pp *within-CAL-graph* screen.
3. For each graph, paired interaction `D=[gap(FP6)-gap(INT6)]_E2-[gap(FP6)-gap(INT6)]_E1` with **seed-level** 95% bootstrap; compare also BFP6. Neither nonzero D nor ranking reversal is necessary for successful FYP. An imprecise D crossing zero is **inconclusive**; do not call it stability/equivalence. No post-hoc practical equivalence margin.
4. Nominal dense 6-bit coefficient payload equal for FP6/INT6, so no same-bit storage advantage can be claimed. No area, energy/time-to-solution claim is licensed until true memory/metadata/data-path/control/pulse costs are evaluated.

**GO outcome:** conditional result identifies whether this specific bounded gain/offset stress changes which fixed 6-bit representation is attractive; if no interaction, retain value of ideal-model coupling quantization and move to **independent held-out graphs and full-cost verification**. **STOP:** never cherry-pick a larger assumed residual to manufacture an FP victory; do not interpret single E2 realization as validated silicon robustness or a moved bit-width knee. A wide CI stays inconclusive rather than being converted into a null claim.

## On NUS — execute only once after tests pass

```bash
cd "$HOME/MRAM_P-bit"
git pull --ff-only
python3 -m unittest tests/test_m2_e2_response_gate.py -v
python3 -m experiments.m2_e2_response_gate \
  --e1-raw-csv "results/m1_precision_global_20261106T195502Z_3314224/precision_paired_runs.csv" \
  --out "results/m2_e2_response_20261107_frozen"
```

The runner rejects an incorrect E1 CSV SHA, keeps a model hash and immutable non-existing output directory, and writes `E2_ASSUMED_MODEL.json`, `E2_paired_runs.csv`, `E2_summary.csv`, and `manifest.json`. Do not run it under GitHub Actions: actual Biq Mac graph inputs and source-verified NUS E1 CSV live on NUS.

**Verified code gate:** GitHub Actions [run 42299340532](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/42299340532) passed the new E2 parity/persistence/unit tests plus all existing M0/M1 checks (7 Nov 2026). This is a tiny *synthetic* regression, not the 288-run evaluation. **No 288-run NUS result has been claimed.** This E2 model is source-agnostic. Keep searching boundedly for useful individual-device *post-calibration* records or a genuinely different published J-format study without blocking a falsifiable E2 sensitivity result.

### Analytic E0 sensitivity bound (not measured)

For ideal logit \`x=2 beta H\` and E2 \`x'=g_i*x + d_i\`, the logistic derivative satisfies \`0 <= sigmoid'(z) <= 1/4\`. By the mean-value theorem:

\`|P_E2(+1)-P_ideal(+1)| <= (0.05*|x|+0.10)/4\`.

Thus at \`x=0\` the bound is 0.025 probability (2.5 percentage points); for \`|x|<=4\` it is 0.075 (7.5 pp). These are *mathematical worst-case envelopes* for the explicitly artificial E2 parameter assumptions, not measured device deviations or guaranteed changes in Max-Cut gap. The bound also becomes loose at saturated logits. It does not imply any actual format ranking reversal.
