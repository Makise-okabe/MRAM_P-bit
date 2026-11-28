# HW02-A: Conditional architectural cost integration

## Status

Offline integration of archived HW01 logic results and
existing registered software quality contrasts.
No new solver trajectories or EDA simulations.

## Hardware

| Format | Logic area (um2) | Dense bits | RTL cases |
|---|---:|---:|---:|
| fp5 | 2760.0 | 24782 | 166 |
| int5 | 2503.0 | 24782 | 164 |
| int6 | 2728.0 | 29732 | 228 |

## Conditional choices

Illustrative assumption: 0.5 um2 per stored bit,
dense triangular storage, +0.5 pp relative tolerance.

| Policy | Family | Certified candidates | Lowest proxy cost |
|---|---|---|---|
| ideal_original | ring | fp5;int6 | fp5 |
| ideal_original | torus | fp5;int5;int6 | int5 |
| ideal_top16 | ring | fp5;int5;int6 | int5 |
| ideal_top16 | torus | fp5;int5;int6 | int5 |
| offset_original | ring | fp5;int6 | fp5 |
| offset_original | torus | fp5;int5 | int5 |

## Interpretation and limits

- Quality is relative to the matched FP64 policy and device regime.
- Generated graph references are best-observed feasible cuts,
  not proven global optima.
- Relative tolerance does not establish absolute solution quality.
- The assumed offset distribution is not physically measured.
- Unregistered contrasts are not treated as failures or passes.
- Area per bit is a sensitivity parameter, not macro characterization.
- No memory peripheral, addressing, routing, gain generation,
  device offset circuit, or complete controller area is included.
- Sparse access scheduling is hypothetical and not synthesized.
- Top-16 payload, host storage and edge-evaluation costs are
  reported separately, not converted into unsupported area numbers.
- Cross-policy total-cost optimality is not established.
- Absolute quality gate remains open.
- Results apply only to the three HW01 hardware candidates.
- No final device-aware representation is certified.

Figure generation: NOT_GENERATED
