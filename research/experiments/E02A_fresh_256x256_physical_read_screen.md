# E02-A — first NEW physical-array experiment (no retired read data)

**Research target:** physically meaningful 256×256 GF 22FDX eMRAM CIM, 65,536 MTJ positions. **Evidence status:** planned; **no Spectre simulation has been run by ChatGPT**.

## Question and falsification logic

> When two read masks represent the **same ideal binary count and P/AP composition**, does their spatial placement on a real 256-row BL/SL/WL network materially change sensed current, settled response or decoded count?

The experiment should either (a) identify a concrete uncorrected physical dependence worth a design intervention or (b) reject positional reliability as the research motivation. It is **not** intended to demonstrate that an existing mapping algorithm is novel.

## Physical architecture gates

1. Work only with authorized GlobalFoundries access transistor models and the authorized student's MTJ source. Do not commit PDK files, model text, licensed parasitic decks or credentials to this public repository.
2. Verify the legitimate bitcell topology, including every terminal and local/floating SL connection. Do NOT assume a 1T1MTJ or 2T1MTJ pin order from an older project. Check safe read voltage/current, WL bias, intended sample time and no unintended write.
3. Create a NEW unit-cell read test, then one DRC/LVS-verified 16x16 or 32x32 tile. At least one tile must have extracted BL/SL/WL parasitics. Build the 256×256 hierarchy from verified tiles; 16x16 tiles imply 16×16 = 256 physical instances, 32x32 tiles imply 8×8 = 64. Keep outer connections explicit.
4. Specify whether the 256×256 study is fully schematic-explicit, PEX-informed hierarchical, or actually full-macro PEX. One populated 256-cell column with equivalent loads for other columns is **only a reduced proxy** until checked against the complete array connectivity.
5. Freeze one selected column and a nominal P/AP state assignment. Keep all unselected cells physically present with a defined state. Other columns must be either explicitly simulated or rigorously reduced to checked equivalent loads. Use the same sense circuit, driver and references for paired cases.

## First matched-pattern matrix

*Row indices are zero-based and must be translated into correct physical row order. 'Near' means electrically close to the sense terminal, not simply row 0.*

| Case | Active mask | P/AP among active | Purpose |
|---|---|---|---|
| Z0 | none | -- | leakage/offset and unselected loading |
| N4 | four nearest rows | 2 P / 2 AP | small read near |
| F4 | four farthest rows | 2 P / 2 AP | exact-count distant pair |
| S4 | rows near 0,85,170,255 | 2 P / 2 AP | spread same count |
| N16 | 16 nearest rows | 8 P / 8 AP | moderate read near |
| F16 | 16 farthest rows | 8 P / 8 AP | matched distant pair |
| S16 | 16 evenly spaced rows | 8 P / 8 AP | spatial moment check |
| N32 | 32 nearest rows | 16 P / 16 AP | only after safe read/headroom checks |
| F32 | 32 farthest rows | 16 P / 16 AP | matched count |
| S32 | 32 evenly spaced rows | 16 P / 16 AP | matched count |
| P4/AP4 | same four spatial positions | all P versus all AP | new-array current step estimate |
| C1 | one selected read at the near/far endpoints | P and AP separately | new-array position-dependent single-cell reference |

12–24 nominal cases were proposed in the CA2 draft; the initial matrix is a designed starting point, not executed data. If any fan-in is outside verified device limits, **do not run it**. Validate all state assignments, source-line topology and unselected-cell behaviour before treating masks as equivalent.

## Solver and physical controls

- Fix **nominal devices** first and disable random mismatch. This isolates spatial/parasitic topology before per-device variation.
- Compare full BL/SL/WL extracted RC against an explicitly labelled lower-R/ideal-wire reference while keeping the *same cell/sense/driver model* (do not reuse retired small-column results).
- Retain full transient currents, BL/SL/WL near and far voltages, driver state, selected and unselected branch currents where tractable, sampled sense-node output and read-disturb/MTJ state.
- Check current conservation including capacitive/displacement branches during transient; at settled state compare DC currents and supply/ground branches. Tighten solver tolerance/time-step to verify the result is numerical-convergence stable.
- Use the **same sampling criterion** for all matched patterns, determined from new target settling and ADC timing. Record near/far `I_sense(t)`, `I_sense(t_sample)` and settling time; do not pick the sample post-hoc for each arm.
- If a real ADC is not available, export raw analog currents and label any offline decoding as `offline_decoder`. Do not claim silicon-bit-error rates.
- Separately check effects of fixed WL driver versus idealized WL, to distinguish wire placement from driver headroom. If local SL floats, include all its relevant connections.
- Only after nominal gate: introduce new chip-specific persistent mismatch and independent, physically justified temporal noise. Keep each chip realization fixed across every compared mask.

## Required experimental record per case

`case_id, subckt_source_sha256, array_netlist_sha256, tile_PEX_sha256, topology_description, row_mask_sha256, state_mask_sha256, active_rows, selected_P, selected_AP, sense_column, near_end, read_bias, WL_waveform, sample_time, sampled_current_A, stable_current_A, settle_time, BL_near_V, BL_far_V, SL_near_V, SL_far_V, sensor_ADC_code_if_real, KCL_steady_residual, MTJ_retention_status, simulator_version, run_timestamp_utc`.

Store proprietary inputs and raw netlists privately in the authorized NUS environment, not in the public repo; upload only legal redacted summaries and numerical outputs.

## Analysis and decision

Define a new-array one-count contrast `DeltaI_count` for appropriate same-activity P/AP substitutions and a normalized position discrepancy:
`D_pos = |I_near - I_far| / |DeltaI_count|`.
If `DeltaI_count` is ill-defined under shared loading, report the full conditional current distributions instead. A value >0.5 would matter for an *ideal midpoint* reference under simple assumptions, but actual ADC thresholds and calibration determine a real code crossing.

Falsify a spatial mechanism if matched read patterns collapse under proper full-array geometry and practical calibration, or if differences are much smaller than new target ADC/thermal/temporal uncertainty. If the mechanism survives, compare against **per-column affine**, **row-weighted / SEC-style** correction, **ADC reference tuning**, and simple shuffling before proposing a new circuit or mapping method.

**No post-hoc novelty certification:** downstream F3 is a distinct cross-cycle decoded covariance problem, not automatically explained by within-cycle spatial dispersion. The Ising F7 branch remains possible but is not part of this run.
