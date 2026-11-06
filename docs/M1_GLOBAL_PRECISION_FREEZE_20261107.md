# Frozen first global-scale precision-quality experiment — 7 November 2026

**Research scope unchanged:** Biq Mac Library **Mac weighted Max-Cut**. This E1 sweep studies encoding versus original-cut solution quality under the frozen mathematical **ideal Gibbs** operating point. It is not STT-MRAM physics or an end-to-end ASIC study.

## Precommitted experiment before any four-bit/eight-bit results

| Axis | Frozen choice |
|---|---|
| Source graphs | Three *already observed calibration* 100-vertex original Mac graphs: signed integer `w01_100.0` (control), sparse wide-range `t2g10_5555`, dense wide-range `ising2.5-100_5555` |
| Solver | Asynchronous Gibbs with original graph derived `beta_G` and linear `beta(t)=beta_G*(0.5+1.5*t/(50000-1))` |
| Budget | **50,000 attempted** single-spin proposals per run; do not change by format or bit width |
| Seeds | **24 NEW paired seeds**: `20261201 + graph_index*100000 + k`, `k=0..23`; FP64 itself is rerun using precisely those seeds; distinct from previous 20261107 calibration stream |
| Configs | `ref64` plus four widths of each FP, INT and BFP = **13 configs per graph**, **936** total candidate/reference runs |
| Coupling | **J=-w, h=0**, each original undirected edge encoded ONCE then mirrored identically: `J_ij=J_ji` |
| Runtime output | Earliest lowest-**represented-energy** visited state; exact unquantized graph weights are NOT consulted for output selection |
| External evaluation | Returned *original-weight* cut, source-hash-matched **published optimum** `C*`, gap `100*(C*-C_returned)/C*` |
| Calibration rule | Source coefficients **only**, one global shared scale per entire graph, frozen `source_mse_loggrid_v1`; NO solution quality, optimum or held-out graph used to select scale |
| CI | Seed-level *paired additional gap* relative to same-seed FP64. Deterministic percentile bootstrap, 4,000 resamples, 95% per-graph intervals; these do NOT estimate across independent graphs |
| Useful precision | Predefine **+1.0 percentage-point permissible additional gap** relative to paired FP64; preliminary within-graph pass ONLY if upper 95% paired CI endpoint <= +1.0 pp. A point estimate within 1 pp alone is not enough. No multiplicity-adjusted global equivalence claim. |
| Cost proxy | `n(n-1)/2*b + metadata` nominal one-copy dense coupling bits: 32 metadata bits for INT/FP global binary32 scale, 8 bits for BFP signed exponent. NOT energy, transistor area, SRAM accesses, p-bit number, timing or scheduling cost. |

**FP codebook:** all four custom *finite-only* sign/exponent/mantissa layouts: FP4 E2M1; FP5 E2M2; FP6 E3M2; FP8 E4M3. Exponent=0 provides zero and subnormal fractions, exponents 1 through `2^e-1` are finite normal values **including all-ones exponent**. No infinity or NaN; signed negative zero is not used in this mathematical encoding. Magnitudes round to nearest representable level (exact ties-to-even by positive code index) and saturate at finite maximum. These are declared **custom formats**, not a promise of IEEE FP8 or full OCP MX fidelity.

**INT:** at b bits use symmetric `[-(2^(b-1)-1), +(2^(b-1)-1)]`, reserved minimum-negative code, nearest-integer ties-to-even, saturating maximum magnitude. A global **binary32** positive scale. Every width 4/5/6/8 explicitly includes unit scale `1.0` in the source-MSE candidate set when the original nonzero coefficients are integers within the signed range; therefore small integer `w01` must produce EXACT identical edges and per-seed state returns for INT5, INT6 and INT8 relative to ref64.

**BFP:** at b bits uses the exact same signed symmetric mantissa integer codebook as INT, but a **single power-of-two** scale `2^k` with one signed 8-bit exponent `k` for the complete undirected edge set. This is **GLOBAL-BFP**, not row/tile/shared-block reoptimization. Different source graph coefficient densities and weight distributions may change the selected exponent without any task-label oracle.

**Scale search:** FP/INT candidate global scales `binary32(fullscale * 2^(k/16))`, integer `k=-48..32`, plus fullscale and (for exactly fitting small INT) unit scale; choose candidate of minimum source coefficient MSE (ties: L1, then smaller scale). FP fullscale is from maximum original absolute J and finite format max; INT from max/(2^(b-1)-1). BFP tests integer powers of two from fullscale `k0-12..k0+8` within 8-bit exponent range. Binary32 global-scale quantization and all codebook semantics are frozen in `experiments/m1_precision_codebooks.py`. This limited grid is source-only but NOT a proof of mathematically globally optimum scaling; stronger calibration or tile-scale competition remains a subsequent gate. Global scale metadata is nominally counted, but arithmetic remains Python float64.

## Output

`bash scripts/m1_biqmac_precision_sweep.sh` first runs 10 synthetic unit tests, then official-source experiment on NUS, creating a new `results/m1_precision_global_...` directory (never overwrite prior E1). Output:

- `precision_paired_runs.csv`: 936 per-seed actual original-cut results, encoded format, scale, flips, best-visited-state and published-optimum gap.
- `precision_summary.csv`: graph and bit-level means, paired FP64 additional gap, seed bootstrap interval, source L1 and erased weight mass, provisional +1.0 pp gate, one-copy bit proxy.
- `plots/gap_vs_bits_*.svg`: exactly three distinct independent graph panels with actual original-cut optimum gap versus b and the **paired** CI whiskers translated to the FP64 reference mean; FP64 baseline and +1.0pp threshold lines.
- `manifest.json`: frozen codebook definitions, source SHA256, reference JSON SHA256, seeds, schedule, update count, files' code SHA256 and evidence qualifications.

**Experimental status when written: authored and requires NUS execution.** Unit/CI tests check synthetic codebook invariants only. Do not invent any precision knee, stochastic MTJ robustness or hardware-cost minimum. Report a nonmonotone curve as observed; do not force it into a knee interpretation.

## Stopping rule and next gates

This is one predetermined *calibration stress plot*, not a held-out statistical result. Whether FP wins or loses, next evaluate response-dependent curves with sourced, differentiated device transfer/noise parameters (E2 illustrative vs E3 validated). A final format superiority claim requires independent held-out graph instances, graph-level uncertainty, symmetry-preserving tile-scale/INT baselines, and mapped Max-Cut-specific h=0 coupling arithmetic with full storage/access, response-interface and annealing schedule costs. A six-bit MIMO row area cannot represent a six-bit Max-Cut coupling datapath.
