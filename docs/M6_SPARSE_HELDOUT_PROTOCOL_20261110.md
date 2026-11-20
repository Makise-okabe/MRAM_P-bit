# Sparse held-out validation (M6) — pre-execution protocol freeze

**Status: protocol choices frozen in GitHub; ZERO sparse-7777 graph reads, ZERO M6 solver runs in this preparation.** On-host code-hash snapshot `--freeze` and CAL smoke test are still required before any `--execute`. This is the second, distinct validation instance after dense M5. Keep the dense M5 and CAL/gain interval-recovery evidence immutable and separate.

## 1. Scientific purpose and predeclared questions

Test whether M5's representation-dependent numerical/probability-fidelity finding also appears on an independently held-out **sparse**, signed-weighted Max-Cut instance. Record negative or inconclusive outcomes; do not retune formats, scales, solver, response or thresholds based on dense held-out results. Only one new graph is evaluated; this does **not** establish population-wide generalization.

Primary predeclared response-fidelity prediction: **FP6 minus INT6 mean static absolute switching-probability distortion is negative** on matched FP64-returned states at **d=0.8** and **d=1.6** separately. This is a directional prediction, not an assertion that the sparse graph will behave like dense M5. Report the ideal d=0 contrast too.

Separate solver-quality question: estimate paired FP6 minus INT6 original-weight optimum-gap differences at each offset; **no sign is assumed**. Test paired difference-in-differences of solver-gap contrast for d=0.8 vs 0 and d=1.6 vs 0, without declaring an interaction merely from one significant format contrast and another non-significant one. Preserve multiplicity caveat (unadjusted per-cell 95% CIs).

## 2. Graph and scoring (do not open graph before freezing)

- Target only `t2g10_7777`, 10×10 weighted toroidal sparse Biq Mac instance, **N=100**.
- Published original-weight optimum: **6,509,837**, Biq Mac Library by Angelika Wiegele, Sep 2007, **Table 10, printed p.13**: https://biqmac.aau.at/biqmaclib.pdf . This value was verified from the published table **without opening the instance file**.
- Original distribution directory is https://biqmac.aau.at/library/mac/ising/ . Graph source URI fixed to `https://biqmac.aau.at/library/mac/ising/t2g10_7777` (not retrieved in this preparation).
- Target local path: `data/biqmac/raw/ising/t2g10_7777`.
- Structural source gate: exactly **100** vertices, expected **200 raw** undirected torus edge entries; no loops or parallel entries; require `len(edges)+zero_sum_edges==200`. Do **not** assume all raw weights are nonzero. If source fails a check, STOP and document; do not silently relax acceptance or overwrite frozen code.
- Record SHA256 of the original Rudy file on first authorized execution and bind it in `source_gate.json` and every `runs.csv` row; source gate must agree on resume. Do not invent a pre-access file SHA.
- Symmetric signed `J_ij=J_ji=-w_ij`, `J_ii=0`, no problem bias. Select earliest lowest *represented* Ising energy visited; score Max-Cut with the *original* edge weights. The original optimum must bound all returned cuts.

## 3. Frozen experiment grid: 216 independent solver evaluations

| Parameter | Frozen value |
|---|---|
| Graph | `t2g10_7777` only |
| Formats | `ref64`, `fp6` E3M2, `int6` signed; same existing global source-only MSE scaling/codebooks |
| Device response | E2 **assumed**, not measured: `gain_i=1`, `offset_i=d*v_i`, one persistent frozen population `v_i` from the existing CAL offset scout, paired across seeds/formats/levels |
| Halfspans | `d={0.0,0.8,1.6}` in **logit units**, not volts |
| Seeds | `BASE_SEED_FROZEN + 100000*3 + k`, `k=0,...,23` (base `20261201`; first `20561201`, last `20561224`) |
| Solver | Existing asynchronous Gibbs + incremental field updates; 50,000 attempted updates per run; original-graph beta, linear schedule from 0.5 to 2.0 times beta; do not retune |
| Output | one retained represented-energy incumbent; original-weight cut and optimum gap; full seed results and SHA/check metadata |
| Trials | `3 formats × 3 offsets × 24 seeds = 216` |
| Device-population replicates | **One** synthetic population (not a manufacturing or cross-device CI) |

Other precision widths, BFP variants, alternate temperature schedules, new gain levels and new benchmarks are **not** part of M6. No new CAL solvers.

## 4. Frozen quality screens and comparisons

For each format and offset, compute the mean optimum-gap percentage `100*(6509837 - returned_original_cut)/6509837` and a 95% 24-seed bootstrap CI. Separately compute same-seed additional gap against `ref64` at the same offset and its paired 95% CI.

