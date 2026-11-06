# M1B held-out coupling scale/granularity pilot — 6 Nov 2026

Research core still **LOW-ORDER FP4/FP6/FP8 coupling × nonideal MRAM p-bits**; BPSK MIMO is only the benchmark. Previous M1A observed representational ground-state loss at 4 bits and BFP tie degeneracy. This new M1B test isolates **H2 representation and scale granularity** and does not purport to prove H1 physically.

**Critically different from M1A:** scale parameters are fit on a separate **calibration** set of complex BPSK MIMO channels and noise, with exactly disjoint frame seeds from the independent held-out set. Once fitted, scales are **frozen for every test frame**; no test-frame coefficient-MSE optimization or ML-oracle tuning.

For each FP4/6/8, INT4/6/8, BFP4/6/8, evaluate BOTH `global` and `tile` groupings on the SAME MIMO data and with equal group membership for J across formats. `h` uses a separate frozen group. For each group, scale is selected by the same `tune_scale` candidate-grid coefficient MSE criterion using all calibration coefficients. FP/INT arbitrary real scale metadata provisionally 32 bits; BFP power-of-two exponent 8 bits. Quantize unique symmetric undirected J once and mirror. FP element exponent is encoded within the 4/6/8-bit coefficient code. This removes one prior granularity confound but is **not** a full optimized INT baseline, nor hardware equal-area/equal-time matching.

Reference is the independent original unquantized MIMO ML residual `||y-Hs||²`. Exhaustively enumerate states for Nt<=12, evaluate which quantized ground states survive and how many degenerate minima occur (energy tolerance 1e-8). Report the minimum and maximum original ML gap and BER among quantized ground states as **possible-choice bounds**, not a p-bit detector outcome. This phase does NOT run stochastic p-bit updates, synthesize FP accumulation hardware, or infer measured MTJ response.

**First NUS pilot:**
```bash
set -euo pipefail
cd "$HOME/MRAM_Pbit_M0"
git pull --ff-only
python3 -m unittest discover -s tests -v
python3 experiments/m1_calibrated_scale_gate.py \
  --tx 8 --rx 8 --snrs 0,5 \
  --cal-frames 24 --heldout-frames 24 \
  --tile 4 --output results/m1b_calibrated_scales_001
```

M1B preserves CAL and HELDOUT complete channel/noise frames, every frozen scale (JSON), per-format exact-quantization state metrics and SHA256 hashes. 24 held-out frames per SNR are preliminary, not sufficient to infer noninferiority or FP advantage. **Next H1:** physically sourced stochastic MRAM p-bit response and independent device populations, finite update-budget time-to-target on a calibrated format/coupling tile. **Next M2/M3:** bit-true FP exponent alignment/accumulation and synthesis cost against equally routed integer schemes. No old TSP/CIM records imported.

## Finite-only FP and J/h extension (integration of earlier draft PR #14)

OCP finite-only E2M1/E3M2 format candidates (fp4_fn and fp6_fn) now run in the same global/tile, CAL-only-fitted framework. The follow-on read-only M1C ablation compares the influence of represented J versus h, and mixed FP4-J/FP6-h against matching mixed INT4-J/INT6-h, without using the original ML optimum to fit scales. See docs/M1C_FINITE_FP_JH_ABLATION.md and the Overleaf-ready report section. OCP element encodings are prior art, not demonstrated MRAM-CIM hardware or novel device results; no new NUS experimental outcome is claimed by this commit.

## First NUS user-run M1B result: frozen CAL/HELDOUT, historical formats ONLY (6 November 2026)

