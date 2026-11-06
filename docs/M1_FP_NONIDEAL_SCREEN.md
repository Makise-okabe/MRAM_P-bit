# M1 preliminary FP4/FP6/FP8 coupling x nonideal p-bit screen

**Scientific scope:** low-order **floating-point coupling** under MRAM p-bit response variations, using independent **complex BPSK MIMO** frames ONLY. This first experiment is **software-model feasibility E1/E2**, not a proof of novelty, not measured stochastic MRAM data, not a bit-accurate RTL implementation or fair area/power equivalence.

## Format definitions (fixed before observation)
FP4 E2M1, FP6 E3M2, FP8 E4M3 signed custom binary numbers; exponent bias 2^(E-1)-1; exp=0 subnormal/zero, exp=1..2^E-2 normal, all-one exp reserved; finite overflow saturates. Nearest finite value with ties to smaller magnitude. Decode zero as +0 (signed-zero **coding** not yet implemented). These are mathematical value codebooks; exact bitstream serialization, rounding corner cases and accumulator quantization remain future M3 work.

INT4/6/8 are symmetric signed fixed-point [-2^(b-1)+1,+2^(b-1)-1] with one unused negative code; round-half-up magnitude and saturate. FP/INT values are multiplied by an instance-optimized global scalar separately for J and h. This is **optimistic per-frame coefficient-MSE scaling**, not deployment-valid calibration and not a cost-optimized INT benchmark yet. The same MSE tuning search is offered to FP and INT. Scales are provisionally counted as 32-bit; all arithmetic costs pending.

BFP4/6/8 uses symmetric tile-pair groups for J, one per-bias global group; signed fixed-point mantissas with a power-of-two scale. Assumes 8-bit scale exponent metadata. The exact scale range and exponent hardware need M2/M3 validation. Quantize unique undirected J edges once and mirror coefficients: J_ij=J_ji after quantization.

FP32: unquantized numerical reference, not an actual FP32 accumulation architecture. FP4/6/8 are the **central research design**; INT/BFP are required independent controls. Initial format comparison is **not yet cost-matched** despite bit and metadata accounting.

## Response models (not physically sourced)
Ideal: logistic sigmoid(2 beta field). Illustrative gain0.80: sigmoid(2 beta 0.8 field); offset015: fixed per-neuron Gaussian offset sigma=0.15 (dimensionless field units, same device population across all frames/formats); contrast090: 0.05 + 0.9 sigmoid(2 beta field). These are not validated MRAM probability curves. Device-seed and offsets recorded. Need physical stochastic MTJ response provenance, calibration and operating range for a physically grounded FYP H1 finding.

## Selection and measurement
Each format samples its **own quantized Hamiltonian** using same seeds and spin-update counts; select the lowest **quantized** energy among fixed post-burnin checkpoints. Full-precision H/y never select a candidate. Only afterwards score selected state against the **original ML residual and transmitted BPSK bits**. Exact ML small-N reference is independent. Output BER, ML-hit, original residual gap, coefficient distortion, nominal coefficient+metadata storage and per-run paired CSV.

A real MIMO receiver must implement coefficient construction, scalar tuning, local-field arithmetic, candidate selection, and any replica overhead; they are not counted by attempted spin updates. Do not interpret a winning BER on a 12-frame pilot as device-grounded or cost advantage. Different SNRs reuse paired channel/noise seed, solver RNG and device populations.

## First small NUS screening
```bash
git pull --ff-only
python3 -m unittest discover -s tests -v
python3 experiments/m1_pbit_screen.py --tx 8 --rx 8 --snrs 0,5 --frames 12 --output results/m1_fp_nonideal_screen001
```

## Next scientific gates
1. Increase independent frames, add multiple chip offset/gain populations, check paired uncertainty, absolute task quality thresholds and independence.
2. Constrain FP and INT scales to deployable train/calibration rules with equivalent scale granularity and metadata cost. Tune strong integer baselines, extend FP tile/block scales fairly.
3. Replace illustrative response with documented stochastic MRAM p-bit switching curve and operating ranges (if available under permitted access); otherwise clearly limit claim to behavioral models.
4. Implement per-element exponent decoding, alignment, bounded-precision local-field accumulation and synthesized tile; compare power, area, delay and bandwidth, not bit count alone.
