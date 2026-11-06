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

## Frozen within-library dynamic-range contrast (7 Nov 2026)

The benchmark does NOT need a new library. The official Mac files are in TWO directories and have the SAME Rudy format:

| Category | Exact official source | Vertices | Raw edges | Evidential role |
| --- | --- | ---: | ---: | --- |
| Low-range signed | `/library/mac/rudy/w01_100.0` etc | 100 | per source | INT-friendly negative control |
| Low-range nonnegative | `/library/mac/rudy/pw01_100.0` etc | 100 | per source | INT-friendly reference |
| Wide-range sparse torus | `/library/mac/ising/t2g10_5555` | 100 | 200 | physical-spin-glass broad-range calibration |
| Wide-range dense Ising | `/library/mac/ising/ising2.5-100_5555` | 100 | 4950 | broad-range dense calibration |

`t2g10_5555` has observed minimum nonzero |weight|=460 and maximum |weight|=294541, ratio about 640.31. The official full source is small enough to inspect completely. For `ising2.5-100_5555`, the official source contains a coefficient of 1 and an edge with weight -101237; the confirmed within-graph ratio is **at least** 101237 and must be recomputed over all entries during E0 rather than asserted as a global maximum. Preserve all original signed weights and zero-valued entries.

Official listing: https://biqmac.aau.at/library/mac/ising/ . Individual files:
- https://biqmac.aau.at/library/mac/ising/t2g10_5555
- https://biqmac.aau.at/library/mac/ising/ising2.5-100_5555

**Predeclared independence:** For initial source audits, only use the `_5555` graphs of these two wide-range families. If calibrated on `_5555` and `_6666`, reserve `_7777` within each family as a separate held-out graph. Three instances per wide-range family are NOT sufficient to claim a broad statistical generalization. Continue the earlier `.0`–`.4` CAL and `.5`–`.9` HELD-OUT partition for Rudy families. Avoid moving or renaming the training/held-out assignments after seeing results.

**First E0 audit run (no optimization):**
```bash
python -m unittest discover -s tests -p 'test_biqmac*py' -v
bash scripts/m0_fetch_biqmac_mac.sh
bash scripts/m0_fetch_biqmac_wide.sh
```

The wide-range script downloads into `data/biqmac/raw/ising`, enforces n=100/m=200 and n=100/m=4950, audits the sign/cut/flip identities, reports source SHA256, and records min|max, dynamic-range ratio, sign counts, number of nonzero/unique edges, and a **simple globally fullscale INT6** zeroing/error diagnostic. That diagnostic is NOT an optimized INT6 result; a calibrated INT6/BFP/FP comparison and actual Max-Cut solving remain future E1.

**Interpretation caution:** large raw |weight| alone is not a test of FP dynamic range. Uniform common scaling preserves relative proportions, and sparsity/density, edge importance, rounding, global vs block scale, device response and returned solution quality all matter. In particular, FP4 E2M1's finite nonzero range cannot simply be assumed to preserve a >600x weight spread, and a per-block BFP design can be competitive even when a global 6-bit INT is not. Freeze numeric format semantics and compare equal resource budgets rather than retune each format using the held-out graphs.

## NUS E0 verification update — 7 Nov 2026
Official Mac/rudy 8/8 and Mac/ising 2/2 original source audits **passed on NUS**. Source hashes are recorded in Draft PR #19. In particular `t2g10_5555` was 100/200, min nonzero |w|=460 max=294541, SHA256 c742b78ebdebb47ad7146bffd657d42fab814a7fa82c4a17942b37f2f7fa96cb; `ising2.5-100_5555` was 100/4950, min=1 max=239752, naive fullscale INT6 4657/4950 edges zeroed, SHA256 c8fa3ce4df1997b89aad6199525a66e55699c259680483b62cc5fd3cfc1e316e. This is E0 **not** an E1 optimizer result. See [first E1 ideal solver protocol](M1_BIQMAC_IDEAL_PILOT.md). The earlier pre-run status statements above describe the state when code was first authored and are superseded by this verification update.
