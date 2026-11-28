# Post-CA2 workbench checkpoint — 29 November 2026 (SGT)

Student-authorized continuation of the 20 November study. Current working title: **Bits Worth Storing: Device-Aware Coupling Precision in STT-MTJ Probabilistic Ising Machines**. Question: Does physical p-bit device quality change how many coupling bits are worth storing, and how should this guide hardware implementation? Historical completed evidence and the original protocol remain unchanged; this checkpoint supersedes their old stop notices only for the work explicitly described here.

## DEV01 — CLOSED / NO-GO

Three historical nominal reproductions succeeded. The subsequent 12-case bounded feasibility experiment (four noise-free controls and eight noise-enabled trials including repeated seeds) completed. Every case remained AP. Noise-free controls did not reproduce nominal switching at the previously observed transition; thus intrinsic stochastic switching was **not tested conclusively**, not shown absent. Statistical mismatch variables exist in the wrapper, but switching-relevant mismatch is unconfirmed; the executed feasibility experiment contained no MC runs. No additional Spectre runs, device characterization or debugging are authorized. This is a rejection of the PDK parameter-source route within the feasibility budget, not a claim of deterministic MTJ physics. Raw PDK materials remain local under NDA. Evidence basis: student-reported terminal results, not independently audited raw logs.

Preferred alternative: group measured per-device STT-MTJ response data (reported 480 devices and three operating voltages), subject to access, operating-protocol compatibility and publication permission. Request joint sensitivity/offset distributions, residuals and conditions. Evaluate published curves with student approval if access remains unavailable at the 5 December fallback gate. No claim that data has been received or permission granted.

## HW01 — mapped logic complete, verification pending

Student-reported NUS server output, 29 November SGT: three Genus 15.22 synthesis jobs succeeded on bose01, using NangateOpenCellLibrary typical, shared illustrative 10 ns constraint and medium effort. One 99-term serial datapath; finite FP5 E2M2 with decoded integer /4, signed symmetric INT5/INT6; one externally supplied Q4.28 gain, common Q6.12 output rounding and clipping. One global binary32 scale, no physical memory macro.

| Format | Cells | Mapped area (reported library area units, nominal square micrometres) | Row area | Accumulator bits | Triangular bits | Duplicated-row bits | Torus CSR bits | Torus bitmap bits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FP5 | 1460 | 2760 | 229 | 13 | 24782 | 49532 | 5741 | 11932 |
| INT5 | 1335 | 2503 | 180 | 12 | 24782 | 49532 | 5741 | 11932 |
| INT6 | 1426 | 2728 | 197 | 13 | 29732 | 59432 | 6141 | 12332 |

FP5 vs INT6: +32 area units (+1.17% from rounded reports), -4950 triangular stored bits (-16.65% including scale). Illustrative linear memory-area break-even 32/4950 = 0.00646 area units/bit, excluding memory peripherals, address/control and routing; not a measured memory macro or total chip area. Row difference accounts for total difference at displayed precision. INT5 has less mapped logic than FP5 at equal storage width. Timing reports not reviewed. The 558 generated RTL test cases (166/164/228) have not been simulated; only software codebook checks and synthesis are reported passing. No new Max-Cut solver runs. No claim of device-aware cost optimality.

Local evidence directory relative to workbench: `results/hw01_20261128T172900Z`; successful synthesis subdirectory `genus_fixed.S7YAkc`. Actual RTL, testbenches, manifests and reports remain on NUS server and require local archive/push. This checkpoint records the terminal summaries only, not a verified raw-data archive.

## Resume

- Python: existing `pbit` shortcut on login node; no Genus needed.
- Hardware: use existing `mram` launcher to enter CentOS 7 container on bose01 with repository directory as argument; set `GENUS_HOME=/apps/eda/cadence/GENUS152`, prepend its bin to PATH, export USER and LOGNAME from id -un. Successful Genus startup and mapping already demonstrated. Avoid login-host legacy library and license network failures.
- Next work: verify all 558 RTL cases and inspect existing timing reports; archive original HW01 evidence without resynthesis. Then matched memory/access cost integration. In parallel obtain measured data; device–precision map awaits physical parameters.
- No new device simulations. No repeated solver or synthesis runs without a specific justification. No report/main branch edits in this checkpoint.
