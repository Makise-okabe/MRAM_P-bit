# M4B common digital logit — first finite-precision hardware gate (7 Nov 2026)

## Scope / FYP decision

This work stays on **low-order FP6/INT6/BFP6 coefficient representation and cost** for the frozen M1 source-calibrated 100-spin *original* weighted Biq Mac Max-Cut problem. M3 proved selected original-graph row bit-true arithmetic and Sky130HD row-core mapped area. M4A proved mathematical gain folding. M4B is the **NEXT** bounded digital step: specify and implement one common **quantized logit interface** with clocked RTL and matched cell mapping. No device-noise tests or full analog p-bit accelerator are added.

## Candidate numerical contract to verify, not a claim of M1 bit identity

| Parameter | Exactly specified M4B candidate |
|---|---|
| Input coupling | Frozen M1 custom finite FP6 E3M2, symmetric INT6 or global-exponent BFP6; one 6-bit code per edge |
| Local-field row | unchanged M3 digital signed integer accumulator, 17 bits FP6 or 13 bits INT/BFP |
| Input gain | per-attempt EXTERNALLY supplied **signed positive Q4.28** (32-bit), G(t)=2*beta(t)*S_eff, with FP S_eff=S_fp/16, INT S_eff=S_int, BFP S_eff=2**k |
| Gain rounding | Python round-to-nearest, ties-to-even to a signed Q4.28 code; must be within (0,8) and not underflow |
| Computation | exact signed integer product A * gain_q28, then shift right 16 with nearest-even rounding |
| Output logit | **signed 18-bit Q6.12**, one LSB=2^-12, saturate to [-12,+12] AFTER rounding; external sigmoid/p-bit input |
| Protocol | gain_q28 latched on CLEAR, one coefficient/spin pair per valid cycle, LAST on 99th term, valid Q6.12 logit exactly one extra clock cycle later |
| Clock/word scale | no fabricated physical clock frequency, analog gain, output voltage range or energy |

The saturation corresponds to sigmoid probability close to 0 or 1 beyond logit +/-12. The end-to-end solver can be affected by even small probability differences; a within-one-graph prefix probability bound is **not** evidence of preserved 50,000-step solution quality. The Q4.28 choice must pass an explicit representability check on all original CAL graph scales at frozen beginning/mid/end beta(t) schedule.

Explicit-scale numerical oracle (Python M1 represented J and beta) and fused-gain hardware are compared at a **common output contract**. Different binary floating intermediates need not match bit-for-bit. M4B uses integer arithmetic after scaling, not an IEEE floating-point adder/multiplier per coupling.

## Evidence and tests

- Codebooks, M3 source manifest and vector SHA256 are checked from unchanged original official Mac graph files.
- Numerical generator: experiments/m4_common_logit.py, tests/test_m4_common_logit.py.
- RTL: rtl/m4_common_logit_row.v; benches: rtl/tb_m4_common_logit.v.
- CI: .github/workflows/m4-common-logit.yml. Runs three original 100-spin CAL graphs, three formats, three beta(t) points (0,24999,49999): **27 clocked full 99-term rows**, with 27 x 99 M3 integer-prefix checks. Each numeric graph/format/time point separately checks 99 ideal-versus-quantized prefix *probabilities*, a total of 3 x 3 x 3 x 99 = **2,673** probabilities.
- Candidate per-sample numerical gate: max absolute probability difference <= **2.5e-4** on those 2,673 prefix cases. This bound is not a generic solver invariant or output-cut quality proof.
- Same M3 pinned Sky130HD tt_025C_1v80 filtered Liberty, same Yosys synthesis / technology mapping flow, fixed compile-time format tops. Report mapped cells/area for the row+gain register+integer multiply+RNE+saturation.

## Caveats and explicit exclusions

The 32-bit gain input is assumed supplied per attempted update by an EXTERNAL beta/scale controller. The RTL includes its row-local register and multiplication, **not** circuitry to generate, update, distribute, or calibrate those gain words. The same Q4.28 bus and protocol are given to all three formats, but the FP6 multiplied operand is 17 bits versus 13 bits for INT/BFP; that cost must not be hidden. This is a hardware **digital interface** cost, not overall Max-Cut implementation area. Coefficient RAMs/banking, address generation, graph state, spin scheduling, incrementally updated local fields, p-bit comparator/DAC, SRAM activity and time/energy per solution remain separate. There is no STA or fitted clock period unless reported independently.

For N=100, serial full row: each attempted update requires 99 coefficient issue cycles plus the one extra logit cycle; this is an architecture assumption. At 50,000 attempts, it implies 4.95 million coefficient issue slots plus 50,000 logit output cycles. It does not represent the incremental cached-field algorithm used by M1 software, and therefore it cannot be silently converted into real wall-clock runtime or energy cost.

## STOP / GO

**PASS** requires all 27 real-graph RTL tests, finite numeric output contract and all three same-flow mapped area results. **STOP** reporting numeric pass if any gain underflows/out-of-range, probability error exceeds frozen gate, or clocked vector mismatches. **GO to held-out original Max-Cut quality** only after a clear comparable cost table and stated gain-controller/memory exclusions. Do not optimize interface bits using M1 labels as feedback; later widths need independent held-out selection/confirmation.
