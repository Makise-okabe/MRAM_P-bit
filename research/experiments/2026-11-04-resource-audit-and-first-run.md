# Reusing existing resources for the first NUS experiment

4 November 2026 (Singapore). User request: inspect previous GitHub work, identify
available resources, give exact instructions and conduct the next experiment.

## Sources actually inspected

The new repository was read at `560ab1af09ce157a358286d788cc7229e9559893` and the legacy
repository at `ac6fbcdcea0a0d0580cd8534c0ae5d44f877c48c`. Reviewed the full Stage4A neural
script, baseline and tiled arithmetic code, relevant Stage4D code, the checkpoint-location
record, active GF-access/custom-MTJ policy and the Spectre launcher's interface. Source
pins and golden-function AST hashes are in `experiments/config/frozen_mnist_source.json`.
No NUS checkpoint, raw dataset, model library or server filesystem was accessed here.

During implementation the public repository advanced to
`c2e4b396d2637b6634b1a7d004fcf5d91e02dd4d`. Preserved its concurrent ADC-screen,
reproduction-disclosure and physical-first/E02-A work, including ADR-0004. The E03Q
record remains constructed-only and was not rerun by this resource audit. The new
handoff also invokes the existing private E02 preparation script before E01; this
creates folders/tool inventory, not an electrical result.

## Resource conclusions

| Existing resource | Reuse decision |
|---|---|
| 784-128-64-10 MLP checkpoint documented in `outputs/mnist_stage4a_v3_15ep/` | Reuse frozen weights after checking current NUS bytes/hash |
| W4A8 quantizer, clips, saved splits and source functions | Reuse exactly; retain development role of previously inspected parents |
| MNIST raw files documented under `data/mnist/` | Read existing original-training IDX files; no download or retraining |
| General signed/bit-plane arithmetic | Audit and extend to explicit 256-row / packed-column bookkeeping |
| Authorized access NFET and student-owned MTJ/Spectre workflow | Source/interface leads for fresh E02 only; no old fitted currents/readout parameters |
| Retired electrical records and old fixed small fan-in | Excluded from export, calibration, validation and target claims |
| Fresh physical 256x256 netlist/PEX/ADC validation | Not found in the inspected repository trees; current NUS assets still need inventory |

The new repository already contains a separate exploratory scikit-learn-digits screen.
It is not repeated or relabelled the frozen FYP workload. Its packet does not replace
the user's saved MNIST reference.

## Implemented experiment, not another manual-export request

`bash scripts/run_first_experiment.sh` resolves the documented NUS interpreter and
saved files, checks resource hashes, validates saved membership, pins only the three
audited golden quantizer functions, verifies the complete selected-parent forward,
packs every FC1 row block and all W4 planes, and runs the CAL-fitted baseline screens.
See [the exact user commands](../../START_HERE.md).

The first protocol uses 128 CAL and 256 previously inspected validation parents, W4A8,
FC1's four row blocks and prospective 32/64/128/256-row groups. These are a bounded
workload-screen effort budget, not powered failure-rate sample sizes or validated fan-in.
Both weight arrays of a row block use the same fitted permutation across all A8 cycles.
Padding, inactive features and the negative sign coefficient are explicit. All baseline
outputs are retained without selecting a winner on development data.

Each new run writes local NPZ traces, metadata, occupancy, exactness checks and a ZIP
for private review. The original checkpoint, PDK, model body, raw netlists and private
paths are excluded from the ZIP. A missing resource or changed golden function stops
with a diagnostic packet. Existing outputs, checkpoints and quantizers are not modified.

## Executed here and still pending

The full 27-test suite passes. Eleven new checks cover signed/partial-row reconstruction,
exact binary sums at the 256 limit, parent-bit identity, saved split leakage/order,
raw/gzip IDX contracts, ties-to-even quantization, golden-source change rejection,
shared mappings, private-packet exclusion and a complete filesystem/packet integration
test with the external NUS loader stubbed. That integration fixture is software
verification, not an executed MNIST result. The shell wrapper passes syntax checking.

The local resource preflight returns the expected missing checkpoint/quantizer/splits/
dataset status and exit 2. The golden source is available from the GitHub audit; actual
NUS binary/data files are not mounted here. A real frozen-MNIST run, real golden-forward
comparison, target Spectre run and E02 physical validation remain **not executed**.

## Next decision

The user runs the ready command in the existing NUS environment and returns its packet.
We then inspect the actual primary-workload counts and nominate the fresh physical
patterns/model-interface work. A lack of skipping savings only narrows the sparsity
claim; it does not settle the equal-resource covariance mechanism. No novelty pass or
new inference/energy benefit follows from runner readiness.
