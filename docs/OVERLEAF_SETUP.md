# Overleaf import

1. Download **Code → Download ZIP** from [MRAM_Path_Finding](https://github.com/Makise-okabe/MRAM_Path_Finding).
2. Go to https://www.overleaf.com, choose **New Project → Upload Project**, and select that ZIP.
3. In Overleaf Menu set **Main document** to `main.tex` and **Compiler** to `pdfLaTeX`.
4. Bibliography is `references.bib` (BibTeX). Compile twice if citations are unresolved.

Local compile: `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`.

The GitHub repository is public. Do not upload restricted PDK models/netlists or credentials. GitHub source import is Overleaf-ready; it does not itself create a separate Overleaf cloud project or guarantee synchronization.
