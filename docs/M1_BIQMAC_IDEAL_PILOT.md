# M1 E1 first paired IDEAL weighted-Max-Cut pilot

**Scope frozen 7 Nov 2026.** This stage can be entered only after 10 official Mac source graphs passed NUS E0 input/hash/Ising mapping checks. 8 Mac/rudy small-integer graphs and 2 Mac/ising wide-range graphs passed; source hashes are in PR #19. Exact original Max-Cut optima/bounds have NOT yet been loaded.

## Pilot selection and parameters

The script `scripts/m1_biqmac_ideal_smoke.sh` uses exactly **four unmodified 100-spin graphs**:
- Low signed: `Mac/rudy/w01_100.0`.
- Low nonnegative: `Mac/rudy/pw01_100.0`.
- Wide sparse: `Mac/ising/t2g10_5555`.
- Wide dense: `Mac/ising/ising2.5-100_5555`.

First E1 pilot: **FP6 E3M2 finite-only (`fp6_fn`), signed INT6 (`int6`), signed BFP6 (`bfp6`)**, global scale only; include exact coefficient software reference `ref64`. Two scale choices per format: original graph's max-absolute coupling fullscale, and **coefficient-only per-instance MSE**. Neither scale may consult an optimum, returned-cut score, or solver seed. They are not yet a hardware-encoded scale-word implementation.

Each run uses **5000 attempted** single-spin updates, three paired solver seeds, and an identical initial state / selected index / sampled uniform variate per graph/seed across every representation. This is **4 graphs x (1 reference + 6 quantized configurations) x 3 seeds = 84 solver runs**. Keep the 6-bit format comparisons as one first gate, not a new unconstrained format search. The four graphs are a PILOT, not independent held-out results or enough evidence for statistical significance.

The same **graph-normalized mathematical beta** is used for all formats on that graph:
`beta = 1/(mean original nonzero absolute weight * sqrt(mean nonzero degree))`. This is a deterministic ideal-Gibbs starting operating point (fixed across representations), **not an STT-MRAM voltage/temperature/offset model**. No adaptive temperature schedule is fitted. Hardware is not simulated. If the chosen beta causes freezing or low solution quality, diagnose it openly before changing the rule on held-out data.

## How the solver handles states

For a candidate vertex, local field `H_i = sum J_ij*s_j`; ideal p-bit mathematical probability is `P(s_i=+1) = sigmoid(2*beta*H_i)`. A flip changes represented energy by `2*s_old*H_i`. An incremental O(degree) field update is checked against a full represented-energy recomputation at the end.

The returned state is the **earliest visited state with minimum represented Ising energy**, not necessarily the final state. The original, unrounded source graph is used to calculate the original-cut score **after** state selection, solely for independent evaluation. Raw reported metrics include best-retained and final original cut, represented E, signed/abs coefficient error, number of deleted nonzero edges, nominal dense coefficient bits and scale metadata bits. Store hashes, update counts and seeds.

**Strict limitations:** No device response has been measured or simulated. The MSE tuning fits coefficient weights of the source graph, not a solver output. No exact optimum/reference bounds are imported; no gap to optimum or target success should be presented. Cell area, timing, memory energy and bit-true Q-format arithmetic are NOT measured by this script. Original H2 MIMO quality and bias-inclusive row area cannot be substituted as new Max-Cut results. BFP global scale does not represent the benefit of optimizing shared scales per tile; both grouping and memory access remain future matched comparisons.

## NUS execution

```bash
pbit
cd "$HOME/MRAM_Pbit_M0"
git fetch origin research/m0-biqmac-maxcut-20261106
git switch --detach origin/research/m0-biqmac-maxcut-20261106
python -m unittest discover -s tests -p 'test_m1_biqmac_ideal_pilot.py' -v
bash scripts/m1_biqmac_ideal_smoke.sh
```

Source graphs are expected in `data/biqmac/raw` from the already completed M0 downloads. Output is a fresh ignored `results/m1_maxcut_ideal_...` directory containing `paired_returns.csv`, `representation_audit.csv` and `e1_manifest.json`.

