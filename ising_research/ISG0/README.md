# Independent MRAM–Ising sandbox · ISG-0

**Status: mathematics smoke tests only. No GF PDK, Spectre, PEX, device-level noise or energy measurements have been performed.**

This is an independent research investigation maintained only in the Git branch `research/ising-machine-isg0` under `ising_research/ISG0/`. Do not merge it into `main`, modify the existing FYP experiments, or reuse FYP experiment labels. To work on Schrodinger, use a **separate clone**, as shown in `RUN_ON_SCHRODINGER.md`.

## What ISG-0 actually tests

- For four spins, build the intended symmetric Ising Hamiltonian and its exact 16-state Boltzmann distribution.
- Generate 64 synthetic field records per scenario (4 target spins × 16 full spin states); this includes two redundant observations per target-spin-agnostic conditional context.
- Detect invalid dependence of a local-field read on the *old state of the spin being updated*. Analysis stops if above the tolerance rather than silently averaging it away.
- Calculate random-scan asynchronous heat-bath transition matrices and exact stationary distributions via linear algebra.
- Calculate pairwise conditional compatibility defects on all contexts of other spins.
- Fit **three competing explanatory models** on six of the eight unique contexts per target spin, then evaluate the other two: (i) fixed symmetric pairwise model, (ii) fixed directed pairwise model, (iii) directed model plus one predeclared nonlinear spatial interaction feature per target.
- Compare raw field MAE, update probability error, total variation (TV) of stationary vs intended distribution, conditional compatibility defect, and forward vs reverse systematic-scan stationary TV.

**Warning:** directed-plus-Q is an intentionally matched upper-bound diagnostic in the nonlinear synthetic fixture, not an original solver, physically validated correction or fair hardware energy comparison. It has four additional fitted coefficients. The constructed fixture must not be cited as evidence that a real MRAM circuit has this specific error mechanism.

## Run on your laptop (Windows PowerShell)

Unzip this package to a folder outside your FYP and open PowerShell there. With Python installed:

```powershell
py -m pip install numpy
py ising0.py demo --out results/ISG0_SYNTHETIC
```

## Run on NUS Linux / inside an existing Singularity shell

Clone the separate research branch following `RUN_ON_SCHRODINGER.md`, then:

```bash
set -euo pipefail
cd "$HOME/Ising_MRAM_Sandbox"  # directory with ising0.py
python3 -c 'import numpy; print("NumPy:", numpy.__version__)'
python3 -m py_compile ising0.py
python3 ising0.py demo --out results/ISG0_SYNTHETIC
```

If NumPy is unavailable, use a supported local Python environment; do not modify the existing FYP environment or repos for this smoke test.

## Analyzing genuinely measured fields (future ISG-1, not yet supported by GF proof)

First satisfy the signed-read feasibility gate in `EXPERIMENT_PROTOCOL.md`. **Do not directly put currents in amperes into the `measured_field` column.** A physically justified read operator must map measured currents/differential signals to dimensionless signed Ising local fields, with a fixed calibration and readout procedure.

CSV file requires **exactly 64 records** per fixed resident coupling assignment:

```csv
state,spin_index,measured_field
-1|-1|-1|-1,0,-0.123
-1|-1|-1|-1,1,0.456
...
```

- `state`: precisely four ±1 spins separated by `|`, ordered `s0|s1|s2|s3`.
- `spin_index`: 0 through 3.
- `measured_field`: **dimensionless** normalized field after fixed, documented signed decoding; no raw uncalibrated amperes.
- Include each of the 16 full spin states for each of the four target-spin reads.
- The physical programming/placement must be *resident and fixed* for all 64 reads, with temperature and read settings unchanged. Changing J for each state destroys the intended test.

JSON config:

```json
{
  "n": 4,
  "beta": 1.3,
  "J": [[0,0.8,-0.5,0],[0.8,0,0.6,-0.7],[-0.5,0.6,0,0.45],[0,-0.7,0.45,0]],
  "b": [0.18,-0.12,0.06,-0.16],
  "source": "GF_PEX_MEASURED_AFTER_SIGNED_READ_VALIDATION",
  "field_units": "dimensionless_Ising_field",
  "scenario": "independent_fixed_coupling_01"
}
```

The numerical matrix above is illustrative **only**. The config is *not* evidence that any GF cells implement those real-valued coefficients. Pick legal physical encodings and measured mapping first.

Then:

```bash
python3 ising0.py analyze \
  --fields physical_fields.csv \
  --config physical_config.json \
  --out results/ISG1_REAL_001.json
```

Use `--self-tolerance` only if justified by measurement uncertainty; otherwise the diagnostic refuses to average away target-spin dependence. Results remain non-comparable across runs if their beta, assigned J, or read mapping changes.

## Scope / claims

- Demonstrates that the analysis code distinguishes mathematical examples and exactly computes a 16-state stochastic transition kernel.
- Does **not** demonstrate an MRAM Ising processor or any actual GF error mechanism.
- Does **not** demonstrate circuit energy savings, temporal-noise utility, algorithmic novelty, or a 256×256 array.
- The strongest simple controls are **fixed symmetric fit** and **directed fit**; a Q feature is admissible for further research only if specified before, calibrated using allowed observations, and shown to predict unseen physical placements or couplings.
- For an implementable correction algorithm, charge calibration, metadata storage, additional reads, ADC and digital arithmetic. A software-fitting result alone is not sufficient.
