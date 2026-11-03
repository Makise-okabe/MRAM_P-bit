# Running the first experiments

The tools need Python and NumPy. No Spectre installation, licensed model or neural-network
checkpoint is included. Run commands from the repository root.

## E00: exact identities

```bash
python3 -m unittest discover -s tests -v
python3 -m experiments.run verify --out experiments/runs/E00_local/verification.json
```

Outputs never overwrite an existing result. Tests use labelled fixtures; their outcomes
are not MRAM reliability or network accuracy results.

## E01: exported real bit-plane traces

Create an NPZ using a frozen model/exporter in the authorized local environment:

| Key | Shape | Meaning |
|---|---|---|
| X_cal | N_cal x 256 | Binary inputs used to fit mapping |
| X_eval | N_eval x 256 | Separate binary inputs used to evaluate frozen mapping |
| W | 256 x 256 | Corresponding binary weight plane; rows are input dimensions |
| cal_ids | N_cal | Stable non-object string/integer IDs |
| eval_ids | N_eval | Disjoint, unique IDs |

If several traces come from one image, include image + layer + patch + bit-plane in each
ID. Keep image membership separated too; the tool checks exact IDs, not hidden parent
image relationships. Bit-plane scaling/signs are accounted for separately by the full
integer reconstruction and E00 checks. One plane's error is not a task-level result.

Map or pad the selected logical block to the physical dimensions explicitly; state which
rows/columns are unused. Do not declare 65,536 independent multibit weights. If exporting
from PyTorch, transpose a Linear layer's usual [output,input] weight array into [input,output].
Use the existing golden quantizer; do not train or requantize just to improve a mapping.

Copy `config/trace_metadata.template.json` to a local input directory, fill its provenance,
and declare previously inspected data as development. Keep input files out of Git by default:

```bash
python3 -m experiments.run trace-screen \
  --bundle experiments/local_inputs/layer_plane.npz \
  --metadata experiments/local_inputs/layer_plane.json \
  --out experiments/runs/E01_layer_plane/screen.json
```

All permutations are fitted on X_cal. Every evaluation run checks exact X_eval@W parity.
The tool reports every predeclared comparator; do not choose a winning mapping using X_eval.
One physical array has one resident row mapping across every activation bit-plane and
input that uses its programmed weights. Pool the relevant calibration traces to fit that
mapping, then freeze it across those operations. Independently optimized per-input-plane
orders are diagnostic oracles unless real reprogramming/routing and its costs are included.
CAR alpha values are comparison arms; select/tune any final choice on calibration only.
The implementation reproduces CAR's grouping rule [S01], not VARA's training or full system.

The report contains counts and activity histograms. Hardware energy, latency, count-error
rate and inference failure remain null. A squared-activity proxy is diagnostic only.
Do not rename quiet-then-balanced comparators into a demonstrated reliability-aware method.

## E02: physical-model preflight

```bash
python3 -m experiments.run preflight --contract experiments/config/architecture.template.json
```

The template intentionally fails physical readiness. Fill a separate local contract with
source references and validation evidence. Completing fields is a declaration, not proof.
See E02 in the experiment plan for the first bounded circuit cases. A target-array netlist
must use the inspected authorized model/port interface; no speculative Spectre command or
unverified port ordering is provided.

## Provenance record for each meaningful run

```bash
python3 -m experiments.new_run --id E02 \
  --hypothesis "Equal-count patterns have a relevant location-dependent readout difference" \
  --command "Record the exact intended NUS command here" \
  --input experiments/config/architecture.template.json \
  --out experiments/runs/E02_example/run_record.json
```

This records command text only. After execution append raw/output hashes, evidence class,
paired uncertainty and a decision in a new analysis record. Update the register, logbook,
claims and CA2 map. Raw runs stay local unless deliberately selected for repository evidence.

## Ising references and a guarded target-kernel contract

`python3 -m experiments.ising_reference verify --out experiments/runs/E09A_NEW/verification.json` checks exact software references, not noisy hardware performance. It uses NumPy only. `python3 -m experiments.ising_reference preflight --out experiments/runs/E09A_NEW/preflight.json` checks the unresolved contract in `config/ising_error_kernel.template.json` and currently exits 2. A scientific target-noise adapter is not implemented. See [the queue](../research/04_screening_queue.md) before a solver campaign.

For the covariance branch, retain parent-input IDs and activation-bit indices alongside the pooled E01 traces. The base occupancy tool does not use those associations or calculate cross-cycle errors; do not infer a complete mapper from an occupancy output.
