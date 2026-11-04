# ADR-0006 — Freeze primary FYP direction: coupled precision × physical nonidealities
**Decision:** 2026-11-05, user explicitly selects this route. **Status:** adopted research direction, NOT a novelty or hardware-performance claim.

## Research question
How do ADC quantization boundaries, position-dependent read-current distortion, and MTJ/access-device variability jointly determine whether a signed MRAM-CIM operation fails? Can a lightweight predictor of these **failure boundaries** generalize to held-out physical circuit configurations and guide precision or simple spatial correction beyond stronger conventional baselines?

The submitted umbrella topic, **"Characterizing Reliability and Failure Regimes of Memory-Centric Neural Inference Under Coupled Precision and Hardware Non-Idealities"**, remains primary. Move Ising-machine field-control and E21 covariance mapping to the alternative archive, not parallel active thesis claims.

## Grounded evidence and earlier negative outcomes
- E17: four-bank joint-operand ADC controller saves 8.8838% *ideal* comparisons with matched metadata; no physical timing/energy.
- E19: GF **access NFET** + student static MTJ, 32-row constructed BL circuit, explicit *assumed* 5Ω/segment line resistor, m=k=16, n7/8. Real NUS Spectre current distributions overlap; original CAL midpoint errors 2/8 and 2/24 DEV. This is NOT a 256×256 foundry-extracted array.
- E19C: CAL-only optimized threshold still made 2/8 and 2/24 DEV errors; ambiguity deferral left 3/8 and 5/24 decisions unresolved.
- E20: on those actual NUS GF-NFET currents, near/far count, centroid and suffixQ CAL correction all reached 0/8 and 0/24 sampled errors. Complex suffixQ has NO demonstrated advantage over cheap input-position controls. E15/E20 retired as primary originality claim.
- E21 software: within-group covariance mapper does not beat simple joint activity sort from original grouping and NanoCiM/Dyn-A-Map are close mapping prior art.
- Ising: E09 cache locking reproduced conventional locked cache; E10A selective symmetrization not compelling; no demonstrated physical Ising local-field operator or specific algorithm winning against exact incremental fields.

## Immediate fixed experimental sequence (DO NOT claim future results before execution)

### E22: full-count GF current + quantization pilot (next)
Run committed `experiments/e22_gf_precision_regime.py` on the student's NUS Singularity using the locally verified, previously created `e19_gf_nfet_mtj_nonideal_count_gate_v2.py`. Preserve a single set of mask IDs across all **assumed** line-R settings. `B=32,m=k=16,n=0..16`, 6 CAL+12 DEV per n, R=0/1/2/3/5Ω per segment, nominal GF hvtnfet and student static MTJ. Generate current per case in Spectre; separately quantize saved current at 4/5/6/7 bits, SAME R0-CAL current fullscale for all r and bits. Compare fixed nominal, per-R CAL offset-only and per-R CAL near/far correction. Baseline continuous current nearest nominal count centroid (b=0) to distinguish analog ambiguity from finite ADC quantization.

**Preliminary numerical study:** per assumption 306 circuit cases per R ×5 = **1,530 per-mask/condition GF compact-model DC circuits**, if no simulation errors. 204 independent DEV masks per R (12 per n), 102 CAL mask identities per R; masks are paired across R, not independent chip assignments. Counts of circuits are not 1,530 statistically independent chip samples. The process of building masks can be reused if additional R settings are studied later.

**Required checks:** 17 nominal ordered R0 levels; same masks across R; CAL-only thresholds and offsets; comparable fullscale across bits; no hidden DEV threshold tuning. Report count-decoding error and MAE, count-pair DEV current overlap, and describe interactions/strong no-interaction null. With 204 DEV masks per condition, error rates are exploratory; bootstrap by mask ID, NOT by R repeat.

**Interpretation warning:** uniformly quantizing at a fixed R0 range may create clipping at large assumed R; isolate genuine analog overlap (b0), quantization (bit depth), and recalibratable global shift (offset-only). A non-monotone precision effect can arise from decoder/fullscale choices and is not automatically an invention.

### E23: first physically grounded failure-boundary predictor
Train only on E22 CAL information:
- simple baseline 1: nearest nominal count margin vs converter threshold;
- simple baseline 2: scalar current-distortion std and worst-case magnitude;
- candidate: margin-to-quantization-boundary combined with input-position-conditioned current bias and empirical variability.
Hold out entire spatial mask combinations; validate probabilistic calibration (Brier/ROC as appropriate), accurate critical R transitions and optionally ADC/correction policy choices on equal-cost objective. A successful rule needs meaningful held-out advantage over cheap margin and near/far controls, not merely a heatmap of E22 error.
**No prediction accuracy/novelty result exists before E23 is executed.**

### E24: variability and actual geometry gate
First obtain physically defensible interconnect RC from an authorized schematic/PEX or declared geometry estimate, rather than treating 5Ω as measured. Then introduce *fixed per-chip* MTJ ±5% resistance spread, as a specified random model (not claimed GF process measurement), multiple independent chips and corners. Preserve chip assignment across read patterns; compare near/far correction and failure-boundary predictor to strong controls. More realistic access NFET variation and PEX are separate data tiers.

### E25: task-level inference
Full valid W4A8 FC1 and downstream MNIST evaluation using frozen trained model/bias and legal bitplane layout; do not claim classification accuracy from only FC1 currents or zero assumed bias. Measure relative to clean quantized reference on held-out images/chips, and include read/ADC/control cost. If full network weights and bias remain absent, mark as a blocking input and report only verified arithmetic/count-level results.

## Contribution/failure gates
1. **Physical coupling**: demonstrate an interaction under controlled matched conditions beyond independently additive quantization and parasitics. Report baseline as well as positive cases; if no interaction, revise rather than claim coupling.
2. **Predictor**: improve held-out failure-boundary prediction relative to simple current-margin/offset/position models; bootstrap proper independent units. If no win, preserve negative result and deliver conventional characterization only, subject to supervisor scope acceptance.
3. **Design guidance**: choose minimal precision/correction to satisfy a PREDECLARED arithmetic/task error target, outperform fixed rules at comparable total readout cost. The threshold must be declared before model comparison. Logical comparator operations alone are not physical energy.
4. **Evidence scope**: distinguish actual GF transistor simulation, explicit line-R assumptions, full-array PEX, actual ADC circuitry, stochastic MTJ/CMOS variation, and inference classification. None of these stronger tiers is to be invented by extrapolation.

## Supervisor meeting message
“We have ruled out several weak novelty claims by strong controls. The main FYP is now reliability and failure-boundary prediction for coupled ADC precision and physical MRAM nonidealities. E19–E20 show GF-access-transistor read-current overlap under assumed line R and demonstrate cheap input-position correction; these are preliminary mechanism results. E22 will characterize all feasible counts across matched R/bit-depth experiments; E23 tests whether a specific boundary predictor generalizes beyond conventional margins and calibration. We will not equate an assumed-wire study with 256×256 PEX or claim task accuracy before the full network is reconstructed.”
