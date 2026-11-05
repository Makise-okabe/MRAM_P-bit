# Overleaf source of truth — BPSK MIMO low-order FP scope

GitHub default main is the authoritative FYP report source. Its main.tex title should read:

**Device-Aware Low-Order Floating-Point Coupling for MRAM-Based p-Bit Ising Machines**.

The application benchmark is complex BPSK MIMO detection only. FP4/FP6/FP8 coupling, device nonideality and hardware scale/accumulation are the research objects. Prior TSP/graph application code is stored on archive/pre-mimo-benchmark-20261106, not main.

To create a new independent Overleaf project: New Project -> Import from GitHub -> select Makise-okabe/MRAM_P-bit (default main). Choose main.tex and pdfLaTeX.

Overleaf import creates a snapshot; already created projects do not automatically refresh when GitHub main changes. Do not accidentally sync an old Overleaf-specific branch or upload November 5 starter ZIP.
