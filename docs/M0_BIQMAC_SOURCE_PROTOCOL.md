# M0 source and mathematical benchmark gate — Biq Mac / Mac

Scope locked 6 November 2026: **weighted Max-Cut** with original instances from the Mac part of the official **Biq Mac Library**, not Biq/QUBO, not MIMO.

## Official source format

- Source: https://biqmac.aau.at/biqmaclib.html
- Actual individual Mac/Rudy files: https://biqmac.aau.at/library/mac/rudy/
- Solver interpretation (loops ignored, parallel edges summed): https://biqmac.aau.at/
- Each text file begins with two integers n m, followed by exactly m lines of u v w, where vertices are numbered from 1 to n. Original edge weights may be signed, zero, integer or real. Never remove negative weights by taking absolute values. Do not alter source graph topology or weights.

## Fixed initial selection (100 original vertices each)

| Original instance family | Source weight type | Density | Source-audit instance |
| --- | --- | --- | --- |
| w01, w05, w09 | signed integer from -10 to 10 | 0.1, 0.5, 0.9 | .0 |
| pw01, pw05, pw09 | nonnegative integer from 0 to 10 | 0.1, 0.5, 0.9 | .0 |
| pm1s, pm1d | signed -1, 0 or +1 | sparse / dense | .0 |

The first import script downloads 8 named, unmodified .0 graph files to a locally ignored directory. No quality comparisons follow from this import. If solver-scale tuning is later implemented, use instance seeds .0 through .4 as calibration and .5 through .9 as held-out; source identity is the statistical unit. Do not add a cropped graph to the benchmark and inherit its published optimum. The Mac/ising subdirectory is also legitimate source data, but is outside this initial 100-spin pilot.

## Exact sign convention and test

- Original score: Cut_w(s) = sum over i<j of w_ij (1 - s_i*s_j)/2.
- Represented Ising energy in the current code convention: E = -sum over i<j of J_ij*s_i*s_j.
- Choose J_ij = J_ji = -w_ij, J_ii = 0, and mathematical h_i = 0.
- Then E = W - 2*Cut_w, with W = sum of original edge weights.
- The pre-update local field is H_i = sum over j != i of J_ij*s_j.
- A single spin flip satisfies deltaE = 2*s_i*H_i.
- E and the cut are symmetric under flipping ALL spins (global spin complement).

The new Python parser stores the original source SHA256; it combines parallel edges and drops self-loops as documented by the official Biq Mac service, with counters, and uses exact Decimal arithmetic for source weights. First-stage audits test objective and flip identities and independently brute-force tiny signed graphs.

## Return-state and reference gates

A solver's selected state is evaluated on the unchanged original cut. The runtime retention policy must use the represented energy, NOT an uncosted original-graph oracle. Report independent graph names/hashes, seeds, attempted updates, returned original-cut values, reference type (certified optimum, best-known feasible value, or upper/lower bound), and proper absolute gap interpretation.

**No optimal values or bounds have been imported yet.** Each M0 report explicitly says optimum_status=NOT_LOADED. Any claimed optimum must first be matched to the official instance identifier and published reference type. Relative gaps may be undefined when the optimum is zero. A p-bit's physical offset is distinct from the zero mathematical h_i.

Common Mac/Rudy benchmark edges are small integers: INT6 and BFP6 at a unit scale can represent -10..10 exactly. FP4 need not. Do not invent fractional weights or wider magnitudes to favor FP. Count sign, scale/metadata, coefficient reads, alignment, device interface, scheduler and best-state-retention costs. The older FP4-coupling/FP6-bias area mapping is historical and bias-inclusive: Max-Cut requires new h=0 synthesis before any area conclusions.

## First NUS E0 gate (not yet executed)

Run in the existing NUS pbit shell, from the project repository:

    pbit
    cd "$HOME/MRAM_Pbit_M0"
    git fetch origin research/m0-biqmac-maxcut-20261106
    git switch --detach origin/research/m0-biqmac-maxcut-20261106
    python -m unittest discover -s tests -p 'test_biqmac_maxcut.py' -v
    bash scripts/m0_fetch_biqmac_mac.sh

Only the 8 source graphs are downloaded from Biq Mac. The original files and local E0 audit JSON are ignored by Git. These commands do not run an Ising solver, new coupling-format sweep or stochastic-MTJ simulation. Do not state PASS before the user supplies the actual NUS output.

## Evidence classification

E0: original graph parser and mathematical consistency (this gate).
E1: seeded solver output quality on original weighted cut.
E2: synthetic illustrative response.
E3: physically sourced or validated p-bit response.
E4: authorized device/circuit simulation.
E5: RTL/synthesis/hardware component evidence.

Preexisting MIMO software results and earlier generic Max-Cut pilots stay historical only. MIMO bit-true generic circuitry may be reused after application-specific validation, not relabeled automatically as benchmark results.
