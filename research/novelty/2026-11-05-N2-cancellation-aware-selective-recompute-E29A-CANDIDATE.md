# N2 / E29A — Cancellation-aware selective digital recovery of signed-W4 MRAM CIM partial sums
**Candidate algorithm, NOT frozen FYP novelty or physical result.** 2026-11-05. The active target is still the user-selected **1T1MTJ** analog CIM research prototype (ADR-0009), NOT historical 2T1 PEX. Recovery is an optional software/scheduler layer; no MTJ writes are required.

## Precise problem

For a signed 4-bit weight reconstructed from four binary planes, let
`c=[1,2,4,-8]`, `e=[e0,e1,e2,e3]` be **joint decoded-minus-ideal count errors** for four plane contributions sharing the *same input and logical output*. For selected set `S` of exactly recalculated digital plane contributions, the remaining reconstruction error is

```
E(S) = sum_{j not in S} c_j e_j.
```

Each plane may comprise up to 8 A8 activation-bit reads over multiple physical row segments. A purported exact digital replacement must compute the **entire declared contribution**, not silently replace one ADC conversion while charging one cheap operation. For the group/plane/activation definition, the physical mapping and actual costs require explicit documentation.

The proposed **calibration-only** selector estimates conditional mean `mu(z)` and covariance `Sigma(z)` of the four aligned plane errors using ONLY training pairs, with runtime observable features `z` (known input activity / location / Q, possibly measured raw ADC output if paid). Selection is

```
S*(z) = argmin_{S: sum_j in S d_j <= B}
        [ (sum_{j not in S} c_j mu_j(z))^2
         + sum_{i,j not in S} c_i c_j Sigma_ij(z)
         + lambda * sum_{j in S} d_j ]
```

where `d_j` is the genuine exact-digital-recompute cost. Compare worst-case per-output and average realized budgets; **allow S=empty**. `lambda` must be prechosen on CAL and not tuned on held-out DEV.

Implementation can use an exhaustive 16-subset CAL-risk LUT for W4; the covariance equation is ordinary conditional squared-error minimization, **not itself an original algorithm**. The deployment cost of classifying `z`, hardware state/per-chip CAL, metadata reads and digital weight/input access must be charged. The predictor must not compute the correct count or true error at runtime for free.

