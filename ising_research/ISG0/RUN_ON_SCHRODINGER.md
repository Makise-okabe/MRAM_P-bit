# Run ISG-0 on NUS Schrodinger — research branch only

The repo's **main branch is untouched**. Do not run git checkout on your existing $HOME/MRAM_Path_Finding working tree. Use a separate clone.

## First run

```bash
set -euo pipefail
cd "$HOME"
git clone --single-branch --branch research/ising-machine-isg0 \
  https://github.com/Makise-okabe/MRAM_Path_Finding.git \
  Ising_MRAM_Sandbox_checkout

cd "$HOME/Ising_MRAM_Sandbox_checkout/ising_research/ISG0"
python3 -c 'import numpy as np; print("NumPy", np.__version__)'
python3 -m py_compile ising0.py
python3 -u ising0.py demo --out results/ISG0_SYNTHETIC | tee ISG0_run.log
git status --short
```

If the destination clone already exists, skip clone and use the update block below.

## Update / rerun later

```bash
set -euo pipefail
cd "$HOME/Ising_MRAM_Sandbox_checkout"
git pull --ff-only origin research/ising-machine-isg0
cd ising_research/ISG0
python3 -u ising0.py demo --out results/ISG0_SYNTHETIC | tee ISG0_run.log
```

All numbers in ISG-0 are **synthetic mathematical tests**. They are not GF or Spectre measurements. Do not cite them as physical findings. No proprietary PDK, netlists, or private simulation data should be committed to this branch. Results, logs, and Python caches are ignored.

The next gate is **signed-read operator feasibility on real GF circuits**. That work requires a separate Cadence testbench and should not modify frozen FYP layouts, PEX, or netlists.
