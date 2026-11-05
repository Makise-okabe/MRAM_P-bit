# E27 — New 1T1MTJ CIM architecture: physical-read gate before joint-error algorithms
**Architecture chosen by user:** 2026-11-05, 1T1MTJ analog CIM. **Status:** user choice frozen; no new 1T1MTJ 4×4 layout, extracted model or GF multi-column test has been demonstrated. Prof Fong signoff pending.

## Physical target and provenance

A **student-built one-access-FET + one-MTJ series bitcell**, using **authorized GF 22FDX compact CMOS transistor models** and a separately authorized student-owned static MTJ model. 1T1-like E19–E24 has GF transistor-level Spectre currents with a **manually ASSUMED 0–5 Ω/BL segment**; it is NOT layout PEX and does not establish read disturb or MTJ variability. This prototype is *not* a foundry-qualified GF embedded-MRAM macro unless shown separately.

Proposed conceptual cell: one BL node, one MTJ, one access NFET (gate WL), one SL node; the exact transistor D/S and MTJ polarity, voltage conditions and sharing of SL and WL drivers must be derived/verified with a valid schematic/model, not asserted from the historical 2T1 local-floating source-line array. Example `BL -> MTJ -> NFET -> SL` is only a candidate wiring. With multiple WL active, same BL current may represent an approximate P/AP conductance sum; test if the sense operation is legal/stable, and ensure unselected cells have defined bias.

**Reject outright:** using old `M047_GF_4x4_TILE_TEST` 2T1MTJ DSPF or MC1 read current as if it were 1T1 physical extraction.

## E27A (execute first, no Spectre)
`python3 experiments/e27a_1t1_cim_preflight.py --selftest`
`python3 experiments/e27a_1t1_cim_preflight.py`
Script checks the existing student static MTJ and E24 data SHA/size, discovers a bounded sample of existing 1T-like Spectre decks, and outputs private 4×4 ten-mask CSV + JSON manifest in `~/mram_private/E27_1T1/`. It does not inspect/provide licensed model body or modify prior files. All mask rows are **logical** row indexes; map to electrical near/far using the actual final sense position.

### Frozen pilot fixed P/AP cell pattern

4×4 columns, row-wise checkerboard. Use P as logical 1 for **composition bookkeeping only**, not a hardwired current direction or simulator `initial_state` value without checking model polarity.

| Physical row candidate | C0 | C1 | C2 | C3 |
|---|---|---|---|---|
| 0 | P | AP | P | AP |
| 1 | AP | P | AP | P |
| 2 | P | AP | P | AP |
| 3 | AP | P | AP | P |

Matched row-activation masks:
- no selected rows Z0.
- each single row S0/S1/S2/S3.
- N2=[0,1], F2=[2,3], D2=[0,3], D2'=[1,2]. All **m=2** and each of four columns has exactly one P and one AP among active rows (so match ideal count and P/AP composition). `near/far` labels depend on actual physical sense location; e.g., when sense sits near row3, swap N2/F2 nomenclature.
- ALL4=[0,1,2,3] sanity and allowable fan-in check.
- For each mask compare fully instantiated 4-column array at the **same read bias and same MTJ state pattern** under schematic wire-only idealization and fresh actual PEX. All unselected BL/SL/WL connections and periphery remain present. A single-column-vs-four-column experiment needs a declared inactive-column termination and identical observable definition.

This matrix is a **stimulus design**, not simulator result. It tests a measurable spatial mechanism while keeping count and state composition fixed. With no read error, this is still scientifically useful negative evidence.

## E27B physical work (stop if failure)
1. **Single 1T1MTJ read cell** (authorized model and schematic): P and AP current, WL enable and disable, BL/SL reference voltage, read current sign, transient settle, constant MTJ state/no disturb over intended time. Verify same states over repeated reads. Use small bias sweep only within model-qualified conditions, NOT arbitrary 1.8 V WL borrowed from old writes.
2. **Schematic 2×2 and 4×4 one-FET cells** with shared/declared BL, WL and SL routes, every unselected cell in both arms. Conduct simultaneous **two-row** activation and four column current read; prove KCL and defined sensing currents. Compare near/far matched states under ideal wires.
3. **Layout 4×4**, DRC/LVS/xACT; save true 1T1 PEX DSPF privately; read actual BL/SL/WL R/C and any coupling/driver effects. Keep published traceability hashes, avoid proprietary source in public repo.
4. **Matched ideal-versus-PEX** with identical cells, MTJ models, drivers, biases, fixed P/AP map, solver settings and sample time, plus nonlinearity/count controls. Report raw transient current vector `[I_BL0,...,I_BL3]` at synchronized times. Check P/AP discrimination for one cell then analog MAC count classes.
5. **Statistical correlation** is NOT identifiable merely from four concurrent deterministic currents. Add physically justified per-chip persistent MTJ/CMOS variation (same draws across all paired masks, proper model provenance) and input variations; test simultaneous joint-vs-independent response with position-conditioned marginal controls before claiming cross-column covariance.
6. Scale physically only after 4×4 passes: 16/32-row representative layout, 2+ columns, and then the 256×256 hierarchical target with separately validated inter-tile paths. A 32-row schematic with assigned 5Ω ladder is NOT a physically extracted macro.

