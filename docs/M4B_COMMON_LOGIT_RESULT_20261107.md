# M4B common digital-logit interface — measured result, 7 Nov 2026

**FYP:** FP6 E3M2 coefficient storage versus matched INT6/BFP6 for original Biq Mac weighted Max-Cut, no device-noise retune.

**Verified GitHub Actions:** [#42358409802](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/42358409802), completed success at commit 2ca6774fda9c3cc62f32dac5cde76d9c10b07a40. Artifact m4b-common-logit-official-graph-sky130 (ID 13568264185). An earlier failed CI attempt was caused by filename variable expansion; it was corrected in the successful run.

## Gate A: numerical and clocked RTL

Candidate contract: positive signed 32-bit Q4.28 external folded gain, exact integer multiplication with the unchanged M3 accumulator, ties-to-even rounding to signed 18-bit Q6.12, saturation at ±12, valid one additional clock after the 99th term.

- Four new Python tests plus existing M3 and M4A regression tests PASS.
- Official original SHA-verified sources: w01_100.0, t2g10_5555, ising2.5-100_5555.
- **27/27** clocked Icarus cases PASS: three graphs x three formats x three beta schedule points; each case checks every one of 99 coefficient/spin accumulator prefixes and final Q6.12 logit.
- **2,673** Python prefix probability comparisons versus ideal represented-field sigmoid(2 beta H) pass the candidate 2.5e-4 absolute-error screen.
- Maximum observed absolute probability differences:
  - w01_100.0: **2.8999986e-05**
  - t2g10_5555: **2.8113431e-05**
  - ising2.5-100_5555: **1.8826462e-05**

These are deterministic row/anneal-point numerical tests, not end-to-end 50,000-step Max-Cut solver preservation, representative graph-population evidence or p-bit measurements.

## Gate B: same Sky130HD mapped standard-cell area, no timing

Same pinned SHA-checked Sky130HD tt_025C_1v80 filtered Liberty and matched Yosys flow as M3.

| Format | Previous M3 row-only area (µm²) | New M4B row+gain-register+digital-multiply+RNE+saturation mapped area (µm²) | M4B mapped cells |
|---|---:|---:|---:|
| FP6 | 1438.8800 | **23481.2704** | **3227** |
| INT6 | 929.6416 | **18061.0720** | **2445** |
| BFP6 | 929.6416 | **18061.0720** | **2445** |

**For this specific non-optimized common digital interface:** FP6/INT6 area ratio ≈ **1.30×** and absolute difference ≈ **5420.1984 µm²**. The multiplier dominates, so this is NOT an optimized lower bound for any format; BFP6 could exploit power-of-two scaling in an alternative implementation. The two separately synthesized M3/M4B tops must not be subtracted as exact isolated cell-block area. No STA, power, physical placement/routing or GF22FDX area.

## Cost limitations and research decision

The external 32-bit gain stream is supplied from outside the block. Only its local register and digital multiplier are costed, not gain-generation/annealing schedule, graph state controller, coefficient SRAM, row scheduling/addressing, spin-retention, sigmoid/DAC, p-bit circuit or system energy. For this explicit serial full recomputation architecture, 50,000 attempted updates imply 4,950,000 coefficient issue slots; this **does not equal** the cost or timing of the original M1 Python Gibbs solver, which maintains incremental cached local fields.

**Next:** document consistent three-format cost table with architecture exclusions, then promptly test independent held-out original Max-Cut graphs and graph-level paired uncertainty. FP6 remains the research subject, not a presupposed winner.

## Reproduce NUS

~~~bash
cd "$HOME/MRAM_P-bit"
git fetch origin
git switch research/m4-gain-fusion-20261107
git pull --ff-only
bash scripts/m4b_run_nus.sh
RUN_SKY130=1 bash scripts/m4b_run_nus.sh
~~~
