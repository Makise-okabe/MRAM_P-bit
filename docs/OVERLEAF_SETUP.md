# Current research report and Overleaf sync

**Authoritative project: https://github.com/Makise-okabe/MRAM_P-bit**

The root main.tex on this repository's **main branch** is the current
FYP report. The prior report repository is a historical archive.
All future FYP report updates belong in MRAM_P-bit.

Report file structure:
- main.tex — only active LaTeX document entry point
- references.bib — scientific citations and specifications
- report/maxcut/10_coupling_matrix_cal_results.tex — completed CAL text and five native TikZ/PGFPlots figures
- report/maxcut/data — frozen source-reported means, documented CI subsets, and static numerical diagnostics
- report/figures — five real rendered PNGs and vector PDFs, created by a figure-only GitHub workflow
- scripts/plot_report_figures.py — the read-only figure generator

To view figures in the connected web editor, ensure it is linked to the
MRAM_P-bit main branch, use its GitHub integration to PULL recent
changes, set main.tex as the main document, and recompile. GitHub
commits alone do not guarantee that the editor has synchronised.

To recreate the physical images locally, without new simulations:

    python3 -m pip install matplotlib
    python3 scripts/plot_report_figures.py --out report/figures

This report intentionally plots only 15/36 source-supported 95% CI
whiskers until the original archived primary and 8-bit summary
tables are supplied for the other 21 intervals. The means for
all 36 graph/format/offset cells are retained. A missing whisker
does not mean a zero confidence interval.

No optimiser run, new synthetic device population, hardware
simulation or held-out graph inspection occurs during a report update.