## What result feeds E26A?
A complete actual per-case joint vector of multi-column read currents + calibrated integer count errors for consistent input activation masks and fixed MTJ-state assignments, with physical array/location and chip IDs, correct W4A8 signed plane mapping. E26A requires `(8,256,8,8,256)` count-error tensor at its full FC1 target; a 4×4 pilot validates a kernel but does **not** fill that array. No fabricated tensor from historical 2T1 results or synthetic copied one-column draws.

## Minimal record per physically run case
`cell_model_hash,cell_topology,layout_name,PEX_hash,mismatch_chip_id,case_id,activation_mask,m,mixed_mtjs_P_AP,BL_SL_WL_driver_bias,sample_time,all_four_BL_currents_A,settle_times,unselected_leakage_A,read_disturb,simulator_version,run_id`

## Gate outcome
- **GO:** 1T1 supported with verified actual PEX shared path and measurable physically relevant nonlinearity; produce multi-column error kernel and begin compute-level algorithm ablations against strong controls.
- **NO-GO:** illegal parallel read, unrepresentative 1T1 layout/periphery, negligible physical effect, or lack of device variation; document falsification rather than fake results.
- **Scope:** the new algorithm must reduce signed multibit / neural inference errors at equal compute/energy/latency or calibration cost, not simply improve P/AP read margin.

## E27A USER-EXECUTED PASS; E27B/C BATCH PREPARED (2026-11-05)

**Actual NUS E27A result:** user ran \`e27a_1t1_cim_preflight.py\`:
- Selftest PASS for 10 4×4 masks with matched near/far P/AP composition.
- Student static MTJ model 376 bytes, SHA256 \`1d22984b7be5135c07bb5e392d73aa53e1ad42b7c4bdc6d2fc11bb3f313b9a88\`.
- Frozen E24 existing data 1,054,271 bytes, SHA256 \`0b8519fcc69bf77466d36f85fd70424675f5ce2b38a62e56b64074db3d6b8dc8\`.
- Existing NUS E19 1T1-like single-column \`input.scs\` 58,998 bytes, SHA256 \`e3841c4954a300e213a0d3d924d5ae40b2a0a799b57a32d54daf3fb43cf47c45\`, identical in two preexisting NUS MC_CURRENT_REAL runs.
- Private E27A frozen case manifest \`~/mram_private/E27_1T1/E27A_1T1_4x4_preflight_manifest.json\` and matched masks CSV.
- **No Spectre, new 1T1 PEX or GF correlation** was executed in E27A; these claims remain explicitly BLOCKED.

**New one-shot bounded electrical next batch:** [\`experiments/run_e27bc_nus.sh\`](../../experiments/run_e27bc_nus.sh). Run \`git pull --ff-only\` and \`bash experiments/run_e27bc_nus.sh\` on NUS. Prerequisites:
- [\`e27c_1t1_physical_handoff_audit.py\`](../../experiments/e27c_1t1_physical_handoff_audit.py) is read only: student VerilogA module/port names, exact source and historical deck file hashes, instance metadata (not foundry contents), local layout candidates.
- [\`e27b_1t1_reference_gf_spectre.py\`](../../experiments/e27b_1t1_reference_gf_spectre.py) is a **16-case nominal GF NFET + student static MTJ single-column** matched-m=2, k=2, n=1 Spectre reference, using **four independent 4-row circuits** (one per conceptual column) and an ASSUMED 0Ω per-segment wire. It relies on exact local E19 v2 generator SHA \`b6bec40bc234fac406d191229146354a5fe47c6969fb6db6a672e607ddf83e54\` and frozen model sha above, then checks real raw Spectre outputs, all 16 source currents, and private results with hash. This is a schematic **zero-resistor null-control**, **NOT a simultaneous 4-column read**, NOT a physically extracted 1T1 4×4, and NOT a correlation test. No other assumed-R sweep or margin-optimization is run.
- 0.05V Vread / 0.8V Vwl are **historical screening biases** from E22 contract, not independently verified safe READ/retention operating conditions for new layout; validate before any physical prototype claim.
- If local E19 v2 generator is absent, script prints a blocker and runs no Spectre. A Spectre failure should be investigated in private log, not converted into a physical conclusion. **Neither E27B nor E27C has been user-executed as of this note.**

**Physical next step after batch:** build single 1T1MTJ cell and 4×4 macro with defined one-NFET-in-series wiring, shared WL and column BL/SL; independently verify read polarity, P/AP control, selected/unselected source/bitline terminations; DRC/LVS/xACT **new 1T1** and extract actual RC; matched two-row and four-column PEX current vector at synchronized sample time. Only those actual currents can advance physical error-correlation E26A.

**IMPORTANT zero-signal gate:** At assumed R0, if selected P/AP count is identical, the ideal-wire nominal currents may be identical. This is expected and not failure of code. The intended purpose is to verify genuine GF transistor currents and the 1T1-like independent-column reference, not to generate fake spatial effects.
