# ADR-0007 — Reintegrate the actual extracted 2T1MTJ array immediately after E24

**Date:** 2026-11-05. **Decision:** Stop expanding the simplified 32-row assumed-resistor model; validate on actual 2T1MTJ extracted geometry before major claims or more synthetic-model algorithm sweeps. This is a next-stage plan, **not an executed PEX-CIM test**.

## Three distinct hardware evidence tiers
1. **Earlier user FYP platform:** GF 22FDX-PLUS local-floating source-line **2T1MTJ 4×4 physical layout**, assembled via 2×2 tiling, earlier reported DRC/LVS complete and xACT/DSPF extraction. This belongs to the prior Cadence FYP work. PEX read/write location studies do exist historically; the exact active DSPF file and top module need to be rediscovered on NUS, with traceability. Earlier E20/E24 scripts did **not** use these extracted DSPFs.
2. **E19–E24 controlled mechanism screen:** a constructed **32-row, one access NFET per branch** shared bitline, GF `hvtnfet` compact transistor model and student-owned static `mtj_read_v0`; series R/segment **assumed** 0–5Ω; isolated single column; no physical source-line topology, 2T1MTJ PEX, neighbor coupling, actual ADC or MTJ variation. The *currents* are from real NUS Spectre circuit simulations, but not the intended physical array.
3. **Intended proposed target:** 256×256 = 65,536 MTJ positions, with physically credible BL/SL/WL routing and multi-column read periphery. Prior E02 256×256 arrangement was ideal-connected modeled subblocks (or software schedule), not a fully extracted 256×256 GF macro. Must not call it 'physical GF 256×256 PEX'.

## E24 actual supporting evidence (do not overclaim)
All **3,168** nominal GF transistor simulation cases completed: 792 distinct spatial mask identities across m=8,12,20,24 with k=16 and assumed Rs 0,3,4,5Ω. The Q-suffix load feature coefficient was trained on *old m=k=16 E22 CAL* and transferred without refitting that coefficient; **per-(m,R) ADC current window and count reference centroids WERE calibrated using NEW CAL** for *every* method. At R5 7bit mathematical ADC, fresh DEV counts /528: raw124, near59, centroid26, Q7; at high m24 R5 Q still 7/108 errors. Not task-level error or power, and not technology-specific R boundary. Exact [E24 result](../experiments/2026-11-05-E24-COMPLETE-cross-activity-GF-Q-transfer.md).

## Mandatory physical validation milestones
**P0, now — Locate actual layout and netlist:** Identify Virtuoso library/cell/view for 4×4 2T1MTJ, xACT/DSPF paths, extracted instance pins and names (BL, source lines, WL, PW), real NFET/MTJ model wrappers, resistance/capacitance unit conventions, read bias and sense path. Keep proprietary foundry files private. Find exact artifact paths and SHAs, not guessed macros.

**P1 — Use true 4×4 extracted read:** Run *matched ideal vs complete PEX* with same actual 2T1MTJ topology on several binary activation and MTJ state masks; verify individual P/AP currents, read-disturb constraints, available parallel-read operation, current extraction node and neighbor-column effects. Interpret weak four-row spatial effects as small-real-geometry physics; do not impose nominal 5Ω as though measured. A layout may have been qualified for writing/read and still need explicit CIM parallel read validation.

**P2 — Physically extended column:** Build an actual **2T1MTJ** 16- or 32-row row-column read structure, including local floating SL, WL, BL, sources, drivers and ADC input. Use physically laid out/extracted BL/SL resistances/capacitances; compare numeric input-only Q vs simple corrected baseline, exactly matched sensing assumptions. Test 32-row grouping versus 256-row long line before scaling Q. If flat 256×256 PEX is not practical, justify hierarchical validated RC extraction and show multiple cross-column spot-checks. No virtual 'ideal-connected tile' mistaken as inter-tile PEX.

**P3 — Device/corner and readout constraints:** Adopt fixed-per-chip MTJ mismatch samples across reads, process and temperature as appropriate, compare physical read-current distributions and sampled count margins; implement/test the relevant ADC/reference topology or explicitly price its approximate quantizer assumptions, include Q extraction/digital control overhead. Nominal 5% MTJ spread is a hypothetical scenario until validated, not PDK sigma.

**P4 — Task-level:** Map true complete W4A8 signed network and bias into bitplanes without silently assuming one logical model weight=one MTJ; validate full inference versus clean quantized reference using held-out images and chips. Report classification, count decoder and electrical outcomes separately.

## Supervisor questions
- Is the previously completed 4×4 local-floating 2T1MTJ PEX an appropriate extracted **topology validation** starting point for proposed multirow CIM?
- What read operation and source-line bias are physically feasible for simultaneous activation while preserving MTJ state?
- Is a new extracted 32-row representative column plus validated hierarchical 256×256 RC sufficient for CA3/CA4, or does supervisor require 256×256 flat PEX?
- Which exact authorized GF MTJ model and periphery/ADC are expected in the reported final platform?

**No physical array integration experiment has been launched by this ADR.**
