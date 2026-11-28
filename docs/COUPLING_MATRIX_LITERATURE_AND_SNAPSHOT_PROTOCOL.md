# Coupling-matrix design basis and frozen snapshot diagnostic

**8 Nov 2026.** This note documents the completed CAL coupling J analysis and the next *read-only* explanatory diagnostic. No new solver/stress campaign is authorized here.

## What the FYP actually encodes

The original weighted Max-Cut edge weights define a symmetric Ising coupling
matrix: J_ij = J_ji = -w_ij for i != j, diagonal J_ii = 0 and problem h = 0.
For a 100-spin vector s, each p-bit receives local field H_i = sum_j J_ij s_j.

The repository stores undirected edges plus adjacency lists, not an explicit
100x100 dense array. Its global quantizer encodes each unique coupling entry
once and mirrors its decoded value into both lists. Thus the adjacency-list
calculation is **mathematically the same symmetric matrix-vector product**;
it does not prove a physical matrix-memory implementation.

Three different precisions must NOT be conflated: (1) stored coupling
coefficient J_ij bits, the variable tested by this FYP; (2) numerical local
field accumulator bits, currently effectively high precision in software;
(3) p-bit input-interface voltage/pulse/DAC precision, not implemented by
this behavioral sigmoid model.

## Literature and format basis

These are prior-art and specification *leads* for the report, not claims that
the FYP reproduced their hardware or measured costs.

- [Volpe et al. 2026 pipelined p-computer](https://doi.org/10.1002/aisy.70521):
  coefficient memory, field-update arithmetic and throughput must be co-designed
  with fixed-point width.
- [Snowball 2026 preprint](https://arxiv.org/abs/2601.21058):
  coupling bit planes and incremental local-field updates are existing ideas.
- [Tao, Zhang and Han, APAIM 2023](https://www.ece.ualberta.ca/~jhan8/publications/ESW_Late_Breaking_R3.pdf):
  floating-point Ising coefficients/field arithmetic are not a first use;
  addition and accumulation cost must be considered.
- [Ising-CF, DAC 2023](https://yunany.github.io/Publications/25_Ising_CF.pdf):
  nonuniform coupling representation motivates analysis of actual coefficient
  distribution and low-energy-task behavior.
- [Yang et al. 250 STT-MTJ p-bit machine 2026](https://www.nature.com/articles/s41467-026-72020-8):
  digital coupling processing driving stochastic MTJ response is precedent.
- [OCP MX v1.0](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf):
  FP4 E2M1 / FP6 E3M2 element value sets have specification precedent, BUT
  the full experiment is not OCP MX: this code uses a source-MSE-selected
  global binary32 scale instead of MX32 blocks. FP5 is custom, FP8 is a
  finite-only custom E4M3 (max 480 vs standard E4M3 max 448). Its BFP control
  is a one-global-power-of-two-scale implementation, not general block BFP.

Coefficient MSE is a reproducible representation objective; it is NOT the
same as minimum Ising energy or original-weight Max-Cut solution quality.

## Why gain/offset could appear — with the correct limits

For a sigmoid-shaped switching curve P(+1|V)=sigma(a_i(V-V50_i)) and a
nominal controller V = V50_0 + 2 beta Hq_i / a_0, substitution yields

P_i(+1)=sigma((a_i/a_0) 2 beta Hq_i + a_i(V50_0-V50_i)).

This derivation motivates a slope-mismatch gain and midpoint-mismatch offset.
It **does not** calibrate the distributions of physical STT-MRAM devices.
Our E2 offset uses one persistent synthetic per-spin population
delta_i = d v_i, with v_i drawn once; +/-0.8 and +/-1.6 are diagnostic
LOGIT halfspans, not measured post-calibration voltages.

## Read-only snapshot analysis

The new script experiments/m2_coupling_matrix_snapshot_diagnostic.py audits
original M1 936-row ideal data, the FP64 offset scout's 240 rows, 576
primary FP/INT low-bit rows and all 192 conditional 8-bit runs.

It uses **144 already-returned FP64 states**:
2 CAL graphs x (ideal, offset 0.8, offset 1.6) x 24 frozen solver seeds.
Every FP4/5/6/8, INT4/5/6/8 and ref64 matrix J is evaluated on the **same**
state in each condition:

delta H_i(s) = sum_j (Jhat_ij-J_ij) s_j

delta logit_i = 2 beta_snapshot delta H_i

delta P_i = sigmoid(2 beta_snapshot Hhat_i+delta_i)
          - sigmoid(2 beta_snapshot Href_i+delta_i).

Three multipliers of original graph beta (0.5, 1.0, 2.0) are STATIC
instantaneous response checkpoints, NOT observed spin trajectories.
The script reports relative RMS field distortion, logit distortion,
probability distortion and the **already observed** solver-returned original
gap for each format. The probability metric is conditional on the same
reference state and the same modeled offset; it is not hardware accuracy.

Outputs are 3,888 state/format/beta rows, 162 summary cells and an integrity
manifest. The code does not run the annealing solver, modify the quantizer,
refit a scale, introduce new formats, or use low-bit states to choose a
snapshot. Associating the state-conditioned metrics with existing solver
quality is NOT a causal account of each trajectory.

These are CAL explanatory diagnostics before holding out the untouched
two 7777 graphs. Do not adjust previously frozen quality/interaction
acceptance thresholds using these results.
