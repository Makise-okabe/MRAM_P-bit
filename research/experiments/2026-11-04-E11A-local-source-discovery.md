# E11A — NUS model-source discovery (user-executed, 2026-11-04)

**Evidence status:** Source path discovery only. No new MRAM electrical results, read current, P/AP state initialization, approved-source verification, multirow analog computation, or physically extracted 256×256 validation.

## NUS execution
- The first `experiments/e11_operator_gate.py` run failed before output because `argparse.add_subparsers(required=True)` is unsupported by the local Python **3.6.8**. The subsequent missing JSON/CSV were consequences of that failure, not a Spectre issue.
- Python 3.6 compatibility was fixed in GitHub commit `b99932e0900ab2173d2fe16f5a7fe0acd1578ad3`.
- After updating, user executed `python3 -u experiments/e11_operator_gate.py audit` successfully.
- Local report: `~/mram_private/E02_256x256/E11/source_audit_fixed_20261104_114547.json`.
- `OLD_GF_NATIVE_PEX: True`; **two unverified model filename candidates** found:
  1. `mram_fyp/cadence/CIM1_SINGLE_CELL/mtj_read.va`
  2. `mram_fyp/cadence/CIM1_SINGLE_CELL/models/mtj_read_v0.va`
- `CUSTOM_MODEL_VERIFIED: False`, `READ_OPERATOR_VALIDATED: False` are correct **not-yet-verified** flags, not evidence the candidates are unusable.
- The historical 4×4 PEX instantiates PDK native `mtj_fls`, not automatically either of these models. The 16×16 zero-bias PEX-tile assembly and 256×256 generated hierarchy therefore do not yet validate the revised student-MTJ target.

## Next immediate action
User will run `experiments/e11b_model_interface_probe.py`, which extracts **only** the local student-model interface, parameter names, keyword clues, file hashes, and candidate usage paths, without exporting model source, GF PDK content, or guessing safe read bias. It was mock-tested and Python-3.6 syntax checked locally; NUS execution is still pending.

After confirming the actual model implementation and authorized circuit/read interface, build the **smallest** nominal P/AP Spectre read, establish nondisturb and common-sample current contrast, then run controlled paired-row reads. Model path discovery alone cannot establish an Ising analog local-field computational primitive or novelty.
