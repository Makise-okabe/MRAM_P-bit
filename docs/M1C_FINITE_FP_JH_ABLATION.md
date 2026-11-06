# M1C — Finite-only low-order FP, frozen scale, J/h sensitivity

## Scope and findings

Core remains **low-order floating-point coupling × MRAM p-bit nonidealities**; BPSK MIMO is only the application workload. The initial 8-spin NUS 12-frame/SNR results found that historical FP4 lost the original ML optimum after quantization in 2/12 frames at both SNRs, while INT4 lost it in 1/12 at 0 dB and none at 5 dB. Every returned sampled state minimized its own represented Hamiltonian within audit tolerance. BFP4/BFP6 additionally showed quantized ground degeneracy. **No FP advantage or physically validated device interaction has been shown.**

## Format definition and OCP prior art

OCP MX v1.0 section 5.3.3 FP4 E2M1 defines finite-positive levels 0, 0.5, 1, 1.5, 2, 3, 4, 6. Section 5.3.2 FP6 E3M2 gives positive maximum 28 and minimum subnormal 0.0625. Both specify no Inf/NaN and nearest-ties-even support. New candidate names fp4_fn and fp6_fn preserve old fp4/fp6/fp8 experiments and no historical data are overwritten. **Only the element value sets are modeled**: arbitrary per-group real scales and Python accumulation are not full MX E8M0/block encodings nor bit-true hardware. OCP standard element formats themselves are not novel.

Source: https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf

## Independent scale calibration followed by J/h diagnosis

M1B calibrates each format's scales using independent training channel/noise frames only, then freezes them across all held-out frames. Same global/tile symmetric J coefficient groups and an h group apply to FP4/6/8, finite-only FP4/FP6, scaled INT4/6/8 and BFP4/6/8. No held-out ML objective tuning.

M1C reads the resulting M1B output without new sampling or calibration. For each held-out frame compare (a) J_only quantization with unquantized h (oracle diagnostic only), (b) h_only with unquantized J (oracle only), (c) both quantized, (d) mixed FP4_fn-J/FP6_fn-h, (e) mandatory matched mixed INT4-J/INT6-h baseline. Score original ML-state preservation (any optimum) and quantized-ground degeneracy, best/worst original residual bounds. A mixed h 4-to-6 bit increase uses 2N additional coefficient bits, 256 for N=128, before metadata, decoder or accumulator overhead. J_only/h_only are not hardware cost comparisons.

This is E0/E1 **representation only**; there is NO physical stochastic MTJ response, device-aware tuning, time-to-target, p-bit sampler comparison, encoded 32-bit real scales, bit-exact exponent alignment or synthesized silicon cost.

## NUS smoke and saved evidence (run after PR merges)

    set -euo pipefail
    cd "$HOME/MRAM_Pbit_M0"
    git pull --ff-only
    python3 -m unittest discover -s tests -v
    OUT="results/m1b_fn_$(date -u +%Y%m%dT%H%M%SZ)_$$"
    python3 experiments/m1_calibrated_scale_gate.py \
      --tx 8 --rx 8 --snrs 0,5 \
      --cal-frames 24 --heldout-frames 24 \
      --formats fp4,fp4_fn,fp6,fp6_fn,fp8,int4,int6,int8,bfp4,bfp6,bfp8 \
      --granularities global,tile --tile 4 --output "$OUT"
    python3 experiments/m1_jh_ablation.py \
      --m1b-dir "$OUT" --output "$OUT-jh"

Data/source SHA256 and independent CAL/HELD frames stay saved. 24 heldout frames per SNR only exploratory. Next scientific gate: finite-budget target-reaching updates with physically sourced stochastic MRAM control-input response, multiple device populations, fair hardware costs (M2/M3 coupling tile).

## User-run NUS M1B/M1C HELDOUT RESULTS — 6 November 2026 (E0/E1, representation only)

**Data provenance:**
- M1B: `results/m1b_fn_20261106T030113Z_3625599`.
- M1C: `results/m1b_fn_20261106T030113Z_3625599_jh`.
- Complex 8×8 BPSK MIMO, SNR = 0 and 5 dB, 24 independent CAL frame seeds and 24 disjoint HELDOUT frame seeds for each SNR. Same H and normalized noise seed are intentionally paired across SNRs. Scales are fitted by calibration-only coefficient MSE and frozen for held-out evaluation; *not* per-test-frame optimization. These values are reported by user NUS output and have not independently been recomputed from the private output files.

### Crucial original-ML preservation results (global scale; original optimum in quantized ground set)

| Representation | 0 dB retained | 5 dB retained | Degenerate quantized-ground frames 0/5 dB | Nominal coefficient + assumed metadata bits |
|---|---:|---:|---:|---:|
| historical fp4 J and h | 18/24 | 21/24 | 2/24, 0/24 | 208 |
| finite-only fp4_fn J and h | 19/24 | 22/24 | 0/24, 3/24 | 208 |
| int4 J and h | 18/24 | 21/24 | 0/24, 1/24 | 208 |
| **fp4_fn J + fp6_fn h** | **23/24** | **24/24** | **0/24, 0/24** | **224** |
| int4 J + int6 h | 21/24 | 24/24 | 0/24, 1/24 | 224 |
| fp6_fn J and h | 21/24 | 24/24 | 0/24, 0/24 | 280 |
| bfp6 J and h | 23/24 | 24/24 | 0/24, 1/24 | 232 |

M1B global finite-only FP4 improves one frame at each SNR versus historical FP4 (19 vs 18 and 22 vs 21), but under **tile** grouping drops to 18/24 at 0 dB and 20/24 at 5 dB (vs historical FP4 18/24 and 21/24). The larger FP4 finite-only element codebook is NOT automatically better after independently fitted scaling. Finite-only fp6_fn is effectively tied with historical fp6 in these counts.

