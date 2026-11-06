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
