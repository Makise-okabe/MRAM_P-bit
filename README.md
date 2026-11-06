# MRAM p-bit FYP — LOCKED low-order floating-point coupling / BPSK MIMO

**Research core:** custom **low-order floating-point FP4/FP6/FP8 coupling** and per-edge/row/tile exponent scale granularity for nonideal MRAM p-bits. Build a bit-true coupling macro and synthesis-backed cost comparison; optimized scaled integers and block floating point are mandatory fair baselines.

**Application:** complex **BPSK MIMO detection** only. It is a benchmark of device-aware coupling quality and hardware cost, **not** an attempt to invent a MIMO detector. Older TSP/Max-Cut/partition/Ising pilot results are excluded. Old task-specific scripts/tests are **removed from the active tree**, but fully preserved on archive/pre-mimo-benchmark-20261106. Active code uses generic exact Ising mathematics and fresh complex BPSK MIMO.

**Question (unchanged):** How should coupling precision and scale granularity be chosen for nonideal MRAM p-bit systems to preserve useful optimization performance at lower implementation cost?

H1 device-dependent useful precision; H2 exponent/scale granularity; H3 conditional scaling with antenna dimensions and SNR. **M0–M5 unchanged.** Floating-point is the design target, not a required performance winner.

See [Architecture and CIM boundary](docs/ARCHITECTURE_CIM_SCOPE.md): **64–128-spin low-order FP coupling tile and RTL/synthesis remain in scope**, but true MRAM-CIM requires actual array-integrated computation; our software currently demonstrates neither a fabricated p-bit array nor a CIM macro.

Read: [Locked roadmap](docs/ROADMAP_LOCKED_2026-11-06.md), [MIMO protocol](docs/M0_MIMO_BENCHMARK.md), [M0 acceptance](docs/M0_ACCEPTANCE.md), [evidence rules](docs/RESEARCH_PROTOCOL.md).

**M0:** independently seeded complex channel/AWGN, exact state-wise ML-to-Ising validation, correct ML vs BER semantics and sampler/reference checks. M1: device-nonideality x FP4/6/8 vs optimized integer/BFP. M2: precision/scale configuration and macro cost. M3: bit-true RTL+synthesis. M4: held-out larger MIMO. M5: report.

No old CIM/ADC/TSP pilot, earlier synthetic pilot or shared-line parasitic data reused. No restricted PDK in this public repository. Active source of truth is GitHub main; existing Overleaf project snapshots do not auto-update.

## M0 command (new)
```bash
python3 -m unittest discover -s tests -v
python3 experiments/m0_mimo_reference.py --tx 4 --rx 4 --snr-db 10 --output results/m0_mimo_first
```

Prior art already demonstrates finite-bit Ising-MIMO couplings (Singh et al., IEEE TWC 2022); our contribution must specifically be device-aware low-order floating-point scale/architecture and implementation evidence.
