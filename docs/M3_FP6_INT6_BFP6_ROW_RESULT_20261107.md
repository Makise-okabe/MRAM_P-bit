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

## Next gate implementation status (same date)

The **source-to-RTL bridge is now authored** in `experiments/m3_actual_graph_row_vectors.py`. It accepts **only** one of the three frozen original Biq Mac CAL graphs, verifies the official source SHA256 and published optimum entry, reconstructs frozen M1 source-only `build_global` coefficient representations, encodes every off-diagonal term (including implicit zeros), and writes three 99-term Icarus-consumable vector files with exact expected cumulative integer sums. For each format it independently verifies that the represented local field computed from floating M1 `Jhat` agrees with decoded integer sum times the appropriate global scale, then records a source-linked `manifest.json`.

[GitHub Actions run 42352795556](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/42352795556) **PASS** on graph-bridge syntax plus existing tests. The **NUS original graph-to-RTL execution is NOT RUN**, as original source files do not exist in the active GitHub worktree. It is not a substitute for a graph-to-row hardware test result.

On NUS, after switching to the updated branch and from the repository root (example using the already frozen dense original graph):

```bash
python3 -m experiments.m3_actual_graph_row_vectors \
  --graph data/biqmac/raw/ising/ising2.5-100_5555 \
  --out results/m3_dense_row0_20261107
# If iverilog/vvp are installed:
for fmt in fp int bfp; do
  case "$fmt" in fp) idx=0;; int) idx=1;; bfp) idx=2;; esac
  iverilog -g2012 -s tb_m3_row -Ptb_m3_row.FORMAT="$idx" \
    -o "/tmp/m3_${fmt}6" rtl/m3_local_field_row.v rtl/tb_m3_row.v
  vvp "/tmp/m3_${fmt}6" +VEC="results/m3_dense_row0_20261107/m3_${fmt}6_vectors.txt"
done
```

**Decision:** software+synthetic RTL component gate PASS, source integrity bridge authored/syntax PASS, original-graph input gate PENDING, full FPGA/ASIC/system costs PENDING. FP direction remains unchanged.

## Scientific closure — original-source-to-RTL plus common Sky130 mapping (7 Nov 2026)

### Gate A: OFFICIAL graph-to-row equivalence: **PASS**

[GitHub Actions 42353562894](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/42353562894) downloaded the *unmodified* official 100-spin Biq Mac CAL graphs, checked their source-file SHA256 against the frozen original-optimum JSON, constructed per-format M1 source-MSE global representations, encoded all 99 off-diagonal terms from row 0, and checked 9 clocked Icarus executions (3 graphs × 3 formats) against step-by-step integer accumulators. All nine passed. Artifacts: `m3-official-BiqMac-row-bridge` (GitHub Actions artifact id `13567155228`). This proves **one row and one fixed spin vector per graph**, not a 100-row system test or full Max-Cut solver RTL.

Observed row-0 local fields after decoding and applying the correctly frozen **external** global scale, from official source-linked manifests:

| Graph (one fixed spin sample) | FP6 H | INT6 H | BFP6 H |
|---|---:|---:|---:|
| `w01_100.0` | -5.7336772084 | -5.0000000000 | -5.0000000000 |
| `t2g10_5555` | -461173.6191406250 | -465564.8388671875 | -466944.0000000000 |
| `ising2.5-100_5555` | -28196.3177490234 | -30935.7421875000 | -24576.0000000000 |

Every displayed `H` was identical between the frozen M1 represented `Jhat` oracle and the raw-bit integer-accumulator plus global-scale reconstruction (absolute difference **0.0** for all 9), in this single deterministic state. These differences *across formats* are expected numerical quantization differences, NOT accuracy superiority, Max-Cut solution quality or device effects. Source hashes match frozen records `3800aa7c...`, `c742b78e...`, `c8fa3ce4...` respectively.

### Gate B: tech-library-mapped row CORE cell area: **PASS, preliminary scope only**

