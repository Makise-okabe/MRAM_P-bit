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

## Fresh NUS 8x8 M1 pilot — 6 November 2026 (E1/E2 only)

User-executed: 24/24 then-current tests PASS. Complex BPSK MIMO N_t=N_r=8, 12 independent frames for each SNR 0 and 5 dB, 96 transmitted bits per SNR, 1,000 attempted spin updates per format/response/frame. These are NEW results; no archived TSP/CIM device values.

| Ideal-response format | 0 dB ML hits | 5 dB ML hits | 0 dB bit errors | 5 dB bit errors | Nominal storage bits (pilot) |
|---|---:|---:|---:|---:|---:|
| `fp32` label = **unrounded Python-double reference** | 12/12 | 12/12 | 7/96 | 3/96 | **1,152 mislabeled as FP32 storage** |
| FP4 E2M1 | 10/12 | 10/12 | 9/96 | 3/96 | 208 |
| INT4 | 11/12 | 12/12 | 9/96 | 3/96 | 208 |
| BFP4 | 10/12 | 10/12 | 8/96 | 5/96 | 176 |
| FP6 E3M2 | 12/12 | 12/12 | 7/96 | 3/96 | 280 |
| INT6 | 12/12 | 12/12 | 7/96 | 3/96 | 280 |
| FP8 E4M3 | 12/12 | 12/12 | 7/96 | 3/96 | 352 |
| INT8 | 12/12 | 12/12 | 7/96 | 3/96 | 352 |

The old `fp32` implementation *returned unchanged Python float64 coefficient values* while counting each coefficient as 32 bits, so the reported 1152 bits is NOT a valid hardware-storage number. Do not retroactively relabel past runs as true IEEE FP32. A newer code revision introduces real binary32 coefficient rounding and a separate `fp64_ref` path. This fixes reference semantics going forward; it does NOT create M1 device/format results by itself.

**Response comparison:** Both `gain080` and `offset015` produced exactly the same **aggregated** ML-hit, BER and mean ML-residual-gap metrics as ideal for every format at 0 and 5 dB. This does not imply identical per-frame final states or update trajectories. `contrast090` altered BFP4 at 0 dB only in the aggregate: 10/12 to 9/12 ML hits (worse), 8/96 to 7/96 bit errors (apparently better), and mean original gap from 0.05281 to 0.08252 (worse). One-bit BER difference is noise at this sample size, not evidence of device benefit.

**Interpretation:** M1 has an early coefficient precision sensitivity at FP4/INT4 and an empirical ceiling at 6/8 bit, but has NOT established device-response-by-format interaction (H1), scaling advantage from exponent granularity (H2), size trend (H3), physically meaningful MTJ nonideality or synthesis-backed cost. FP/INT use per-instance optimized global real scales, while BFP uses symmetric tile-pair power-of-two scales; format and granularity are confounded. Best-of-120 post-burn-in checkpoints may mask nonideality in returned best solution. 12 frames = 96 bits/SNR gives wide BER uncertainty.

**Follow-up gate (no new MIMO application):** Analyze the already saved per-frame `m1_paired_runs.csv` using `experiments/m1_paired_diagnostics.py` to measure (a) response-vs-ideal selected-state divergence, ML-hit flips, first-best checkpoint changes; (b) 4/6/8-bit FP vs INT paired discordances. Preserve the original pilot files and commit hashes. Then design controlled equal-scale-granularity INT/FP, physically sourced p-bit response, time-to-target and macro synthesis studies.
