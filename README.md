# MRAM P-bit FYP — Fresh research baseline, 6 November 2026

**Locked research question:** How should coupling precision and scale granularity be chosen for nonideal MRAM p-bit systems to preserve useful optimization performance at lower implementation cost?

The goal is a **device-aware configuration rule and coupling macro**; float is a candidate, not a mandated winner.

**H1:** device-dependent useful precision. **H2:** optimized scale granularity vs per-element exponents. **H3:** conditional size dependence.

See [locked roadmap](docs/ROADMAP_LOCKED_2026-11-06.md), [evidence policy](docs/RESEARCH_PROTOCOL.md), and [M0 gate](docs/M0_ACCEPTANCE.md).

**Reset:** No previous CIM/ADC/sensing margin, reported TSP FP4/INT4, or earlier assistant-pilot results can be reused. Earlier Git history is preserved for CA2; a pre-reset snapshot is at archive/pbit-bootstrap-pre-M0-20261106.

**Locked benchmark scope (no change to H1/H2/H3):** primary weighted Max-Cut; secondary balanced graph partitioning/bisection; independent weighted spin-glass controls for generalization. Constrained TSP is kept **only as a small-N mathematical mapping and solver diagnostic**. No TSP runs will support H1/H2/H3 or architecture claims.

New M0 software reference: exact small-N Ising, Max-Cut, legacy-independent TSP mathematical checks and asynchronous Gibbs tests. Run:
    python3 -m unittest discover -s tests -v
    python3 experiments/m0_reference.py --family maxcut --size 8 --output results/m0_maxcut_demo
    python3 experiments/m0_paired_solver_gate.py --family maxcut --size 8 --instances 4 --trials 4 --cycles 250 --output results/m0_paired_maxcut_demo

A separate **balanced graph partitioning benchmark implementation is pending**; do not interpret the existing TSP code as that benchmark.

M0 mathematical validation is underway, but full benchmark acceptance and physical provenance are NOT yet complete. This project makes no numerical device or hardware-efficiency claim. Outputs are gitignored. Public repo: no licensed PDK, private netlist or unpublished confidential material.

Import GitHub default main into Overleaf to read the updated main.tex; Overleaf and GitHub remain separate projects unless explicitly synced.