# M3 FP6/INT6/BFP6 matched local-field row — frozen component comparison (7 Nov 2026)

**Core FYP target (GO):** original Biq Mac Mac weighted Max-Cut, low-order **coupling representation J_ij** (not device noise), comparing FINITE FP6 E3M2 against source-only calibrated symmetric INT6 and GLOBAL BFP6. Determine when FP storage preserves sufficient **original-cut** quality at lowest end-to-end hardware / whole-solution cost. The user's 936-run E1 study is complete and is **not** being repeated here; no new stochastic response or beta tuning.

## Important discovery and scope decision

The **active** `MRAM_P-bit` research worktree contains Python codebooks and the solver but **no existing Verilog/SystemVerilog local-field row files**. The renamed old repository history and the separately accessible report repository did not reveal an inspectable row RTL. The previously mentioned hardware row cannot be assumed to have the correct codebook/sign/scale and is not yet reusable evidence. Rather than claim an unseen legacy row has been adapted, M3 adds one minimal **independent RTL baseline** for a *streaming local-field row* in `rtl/m3_local_field_row.v`, with parameter-selected FORMAT fixed at synthesis. If the original older RTL is recovered, compare against this reference later.

The row processes one non-diagonal 6-bit coefficient and corresponding spin per clock using an integer accumulator. This **retains floating-point as the stored coupling representation**: the FP6 row performs exponent/mantissa decode and sign accumulation, but not floating-point addition. All three formats use the same clear/valid/clock protocol and the same 99 terms for 100 original spins. Only raw `J_ij\cdot s_j` sums are calculated, with NO Max-Cut bias `h=0`.

## Bit-true frozen representation and scale conventions

| Format | 6-bit stored coefficient | Per-edge decoded integer | Final represented local field | Row max absolute integer (99 terms) | Signed accumulator |
|---|---|---|---|---:|---:|
| FP6 | sign 1 + exponent 3 + mantissa 2; custom finite-only E3M2, including exponent 111 as FINITE | `q4 = sign * (frac if exp=0 else ((4+frac)<<(exp-1)))`, max ±448 | `H = q4_sum * global_f32_scale / 16` | 44352 | 17 bits |
| INT6 | symmetric signed 6-bit two's-complement, -32 reserved | signed integer in [-31,+31] | `H = int_sum * global_f32_scale` | 3069 | 13 bits |
| BFP6 | same six-bit signed mantissa as INT6 | signed integer in [-31,+31] | `H = int_sum * 2**global_8bit_exponent` | 3069 | 13 bits |

FP6 exp=0 has zero/subnormal values `frac/16`; exponent=1..7 uses finite normal values. Maximum FP6 magnitude is 28 * global scale (28*16=448). Negative zero is interpreted as zero. The exact integer output and shared scale reproduce frozen M1 `scalar_quantize` values after global-scale application; all 64 FP bit patterns are exhaustively checked.

For global source-MSE scale `S`, coefficients are codebook values *times* `S`; `S` is **one 32-bit value** for INT/FP and one **signed 8-bit shared exponent** for BFP. Scalar scale application and beta modulation at the p-bit interface are not inside the row. These omissions must be explicitly charged in an end-to-end cost comparison. Unlike an unjustified "FP6 adder must be used" assumption, a common fixed/integer accumulator is legal after decoding FP coefficients.

## Fair digital component evaluation

- Same `MAX_TERMS=99`, clock protocol, one coefficient/spin pair per cycle, control reset/clear; compile-time FORMAT=0/1/2, not a runtime three-way multiplexer.
- Use bit-true encoder `experiments/m3_sixbit_encoding.py`, which rejects values not already on the frozen M1 six-bit codebook. No repruning, scale retuning, or data-source modification.
- `tests/test_m3_sixbit_encoding.py` exhaustively checks all signed FP6 codes, all legal integer codes, the reserved -32, M1 codebook round trips, and complete 99-term software row sums.
- `rtl/tb_m3_row.v` checks every one of 99 cumulative sums of each format against deterministic independent Python reference-vector files.
- `.github/workflows/m3-row.yml` runs Python tests, Icarus HDL simulation, then an identical **generic Yosys** synthesis flow for all three separately elaborated tops; archives logs as a CI artifact.
- **Do not call generic Yosys gate counts actual GF22FDX area or timing**. This is component RTL/functional evidence and an exploratory logic-complexity proxy, not technology-mapped E5 area, post-route parasitics or system energy.

## What the row does NOT cover

1. Original symmetric `J` coefficient memory, address/data movement, source-MSE scale metadata storage and load.
2. Each format's realistic shared-scale decoding/application, beta schedule and logit/voltage/DAC conversion; BFP has cheap power-of-two scaling but potentially different interface cost.
3. p-bit response, pulse reset/perturb time and energy, total parallelism/row sharing, graph-state registers, controller, annealing update scheduling.
4. Represented-energy best-state retention, retry-to-target quality/time/energy and whole-system area/timing.
5. Physical characterization or E2/E3 response-dependent Max-Cut solution quality, independent held-out graph validation.

The **research main question** is still whether FP improves original Max-Cut quality at matched *total* cost, not whether the FP6 row alone has fewer gates than INT6. At 6 bits the coefficient payload is equal (dense one-copy 100-spin storage: `4950*6=29700` bits; plus 32-bit FP/INT or 8-bit BFP global metadata before real memory overhead). FP could be valuable if less precision achieves matched quality on independent graph families, not automatically at matched nominal bits.

## Next discriminating gate and STOP rule

**Gate A (bit-true row):** verify Python M1 codebook ↔ stored bit pattern ↔ clocked RTL local-field equality. STOP claims of functional hardware readiness if any regression/vector mismatch occurs. PASS licenses only this component.

**Gate B (implementation cost):** first compare generic Yosys numbers for indication, then synthesise the three row variants in the *same authorized technology, constraints and timing targets*, adding equal-format source-memory access and complete shared-scale/interface overhead. STOP any claim that 6-bit FP is cheaper from equal payload width or generic gate counts alone.

**Gate C (FYP claim):** pair full-cost hardware results with existing original-cut quality, then independently validate representative held-out Mac graphs and the most informative format/width operating points. STOP FP superiority claim if appropriately matched INT/BFP dominates on quality-cost; conditional negative result remains valid FYP output. E2 model is parked as later device-robustness check.

## Reproduce locally (requires Icarus and Yosys)

```bash
python3 -m unittest discover -s tests -p 'test_m3_sixbit_encoding.py' -v
python3 -m experiments.m3_sixbit_encoding --out /tmp/m3_vectors
for fmt in fp int bfp; do
  case "$fmt" in fp) idx=0;; int) idx=1;; bfp) idx=2;; esac
  iverilog -g2012 -s tb_m3_row -Ptb_m3_row.FORMAT="$idx" -o "/tmp/tb_${fmt}6" rtl/m3_local_field_row.v rtl/tb_m3_row.v
  vvp "/tmp/tb_${fmt}6" +VEC="/tmp/m3_vectors/m3_${fmt}6_vectors.txt"
done
for fmt in fp6 int6 bfp6; do
  yosys -Q -p "read_verilog rtl/m3_local_field_row.v; synth -top m3_${fmt}_row; stat" > "${fmt}_generic_synth.log"
done
```

**Evidence status:** design/RTL/bit-true tests + repeatable CI flow committed; until CI outputs are verified, no RTL PASS or synthesized-cost claim is made. Older NUS and other-platform physical/device findings are not silently imported into this scope.
