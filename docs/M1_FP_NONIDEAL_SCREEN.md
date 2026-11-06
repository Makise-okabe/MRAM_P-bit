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

## Paired diagnostics result (user-run NUS, 6 November 2026)

Input: original `results/m1_fp_nonideal_screen001/m1_paired_runs.csv`; analyzer output saved to `results/m1_paired_diagnostic002/m1_paired_diagnostics.json`. This is a **read-only analysis**, not a new simulation and not a physically measured MTJ result.

- `gain080`: zero changed final selected states / zero original ML-hit flips across both SNR and all ten original format labels. In individual pairs, the first checkpoint at which the **eventually selected best quantized-energy state** was recorded changed in approximately 1–5/12 frames per format/SNR.
- `offset015`: zero changed final selected states / zero ML-hit flips; some selected-best checkpoints changed (0–4/12).
- `contrast090`: 1 changed final selected state (BFP4 at 0 dB) / 1 ML-hit flip; all other format/SNR selected states unchanged, although best checkpoints changed (typically 3–6/12).
- There are 10 labels × 2 SNR × 3 response changes × 12 frame pairs = 720 `final-state` comparisons, but **NOT 720 statistically independent trials**. Only one selected state differed.
- Paired FP4 vs INT4 original-ML discordances (under ideal response): 0 dB FP-only=1, INT-only=2; 5 dB FP-only=0, INT-only=2. Aggregate transmitted-bit errors match, so BER conceals some optimization-quality differences. At 6/8 bits, no ML-hit discordances in these 12-frame pilots.

**Important timing distinction:** `selected_at_update` is the *first recorded checkpoint of the ultimately selected best quantized-energy state*. It is NOT necessarily the earliest sample to meet a predefined original-task residual/BER threshold; it is not a measured hardware latency or full application time-to-target. Observed changes cannot yet be called faster/slower convergence.

**Primary next mechanism test:** `experiments/m1_exact_ground_audit.py` will enumerate all 256 states in each 8-spin quantized Hamiltonian, using saved `m1_frames.jsonl` and CSV to distinguish (a) original ML optima surviving quantization, (b) selected state being a ground state under quantized coefficients, (c) original ML hit. It reconstructs old `fp32`-labeled *unrounded software* reference using the new `fp64_ref`, verifies logged energies and does not produce any new device simulations. This must be run on NUS before drawing conclusions about quantization vs sampling failures.

## M1 exact oracle audit command — separates representation from sampler

A **new read-only diagnostic**, not new stochastic simulation. The historical 6 November pilot used unrounded Python coefficients under the `fp32` name; to reconstruct its saved energies correctly, pass `--legacy-unrounded-fp32`. New runs with genuine binary32 `fp32` must **omit** that flag.

```bash
python3 experiments/m1_exact_ground_audit.py \\
  --runs results/m1_fp_nonideal_screen001/m1_paired_runs.csv \\
  --frames results/m1_fp_nonideal_screen001/m1_frames.jsonl \\
  --legacy-unrounded-fp32 \\
  --output results/m1_exact_quantized_ground001
```

Enumerates all 256 Ising states in each saved 8-spin case; verifies the selected state's logged quantized energy against reconstructed J,h; computes whether (1) the original ML state is a quantized Hamiltonian minimizer and (2) the returned selected state is quantized-optimal. These diagnose **representation distortion vs sampling failure**. The original ML optimum can be lost in the quantized Hamiltonian even if a lucky finite-budget sample finds it. Conversely a chosen quantized minimum need not solve original ML. Log all caveats, avoid claiming causal MRAM nonideality or area/power. Do not alter or overwrite the original NUS saved pilot.

## M1 exact quantized-ground audit — completed on NUS (6 November 2026)

**Input:** user's saved original 8x8 MIMO pilot frames/CSV. Command used `--legacy-unrounded-fp32`, preserving the old mislabeled unrounded-double reference. **Output:** `results/m1_exact_ground_20261106T015525Z_3625599`. Original files were not overwritten. No new p-bit simulation or physical measurement; E0/E1/E2 analysis only.

**Main finding:** every reported selected state was a ground-state minimizer of its *own quantized Hamiltonian*: `selected-quant-min=12/12` for all 80 format × response × SNR combinations (10 format labels × 4 response models × 2 SNRs). These are highly correlated observations, not 960 independent frames.

Original ML state **preserved within quantized ground-state set**:

