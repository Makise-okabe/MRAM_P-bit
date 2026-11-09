# Current research report and Overleaf sync

**Authoritative project: https://github.com/Makise-okabe/MRAM_P-bit**

The root main.tex on this repository's **main branch** is the current
FYP report. The prior report repository is a historical archive.
All future FYP report updates belong in MRAM_P-bit.

Report file structure:
- main.tex — only active LaTeX document entry point
- references.bib — scientific citations and specifications
- report/maxcut/10_coupling_matrix_cal_results.tex — completed CAL text and five native TikZ/PGFPlots figures
- report/maxcut/20_heldout_m5_results.tex — independent M5 dense-held-out results, paired CIs and native PGFPlots figure
- docs/M5_HELDOUT_DENSE_20261109.md — validation and data provenance
- report/maxcut/data — frozen source-reported means, documented CI subsets, and static numerical diagnostics
- report/figures — five real rendered PNGs and vector PDFs, created by a figure-only GitHub workflow
- scripts/plot_report_figures.py — the read-only figure generator

To view figures in the connected web editor, ensure it is linked to the
MRAM_P-bit main branch, use its GitHub integration to PULL recent
changes, set main.tex as the main document, and recompile. GitHub
commits alone do not guarantee that the editor has synchronised.
The M5 results chapter is included from the root main.tex, so a fresh
pull of the `main` branch followed by recompilation is sufficient to
render its native plots; no host-generated PNG is required.

To recreate the physical images locally, without new simulations:

    python3 -m pip install matplotlib
    python3 scripts/plot_report_figures.py --out report/figures

The CAL plot currently has 15/36 source-supported 95% CI whiskers;
the missing 21 interval bounds were separately recovered from the
original host-side sources but have not been imported into the report
data mirror yet. The means for
all 36 graph/format/offset cells are retained. A missing whisker
does not mean a zero confidence interval.

The completed M5 study used the dense held-out graph; the remaining
sparse held-out graph is untouched. This GitHub/Overleaf report update
does not itself run an optimiser, create a device population, or inspect
another graph. The M5 raw CSV/PNG/PDF archives remain local to the
experiment host until separately uploaded.
