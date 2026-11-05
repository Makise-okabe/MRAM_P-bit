## NEW: ready-to-pull read-only audit
A minimal user-runnable discovery script is now committed at [`experiments/e26b_pex_discovery.sh`](../../experiments/e26b_pex_discovery.sh) (commit `3936ab9562db3398a8c8f74cb5709b92b67867b5`). Run `bash experiments/e26b_pex_discovery.sh` after `git pull --ff-only`. It reports file checksums, rough structural counts, existing R1/R2/MC result filenames and checkpoint hashes. **It does not execute Spectre, inspect actual currents or prove correlation.** A separate optional extended local Python auditor exists for richer structural metadata. Previous statement below that no audit code is tracked refers only to the extended Python auditor.

# E26B — Actual GF 2T1MTJ 4×4 PEX discovered, existing four-BL CIM pilot found

**Date:** 2026-11-05. **Status:** NUS FILE DISCOVERY COMPLETED; physical joint-error measurements NOT YET EXAMINED OR EXECUTED. Do not claim correlation from file names.

## Actual user-run read-only discovery
The NUS console confirmed the following files exist in `~/mram_fyp/cadence`:
- `calibre/xact/M047_GF_4x4_TILE_TEST_PEX/M047_GF_4x4_TILE_TEST.pex.dspf` — original 4×4 xACT physical extraction.
- `calibre/xact/M047_GF_2x2_PEX/M047_GF_2x2_PEX.pex.dspf` — separate 2×2 xACT.
- `lvs_source/M047_GF_4x4_TILE_TEST/M047_GF_4x4_TILE_TEST_source.cdl` — original LVS source.
- `manual_cross5_runs/M047_READ_CIM_PILOT/R1_4BL_SIMULTANEOUS_READ/pex_R1_4BL_read.scs` — existing deck explicitly named **simultaneous 4 BL read** (must audit actual WL/SL/BL stimulus, parallel row activation, sensing output, PEX inclusion, and existing result validity).
- Same R1 folder has `M047_GF_4x4_TILE_TEST_initP.pex.dspf`; `R2_MTJ_LOCAL_MC_PILOT` also has an init-P DSPF; `MC1_CONTROLLED_READ_MARGIN_MC` has init-P/init-AP DSPFs. Names alone do NOT establish physically coupled uncertainty or multiple physical chips.

User also found probable complete-model candidates in `~/MRAM_FYP_Overleaf/outputs`:
- `mnist_stage4a_v2/fp32_checkpoint.pt`
- `mnist_stage4a_v3_15ep/fp32_checkpoint.pt`
- `mnist_stage4a_v3_15ep/stage7b_W4A8_B6_FS31_pilot128train128dev_1epoch_v1.pt`.

**Checkpoint caution:** stage7b name includes `pilot128train128dev_1epoch`, so do NOT silently treat it as the frozen E01 full-network quantized model. Need compare model fingerprints, exact W4A8 quantization, dimensions, non-FC1 weights and biases and confirm whether original E01 frozen evaluator depends on one of the full FP32 checkpoints. Avoid untrusted `torch.load` arbitrary pickle deserialization; use proven NUS project code/trusted sources/weights-only loading.

## Physical integration next gate
1. **Audit in place**, preserve PDK confidentiality: check file SHA/size and `subckt` pins, R/C element counts, R1 deck's PEX reference, active WL/SL/BL drive, actual simultaneous operation and existing result artifacts. Compare R1 DSPF SHA with canonical xACT and MC copies, not assume same extraction.
2. Determine whether R1 actually produced **simultaneous multi-row analog CIM** or only one MTJ read per BL. Four BL independently sensed does not establish shared-circuit correlation by itself. Confirm P/AP programming state masks; all-initP only cannot provide a complete binary neural MAC kernel.
3. Preserve same-device/static-MTJ chip assignment and synchronous multiple-column currents when measuring a joint vector. Couple to signed W4A8 only after mapping read paths; begin with 4×4 paired pilot, not pretend it is fully extracted 256×256 or fill E26A's 8×256×8×8×256 tensor artificially.
4. Identify full network FC2/FC3/logit source and checksum before claiming any classification outcome.
5. Only **after audit** run an authorized physically validated SPICE experiment with specified read stimuli, accepted R/C, actual MTJ models and calibration.

