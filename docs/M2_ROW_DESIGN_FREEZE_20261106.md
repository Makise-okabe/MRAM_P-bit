# M2 — One implementable local-field row, with a defined output policy

**Status: candidate RTL and smoke test, NOT synthesis-validated or measured physical MRAM.** This is the only hardware deliverable at this gate. No new format sweep, CI infrastructure, or arbitrary beta tuning.

## Prior evidence, closed

- NUS 16-spin 16-QAM H2, 300 held-out frames (100 CAL): mixed FP4-J/FP6-h global 48/300 retained original ML, 0.20490 uniform-ground-tie Gray BER, 640 nominal bits; matched INT4-J/INT6-h global 39/300, 0.22403, 640 bits; BFP6 global 109/300, 0.17959, 832 bits, with 107/300 quantized-ground degeneracies. Significance-group FP gave 57/300 retained but slightly worse tie BER 0.20625 and 704 nominal bits. Tile FP was worse, at 45/300 and 928 bits: **do not implement tile first**.
- Exact eight-spin H1 tested an E2 behavioral p-bit response, not an MRAM device. At 500 attempted updates, beta=1 mixed FP ideal P(any visit to original-quality target)=0.9713 and P(fixed-time snapshot)=0.0507. The single predeclared posterior-consistent beta=15.8489 check gave mixed FP P(any visit)=0.6421, snapshot=0.3645; mixed INT 0.5462 / 0.2434; BFP6 0.6490 / 0.3796; uniform FP6 0.6315 / 0.4392. Nonideal contrast090 changed mixed FP snapshot to 0.2250. Some beta=15.85 stationary chains did not converge within the allotted steps; do not claim stationary values. These are 20 distinct held-out MIMO channel frames paired with 2 synthetic device populations, NOT 40 independent channels. **H1 physical novelty is not proven.**

## First global-scale architecture

RTL: rtl/pbit_local_field_row.sv. Test: rtl/tb_pbit_local_field_row.sv.

One cycle-serial digital engine computes pre-update local field H_i = h_i + sum_{j!=i} J_ij*s_j for one selected spin i. A scheduler provides N-1 codewords and their current spin signs in successive accepted cycles. The spin array, scheduler, addressing, MRAM read circuits, stochastic p-bit, bias-voltage DAC, and monitoring controller are NOT included in the RTL.

Three frozen formats:

| RTL mode | J element | h element | Group scales | Arithmetic in last cycle |
|---|---|---|---|---|
| 0 | OCP finite-only FP4 E2M1 | OCP finite-only FP6 E3M2 | two unsigned 32-bit fixed Q12.20 | 16-by-32-bit integer multiplications, shifts, add |
| 1 | symmetric signed INT4 | symmetric signed INT6 | two unsigned 32-bit fixed Q12.20 | SAME multiplications/shifts/add |
| 2 | symmetric signed BFP6 | signed BFP6 | two signed 8-bit base-2 exponents | variable binary shifts and add |

FP4 is decoded to integer units of 1/2 and FP6 h to integer units of 1/16. INT4 and INT6 use signed two's-complement codewords with unused most-negative codes clamped to -7 and -31, matching the earlier software's symmetric alphabet. BFP6 also clamps -32 to -31.

The raw 16-bit signed accumulator adds or subtracts each J code according to spin sign. At N=128, the worst-case BFP6 raw magnitude is 127*31=3937 and FP4 raw magnitude is 127*12=1524, so 16-bit signed is sufficient for the stated modes. The final field_q24 is signed 64-bit Q40.24 for consistent fixed-point energy tracking. field_q16 is a saturated signed 32-bit Q16.16 result for an as-yet-unimplemented field-to-voltage/p-bit interface.

For FP/INT, stored scale words are **hardware Q12.20**, unlike the earlier H2 program's arbitrary Python float scale values which it counted as nominal 32 bits. A fixed-point rescore using the actual encoded scale words is REQUIRED before comparing implementation quality. MODE0 field_Q24 = ((sum_raw*scale_J_Q20)<<3) + (hraw*scale_h_Q20), with FP4 J raw in half units and FP6 h raw in sixteenth units. MODE1 shifts both multiplied terms by 4. MODE2 shifts raw J/h by (separate 8-bit scale exponent+24), with bounded/saturated shifts. Saturation or overflow invalidates exact energy-difference consistency and requires explicit detection in a future verified implementation.

**Throughput lower bound:** one row at N=128 consumes 127 accepted J-spin input pairs, one start clock and one output clock, at least 129 cycles. N=64 consumes at least 65 cycles. One row engine reused serially across 128 spins would need at least 128*129 cycles per full sweep, plus memory, routing and stochastic-device latency. This is NOT a proven high-throughput macro.

