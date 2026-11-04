# E03S — cheap analytical mapping-ranking screen with bounded decoder

Date: 2026-11-04 (Singapore). Evidence: independently executed local software using the hash-verified user E01 frozen MNIST packet and *explicitly assumed*, IID persistent Gaussian cell perturbations at sigma=0.20 normalized count units. **Not MRAM PEX/Spectre, no neural classifier-failure outcome, no energy or novelty pass.**

## Response to E03R peer review
The E03R count decoder had clipped to 0..32 without exploiting the exact combinatorial bounds. This screen uses [max(0,m+k-32), min(m,k)] for every 32-row read, where m is active input rows and k is stored ones. CAL/DEV parent identities are disjoint. Chip variation remains fixed over all bit cycles and separately drawn for 48 DEV chips. Note that read counts originate from the full first E01 packed-array workload, whereas arithmetic quality is measured for 8 output channels of the first FC1 256-row block; read count is a resource proxy.

## Implemented estimator (candidate F1-supporting method, not a validated inference-failure predictor)
- **Exact Gaussian marginal decoder moment:** compute mean/variance of the bounded nearest-integer count error analytically using normal CDF threshold intervals, with no sampled CAL chips.
- **First-order Hermite cross-read estimator:** for two activation bit-plane reads of the same resident cells, use overlap-derived analog correlation rho, and approximate quantized covariance as rho * E[e_b Z_b] * E[e_d Z_d]. Add signed shift-and-add coefficient products (including negative W4 coefficient). Marginal-only comparator drops this covariance term but preserves accumulated bias and marginal variances. These calculations are known mathematical tools; originality is unproven.
- Compete with direct noisy calibration Monte Carlo using either 4 or 48 chip draws, with the *same assumed* sigma. All mappings are frozen E01 orders; this is a **fixed pool**, not an optimized new resident mapper.
- Independent DEV quality metric: reconstructed arithmetic MSE on 256 DEV MNIST parents x 48 disjoint simulated chips x 8 outputs, **not full neural-network failure probability**.

## Held-out result, synthetic sigma=0.20 only

| Mapping | Nonempty vector reads (E01 first packed array) | DEV bounded-decoder MSE |
|---|---:|---:|
| Original | 7,919 | 700,840 |
| Dead-feature packed | 7,173 | 729,733 |
| Zero-rate sorted | 5,478 | 704,865 |
| CAR alpha0 | 5,468 | 784,337 |
| Activity-balanced | 14,824 | 476,116 |
| Random | 14,078 | 565,868 |

E03S reproduces the independently observed bounded-decoder DEV numbers for CAR and balancing.

**Budget-aware mapping selection:**
- <=6,000 reads: both analytical scores, direct MC4 and DEV point-estimate oracle choose *zero-rate sorting*; CAR has the fewest reads. Paired chip bootstrap 95% interval for DEV difference (zero-rate minus CAR): [-176,288,+9,246] MSE. Not a certain ranking win.
- <=8,000 reads: marginal score chooses *zero-rate sorting*, Hermite1 chooses *original*. DEV MSE original 700,840 vs zero 704,865 (0.57% point estimate). Paired chip bootstrap 95% interval for original-minus-zero [-88,080,+80,102]: **no independently established value of the covariance term**.
- <=15,000 reads: both analytical scores and direct MC48 choose *activity-balanced*, whereas noisy CAL MC4 selects random. Balanced spends substantially more reads; no claim of matched-cost energy benefit.

For the six frozen policies, Spearman rank correlation of CAL analytical score with independent DEV MSE is marginal 0.714 and Hermite1 0.943. This is a descriptive *six-point* result, not evidence of robust superiority. Analytical scores markedly underestimate absolute held-out MSE and have no calibrated failure probability.

**Timing control (illustrative same local CPU, warmed arrays):** analytical Hermite score ~0.094s/policy; direct 4-chip MC ~0.039s/policy; direct 48-chip MC ~0.378s/policy. Shared model fitting/CDF LUT and dataset preparation excluded. Hence **not cheaper than small-sample MC**, even if cheaper than 48-chip MC. The estimator assumes sigma is already known; fitting it on real hardware would incur further characterization cost.

## Provenance / package
- Reproducibility package provided as a conversation download `e03s_analytic_mapping_ranker_package.zip`; SHA256 `8968de6be797cb8ff82bb3218841b746ef497c1e3bbbe2762fa75f5cec384bef`. It contains code, README, independent chip-level JSON, bootstrap and timing audit. This GitHub note does not claim the package is stored inside the repository.
- Python ranker SHA256 `0e78e25cd34d298ff04a7d2a13030a96b613de431a529e2316e302e1d65c3ccf`.
- E01 packet SHA256 `400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a`.
- Neither historical eight-cell measurements nor proprietary GF PDK contents entered any E03S score.

## Disposition
A concrete, low-dimensional **mapping MSE ranker** now exists. This is a methodological step beyond rerunning E03R sigma sweeps, but it has **not** shown incremental fixed-budget selection value from covariance, cheap rare-failure prediction, a new mapping algorithm, or full-network task improvement. No new thesis direction selected. To promote F1/F3, the next demonstration needs calibrated new-array read/ADC error structure, a broader cost-matched mapping candidate set, a real full-network decision/failure surrogate and independent held-out reliability at an equal total resource budget. Leave Ising as the separately prioritized novelty discovery requested by the student.
