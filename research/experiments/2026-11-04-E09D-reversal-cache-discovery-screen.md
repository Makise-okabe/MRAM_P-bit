# E09D — reversal-consistent coupling cache: first bounded discovery screen

Date: 2026-11-04 Singapore. **Research status: investigative / UNVALIDATED against target MRAM; no method or novelty selected.**

## Question

Can pinning an imperfectly read coupling column for the full departure/return excursion of a spin reduce additional local-field drift while using less total computation than ordinary bounded caching, tuned periodic exact refresh, and accurate digital incremental fields?

Candidate: on departure from a reference spin assignment, retain the imperfectly measured column until reversal, then apply its exact sign-inverse and release it. When B slots are full, use **exact digital fallback on both halves** of uncached departures. This fallback is an idealized, potentially expensive resource that must be charged.

**Proof under strict assumptions.** If every retained coefficient error is bounded elementwise by epsilon, at most B columns are outstanding, fallback is exact, fields are initialized exactly, and arithmetic is exact, then |h_i_est-h_i_true| <= 2B epsilon. This is a bound on *field state* for a fixed spin state, **not on spin trajectory or solution quality**. Every temporary excursion can still change a heat-bath decision. Purely persistent per-coupling errors reread identically already cancel on reversal without pinning.

## Actual work performed (software, not NUS hardware)

Local independently scripted **synthetic** 12/14/16-spin weighted random Max-Cut screens, exact target optima, 24 restarts per graph, 12 annealing sweeps, paired update order and external uniform random numbers. Modes: exact digital incremental, fresh imperfect read per accepted flip, ordinary bounded LRU, proposed pinned-with-exact-fallback, and fixed-period exact field refresh every N accepted flips (NOT tuned). Three ASSUMED error models: (1) persistent Gaussian coupling perturbation, (2) independent temporal Gaussian read error, (3) mixed perturbations, with sigma=0.6 in abstract coefficient units; no GF or other physical parameters and no eight-cell data. Budgets B=2, 6, plus B=16 (full graph). Exact field initialization for all arms, no arithmetic rounding. Spin paths diverge naturally. Each method is assessed against the exact field of *its own current spin state*; cut success and update-decision disagreement are different metrics.

**Local source SHA-256:** `81384c7186ab2757e40b5979efcbd4105c150108c60338bd8288cfc1aaad5a2b` (source delivered with accompanying ChatGPT conversation as `e09d_reversal_cache_screen.py`; this record does not claim the script is tracked in GitHub). **Results SHA-256 (B=2,6):** `902df7fcfde256cb6e99a2a49f5de6cb5cc35429933a8fb5a310a83801f448f9`.

### Selected 16-spin results (24 restarts, 12 sweeps, illustrative only)

| Mode | Temporal error / cache B=2: maxcut optimum hits | Mean analog column reads | Mean exact digital column reads | Mean cache hits |
|---|---:|---:|---:|---:|
| Exact digital incremental | 12/24 | 0 | 23.6 | 0 |
| New imperfect read per flip | 5/24 | 26.4 | 0 | 0 |
| Bounded ordinary LRU | 5/24 | 22.5 | 0 | 2.0 |
| Pinned + **exact fallback** | 8/24 | 3.9 | **18.0** | 2.0 |
| Periodic exact-field refresh | 7/24 | 23.3 | 0 | 0; plus ~1.0 exact full-field recomputation |

At B=6 under temporal error: ordinary LRU 7/24 optima with 17.4 analog reads and no exact column reads, while pinned 7/24 with 10.0 analog + 8.2 exact digital column reads. **Neither is a matched-cost gain; exact fallback dominates the interpretation.**

At B=16 (whole graph) under temporal error, ordinary persistent LRU achieved 8/24 optima, 13.3 analog reads; pinned achieved 6/24, 16.1 analog reads. Under persistent error, B=16 LRU and pinned tie at 6/24; LRU needs fewer reads (13.2 vs 16.3). All 24-restart success comparisons are preliminary and have large uncertainty. The fixed periodic schedule and failure correlation are not tuned.

**Crucial confound:** At B=2, pinning effectively runs many updates through the exact digital route. Its apparent accuracy advantage therefore **does not isolate reversal-consistent retention**. At B=16, when the expensive fallback disappears, conventional persistent memoization is a powerful or better baseline.

## Elimination/continuation gates

1. **Physical operator gate:** specify whether the actual GF/MTJ array reads an individual J_ik, an entire coupling column, or a many-row dot product. Validate the actual read's repeatability (persistent vs time-varying conditional error) with fresh E02, not assumed Gaussian coupling noise.
2. **Cost gate:** declare the energy/latency/area and realistic accuracy of a fallback coefficient-read route. If exact digital is cheap, the analog approximate update may be irrelevant. Count initial field solve, B x N retained coefficient bits, flags, cache hits, transpose/coupling duplication, and refresh, including cost of reading zeros.
3. **Strong cache gate:** baseline a persistent frozen coefficient table, ordinary LRU, locked LRU with bypass, and a matched-cost/tuned periodic reset policy. A locked cache with exact bypass can implement the proposed scheme verbatim; the method as currently stated might be only conventional cache locking. Don't claim new Ising arithmetic.
4. **Solver gate:** predeclare held-out graphs/chips, multiple independent cases, true maximum cuts, paired random streams and tuned equal-budget schedules. Report conditional decision divergence at each arm's own current spin and cost-quality Pareto curves. No claimed time-to-solution or joules until actual costs are sourced.

**Current disposition:** useful mechanism demonstration but **insufficient reason to prioritize an Ising thesis** over F3/F1. The next discovery step is the cost+cache equivalence falsifier, not constructing a new 256x256 array for this candidate.

Close literature: Snowball 2026 incremental digital fields (https://arxiv.org/abs/2601.21058); SACHI HPCA 2024 reuse-aware all-digital compute (https://ieeexplore.ieee.org/abstract/document/10476402); Müller & Janke PRL 2026 predecision (https://doi.org/10.1103/29yw-9grr). Similarity does not prove exact procedure is previously published; precise novelty remains unresolved.
