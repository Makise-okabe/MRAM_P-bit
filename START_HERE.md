# First real FYP workload experiment: run this on NUS

This runner uses your saved MNIST network. It does not retrain, recalibrate the
quantizer, read historical electrical results or run Spectre. E01 supplies workload
structure; the new physical 256x256 array is the subsequent E02 task.

## Paste in your usual NUS MRAM shell

Use a fresh checkout, leaving your existing project and model files in place:

```bash
cd "$HOME"
git clone https://github.com/Makise-okabe/MRAM_Path_Finding.git MRAM_Path_Finding_E01
cd MRAM_Path_Finding_E01
bash experiments/e02_private_preflight.sh
bash scripts/run_first_experiment.sh
```

If that checkout already exists, enter it and use `git pull --ff-only` instead of
cloning over it. Every execution creates a new result directory automatically.

The first script prepares the private E02 workspace and reports the Cadence tools
available in that shell. It does not construct an array or run an electrical solve.
The second script runs the frozen-workload experiment. The next physical circuit
procedure is [E02-A](research/experiments/E02A_fresh_256x256_physical_read_screen.md).

The wrapper prefers `$HOME/venvs/mram-stage4a/bin/python`, which your previous runs
used. It preserves the CPU/thread settings documented after the earlier SIGILL.
To select an already working interpreter explicitly:

```bash
MRAM_RUN_PYTHON=/absolute/path/to/your/python bash scripts/run_first_experiment.sh
```

It installs nothing and never launches a substitute training run.

## Existing resources it checks automatically

Relative to `$HOME/MRAM_FYP_Overleaf`:

| Resource | Default location |
|---|---|
| Frozen trained weights | `outputs/mnist_stage4a_v3_15ep/fp32_checkpoint.pt` |
| Frozen W4A8 quantizer | `outputs/mnist_stage4a_v3_15ep/frozen_quantization.json` |
| Saved parent membership | `outputs/mnist_stage4a_v3_15ep/split_indices.npz` |
| Original MNIST training images/labels | `data/mnist/MNIST/raw/`, raw IDX or gzip |
| Original golden quantizer source | `research/software/mnist_precision_stage4a.py`, or its preserved archive path |

These paths are documented by the old repository; current file presence and hashes
must be checked on NUS. No checkpoint binary or dataset is committed here.

If files are elsewhere, override only their locations:

```bash
bash scripts/run_first_experiment.sh \
  --legacy-root "$HOME/MRAM_FYP_Overleaf" \
  --model-dir /absolute/path/to/mnist_stage4a_v3_15ep \
  --data-root /absolute/path/to/mnist
```

## What the run does

1. Check checkpoint/quantizer hashes, saved split membership and the original neural
   quantizer functions. A changed function stops for review.
2. Reproduce the frozen W4A8 network on the first 128 saved calibration parents and
   first 256 saved validation parents. Validation is labelled **development**, because
   it was inspected previously. The original MNIST test files are not opened.
3. Compare the NumPy export with the original PyTorch golden forward on all selected
   parents. Require matching predictions and maximum logit difference <=1e-10.
4. Export all four FC1 row blocks: 256, 256, 256 and 16 used input positions. Each
   block packs 128 outputs x four weight planes into two 256x256 binary position maps.
   This gives eight prospective arrays. The last block has 240 padding rows per array.
   These are capacity/address maps, not electrically validated arrays.
5. Check signed reconstruction of every selected layer output, including the -8 sign
   plane. Keep one resident permutation across all eight activation bits and both
   weight arrays of each row block.
6. Compare original, one fixed seeded random, dead-feature packing, zero-rate sorting,
   activity balancing, CAR and quiet-then-balanced baselines at prospective group sizes
   32/64/128/256. Report every arm; choose no winner on development data.
7. Save traces with parent/activation-bit associations, full occupancy and permutation
   checks, row-padding/dead-feature counts, source hashes and a compact review packet.

The runner also records whether Spectre/OCEAN are on PATH and looks for the declaration
of the student-owned `mtj_read_v0` module in bounded source directories. It copies no
model body, PDK coefficient, old simulation deck or old read measurement. This is only
an E02 resource lead, not a verified cell/array interface or circuit result.

## What to return

At the end it prints an absolute `review_packet.zip` path. Upload that ZIP to this chat.
It contains the exported workload/packed integer weight planes, results and hashes;
it excludes the checkpoint binary, PDK/netlists, private resource paths and old read data.
Keep the generated run directories local rather than committing them to this public repo.

If a resource is missing or the golden check fails, the same mechanism produces a
diagnostic packet and exits 2. Return that packet; do not retrain or guess new scales.

## How the result changes our next decision

We will identify savings beyond dead-feature/padding packing, inspect activity and
cross-bit overlap, and nominate useful masks for the fresh E02 physical build. Read
counts are not ADC energy, inference failure or physical read reliability. If simple
controls explain the savings, narrow the sparsity claim; the separate equal-read-count
covariance hypothesis still needs its physical and strong-baseline gates.
