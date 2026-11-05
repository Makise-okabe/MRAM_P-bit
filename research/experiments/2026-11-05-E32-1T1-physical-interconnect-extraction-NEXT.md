# E32 — 1T1MTJ physically grounded interconnect handoff (NO arbitrary-R sweep)

**Status 2026-11-05: proposed physical implementation milestone, not executed.** Architecture: user-selected **1T1MTJ** CIM. Historical `M047_GF_4x4_TILE_TEST` 2T1 local-floating SL DSPF CANNOT be reused as new 1T1 physical topology. E31 completed: on real GF transistor nominal Spectre model with *ASSUMED* 0.25 Ω per BL row segment and 0.25 Ω shared return, frozen E30 CAL input-Q achieved 0/36 errors on 36 new 256-row×4-column DEV read patterns (including 18 new spatial distribution types). Global count decoder 15/36 and simple categorical area-offset 6/36. This is NOT a PEX-derived 1T1 result, independent-chip reliability, or evidence a digital correction policy is novel or necessary.

## Nonnegotiable deliverable
**An extracted, electrically connected 1T1-specific 256-row representative BL/WL/SL route (ultimately 4 columns), with actual GF metal-layer geometry, widths, lengths, vias, and extracted R/C**, and a traceable mapping to the 256-row transistor+student static-MTJ read circuit. Ideally a GF-layout-qualified one-select-NFET series MTJ bitcell; if no authorized physical 1T1 MTJ layout cell is available, *do not pretend otherwise*. A permitted layout-only geometric MTJ landing-pad/abstract interface plus external static MTJ Spectre model is a **CMOS+wire-only PEX hybrid**, not a GF production 1T1 eMRAM macro or full MTJ PEX.

### What a student should actually build in NUS Cadence/Calibre
1. Inspect the preexisting student Cadence `Yanzhang_CIM/tb_CIM1_1T1MTJ` schematic, actual `mtj_read_v0(top,bottom)` two-terminal model and GF access transistor pins. Record exact ordering and safe 50mV read, 0.8V WL as *provisional* until transistor/MTJ read-disturb/operating limit verified. The prior behavioral MTJ source has no automatically guaranteed physical layout view.
2. Create/review a real **1T1MTJ cell schematic and layout representation** with exactly one GF NFET and one MTJ, and explicit `BL`, `WL`, `SL` terminals. Define body/well and unselected WL terminations. Determine physical MTJ layout/signoff support from the licensed GF PDK/supervisor BEFORE assuming Calibre LVS can match it. Do not substitute historical 2T topology or use its RC as the new target.
3. Build a repeated **256 physical-row, at least 4-column routing structure** or a physically extracted representative BL/WL/SL metal geometry with actual cell pitch. Supply actual GF BEOL levels, via stacks, metal width and routing. Every unselected 1T1 location remains in the electrical schematic even when unselected.
4. Run Calibre DRC/LVS (where supported) and xACT PEX of the **metal routing and CMOS**; track the qualified scope precisely. Archive DSPF privately on NUS, with model deck/wrapper hash, layout path, extractor tool/version and verification results. A synthetic sequential-ladder in `E30` is NOT PEX.
5. Extract 256-row BL and SL path R/C: `R_BL(row→sense)`, per-segment R distribution, `C_BL`, `R_SL` and shared-return network, physical WL branch capacitance/driver loading; include extracted coupling caps only if solver can handle them. Compare real values against E30 ASSUMED `0.25 Ω/segment`, `0.25 Ω common SL`. Determine whether those values were realistic, optimistic, or exaggerated. Never force a larger R to get errors.
6. Embed the extracted physical interconnect into the same matched nominal GF 1T1 static-MTJ Spectre source/weights and 24-active-row masks. Validate actual simultaneous 4-column topology, branch-terminal polarity, KCL, source drivers, and convergence; compare ideal and physically grounded read timing/currents. If actual BL/SL RC is tiny and Q leaves zero decoded count error, report the negative result and retire N2 selective recomputation for this configuration.
7. Only after real physical RC and legal read, expand row activity and multiple independent chip/dynamic read conditions as supported; **actual ADC transfer function and complete signed W4A8 plane mapping** are needed before N2 neural-accuracy claims. E31's 36 input masks are not 36 independent chip trials.

## Minimal E32 result handoff
Report:
- `layout_cell_path`, exact `BL/WL/SL` pin ordering, authorized PDK device/MTJ model provenance;
- physical cell and wire geometry, PDK metal/via stack used, 256-row pitch and sensor end;
- DRC/LVS/PEX **scope**, success/blocked reason, xACT netlist private path + SHA;
- extracted resistance summaries: 256-row path RBL near/far, local segment median/range, RSL shared return and per-column differences, BL/WL/SL C/coupling;
- analog state/safe read-bias assessment; exact matched Spectre test run names and current vector outputs;
- explicit claims: `GF_compact_NFET=True`, `student_MTJ_behavioral=True`, `actual_1T1_PEX=False` until the extraction truly exists.

## Decision and scope guard
E31 results are a **software-calibration success in a constructed large circuit**; there is no reason to launch additional arbitrary-R sweeps to manufacture residual count errors. The next milestone is a **real metal RC value**. A large ideal schematic alone or a 256×256 flat netlist does not constitute physical 256×256 PEX. Do not import historical 2T1 R1/MC1/PEX as 1T1 numbers. If the GF PDK does not permit a 1T1 MTJ physical cell, explicitly document a CMOS/wire-only hybrid and obtain Prof Fong's approval for its intended evidence scope.
