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