### J/h mechanism isolation (global scale; original ML retained)

| Coefficient format | 0 dB J-only; exact h | 0 dB h-only; exact J | 0 dB both | 5 dB J-only; exact h | 5 dB h-only; exact J | 5 dB both |
|---|---:|---:|---:|---:|---:|---:|
| fp4_fn | 23/24 | 19/24 | 19/24 | 24/24 | 23/24 | 22/24 |
| int4 | 21/24 | 18/24 | 18/24 | 24/24 | 21/24 | 21/24 |
| bfp4 | 21/24 | 18/24 | 19/24 | 23/24 | 20/24 | 21/24 |

J-only and h-only retain the **other operand at full precision** and are diagnostics, not deployable low-bit formats. The comparison indicates low-bit bias representation is a primary constraint in these frames, but J/h errors interact: the effects cannot be added or used to establish universal h dominance. A mixed-precision configuration is more informative and must be compared with a matched mixed INT candidate.

### Mixed precision and hardware interpretation

- **Global**: fp4_fn-J/fp6_fn-h retained **23/24 at 0 dB, 24/24 at 5 dB** using **224 nominal bits**. Matched int4-J/int6-h retained **21/24 and 24/24** at **the same 224 nominal bits**. It is a **2-frame exploratory difference**, not a statistically established FP advantage.
- **Tile**: fp4_fn-J/fp6_fn-h retained **22/24, 24/24** at **288 nominal bits**, versus INT mixed **22/24, 24/24** at **288 nominal bits**. Tile scaling adds assumed scale words but does not improve these mixed outcomes.
- Compared with uniform fp6_fn global (280 nominal bits), mixed FP (224 nominal bits) uses 56 fewer bits in this **N=8** representation model; physical area/energy might still be higher due to per-element exponent, scale decode, alignment, bias precision and accumulator overhead. BFP6 global gives **23/24 and 24/24** at **232 nominal bits**, and deserves a genuine synthesized fixed-point/PoT-scale baseline.
- At N=128, changing h only from 4 to 6 coefficient bits adds 2N=256 coefficient bits before metadata and logic; this does not establish 128-spin quality or hardware feasibility.

**STOP/GO conclusion:** Stop open-ended FP-codebook sweeps. Retain just three implementation candidates for the next M2/M3 proof-of-concept: (A) FP4_fn-J/FP6_fn-h, (B) matched INT4-J/INT6-h, (C) BFP6. Additional FP4 uniform / FP6 uniform form transparent reference controls, not new research branches. The next decisive work is (1) real/sourced stochastic MRAM p-bit transfer-input/response, and (2) bit-accurate local-field arithmetic and synthesis for the 64–128-spin coupling array. The quantitative hardware-quality-cost criterion must be predeclared; no result here yet demonstrates MRAM p-bit nonideality interaction, lower hardware cost, or FYP novelty.

**Limitations:** 24 HELDOUT frames per SNR is too few for statistical superiority. No p-bit sampling or time-to-target is performed in M1B/M1C, the 32-bit per-group scale costs are nominal while actual scalars are Python floating point, and only unique symmetric J coefficient storage is counted (not access paths, mirror reads, circuit peripherals, or physical stochastic MTJs). Old CIM/TSP physical datasets are excluded.

## Physical gate: what will qualify as MRAM p-bit nonideality evidence?

The hardware novelty is still *low-order FP coupling under nonideal stochastic magnetic p-bits*. A conventional high-retention storage MTJ/MRAM bit-cell model is NOT a validated low-barrier/superparamagnetic p-bit. No foundry 22FDX device capability for stochastic p-bits has been demonstrated here. This is the primary unresolved feasibility dependency, and it must be settled before treating synthetic sigmoid variants as physical H1 evidence.

Grounded external device references available as of 6 Nov 2026:

1. **Iftakher et al., Nature Communications (2026), DOI 10.1038/s41467-026-71844-8**: a hybrid HfO2-memristor-crossbar/SMTJ Ising machine reports experimentally fitted switching probability versus applied voltage, logistic in device slope and midpoint; pulse-width-dependent slow versus fast SMTJ response (fast measured down to 130 ns), significant device variability. Its circuit is a related published architecture, NOT a validation of FP4/FP6 coupling, our process or a direct model of a different MTJ.
2. **Cacoilo et al., IEEE Electron Device Letters (2026), DOI 10.1109/LED.2026.3696800**, NIST: experimentally CMOS-integrated superparamagnetic MTJ p-bit at 130 nm, with voltage-tunable output. Does not imply availability in GF22FDX eMRAM.
3. **Daniel et al., Nature Communications (2024), DOI 10.1038/s41467-024-48152-0**: measured stochastic-MTJ + MoS2 p-bit core, demonstrating nonideal characteristics including output plateau/threshold mismatch and significant dependence on device/transistor design. Not a directly portable silicon process.

**Stop/go rule for H1:** (a) determine with Prof Fong whether a permitted stochastic MTJ/p-bit Verilog-A or measured V/I-to-probability-versus-pulse-width dataset exists; (b) otherwise extract parameter values, uncertainty, pulse-dependence and variability from published measured studies and label the model **literature-informed cross-technology behavioral**, NOT GF22FDX-fitted; (c) clearly declare the mapping of quantized local field to voltage/current, limiting/clipping and update period; (d) evaluate fixed update budgets on held-out BPSK MIMO with multiple stochastic seeds/device populations and confidence intervals. Compare mixed FP, matched mixed INT, BFP6 under equal task quality and explicitly costed bit-true RTL. If no credible p-bit device input model can be sourced, narrow the final hardware claim rather than simulate a fabricated stochastic array.
