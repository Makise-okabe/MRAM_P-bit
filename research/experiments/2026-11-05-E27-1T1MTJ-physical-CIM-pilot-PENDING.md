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
