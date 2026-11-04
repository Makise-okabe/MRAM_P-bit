# E11E NUS reproduction — 2026-11-04

## Evidence and provenance

**Student-executed NUS Singularity output** (not assistant hardware simulation). Python 3.6.8, script SHA256 `863f1d3f0ce41801caf51fa7a4d1c09725e44856a414927bd80f42ce0aae218f` from package. Raw local artifacts:
- `~/mram_private/E02_256x256/E11/E11E_ising_20261104_123413.json`
- `~/mram_private/E02_256x256/E11/E11E_SPECTRE_20261104T123419/spectre_results.json`
- Local Spectre deck and raw currents in that same `E11E_SPECTRE_...` directory.

These local paths were provided in the user's terminal output and are NOT assumed to exist in GitHub. Only research documentation is saved here.

## E11E Python / Ising software result

Selftest PASS across C(12,4) mask properties, zero-R parity, one-shunt KCL and PSF parser; this is not an electrical measurement.

| Policy | Exact optimum hits/200 | Gap | Field MAE | Analog reads / restart |
|---|---:|---:|---:|---:|
| exact digital incremental | 150 | 0.720 | 0 | 0 (different hardware operations) |
| none | 151 | 0.650 | 0.2195 | 192 |
| split all | 146 | 0.740 | 0.1768 | 384 |
| random | 151 | 0.650 | 0.2100 | 240 |
| near×far count | 150 | 0.670 | **0.2092** | 240 |
| centroid | 150 | 0.660 | 0.2089 | 240 |
| suffix-Q | 149 | 0.680 | 0.2088 | 240 |
| cross-segment | 151 | 0.650 | 0.2093 | 240 |

Exact digital baseline mean coefficient terms = 67.6 initialized + 102.8 incrementally updated per restart, **not directly comparable energy with analog source-read counts**. Paired graph-cluster cross minus count success bootstrap interval [0,0.015] in this small experiment. Cross-segment splitting does not beat simple count on field MAE, and a +1/200 optimum-hit point estimate is not a meaningful solver win. **Reject Ising superiority claim for current E11E rule.**

## E11E new Spectre model-only ladder result

- 31 P/AP masks; FULL/NEAR/FAR = 93 independent circuits in one deck.
- `E11E_SPECTRE_EXIT: 0`, 31 parsed cases, numeric parity with independent Kirchhoff solver. Maximum absolute difference 3.3457801416544863e-20 A.
- Selected reported currents:
  - Z0: 0
  - NP: 1.98019802e-7 A
  - NAP: 9.95024876e-8 A
  - FP: 1.8957346e-7 A
  - FAP: 9.7323601e-8 A
  - NF: full 2.9343034e-7 A, split 2.95343403e-7 A, difference 1.91306255e-9 A
  - MATCH_A: full 5.64110466e-7 A, split 5.7353298e-7 A, difference 9.42251401e-9 A
  - MATCH_B: full 5.6134886e-7 A, split 5.76040492e-7 A, difference 1.46916319e-8 A
- One benign Spectre warning: `SPECTRE-294`, saving 1409 signals; optimize save directives. Simulation otherwise `0 errors, 1 warning, 2 notices`.
- **Interpretation:** proves Kirchhoff parity for the *assumed* one-ended ladder with r=25 Ohm/segment, direct two-terminal static student MTJ, 1mV mathematical source. Does **not** measure GF access NFETs, local floating SL, actual sense amplifier/ADC, extracted macro R/C, MRAM read disturb, stochastic MTJ or advantage in Ising solver.

## Decision for Prof Fong discussion

1. A mathematically motivated electrical interaction exists in the *constructed network* and numerical Spectre confirms it.
2. A weight-blind cross-segment adaptive split trigger is an explicit policy, but the strong count/centroid/random baselines are competitive or better for Ising field accuracy. **No algorithmic novelty or task improvement is established**; do not rename known IR-drop correction.
3. Next gate is **E11F GF NFET + student-owned MTJ**, using original local `cim_c03_dot2.py`, `cim_c04_dot4.py`, `cim_c2_fanin.py` only as topology leads. Audit the exact licensed transistor model and original SL/BL/WL connections before generating a new deck. Compare no-load/controlled shared-load, near/far P/AP, identical readout, and actual corrected decision quality against count-trigger and exact digital cost.
4. If the physically legal read operation lacks sufficiently large nonlinearity or Ising advantage, choose Directions 1+2 as the provisional main line and use electrical mechanism to guide an actually distinct mapping/prediction policy rather than keep tuning E11D.

### E11F preflight diagnostic (paste at NUS to identify *user-authored* circuit construction)

```bash
cd ~/mram_fyp/cadence/CIM1_SINGLE_CELL
python3 - <<'PY'
from pathlib import Path
import re
for name in ('cim_c03_dot2.py','cim_c04_dot4.py','cim_c2_fanin.py','cell_read_transient_energy_pilot.py','cim_c0_two_cell.py'):
    p=Path(name)
    print('\n====',name,'====')
    if not p.exists():
        print('NOT FOUND');continue
    lines=p.read_text(errors='replace').splitlines()
    match=re.compile(r'hvtnfet|nfet|mtj_read_v0|VREAD|VWL|SL|BL|ahdl_include|design_wrapper|spectre|include|pex',re.I)
    rows=[(j+1,s.strip()) for j,s in enumerate(lines) if match.search(s) and not s.strip().startswith('#')]
    print('FILE_LINES',len(lines),'MATCHES',len(rows))
    for no,s in rows[:32]:print('%4d %s'%(no,s[:190]))
PY
```
This prints only selected lines from student-authored Python; do not print/sync licensed model source. No prior circuit currents are promoted as new target evidence.