| Format | 0 dB | 5 dB |
|---|---:|---:|
| FP4 | 10/12 | 10/12 |
| INT4 | 11/12 | 12/12 |
| BFP4 | 11/12 | 11/12 |
| FP6, FP8, INT6, INT8, BFP6, BFP8 | 12/12 | 12/12 |
| historical `fp32` = unrounded double value reference | 12/12 | 12/12 |

The original ML preservation numbers repeat across response models because those models alter the **sampling probability** but **not the quantized coefficients**.

**Representation error versus sampler error:**
- FP4 at both SNRs lost the original ML optimum from the quantized ground-state set in 2/12 frames each. INT4 lost it in 1/12 at 0 dB and 0/12 at 5 dB. This is a coefficient-landscape effect, not a failure to minimize the quantized energy.
- BFP4 (0 and 5 dB) retained the original ML state in 11/12 sets yet achieved 10/12 original ML hits with ideal response (contrast090 BFP4 0 dB had only 9/12). BFP6 at 5 dB retained 12/12 but achieved 11/12 original ML hits. Because the selected solutions all minimize the quantized energy, this indicates **degenerate quantized minima with unequal original residuals** (or ties at the numerical energy tolerance), not failure to reach the quantized minimum.
- No response model caused the final selection to miss the quantized ground under the tested 1,000-update best-of-samples budget. Some models changed best-recorded checkpoint indices, which **are not** time-to-target.
- Hence H1 (device-dependent useful precision) has NOT been demonstrated; H2 (floating-point exponent/scale granularity value) is NOT isolated, H3 not studied; the MRAM response models remain synthetic E2.

**Next required scientific gate:** use existing `format_exact_minima.csv` to quantify ground-state multiplicity and margin/degeneracy, then compare FP versus tuned INT at **the same global/tile scale granularity and full hardware metadata cost**. Follow with finite-budget, multi-seed p-bit dynamics under a physically justified stochastic MRAM transfer curve. The architecture remains a 64–128-spin low-order FP coupling array; BPSK MIMO remains the sole application benchmark.

## Confirmed ground-state multiplicities (additional NUS read-only diagnostic, 6 Nov 2026)

User inspected the original `results/m1_exact_ground_20261106T015525Z_3625599/format_exact_minima.csv` and `frame_exact_audit.csv`, **without rerunning the solver or importing prior project results**.

| Format | 0 dB degenerate frames (of 12) | 5 dB degenerate frames (of 12) | Maximum quantized ground degeneracy |
|---|---:|---:|---:|
| FP4 | 0 | 0 | 1 |
| INT4 | 0 | 0 | 1 |
| BFP4 | 2 | 1 | 3 |
| BFP6 | 0 | 1 | 2 |
| FP6 | 0 | 0 | 1 |

The exact frame identifiers where the original ML solution remains in the quantized-ground set but **is not** the ultimately selected quantized-ground solution (under ideal response) are: `BFP4 @ 0 dB, frame 10`; `BFP4 @ 5 dB, frame 8`; `BFP6 @ 5 dB, frame 10`. These confirm a restricted **ground-state tie / degeneracy mechanism** only for some BFP quantizers in this dataset. In contrast, FP4 and INT4 failures here arise from a unique quantized minimum that no longer matches the original ML solution, so making the sampler converge harder to the *same* quantized Hamiltonian cannot fix those original ML errors.

The exact audit uses `ATOL=1e-8` on energies; degeneracy is mathematical/software-level within that tolerance, not proof of equal physical currents or identical magnetic free energy. A different nonideal p-bit trajectory might select among tied minima, but there is no current evidence of a general device-dependent useful precision advantage. At 0 dB, BFP4 had two frames with degeneracy >1, but only one ideal-response frame with ML-preserved-but-not-selected; those counts must not be conflated. At 5 dB, BFP4 and BFP6 each had one identified discrepancy. Multiple SNR points use the same channel seeds; not independent populations.

**Decision to stop repeated tiny-pilot diagnostics:** next substantive M1 experiment must use (a) frozen CAL-versus-HELDOUT coefficient scales, (b) both global and matched tile-pair granularity for **each** FP and INT/BFP baseline, (c) equal spin-update budget and a fixed quantized-Hamiltonian selection rule, (d) representation metrics including original-ML optimum retention, ground degeneracy, original residual gap and BER, and (e) independently sourced or physically validated stochastic MRAM p-bit response before any H1 physical claim. Report actual coefficient+scale bits and later RTL alignment/accumulator costs rather than calling bit counts silicon area/energy. The locked 64–128-spin array, FP4/6/8 core design and BPSK MIMO application do NOT change.
