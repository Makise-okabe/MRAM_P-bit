# MRAM P-Bit FYP — Low-Precision Coupling Architectures

NUS Electrical and Computer Engineering | Research reset: 5 November 2026

**Supervisor:** Prof. Kelvin Fong. **Status:** working research proposal; no physical or algorithmic improvement has yet been demonstrated.

## Research question
How can low-precision coupling representations reduce hardware cost while preserving optimization and sampling quality in non-ideal MRAM-based p-bit networks?

## Workstreams
1. P00: prior-art audit and device-response feasibility.
2. P01: exact small-N Ising energy and asynchronous Gibbs reference.
3. P02: optimized fixed-point vs low-bit float vs shared-exponent coupling formats at matched cost.
4. P03: response distortion, mismatch, stochastic variability, and credibility checks.
5. P04: bit-true coupling macro and architecture/cost audit.
6. P05: scaling, held-out workloads, sensitivity and failures.

## Evidence rules
- Do not bring earlier experiment data, fitted device parameters, or hardware cost assumptions into this work.
- Software examples are not MRAM device evidence. Use separate labels for mathematical derivation, software simulation, behavioral modeling, authorized circuit simulation, and extracted circuit evidence.
- Evaluate candidate states using the **original, unquantized** Ising energy; optimize fixed-point baselines before comparing.
- Never claim novelty or savings without an adequate literature and hardware-baseline comparison.
- No restricted foundry material, private netlists, passwords, or unreleased manuscripts in this public repository.

## Files
- `main.tex`: Overleaf-ready preliminary paper outline.
- `references.bib`: verified foundational reading.
- `docs/RESEARCH_PROTOCOL.md`: hypotheses and experimental gates.
- `docs/OVERLEAF_SETUP.md`: import an independent new Overleaf project.

**Full six-page LaTeX research proposal, smoke-test code, tests and importable ZIP** are maintained in the dated ChatGPT handoff from 2026-11-05. The expanded ZIP is the report authoring source; this GitHub branch is the isolated initial working scaffold.

No legacy results or code have been imported into this branch's current working tree. The dated archive branch preserves old work.
