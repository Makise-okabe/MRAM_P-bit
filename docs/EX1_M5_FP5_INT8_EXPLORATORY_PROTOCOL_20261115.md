# EX1 — exploratory FP5 / INT8 extension on previously viewed M5

**Protocol authored 15 November 2026. Status: NOT EXECUTED.** Only source-independent synthetic tests and a read-only coefficient and baseline audit are permitted during preflight. There is no new held-out validation in EX1.

## One question, limited purpose

At the original **50,000 attempted updates**, **linear annealing**, **d=0** and the original 24 paired M5 seeds, where do **FP5 and INT8** fall relative to the **already completed FP64, FP6 and INT6** quality-versus-payload-bit anchors?

EX1 is an **exploratory feasibility and width-boundary investigation** on a previously seen graph. It cannot by itself certify minimum useful width `b*`, per-edge saving `k`, graph-family generalization, or a physical MTJ nonideality mechanism. This test must not be described as an independent held-out result.

## Frozen study design and controls

| Parameter | Frozen value |
|---|---|
| Graph | Previously viewed M5 `ising2.5-100_7777` |
| Source SHA256 | `109e1ed2edc71d5f43d623367410d9257a72662d665c7a0c71af4cdd8babaf99` (strictly checked against original M5 source, source gate, and manifest) |
| Published optimum | 3,363,230 |
| Response | Ideal/zero variation: existing M5 `device_models()[0.0]`; persistent gain 1, offset 0 |
| Solver | Unmodified original M5 `solve_with_response`; 50,000 updates; linear $\beta_G(0.5+1.5t)$ |
| Pairing | Original M5 seeds **20661201–20661224**, exact same original graph beta and source-only global MSE scale policy |
| New formats | **FP5 finite-only E2M2** and **signed INT8**; existing `m1_precision_codebooks.py` without modification |
| Reused original rows | FP64, FP6, INT6 at d=0, **72 original runs** |
| New solver budget | **2 formats × 24 seeds = 48**; **hard cap 48**, no new ref64/FP6/INT6 solver runs |
| Output folder | `results/ex1_m5_fp5_int8_20261115`, separate from original `results/m2_heldout_dense_fp6_int6_20261109` |
| Numerical read-only stage | Print `scale`, `zeroed_edges`, `relative_abs_coefficient_error`, `coefficient_mse` and nominal dense payload+32-bit global-scale metadata for FP5/FP6/INT6/INT8 |
| Primary descriptive contrasts | New FP5 and INT8 paired **extra gap vs FP64**, and **direct difference vs FP6**; reuse historical FP6/INT6 |
| Secondary sensitivity thresholds | **+0.5 and +1.0 percentage points**, both **exploratory**, not yet agreed as formal pass/fail decision criterion |
| Uncertainty | 4,000 deterministic paired-seed bootstrap draws, ordinary 95% intervals; **not multiplicity-corrected and not confirmatory** |
| Stop | After the 48 new runs and archive audit, stop and interpret. No automatic INT7, no seed top-up, no new graph access, no extra stress conditions |

## Execution safety

The runner at `experiments/ex1_m5_fp5_int8_exploratory.py` has four separate modes:

1. `--selftest`: synthetic four-spin example; verifies both codebooks and exact zero-offset parity between existing ideal and device-response Gibbs routines. **No M5 source read**.
2. `--preflight`: read-only load of **already viewed** M5 source; confirms original source hash and edges, immutable M5 archive protocol/manifest SHA256, 216 unique original rows and exact 72-row d=0 baseline. Computes static coefficient-only metrics and verifies FP6/INT6 fitted scales agree with the archived runs. **No solver execution, no files written**.
3. `--freeze`: repeats checks and creates a **new** `protocol.json` recording existing archive hashes, graph hash, M5 seeds, candidate widths, source-only scales, model hash and all key source code SHA256 values. Refuses to overwrite a prior output directory. **No solver execution**.
4. `--execute`: compares the current protocol **exactly** with the frozen JSON and fails closed if code, graph, source scale or existing archive changed. Refuses output overwrites. Runs exactly the specified 48 solver evaluations, then writes `new_runs.csv`, `exploratory_summary.csv` and `manifest.json` to the **new** directory.

No original M5/M6/E0 data or frozen experimental scripts are altered. All results remain attached to the old 500-sweep operating point; EX1 does **not** recalibrate it.

### Proposed host commands, stage 1 only

```bash
cd "$HOME/MRAM_Pbit_M0" || exit 1
set -euo pipefail
git fetch origin
git switch research/m4-gain-fusion-20261107
git pull --ff-only

python3 -m experiments.ex1_m5_fp5_int8_exploratory --selftest
python3 -m experiments.ex1_m5_fp5_int8_exploratory --preflight
python3 -m experiments.ex1_m5_fp5_int8_exploratory --freeze
cat results/ex1_m5_fp5_int8_20261115/protocol.json
```

### Stage 2: separate execution, after examining the frozen protocol

```bash
cd "$HOME/MRAM_Pbit_M0" || exit 1
set -euo pipefail
python3 -m experiments.ex1_m5_fp5_int8_exploratory --execute \
  2>&1 | tee results/ex1_m5_fp5_int8_20261115/run_console.log
```

Do not run stage 2 if stage 1 fails. A retrospective graph cannot be converted into a held-out test by re-freezing it. Any subsequent `_6666` validation requires checking that it truly has not been seen and preparing a separate **prospective** statistical protocol.

## Statistical guardrails

The frozen `+0.5` and `+1.0` pp thresholds are **sensitivity summaries**, not definitive evidence that an underpowered format is inferior. Use:

- If upper paired interval ≤ margin, label *exploratory noninferior*.
- If lower paired interval > margin, label *exploratory inferior*.
- Otherwise, label *exploratory inconclusive*.

The direct FP5–FP6 and INT8–FP6 intervals answer a different question from the FP64-reference additional gap: one does not imply the other. Multiple formats/thresholds and retrospective choice of this graph mean **none of these preliminary labels qualifies as a family-wise confirmation**. No sequential looks or top-ups. If FP5/INT8 gives uninformative intervals, report that limitation and use the result to design, not pre-empt, a later independent validation.

**Interpretation to protect:** We are investigating if numerical field-fidelity changes are consequential for Max-Cut quality and therefore what storage widths are worth implementing. We are not required to find a positive FP bit-saving outcome.