### Novelty plausibility
The underlying idea of selected computation protection/recovery is existing art:
- SEC-CiM (ITC 2024) selected ReRAM-column compensation, DOI 10.1109/ITC51657.2024.00037.
- *Trust, but Verify* (IOLTS 2026) flags risky CiM outputs and selectively recomputes on CPU, DOI 10.1109/IOLTS69666.2026.11633847.
- CorrectNet+ (IEEE TCAD 2024) RL-selects error compensation locations, DOI 10.1109/TCAD.2023.3313089.
- Mixed-precision iterative refinement / bit slicing are established (Mannocci et al., npj Unconventional Computing, January 2026, https://www.nature.com/articles/s44335-025-00044-2).

Our *conditional potential* is demonstrating on **actual 1T1MTJ physical joint plane errors** that *sign-sensitive, nonnested, computation-level* subsets outperform strong contextual baselines at equal hardware cost, when allowed runtime features predict cross-plane cancellation better than marginal-only predictors. Without that, reject as a relabeling of selective recompute.

## E29A independent software falsification program
Source: [`experiments/e29a_joint_recovery_gate.py`](../../experiments/e29a_joint_recovery_gate.py). Tested in chat container Python (no NUS Spectre). Supports `selftest`, `demo`, `evaluate --csv --attestation`. The demo uses **entirely artificial error signs**; its only use is checking the algorithm and showing a possible nonnested advantage. Does not use 1T1 PEX or neural inference.

### Constructive toy: identical *per-plane marginals*, different **joint covariance**

Two observable, **invented** regime labels `A`, `B`, equally represented; each sample multiplies the sign vector by a hidden fair random sign `u = ±1`. Therefore each plane's own conditional error distribution is `P(e_j=-1)=P(e_j=+1)=1/2` for either regime.

- `A: e=u*(-1,+1,+1,+1)`: no repair has `E=-3u` -> MSE `9`; repair non-prefix plane **bit0** leaves `E=-2u` -> MSE `4`; sign-plane-only repair yields `+5u` -> MSE `25`. **A requires bit0, not a most-significant-bit repair**, if unit cost is affordable.
- `B: e=u*(+1,+1,+1,-1)`: no repair `E=15u` -> MSE `225`; repair sign plane **bit3** leaves `E=7u` -> MSE `49`. **B requires bit3.**

Exactly CAL-only fit and separate held-out synthetic DEV with per-sample at-most-one-bit digital correction, costs=(1,1,1,1), penalty=0:

| Policy | DEV signed-MAC MSE | Mean repairs |
|---|---:|---:|
| No repair | 117.0 | 0 |
| Globally optimal fixed arbitrary subset | 37.0 | 1.0 |
| Individual-plane scoring / diagonal-moment context | 37.0 | 1.0 |
| **Optimally calibrated significance PREFIX PER REGIME**, zero allowed | **29.0** | **0.5** |
| **Full joint context arbitrary subset** | **26.5** | **1.0** |
| Unusable DEV true-error oracle lower bound | 26.5 | 1.0 |

**Major fairness caveat:** the 26.5 vs 29.0 comparison is **not at equal mean recomputation cost**: joint uses 1.0 versus prefix 0.5. When predeclared abstract cost penalty `lambda=5` MSE units per repair is applied on CAL, JOINT chooses **no repair in A, sign-plane repair in B**, precisely matching contextual prefix: **both MSE 29.0 at average cost 0.5**. Thus this toy is *not evidence of cost-effective superiority*, let alone a paper novelty claim. Its regime labels are artificially observable; actual hardware must demonstrate that inexpensive runtime features reveal any relevant dependence.

## Strong-baseline and evidence gates
1. **Physical data gate:** E28S real GF-NFET shared-SL assumed-resistor Spectre had 0/28 count errors at all 0.01/5/20Ω, so recovery there is pointless. E24 assumed-BL-R single-column 32-branch GF counts contain errors but **cannot supply jointly synchronized four signed-plane errors on a real 1T1 layout**. Do not fabricate the 4-plane vector from independently sampled E24 cases or E26A mock errors.
2. Collect aligned repeated `(input_id, chip_id, logical_output, physical_locations, activation_bit, row_group, e[4])` from a legitimate 1T1 4-column multi-WL read; preserve per-chip paired states, P/AP and physical mapping. 4 bitplanes may occupy separate arrays; explicitly control array/chip/temporal covariance and physical sharing. Repeated input reads are not independent chips.
3. The complete digital replacement must be mechanically defined (subread vs entire weight plane, repeated A8 cycles, weight memory access and digital MAC), with **realistic energy/latency and output timing**. Do not equate abstract `cost=1` to a measured joule.
4. CAL-only features: active count `m`, input mask / spatial `Q`, column/row group, known stored bitplane mapping, and optionally observed ADC code **only if its hardware and inference cost are charged**. `n`, `e`, true logits and clean labels are **never runtime features**. Note: if exact `n` is computed online from weights and input, that work itself is the digital recomputation and must be charged; no hidden oracle.
5. Compare on fixed unseen DEV samples and independent physical chips: no-repair, fixed highest significance prefix with zero option, **contextual CAL-optimal prefix**, fixed CAL-optimal arbitrary subset, independent diagonal-moment per feature, individually scored features, no new recovery with calibrated Q, and offline oracle only as an upper bound. For task-level claims additionally full frozen W4A8 NN clean/injected predictions and correct-vs-clean labels.
6. Report error and **mean/worst recompute cost** as a Pareto frontier including `lambda`, CAL memory size, detector cost, and confidence/uncertainty across chips. Prefer the simpler baseline if tied. Correct only when there is demonstrable encoded count failure; zero repair should win on clean hardware.
7. If cross-plane covariance is too weak, not predictable from low-cost features, or adaptive gains vanish at cost matched contextual-prefix/independence baseline, **reject N2** and preserve the negative finding.

## Execution
```bash
cd ~/MRAM_Path_Finding
git pull --ff-only
python3 -m py_compile experiments/e29a_joint_recovery_gate.py
python3 experiments/e29a_joint_recovery_gate.py selftest
python3 experiments/e29a_joint_recovery_gate.py demo --budget 1 --costs 1,1,1,1
python3 experiments/e29a_joint_recovery_gate.py demo --budget 1 --costs 1,1,1,1 --cost-penalty 5
```

**Stop here until genuine aligned physical error traces exist.** E29A does NOT require another artificial electrical R sweep and does not request new CAD preflight. This candidate should not override existing frozen 1T1 architecture or claim discovery.