**Eligible** if and only if BOTH CI upper bounds satisfy: (i) mean original-weight gap **≤5%**, and (ii) paired additional gap vs same-offset FP64 **≤+1 percentage point**. A non-certified condition is not evidence of equivalence or an established 7.5% failure regime.

Other frozen comparisons:
- Direct paired `fp6_gap - int6_gap` at each d, mean and 95% CI.
- Paired difference-in-differences: the per-seed direct gap contrast at d=0.8/1.6 minus that seed's contrast at d=0.
- Common-state 24 FP64-returned snapshots per d × 2 low-bit formats = **144 derived rows**, final beta multiplier 2.0; mean absolute `ΔH`, exact sigmoid mean absolute `ΔP`, paired low-bit differences and seed-bootstrap 95% CI. Static p-bit response differences are **not** actual diverging solver-trajectory error rates.
- Same M5 seed-bootstrap implementation and **4,000** replicates; preserve the documented deterministic bootstrap seed offsets from the runner. Confidence intervals are seed-conditional, not graph-population or device-population intervals.

## 5. Implementation, hashes and execution gate

- Isolated source: `experiments/m2_heldout_sparse_sixbit.py` on research branch. It was derived from the archived M5 runner but changes only graph identity/index, published optimum, expected sparse topology, distinct output directory/status, code-hash path, and synthetic/CAL smoke-test support. It preserves existing quantizer/solver/offset/CI imports.
- New output root: `results/m2_heldout_sparse_fp6_int6_20261110/`; never reuse or rewrite dense M5 files.
- Exact on-host source and dependency SHA256 hashes, full seed list and response-model hashes must be recorded by running **`--freeze` BEFORE `--execute`**. The script's self-test is synthetic; `--smoke-cal` uses **only** `t2g10_5555` (CAL) with 300 attempted steps per representation as a non-scientific integration smoke test.
- A successful GitHub script commit or this protocol document does **not** count as passing the host smoke test or executing/freezing the on-host protocol.
- Do not launch the full 216-run M6 until synthetic + CAL smoke gates pass, the frozen protocol file is inspected, and no graph content has been accessed beforehand.
- Check script's source SHA256 against the committed version before `--freeze`; do not edit the file after freezing without an explicit audit amendment.
- After full completion, verify 216 unique keys, hash match, 9 quality-summary rows, 6 contrast rows, 144 snapshot rows, 6 snapshot-summary rows, manifest and no zero-byte files; then publish conclusions regardless of sign.

### Intended host-side commands (NOT executed by this document)

```bash
cd "$HOME/MRAM_Pbit_M0" || exit 1
git fetch origin
git switch research/m4-gain-fusion-20261107
git pull --ff-only

python3 -m experiments.m2_heldout_sparse_sixbit --selftest
python3 -m experiments.m2_heldout_sparse_sixbit --smoke-cal

# Only after the two tests PASS, and BEFORE source graph is accessed:
python3 -m experiments.m2_heldout_sparse_sixbit --freeze
cat results/m2_heldout_sparse_fp6_int6_20261110/protocol.json

# Separate explicit execution step AFTER protocol review, not yet run:
# python3 -m experiments.m2_heldout_sparse_sixbit --execute
```

## 6. Next stage is NOT part of this freeze

Do not start the width extension until M6 sparse results and provenance are closed. A *later separately frozen* **width-E2** study may reuse already-viewed dense M5 d=0.8 and add FP8 + INT8 × 24 seeds = **48 new solver runs**. The proposed FP6 vs INT8 two-bit payload saving is **conditional** on INT8 passing both quality screens and is not a demonstrated hardware-area saving. A matched INT8 mapped datapath is needed for a format-level logic-area comparison. Do not conflate the proposed width-E2 experiment label with **E2 assumed p-bit device-response evidence**.

## 7. M5 reference, status and boundaries

Dense M5 evidence archive: https://github.com/Makise-okabe/MRAM_P-bit/commit/755e4199f4542088b1dfc59f6bcb1e668d54f0a4

Dense M5 conclusion: complete on the dense graph; FP6 certified the two screening criteria at d=0/0.8 but not d=1.6. Direct FP6-versus-INT6 gap CI at d=1.6 and both format-by-offset interactions were inconclusive. Do not interpret zero-crossing CIs as equivalence. Keep CAL source-CI import and gain-data recovery in their separate workstreams.

**Change control:** If a preflight check fails, patch and re-smoke-test **before** the on-host freeze; if a failure occurs after freeze, write an explicit amendment and re-evaluate affected scientific invariants. Never choose a new graph, scale or stress level to manufacture a desired result.