## Storage cost at global grouping (unique symmetric J, before memory decoder and arithmetic)

| Spins | Unique J edges | Mixed FP or INT code + scale | BFP6 code + scale | Mixed FP/INT if mirrored by row | BFP6 if mirrored by row |
|---:|---:|---:|---:|---:|---:|
| 16 | 120 | 640 bits | 832 bits | 1120 bits | 1552 bits |
| 64 | 2016 | 8512 bits | 12496 bits | 16576 bits | 24592 bits |
| 128 | 8128 | 33344 bits | 49552 bits | 65856 bits | 98320 bits |

Mixed/global bits = 4*N*(N-1)/2 + 6*N + 64. BFP/global bits = 6*(N*(N-1)/2+N)+16. Mirrored row storage duplicates all off-diagonal J entries, potentially simplifying one-read-per-row access; triangular unique-edge storage requires addressing/selection logic. Neither memory energy nor decoder area is measured. A bit count is NOT an area/power result. Each of the two fixed real-scale multipliers may be time-multiplexed at a cost in cycles, but the current RTL implements both combinationally.

## Practical output retention policy: best of visited REPRESENTED energy

**Do not use original-ML target as an on-chip oracle**. The proposed output is a best-state register updated according to the quantized represented Hamiltonian, with NO knowledge of the original H/y residual. On a flip of spin i, the symmetric Ising Hamiltonian changes by

Delta E = 2 * s_i_before * H_i_before.

The pre-flip field_Q24 from the row can feed a signed energy accumulator and compare against best recorded represented energy. If the update does not flip the spin, energy does not change. Initialize current represented energy to arbitrary zero at the initial state, best energy also to zero, and best_state to the initial spins; relative differences among visited configurations are sufficient if all field and energy calculations are exact in the **same** implemented fixed-point semantics and do not saturate/overflow.

Incremental selection cost (not implemented): N extra best-state bits, 64-bit running energy, 64-bit best energy, a 64-bit comparator, a 64-bit signed adder/shift/conditional negate, capture control and control/clock/power overhead. At N=128 that is 256 additional storage bits, *not* a free oracle. The actual return probability for this policy has NOT been measured; P_hit from the exact chain describes an unimplementable original-task target oracle and P_snapshot describes only a final state readout. Neither equals the best-represented-energy selection. Actual returned-solution BER is the next meaningful joint result, once device physics and controller are defined.

## Physical evidence and first hardware gate

The legacy GF22FDX conventional **stable-storage** MTJ model has NOT been validated as a low-barrier stochastic MTJ. NIST demonstrated CMOS-integrated sMTJ p-bit circuits at 130nm (Cacoilo et al., IEEE Electron Device Letters 2026, DOI 10.1109/LED.2026.3696800). Nature Communications 2026, DOI 10.1038/s41467-026-71844-8, experimentally measured voltage-dependent sigmoid response and strongly device-dependent pulse-width behavior in hybrid memristor-SMTJ Ising hardware. Those studies are real device evidence, but not GF22FDX device characterization, and their parameters cannot be relabeled as foundry-specific.

NEXT VALID GATE is actual simulator/synthesis of this candidate row, checking random vectors against a bit-true software decoder, measured LUT/cell area and critical path, coefficient read bandwidth, and explicit p-bit field-to-voltage/pulse-width transfer. Then implement/measure the best-represented-energy output policy. No other β, grouping, codebook, or 8-spin diagnostic expansion by default.

## Exact commands for NUS (only if tools already installed)

    cd "$HOME/MRAM_Pbit_M0"
    git pull --ff-only
    if command -v iverilog >/dev/null 2>&1; then
      iverilog -g2012 -s tb_pbit_local_field_row -o /tmp/m2_row.vvp rtl/pbit_local_field_row.sv rtl/tb_pbit_local_field_row.sv
      vvp /tmp/m2_row.vvp
    else
      echo "IVERILOG NOT INSTALLED: RTL has NOT passed simulation"
    fi
    if command -v yosys >/dev/null 2>&1; then
      yosys -p 'read_verilog -sv rtl/pbit_local_field_row.sv; hierarchy -top pbit_local_field_row; proc; opt; stat'
    else
      echo "YOSYS NOT INSTALLED: no synthesis/area result"
    fi

**Verification status: repository RTL candidate authored; neither Icarus testbench nor synthesis has yet been executed in NUS. The existing GitHub CI tests Python experiments only. No quantitative area/energy comparison is claimed.**
