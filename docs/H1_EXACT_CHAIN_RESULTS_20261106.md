# H1 first exact random-scan chain result — NUS, 6 Nov 2026

**Evidence:** User-run NUS file `results/h1_16qam_20261106T054924Z_4108213`. Existing script `experiments/h1_16qam_exact_chain.py` self-test PASS: random-scan transition, ideal Gibbs stationary distribution, correct *unrenormalized* first-hit calculation, fixed-time snapshot policy. No new code or CI added for this results note.

**Parameters:** complex 2×2 16-QAM = 8 spins, 12 dB, 40 independent calibration frames and 20 HELDOUT channel frames, each with two simulated device populations. Global coupling scales fitted on CAL only; 4 frozen representations (mixed FP4_fn-J/FP6_fn-h, mixed INT4-J/INT6-h, BFP6, uniform FP6). Three E2 response rules: ideal sigmoid, contrast090, and static per-site gain/offset mismatch (`gain_sigma=0.20`, `offset_sigma=0.10`). Fixed `beta=1.0`, original ML residual target gap ≤0.05, budgets 0/20/100/500 one-spin attempted updates. 40 reported frame-population pairs are **NOT** 40 independent channel frames. Ideal and contrast models repeat across populations (except any shared frame bookkeeping); the device-population dimension mainly varies mismatch response. Software-stationary distributions converged for all printed aggregate groups.

## Numeric result at 500 updates

| Code | Nominal bits | Ideal P(hit by 500) | Ideal P(snapshot target) | Ideal expected Gray BER | Contrast P(snapshot target) | Mismatch P(snapshot target) |
|---|---:|---:|---:|---:|---:|---:|
| mixed_fp | 224 | .971296 | .050675 | .383420 | .042977 | .054928 |
| mixed_int | 224 | .970941 | .052106 | .382489 | .043918 | .056924 |
| bfp6 | 232 | .975197 | .052209 | .381065 | .044088 | .056800 |
| uniform_fp6 | 280 | .976147 | .052561 | .381760 | .044228 | .056757 |

For mixed_fp under ideal response, P(hit by K) at K=0,20,100,500: 0.009375, 0.184708, 0.617395, 0.971296. Corresponding P(snapshot target at K): 0.009375, 0.046076, 0.050620, 0.050675. After 100 updates the snapshot distribution is near stationary at this `beta=1` operating point, but the any-visit probability continues rising. P(hit) is NOT the old software's quantized-energy best-of-checkpoint output success and is not hardware performance without a mechanism to recognize/retain a target.

## Interpretation and scientific gate

1. **No established H1 precision–nonideality interaction yet.** Mixed FP vs matched INT snapshot differences ≤~0.002 across response models; uniform FP6 minus mixed FP snapshot probability at K=500 is 0.001886 (ideal), 0.001251 (contrast), 0.001829 (mismatch). These are tiny and from 20 HELDOUT frames, not evidence of statistically robust device-dependent useful coupling precision.
2. **The observed ~0.38 expected Gray BER is poor absolute quality** despite ~0.97 probability of ever visiting an original residual-gap target by 500 updates. Increasing K without an output-selection/annealing policy does not substantially improve snapshot BER at this operating point.
3. `contrast090` reduces mixed_FP stationary target mass from 0.050675 to 0.042977, while `mismatch` raises it to 0.054928; both are synthetic E2. The log-normal `gain=exp(N(0,0.2))` has mean exp(0.2²/2)>1, so *mismatch improving average quality* may partly be an effective beta shift rather than beneficial hardware mismatch; no physical claim.
4. **A predeclared temperature check is necessary before interpreting saturation.** The generator draws complex noise CN(0,sigma²) with sigma²=(tx/rx)10^(-SNR/10); for square MIMO at 12dB, sigma²=0.06309573445. If the target is sampling the AWGN posterior proportional to exp[-||y-Hx||²/sigma²], the ideal Gibbs inverse temperature is beta_AWGN=1/sigma²=15.84893192461. The current beta=1 is much hotter than this posterior-consistent ideal. Optimization-focused p-bit machines can operate at other temperatures, but beta must be a defined physical/input scaling or CAL-fitted operating policy, not opportunistically chosen from test outputs.
5. **Next single check, not a sweep:** run the same H1 program, same exact CAL/HELDOUT, group, 4 formats, device populations, contrast/mismatch rules and budgets with `--beta 15.84893192461113`. Compare finite-budget snapshot BER/gap/target and any-visit. Strong beta can slow mixing; stationarity may fail to converge within 15000 iterations, in which case report stationary P as NA rather than claiming it. This is a likelihood-consistent **software operating-point diagnostic**, not a demonstrated stochastic MTJ voltage transfer.
6. After this one diagnostic, do not keep scanning beta or formats. Either source a physically characterized p-bit input transfer/time/mismatch model and define output retention/annealing cost, or honestly state H1 remains unsupported by device data. The 16-spin H2 results remain a different MIMO regime; do not compare H1 8-spin absolute BER directly to H2 16-spin Gray BER.

**Research focus remains low-order FP couplings × nonideal MRAM p-bits, with 64–128-spin bit-true coupling tile and synthesis as required hardware proof.** Current H1 is exact mathematics under assumed behavioral response only.