This script was authored and its invariants unit tested in GitHub Actions. **The actual 4-source E1 pilot has NOT been run on NUS at the time of writing.** Do not confuse CI tests with real source-graph solver evidence.

## Decision after first pilot

- If tuned INT6 matches the exact source reference on returned cut at lower modelled cost, FP6 is not the winner at that regime.
- If BFP6 global loses because small edges collapse, future matched **tile-scale** comparisons could matter.
- If FP6 retains more original-cut quality, quantify whether this is stable over graph seeds and whether metadata, arithmetic and p-bit field-to-voltage costs erase the advantage.
- Count original edges and **sum of absolute discarded weight**, not just number of zeroed edges. The previously observed 4657/4950 zero edges under a single naïve global INT6 is not a measure of lost optimization quality.

The subsequent stage must import published reference objective/bound provenance, run held-out graph seeds and a documented stochastic-p-bit response; do NOT treat an illustrative ideal Gibbs model as measured MRAM evidence.


## First NUS four-source E1 pilot completed — diagnostic only, superseded INT-MSE scale policy

**User-run path:** `results/m1_maxcut_ideal_20261106T181543Z_2961844`.
**Source-graph pilot:** 4 original 100-spin graphs x 7 configs x 3 paired seeds = 84 solver runs, 5000 attempted updates each, original-cut evaluation, best-represented-energy returned state. Script source SHA256 `c11a19ea91f8ad6aa2c508cf67328db678e740c55f7ac9d151e2cb452a20bd7e` (historical pilot, do not overwrite or silently reclassify).

| Graph | ref64 returned mean | FP6 MSE | INT6 MSE | BFP6 MSE |
| --- | ---: | ---: | ---: | ---: |
| w01_100.0 | 567.667 | 562.667 | 571.667 | 567.667 |
| pw01_100.0 | 1921.000 | 1933.333 | 1946.000 | 1921.000 |
| t2g10_5555 | 5185275.333 | 5069377.000 | 5193319.667 | 5187966.000 |
| ising2.5-100_5555 | 2301758.333 | 2274156.333 | 2313754.667 | 2281519.000 |

Notably, on the dense wide-range graph, FP6 MSE has lower relative coefficient L1 distortion (0.070301 vs INT6 0.16441), but lower mean returned original cut for these 3 seeds. **This is not statistically supported evidence of INT6 superiority**; coefficient fidelity does not directly equal finite-budget stochastic solver quality. Some approximate representations exceed ref64 mean returned cut because the reference is NOT an exact optimum, and numerical perturbations change finite-budget trajectories.

**CRITICAL fairness correction after inspecting source:** legacy `tune_scale`'s heuristic max-weight grid failed to offer INT6 `scale=1` for small *integer* weight graphs, despite exact representability with signed six-bit values. Updated `m1_biqmac_ideal_pilot.py` now selects `scale=1` in its `int6/mse` path when source coefficients are integers fitting signed magnitude 31. This changes low-range INT6 outcomes; the 84-run pilot is retained as the uncorrected historical result. New script also distinguishes **percentage of ORIGINAL absolute weight mass discarded** from count of nonzero edges zeroed. For dense graph, the original 4657/4950 count uses all edges; 4657/4881 = approx 95.4% of initially nonzero edges after the loader drops original zero weights.

**Next reproducibility gate:** first use `scripts/m1_biqmac_paired_report.py` to audit original pilot seed pairing, then run a NEW frozen 24-seed ideal E1 repetition at unchanged 5000 attempted-update budget, with unit-INT correction and zeroed-magnitude mass. Keep results in a fresh, SHA-recorded folder; do not overwrite original run. 24 seeds reduce within-graph Monte Carlo noise but the independent units are still FOUR graphs, not 96 independent graphs. No p-bit physical response, certified optimum, bit-true RTL or complete hardware cost is claimed.
