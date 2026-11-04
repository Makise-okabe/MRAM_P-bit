# E11B — verified local student Verilog-A model interfaces (2026-11-04)

**User-executed NUS terminal evidence.** Read-only source-interface check; **no new Spectre read or P/AP current**, no read-retention validation, no 2T1MTJ array read, no measured Ising analog local-field operation.

Executed with **Python 3.6.8**, `spectre -W` reports `23.1.0.403.isr6`. Probe `experiments/e11b_model_interface_probe.py` completed, checked 512 candidate source files without truncation, saved a private JSON in `~/mram_private/E02_256x256/E11/model_interface_20261104_115042.json`.

Two *distinct* student Verilog-A source models found:

1. `~/mram_fyp/cadence/CIM1_SINGLE_CELL/mtj_read.va`, SHA256 `51b2797589f4ec4514f76df8dd2ef8d76ffbf29d1905894d1b23593491141a6d`, module `mtj_read(p,n)`, parameter names `rp, tmr, p_state`.
2. `~/mram_fyp/cadence/CIM1_SINGLE_CELL/models/mtj_read_v0.va`, SHA256 `1d22984b7be5135c07bb5e392d73aa53e1ad42b7c4bdc6d2fc11bb3f313b9a88`, module `mtj_read_v0(top,bottom)`, parameters `rp, tmr, p_state`.

Keyword-token inspection found `rp` only in both; this alone cannot prove absence of time dependence/noise. Found 20 local usage candidates, including `cell_read_transient_energy_pilot.py`, `cim_c03_dot2.py`, `cim_c04_dot4.py`, `cim_c2_fanin.py` and `mram_cim_mc_current_plot.py`. These *historical scripts are interface/readout examples*, not usable 256×256 target electrical measurements. `Yanzhang_CIM/mtj_read_v0/veriloga/veriloga.va` is another Cadence-view candidate and has not been examined.

**Subsequent step:** E11C model-only direct 1mV small-signal Spectre probe in `experiments/e11c_two_state_model_spectre.py`. This tests `p_state=0/1` existence and observable response; it **cannot** establish meaningful P/AP read, retention, access NFET operation, safe bias or Ising CIM. Reusing earlier scripts for an NFET + MTJ test requires checking the source's actual state polarity and intended bias. Model source license/ownership remains to be confirmed by the student; none is uploaded.