[GitHub Actions 42354259889](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/42354259889) passed one matched open Sky130 HD 130nm typical 25°C/1.8V Yosys 0.33 technology-mapping flow for all three fixed format tops. The source Liberty was pinned to OpenROAD-flow-scripts commit `aef47dd6ed123b0ed7cedac372b00456722be327`, original SHA256 `ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9`. A reproducible filtered Liberty `cd8abb502b47e96b31b0f179b8f16c34fd2f027c3cc4c7e0dbdbadc71030367b` omitted 39 multi-power/clock-only cells, leaving 389 of 428 original cells, because Ubuntu Yosys 0.33 lacks `-dont_use` support in ABC/dfflibmap. Filter process is saved in `scripts/m3_filter_sky130_liberty.py`; the comparison rejects those excluded cells in mapped netlists. The earlier unfiltered synthesis counts/area are **superseded**, not suitable for reported normal digital row cost.

| Row variant (99 coefficient terms, serial) | Std-cell instances | Flip-flops | Standard-cell area from Liberty |
|---|---:|---:|---:|
| FP6 finite E3M2 | **171** | **17** | **1438.8800 µm²** |
| INT6 symmetric | 107 | 13 | **929.6416 µm²** |
| BFP6 global exponent, integer mantissa row | 107 | 13 | **929.6416 µm²** |

Under this *specific row-only architecture and library mapping*, FP6 requires `1438.88 / 929.6416 = ~1.55×` the cell area of INT6/BFP6, ~509.24 µm² extra. INT6 and BFP6 rows map identically **only because external BFP scale handling is outside the row**. This is an important quantitative **FP cost penalty** rather than a whole-machine FP failure.

**Not yet represented:** FP/INT floating-scale and BFP power-of-two metadata/transfer, scheduling beta(t), voltage/logit interface, coefficient RAM banking/ports/access energy, pulse/reset/perturb and any STT-MTJ circuit, graph/energy retention, retries-to-target, placement/utilisation, post-route timing, total dynamic energy or power. Source-to-row test is functionality; mapped area is technology-library logic area, neither physical implementation nor energy. Yosys observed unsupported Liberty expressions in several unused scan cells; final mapped netlists do not use excluded isolation cells. No STA/critical-path report was produced.

### Cost and scheduling baseline

All three formats have six physical coefficient payload bits. For a dense 100-spin graph, one copy of undirected coefficients requires `100*99/2*6 = 29,700` bits before scale metadata (FP6/INT6: 32-bit global binary32 scale, BFP6: 8-bit signed global exponent); a row-addressable mirrored dense matrix could require more. A serial 99-term row sampled on each of the frozen 50,000 attempted updates requires at least `99*50,000 = 4,950,000` coefficient issue slots in that *explicit* naïve implementation. This is an architectural operation count **only**, not measured time/energy or necessary for a more parallel/updated-field design. Sparse-row skipping, row-memory organization and read ports must be specified and costed rather than assumed free.

### Final GO/STOP after two verified gates

- **Target:** test whether numerical FP6 `J` storage can be implemented faithfully and quantify its standalone local-field row arithmetic price: **YES, accomplished on three original CAL graphs for one row; YES, area penalty measured in one open library.**
- **Hypothesis/expected observable:** FP6 may preserve some wide-dynamic-range Max-Cut quality while paying more decode/accumulator cost. The result supports *hardware penalty*, not an unconditional quality benefit.
- **Evidence:** original source SHA256 verified; 9/9 clocked original-weight tests; technology-library mapped cell area (not GF22FDX nor complete p-bit).
- **Closest novelty risk:** coefficient precision/resource tradeoffs in Ising/p-computers are prior art. The unique conditional full-cost original-weight Max-Cut selection rule is **not yet established**.
- **Failure/STOP:** do not assert that 1.55× is a full-ASIC area or energy ratio; don't infer general FP win from the single dense E1 graph.
- **Next smallest discriminating question:** when scale/interface costs and coefficient memory access are included with the same frozen update schedule, does the **component-relative** row penalty materially change whole-solution cost or is it amortized? Freeze a single row-streaming memory/interface architecture and **common logit precision** before cost comparison. Then independent held-out graph quality; E2 response remains parked.
- **Decision: GO to full-scale/interface + memory-cost closure, keep FP as primary FYP object.** No solver retune, no new benchmark, no invented device residuals.
