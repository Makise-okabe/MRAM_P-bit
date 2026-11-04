# E11D — First-principles cross-segment read decision (discovery candidate, not selected)

Date: 2026-11-04 Singapore. **Constructed resistor-ladder software only; NOT new GF 22FDX+ / Spectre read, PEX, ADC, Ising solver improvement, silicon energy, or originality certification.** Source package `e11d_ising_pathfinder.zip` produced in this ChatGPT conversation, SHA256 `747879abd1e3a65b2f632e134b2258eec2fb4a77a3055b5b12c8948d5013458e`; includes stdlib Python 3.6 scripts, JSON and reproducibility README. Source code has **not** been committed to GitHub by this note. Not based on retired eight-cell results.

## Why this is more specific than generic Ising calibration

A first-order one-ended shared-resistance ladder with per-segment resistance r, input voltage V, and active row conductances a_j has current I ≈ V(G-rQ), with G=sum_j a_j and Q=sum_{l=1}^N (sum_{j>=l}a_j)^2. It follows from first-order nodal KCL, not an original theorem.

For two disjoint simultaneously active mask groups A={1..6} (near) and B={7..12} (far), the first-order physical *benefit of splitting* is V r [Q(full)-Q(A)-Q(B)]. A **weight-blind** approximation uses unit conductances x_j in the mask:

`Delta Q_mask = 2 * n_far * M_near`, where n_far is the number of active far rows and M_near = sum_(j<=6) j x_j. Both counters update in O(1) per accepted spin flip, without reading stored J coefficients or computing the dot product. The proposed *algorithmic decision* is to use a second read for the highest estimated cross-segment interaction masks under a fixed read-resource allowance. This is a candidate to distinguish from simple activity/count/centroid-based splitting, NOT yet a claim that splitting, IR-drop modelling, or dynamic WL allocation is novel.

## New illustrative results from independent software execution

Assumed 12-row one-ended passive ladder, r=25 Ohm/segment (arbitrary), Rp=5k and Rap=10k (from E11C student behavioural-model default parameters), V=50mV (chosen mathematical source voltage, **not newly verified safe read bias**). No access MOSFET, ADC, MTJ dynamics or full 256x256 parasitic network.

Matched 2P/2AP example:
- A: P rows 2/11, AP rows 3/10; exact Kirchhoff current 28.205523 microA.
- B: P rows 5/8, AP rows 1/12; exact current 28.067443 microA.
- Same total conductance and conductance-weighted spatial first moment; 0.138080 microA difference, captured to first order by the shared-wire Q term (predicted 0.150000 microA).
- In 400 CAL / 1000 DEV resistor-ladder samples, *full conductance-aware* Q fitted response has MAE 0.01354 microA vs 0.14270 microA centroid-only. **Full Q uses hidden weight information and is NOT a deployable cheap controller; this number is mechanistic only.**

Action test on all 2,970 combinations of 2 P/2 AP among 12 rows: splitting near/far improves absolute linear-current error. An optimistic full-pool top-quartile allocation captures 38.46% of all possible aggregate split benefit versus 40.43% for an omniscient oracle. More important, in a CAL-only deployment test, 200 **unique masks** define a 25% CAL trigger threshold; 295 distinct mask identities are held out (six independent P/AP assignments per mask, 1,770 evaluated patterns).

At seed 20261104:

| policy | DEV extra-read fraction | DEV mean absolute current error (microA) | useful error reduction / extra read (microA) |
|---|---:|---:|---:|
| no split | 0 | 2.04698 | -- |
| random | 30.17% | 1.87852 | 0.5584 |
| simple near x far popcount | 25.42% | 1.87878 | 0.6616 |
| **cross-segment mask moment** | **23.05%** | **1.85218** | **0.8451** |
| all split | 100% | 1.51227 | -- |

Across **five CAL/DEV mask-split seeds**, the cross-segment mask moment gives 0.845..0.874 microA benefit per extra read, compared to 0.649..0.665 for simple near x far popcount. These are NOT five independent chip realizations, and DEV read fractions differ, so a matched-operating-point curve is still required. On some seeds a count-based rule gets lower absolute error by spending more reads. No ADC code crossing, signed coupling reconstruction, Ising solution success, latency or energy measured.

## Prior art and rejection gates

- Rasch et al. Nature Communications 2023 show that input- and weight-dependent IR drop affects analog crossbar response: https://www.nature.com/articles/s41467-023-40770-4
- IEEE TED 2022 IR-drop analytical modelling and compensation: https://ieeexplore.ieee.org/document/9693956/
- DIB-CIM (TCAS-I 2026) adapts WL group sizes based on input-bit/distribution and ADC constraints; full detailed method comparison is unresolved: https://ieeexplore.ieee.org/abstract/document/11672681

Novelty could survive only if the **cheap mask-only physical interaction trigger** makes a different reliable intervention versus optimized count, centroid, position-aware calibration, SEC, adaptive split and equal-cost random, *and* if real target RC/periphery creates the assumed shared-wire effect. Same rule could be evaluated for neural inference; Ising adds O(1) event-updateable spin-mask counters, but the Ising motivation requires a real analog field operation and an advantage over exact digital incremental updates. The relevant actual GF 2T1MTJ SL wiring may invalidate the simple one-ended ladder.

**Research status:** promising *candidate method decision* supported by constructed circuit mathematics. Do not certify novelty or pick final FYP from this result. Most valuable next test: actual access NFET + student-MTJ nominal near/far and pair read; then ADC/Ising task-quality and full-cost comparison.
