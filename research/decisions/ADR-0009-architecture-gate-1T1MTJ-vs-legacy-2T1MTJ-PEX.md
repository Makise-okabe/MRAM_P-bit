# ADR-0009 — Do not substitute historical 2T1MTJ PEX for a new 1T1MTJ CIM target

**2026-11-05 | Architecture clarification raised by user. STATUS: architecture decision pending formal scope confirmation with Prof Fong, but E26B's 2T1MTJ-to-target substitution is explicitly disallowed.** The current research README does not actually freeze a 1T1MTJ or 2T1MTJ physical CIM cell. The user flags the difference and questions the unsupported assumption that the old 2T1MTJ is our new primary array.

## Correct distinction
- **Old physical array:** previously user constructed GF 22FDX-PLUS `M047_GF_4x4_TILE_TEST` 2T1MTJ *local-floating-source-line* topology, DRC/LVS and xACT PEX. Historical read/write/simultaneous-four-BL R1 data belong to that architecture. R1, R2, MC1 PEX shares a traceable init-P DSPF file; a file inventory is not a general CIM MAC qualification.
- **E19–E24:** constructed single-access-NFET/static-MTJ **1T1-like** shared-column 32-branch circuit with **manually assumed** 0–5Ω/segment resistors, nominal GF access transistor model, not a physical 1T1MTJ 256×256 PEX and not the old 2T1MTJ PEX. E24 correction behavior does not establish a physical 1T1 target.
- **Proposed new physical architecture:** if primary CIM array is **1T1MTJ**, it requires its own valid cell connectivity, select/BL/SL/WL read biases, mixed P/AP states, power/read-disturb assumptions, layout-derived parasitics and multicell read. The additional device in historical 2T1 and distinct local-floating SL lead to physically non-equivalent transfer functions.

**Do not directly use old 2T1MTJ PEX RC, raw current, spatial errors, or MC1 P/AP read distributions to calibrate/validate a newly chosen 1T1MTJ CIM architecture.** The difference is fundamental, not a minor file-format conversion. Do not claim an old 4×4 2T1 PEX read as the new target's physical covariance.

## What remains legitimately reusable
- GF licensed environment and permitted access NFET transistor models; appropriate MTJ model only with project authorization/provenance.
- Workflow: Spectre, Calibre DRC/LVS/xACT, device/bias sanity checks, data export protocols; 2T1 PEX may be illustrative counter-architecture/control if **clearly labeled**, not the target.
- E19–E24 are 1T1-like mechanism **screens** and error-control software; actual 1T layout/interconnect must replace their assumed resistor ladder.
- E01 frozen MNIST W4A8 signed arithmetic and E26A exact FC1 software reconstruction remain architecture-independent math. The physical mapping and error kernel must be rebuilt for any new architecture.

## Why 1T1MTJ can be more suitable (conditional)
A one-select-FET + MTJ structure is a simpler circuit baseline for parallel selected-row bitline current accumulation, minimizing unjustified added transistor topology/cell area. This does NOT automatically establish valid parallel WL operation, actual GF foundry-qualified bitcell, correct sensed current, acceptable read disturb or an efficient macro. A 2T topology can be justified only by an explicit target macro requirement or measurable read/write/compute role of its second FET. The GF historical local-floating 2T device cannot be conflated with arbitrary 2T read/write separated cells found in literature.

## Revised experiment priority
1. **Confirm architecture:** 1T1MTJ analog current-sum CIM vs foundry-native 2T1MTJ local-floating SL; record actual per-cell pin current paths and reason for choice. If one-transistor selected, officially retire R1/MC1 2T1 as physical **target** input (can inspect as historical comparator only).
2. **1T1 physical minimum:** single-cell GF authorized NFET+MTJ read P/AP validation (voltages, currents, read-disturb), build 2×2/4×4 multiple-row read layout with matched ideal/PEX testbench; extract real parasitics. Do not create a flat 256×256 PEX without pilot.
3. **Scale to representative 16/32-row physically extracted 1T1 column and multiple columns** preserving shared networks and fixed-chip variation; determine if cross-column errors really correlate; verify common WL/BL/SL paths.
4. **System:** only then provide joint count-error measurements for E26A (conditional marginal controls should also account for spatial position/Q); full W4A8 inference after matching complete frozen downstream weights and biases.

No new PEX or physical result claimed by this ADR.
