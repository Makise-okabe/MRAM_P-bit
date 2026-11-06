# Bounded E1 evaluation sequence — 7 November 2026 (NOT a direction reset)

Supervisor-selected direction unchanged: STT-MRAM p-bit coupling precision on **original Biq Mac / Mac weighted Max-Cut**. MIMO archived. No new physical or Max-Cut-specific ASIC results claimed.

## Evidence already completed
- M0/E0: 10/10 source/hash/Ising-math checks on NUS.
- E1: initial 84-run 4-graph/3-seed ideal-Gibbs pilot. Historical code `1f6839f` had an INT6 small-integer MSE-scale search fairness issue, fixed afterwards. Original result preserved.
- 24-seed corrected 6-bit rerun: pending/unreported. If already underway, finish and compare source-hash-aligned seeds. Do not repeat it just to obtain a new report format.
- The official Biq Mac 2007 PDF publishes original-weight Max-Cut optima for all ten source-audited graph files. Curated table/page/hash-linked values in `docs/BIQMAC_OFFICIAL_OPTIMA_2007.json`. Validate raw-file SHA256 before using a reference value. PDF: https://biqmac.aau.at/biqmaclib.pdf, Tables 7–10 (printed pp. 10–13).

## Next bounded gate: check *unquantized* solver operating point once
`scripts/m1_biqmac_reference_quality_smoke.sh` uses four original calibration graphs:
`w01_100.0`, `pw01_100.0`, `t2g10_5555`, `ising2.5-100_5555`.
Run **six paired seeds**, update counts **5k, 20k, 50k**, two mathematical ideal Gibbs profiles: `fixed` beta_G and `linear` beta(t) ramping from 0.5*beta_G to 2*beta_G.
Original-weight Cut is the returned-state external evaluation; retaining a state uses the lowest represented energy only. Fit no formats or response parameters here. Six seeds are nested within **four** graph instances; the four are already observed calibration data, not held-out.

For each graph, the official original-weight optimum permits a legitimate nonnegative gap `C* - C_returned` and normalised gap percent `100*(C* - C_returned)/C*` (all chosen C* > 0). The unquantized solver is a finite-budget baseline, not a proof of global optimum. Prior 3-seed mean optimum ratios were ~87.2%, 95.1%, 85.7%, 93.6% for w01,pw01,t2g10,ising2.5, respectively. This makes a bounded quality-vs-budget check worthwhile, but **does not require** hitting within 1% of optimality.

**Preregistered operating-point choice:** Average mean normalised optimum gap across the four CALIBRATION graphs (one graph one vote). Find the minimum gap among six budget/schedule combinations. Select the **smallest budget within 1.0 absolute percentage point** of that minimum; for budget ties prefer fixed schedule as simpler control. This 1pp is a cost/quality plateau *selection tolerance*, not a requirement for optimum quality. Store recommendation and per-graph/seed uncertainty; freeze the selected schedule and attempted-update budget **before** running multi-format comparisons. A graph with negative/signed edge weights still has its published **positive** Max-Cut optimum, so the normalized metric is well-defined for these ten specific cases. Never retune using held-out `.5`-`.9` or `_7777` graphs.

## After reference quality: compact precision sweep
**Proposed bits (not implemented/tested yet):** b in {4,5,6,8}, with explicit signed codebooks:
- FP4 finite E2M1; FP5 finite E2M2 (primary fixed candidate); FP6 finite E3M2; FP8 finite E4M3.
- Signed INT4/5/6/8, symmetric [-((1<<(b-1))-1), +(same)] and common source-only scale.
- BFP4/5/6/8 with b-bit signed mantissa and one shared power-of-two exponent per *undirected-edge* group (global grouping first); any tile-pair grouping later must use one and the same quantized J_ij for both directions, preserving symmetry.
These planned FP5/FP8 variants require explicit coding/bit-true tests, and the present `fp8` codebook does not automatically implement finite-only FP8. Never silently conflate or compare incompatible scale encodings or report E5 area for a different format (e.g., older FP4-J with FP6-h when evaluating FP6-J).

Calibrate coupling scales from source coefficients only and charge the same type of metadata, rounding/saturation semantics, memory access and control costs. Strongest practical source-only INT/BFP scales must be included. Run matched seeds, budget and schedule from FP64 CALIBRATION, using original weighted Cut/official reference gap. Show per-graph and across-independent-graph outcomes; repeated seeds reduce Monte Carlo noise within a graph but do not create independent graph samples. The two wide-range `_5555` graphs are primary **calibration stress cases** and the small-integer control is necessary, but there are far too few wide-range independent graphs to claim a general knee.

## Response distortion and hardware gates
Once an ideal precision profile is available, repeat with **physically supported** STT-MRAM low-barrier p-bit gain/offset/time-correlation models, including persistent device identity. E2 illustrative response ≠ E3 validated p-bit curve ≠ E4 transistor simulation. Do this even if ideal FP does not beat INT: research question is interaction with physical response.

Use reusable historical M2 RTL as component starting point only. Native Max-Cut has h=0; implement actual selected FP/INT/BFP *J* width and metadata, verify a row + best-state retention, then compare preplacement area/timing, coefficient storage, memory-access energy proxies, p-bit and interface costs. A bias-inclusive MIMO FP4-J row is not the area of an FP6-J Max-Cut solution.

## Order; no extra prerequisites
1. If corrected 24-seed 6-bit pilot is running, finish its immutable output. Otherwise, do not needlessly rerun before solver quality gate.
2. Run one bounded reference-only quality-vs-budget gate, freeze the CAL operating point and archive its evidence.
3. Implement and test precisely one 4/5/6/8-bit sweep.
4. Repeat it under a defensible stochastic p-bit response model.
5. Evaluate full hardware cost only for configurations relevant to achieved cut quality; use independent held-out graphs for final inference.

**Scientific end-point:** Which coupling format reaches a specified original-weight Max-Cut solution-quality target at minimum comprehensive cost under a documented p-bit response? It is acceptable if INT/BFP wins. A bit-width knee alone has prior art in other Ising technologies; device-aware hardware tradeoff is the candidate novelty, still unproven.