- User output: `results/m1b_calibrated_20261106T022926Z_3625599`.
- NUS test output: **36 tests PASS**. This predates merged M1C / finite-only integration (now 50 CI tests); no `fp4_fn`, `fp6_fn`, J-only/h-only or mixed-precision results are contained in these data.
- Setup: 8x8 complex BPSK MIMO, 24 separate CAL and 24 HELDOUT channel seeds per SNR (0,5 dB), frozen CAL-only group scales, global or symmetric tile grouping (tile size 4). Same 24 HELDOUT channel seeds reused across the two SNR conditions. This is E0/E1 **exact representation**, not a stochastic p-bit detector run, device nonideality or fabricated 64–128-spin array.
- Tables show `ML` = **original exact ML optimum retained in the quantized minimum set**, not hit rate from finite sampling or transmitted-bit BER. `Deg` = frames with >1 minima within the 1e-8 energy tolerance. Nominal bits include unique undirected J + h plus assumed real/PoT scale words; no coefficient-construction, programming, alignment, accumulation, area or timing.

| Format | Global 0 dB ML/Deg | Global 5 dB ML/Deg | Global bits | Tile 0 dB ML/Deg | Tile 5 dB ML/Deg | Tile bits |
|---|---:|---:|---:|---:|---:|---:|
| fp4 | 18/24 / 2 | 21/24 / 0 | 208 | 18/24 / 0 | 21/24 / 0 | 272 |
| int4 | 18/24 / 0 | 21/24 / 1 | 208 | 18/24 / 0 | 22/24 / 0 | 272 |
| bfp4 | 19/24 / 3 | 21/24 / 3 | 160 | 19/24 / 3 | 21/24 / 3 | 176 |
| fp6 | 21/24 / 0 | 24/24 / 0 | 280 | 21/24 / 0 | 24/24 / 0 | 344 |
| int6 | 21/24 / 0 | 24/24 / 0 | 280 | 23/24 / 0 | 22/24 / 0 | 344 |
| bfp6 | 23/24 / 0 | 24/24 / 1 | 232 | 23/24 / 0 | 24/24 / 1 | 248 |
| fp8 | 24/24 / 0 | 24/24 / 0 | 352 | 24/24 / 0 | 24/24 / 0 | 416 |
| int8 | 24/24 / 0 | 24/24 / 0 | 352 | 24/24 / 0 | 24/24 / 0 | 416 |
| bfp8 | 24/24 / 0 | 24/24 / 0 | 304 | 24/24 / 0 | 24/24 / 0 | 320 |

### Interpretation / follow-up gates

1. **FP4 is not demonstrably superior to INT4**: global 0/5 dB ML preservation identical, tile INT4 improves by one heldout case at 5 dB. Different representations still have different coefficient MSE, original decision margins and quantized tie patterns.
2. **BFP6 merits follow-up, not a winning claim**: global and tile 23/24 at 0 dB, 24/24 at 5 dB, lower *nominal* storage than FP6 or INT6 because of the assumed compact PoT scale metadata. It is not a proof of lower circuit power/area or a large-sample result.
3. **Eight-bit ceiling**: all retained ML optimum in these frames, so larger/harder BPSK MIMO is needed for format discrimination; these small instances are valuable primarily for exact mathematical checks.
4. **Scale granularity needs cost accounting**: tile FP4 increases storage 208 to 272 with no improvement here; INT6 tile improves at 0 dB yet worsens at 5 dB. Global/tile matching prevents a grouping confound, but scale encoding differs between INT/FP real and BFP PoT.
5. **Identical J-MSE across SNR is expected** because the paired H realizations are reused, while J depends on H alone; transmitted/channel noise affects y, hence h and ML residual. J-MSE cannot be used as a proxy for detection accuracy.
6. **Next numerical experiment**: pull latest main (merged PR #16, initially 50/50 CI tests), rerun M1B with `fp4_fn` and `fp6_fn` under the SAME frozen CAL/HELDOUT seeds, then M1C's J-only/h-only oracle diagnostics and mixed FP4_fn-J/FP6_fn-h versus matched INT4-J/INT6-h. Report source hashes and independent CAL vs HELDOUT. Do not overwrite previous evidence.
7. **Physical-H1 remains open**: no electrically validated stochastic MRAM p-bit control-input transfer function, finite-time original-task target-reach, or synthesized coupling tile has been measured.

No claim of low-order-FP novelty, FP statistical superiority, device-aware rule, or CIM implementation follows from this pilot.
