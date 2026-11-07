# M3 matched 6-bit FP/INT/BFP row — FIRST verified component result (7 Nov 2026)

## Decision and FYP relevance

**GO** floating-point coupling research, **GO** matched hardware cost analysis, **NO** FP format superiority claim. The frozen FYP is low-order symmetric `J_ij` representation for original Biq Mac Mac weighted Max-Cut, not fitting STT-MTJ noise models. This experiment tests whether the **per-element FP6 exponent/mantissa representation costs more combinational logic than 6-bit INT/BFP** when all three drive an integer local-field accumulator; it does **not** test a complete accelerator.

## Verified artifact and scope

- Commit under research branch: code `rtl/m3_local_field_row.v`, encoder `experiments/m3_sixbit_encoding.py`, tests `tests/test_m3_sixbit_encoding.py`, HDL bench `rtl/tb_m3_row.v`, CI `.github/workflows/m3-row.yml`.
- [GitHub Actions successful run 42352449618](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/42352449618) at commit `5b5852baaf3cc7e2b0af37b907d0b90228dd9a5a`; all Python codebook/row checks, three separate Icarus clocked 99-term vector simulations, and three individual Yosys generic synthesis jobs passed. Artifact `m3-sixbit-row-generic-yosys`, artifact id `13566435506`, contains three raw logs and Yosys version. These logs were downloaded and examined.
- Single row streams one 6-bit coefficient and spin sign per cycle, reset/clear and valid; 99 off-diagonal terms for 100-spin workload, `h=0`. The codebook and scale conventions are frozen in `docs/M3_FP6_INT6_BFP6_ROW_COMPARISON_20261107.md`. FPGA/Icarus simulation tests functional bit-true integer output, not silicon timing or pulse response.
- All three formats use **different fixed compile-time top modules** and the *same* synthesis command `read_verilog; synth -top <module>; stat`, Yosys **0.33** (git sha1 `2584903a060`). The 6-bit stored coupling is decoded, then accumulated as integer; FP is not removed by this implementation choice.

## Observed generic Yosys synthesis counts — 99 terms, one row

| Format | accumulator width | total flattened generic cell count | sequential $_DFFE_PN0P_ cells | HDL vectors |
|---|---:|---:|---:|---|
| FP6 E3M2 finite | 17 bits | **274** | **17** | PASS 99/99 |
| INT6 symmetric | 13 bits | **138** | **13** | PASS 99/99 |
| BFP6 symmetric mantissa | 13 bits | **138** | **13** | PASS 99/99 |

FP6 yields **274/138 ≈ 1.99×** generic cell count *for this narrow row core*. This includes FP sign/exponent/mantissa decoding and wider accumulating logic; INT and BFP rows are equal because their mantissas/row cores are bit-identical. The 1.99× is **NOT** a technology-mapped silicon area ratio, **NOT** power ratio, and **NOT** the ratio for complete p-bit Max-Cut cost. Synthesis flow/library and architecture may affect ordering. There are **zero memory bits** and **zero coefficient-scale multipliers** in these tops.

## Compare against existing *ideal-model* original-cut quality — CAL only

These are the already documented NUS 936-run **E1** results, *not* new RTL Max-Cut end-to-end measurements:

| Original Biq Mac calibration graph | FP6 mean optimum gap | INT6 mean optimum gap | BFP6 mean optimum gap |
|---|---:|---:|---:|
| `w01_100.0` (small integer control) | 0.9089% | **0.7744%** | **0.7744%** |
| `t2g10_5555` (wide sparse) | 3.6097% | 3.3231% | **3.1913%** |
| `ising2.5-100_5555` (wide dense) | **4.1369%** | 4.4665% | 4.8365% |

The FP6 dense-graph point estimate improves the INT6 mean by 0.3296 percentage points, **but no paired FP6-vs-INT6 significance test or across-independent-graphs proof has been established**. Two other CAL graphs prefer INT6 on mean original gap. FP6 is not a general winner from these results.

This row result and E1 table together identify a meaningful quality–logic-cost tension. However adding a software gap to a generic-gate count does **NOT** create a Pareto proof of whole-system energy/time/area. The same 6-bit payload is 29,700 one-copy undirected coefficient bits for a 100-spin dense adjacency model; 32-bit FP/INT global scale and 8-bit BFP exponent are separate metadata, before actual RAM and data movement costs.

## Evidence boundaries

**Verified:** bit-level codepoint mapping to the specified source-only M1 codebook; deterministic integer accumulator sums for a streaming row; standard open-source generic synthesis counts under exactly one architecture/tool flow.

**Unverified:** actual graph-specific encoded memory image fed through row plus global scaling/voltage; memory access count and energy, global scale application, full graph scheduling/parallelism, represented-energy selection, p-bit pulse/circuit interface, overall time-to-original-cut target, physical area/timing, independent held-out graph behavior. This is a **component-level digital result**, not a Max-Cut hardware accelerator, even though the signed coefficient encoding is Max-Cut compatible.

## Required next discriminating experiment

1. **Small and mandatory correctness bridge:** use one actual original Biq Mac CAL graph with SHA-verified source and M1 source-MSE representation; encode each distinct `J_ij` once, replay at least one 99-term local-field row and chosen spin vector through integer hardware/oracle, then multiply by the *correct global scale* and compare to frozen `sum(Jhat_ij*s_j)`. This guards against codebook mismatch between current gate-level test vectors and actual graph inputs. Stop on any mismatch.
2. **Cost completion:** measure full-format global scale/interface arithmetic and metadata/memory access in the same architecture; later use a common authorized std-cell library/constraints for actual area/timing. A 6-bit row-core alone cannot decide FP viability.
3. **Generality:** evaluate independent held-out Biq Mac original graphs at an explicitly frozen quality threshold, with graph-level uncertainty. Only after correct format / hardware alignment, optionally revisit E2/E3 device response.

## Five-question decision feedback

- **Target:** Is FP6 row logic cheaper/enough relative to matched INT6/BFP6 to justify its stored-number representation? Narrow answer: FP6 row is larger under this flow.
- **Evidence:** E1 software CAL plus new verified generic RTL component. No measured physical/dynamic energy.
- **Hypothesis:** quality gain on some weight distributions could justify extra FP decoding logic; not assumed or established.
- **Minimum test:** one 99-term matched clocked RTL vector test per format + same generic synth flow, no new solver runs or device assumptions. **COMPLETE**.
- **Stop/novelty:** do not claim FP wins from dense graph; do not treat generic gates as area or energy; bit-width-vs-resource comparisons are prior art, and a distinctive end-to-end **format–quality–cost design rule** remains unverified. **GO** next only to graph-to-RTL integrity bridge then fully costed comparison. No need to repeat or expand E2 noise runs.
