# E0-A: bounded two-CAL FP64 schedule diagnostic — protocol freeze (12 November 2026)

**Status: code + predeclared pilot design committed; on-host preflight, on-host `--freeze`, and 80 FP64 trial runs are NOT yet performed.** This is a deliberately narrow new solver-calibration pilot, explicitly requested after M5/M6 closure, not a retroactive modification of those held-out studies.

## Decision addressed

At 500 sweeps / 50,000 attempted asynchronous updates on 100 spins, does a **source-field-calibrated geometric inverse-temperature schedule** reduce reference FP64 original-weight Max-Cut gap and early freezing compared with the **unchanged previously used linear schedule**, on two already-viewed calibration graphs? Is FP64 near the proposed 1% mean optimum-gap target at the same budget? Do not assume an answer.

Old M5/M6 and CAL quantization results remain an intact **historical short-budget condition**. Do not silently replace their reference curves or retrospectively change quality screens.

## Graphs and immutable source references

- **CAL only**: `ising2.5-100_5555` (dense) and `t2g10_5555` (sparse). Each is 100 vertices, previously viewed.
- Local graph directory: `data/biqmac/raw/ising/`.
- Published official optimum and source SHA256 must both match `docs/BIQMAC_OFFICIAL_OPTIMA_2007.json`. The source references presently record the dense optimum **2,460,049** and sparse optimum **6,049,461**.
- No graph downloads or access to any `_6666` or `_7777` source. No newly selected format, field width, devices or Max-Cut instances.

## Fixed pilot comparisons

| Design parameter | Frozen choice |
|---|---|
| Solver representation | **FP64 reference only**, symmetric `J=-w`, zero diagonal/bias, no device variation |
| Graphs | 2 CAL only |
| Schedules | Legacy linear `beta_G*(0.5+1.5t)`; geometric uphill-calibrated `beta_start*(beta_end/beta_start)^t` |
| Budget | **50,000 attempted updates per run** (500 sweeps), identical for both schedules |
| Paired seeds | 20 per graph and schedule; `20261112 + 100000*graph_index + k`, `k=0..19` |
| New full solver evaluations | **2 graphs × 2 schedules × 20 seeds = 80 runs** |
| Checkpoints (read-only in each run) | After 5k, 15k, 30k and 50k attempts; these are **not** independently retuned budget runs |
| Trace bins | 10 non-overlapping bins of 5k attempts each |
| Primary endpoint | Original-source-weight optimum gap at 50k and paired geometric-minus-legacy difference, per CAL graph |
| Other outcomes | Conditional uphill acceptance by trace bin; total flip rate by bin; fraction of returned solutions within 1% optimum gap; early best-cut improvement |
| Uncertainty | 4,000 deterministic paired seed-bootstrap resamples per graph/checkpoint |
| Target | **Exploratory** mean FP64 gap ≤1% on both CAL graphs; failure triggers a separately frozen larger-budget study, not an ad hoc pilot extension |
| Code | `experiments/e0_fp64_two_cal_pilot.py` |
| Results | `results/e0_fp64_two_cal_20261112/` |

**Why uphill acceptance rather than unconditional flips on random states?** At zero bias, a random independent spin agrees or disagrees with the local field with equal probability, so the unconditional expected heat-bath flip probability is exactly **0.5 at any finite beta**, after averaging the two initial spin signs. Thus a 40%-unconditional-flip starting condition cannot calibrate temperature. Instead record positive-energy change `DeltaE=2*s_i*H_i>0` for candidate spin flips on a fixed set of 80 unbiased random FP64 spin states per graph. Select `beta_start` to yield mean **conditional uphill flip probability 0.4**, and `beta_end` to yield **0.001**, both computed as `mean(1/(1+exp(beta*DeltaE)))` over these strictly positive `DeltaE` proposals. Unconditional random-state flip is NOT the target. These field-only calibrations require no solver evaluations or score labels, and are saved in `protocol.json`.

One beta normalization `beta_G=1/(mean|w|*sqrt(mean_degree))` comes from the original CAL graph, and the same graph/profile is used for every paired seed. No beta schedule is tailored to each solution-quality result.

## Engineering and statistical controls

- Use `--selftest` on a tiny synthetic graph before freezing: three exact legacy linear-solver parity checks plus geometric trace test. Failed parity = STOP.
- Run `--freeze` on CAL source data ONLY after `--selftest`. Writes protocol with all solver/dependency SHA256 values, original source graph hashes, seeds, source-field-derived `beta_start/end`, target uphill probabilities and protocol status. No E0 solver runs during freeze.
- Inspect printed hot/cold beta and `results/e0_fp64_two_cal_20261112/protocol.json` before execution. If suspicious, STOP and document the amendment *before* the first pilot solver run.
- `--execute` fails closed if current source/code/protocol differs from frozen JSON. It refuses to overwrite existing run CSVs. The solver uses exactly the same `random.Random(seed)` draws for old and new schedules, so differences are paired.
- At every checkpoint, retain the **earliest lowest represented energy** state; for FP64 this corresponds to the original cut. Original-weight scoring is evaluation-only and does not drive acceptance/schedule choice.
- Report absolute mean gap and **paired** geometric-minus-legacy mean gap CI; do not declare equivalence from an interval crossing zero. Twenty solver seeds per graph are not 20 graph instances.
- Use CAL performance only to choose whether a wider budget is necessary. Do not re-open old held-out graphs to select the schedule. Schedule/budget for new width studies requires a separate prospective protocol.
- Archived M5/M6 nonideal STT-MRAM results are historical at their original solver operating point. This E0 diagnostic studies neither gain nor offset, and it is **not** a measured device result.
- A two-graph **pilot** is deliberately smaller than the full multi-instance E0 described in Claude's roadmap; it does not yet establish general convergence or authorize other graph families.

## Host commands (execution not yet performed)

```bash
cd "$HOME/MRAM_Pbit_M0" || exit 1
git fetch origin
git switch research/m4-gain-fusion-20261107
git pull --ff-only
source "$HOME/.venvs/mram-pbit-h2/bin/activate"

python3 -m experiments.e0_fp64_two_cal_pilot --selftest
python3 -m experiments.e0_fp64_two_cal_pilot --freeze

cat results/e0_fp64_two_cal_20261112/protocol.json

# Only after comparing printed/recorded uphill calibration and
# explicitly proceeding under this frozen protocol:
# python3 -m experiments.e0_fp64_two_cal_pilot --execute
```

After full completion, audit 80 unique run keys, 320 checkpoint rows, 800 trace-bin rows, **16 summary rows total** (2 graphs × 2 schedules × 4 checkpoints), 8 paired difference rows and frozen source/code SHA matches, then archive the raw output and summarize. **Do not start FP8/INT8 yet.**

## Proposed later thesis metric, distinct from E0

Once E0 establishes the solver operating point, propose to Prof Fong a primary endpoint `k=b*(INT)-b*(FP)` bits saved per undirected coefficient at a **prospectively agreed equal-quality criterion**, where `b*` is the minimum certified useful width. `Delta=0.5` percentage points is a **proposed** tolerance, not a rule approved by Prof Fong or validated by the current studies. New width, device-population and hardware protocols remain unopened until E0 results and project scope are reviewed. For untested INT7, use the separately frozen symmetric signed codebook/RTL extension; it is not currently implemented by the frozen 4/5/6/8-bit pool.