A generic metadata-only audit script `e26b_existing_pex_audit.py` was created and self-tested locally in the ChatGPT session, but at this log commit is **distributed as a conversation-generated artifact**, **NOT yet checked into public GitHub**. Keep its private JSON report and PDK/PEX netlists on NUS. The read-only script does NOT run Spectre and thus reports NO actual multi-column correlations.

## Research impact
This is a meaningful milestone: it removes the *file discovery* blocker in E26A's physical gate. It does NOT yet remove the *joint error tensor* blocker. The strongest realistic next path is to reuse R1 4-BL reader if and only if the actual existing topology/stimulus matches intended 2T1MTJ parallel compute read. No new margin circuit or invented algorithm needed yet.


## E26B NUS audit result confirmed (2026-11-05 09:04 Singapore)
The user's **executed** `experiments/e26b_pex_discovery.sh` succeeded after resolving a safe local untracked-E26A file conflict by backing it up. **NO Spectre run**, only file inventory.

**Main 4×4 GF xACT DSPF:** `~/mram_fyp/cadence/calibre/xact/M047_GF_4x4_TILE_TEST_PEX/M047_GF_4x4_TILE_TEST.pex.dspf`, SHA256 `ca249d4486248cc318f1b4a97a885e7c33d22d28452f8de68b67baa462d49436`, 122969 bytes, 1 subckt, roughly 406 R and 1468 C component lines (regex approximations, **not** total resistance/capacitance). Regex output `WL_TOKEN_LINES=0` **does not demonstrate no wordlines**; likely WLL/WLR pin naming is outside `WL([_<digit)` matches. Require exact top-level pin audit.

**Original four-BL read experiment:** `~/mram_fyp/cadence/manual_cross5_runs/M047_READ_CIM_PILOT/R1_4BL_SIMULTANEOUS_READ/pex_R1_4BL_read.scs`, SHA256 `e6d833de5bd485e7e7022a2e4d9446c349ae91809e4c53710d718449c1f62230`. This directory ALREADY has `R1_IDEAL_currents.csv`, `R1_PEX_currents.csv`, `R1_current_comparison.csv`, `R1_final_summary.txt` and `RUN_IDEAL/RUN_PEX/spectre.log`. Such names are **not yet inspected numerical evidence** of actual simultaneous 4BL or multirow CIM. Inspect stimulus and summary next before any new run.

**Important reuse integrity:** R1 init-P 4×4 DSPF = R2 init-P = MC1 init-P by exact SHA256 `c623dd1b5e909c2b96c6d6b88b0e235298b96598825ae6075238bc62f2761f7b` and identical 123225 bytes, 406 R /1468 C line approximations; MC1 init-AP differs `a15f4802c6a7f99a3685842053639984e0e887c912e2fd9be91f3a4edace92fe`. Original canonical xACT DSPF differs from init-P by SHA and size. **Do not assume the differences are only initial MTJ state** without comparing parsed structural invariants.

**User already has extensive P/AP variability data** under `MC1_CONTROLLED_READ_MARGIN_MC`: `MC1_FORMAL100_paired_1600.csv`, `MC1_FORMAL100_by_location.csv`, `MC1_FORMAL100_analysis.txt`, and independent prior 5-run /80-pair data. Need inspect whether 1600 rows are paired same-chip P/AP across 16 locations, and whether any simultaneous 4BL vector was obtained under same random draw. These remain **unverified interpretations** until schema/provenance reviewed.

**Possible full-network checkpoint candidates found (SHA only, NOT identified as frozen E01):**
- fp32 v2 `971f875242d266e5a5c61dd32af287230a9e0265114eeac3114b64ea5632efaa`
- fp32 v3 15 epoch `455662670e868006c0b3d375f850336fc82f036190a493ea236f2b349034d485`
- stage7b 1epoch pilot W4A8 `788cc1ef7d7ad35395c159385d18574283fd0e07077cbf9a513574bd53e6e095`.
Do not equate model by checkpoint name alone. Frozen E01 bitplane packet still lacks FC2/FC3/bias adapter.

**NEXT READ-ONLY EXTRACTION:** [`experiments/e26b_existing_results_inventory.py`](../../experiments/e26b_existing_results_inventory.py) commit `6d0c43771342542a48ae22aacad87931bf4de2a6` discovers R1 summary/current-comparison CSV schema, R1 deck stimulus, MC1 FORMAL100 summary and columns, E01 manifest model provenance without changing PDK/PEX or running Spectre. User has not yet executed this script. A successful inventory will help decide a small 4×4 physical multiple-column probe; does **not** by itself satisfy the joint count-error tensor needed for E26A.
