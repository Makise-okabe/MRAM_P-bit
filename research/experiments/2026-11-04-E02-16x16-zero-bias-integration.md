# E02 16×16 zero-bias hierarchical PEX-tile integration — 2026-11-04

**Evidence:** User-provided NUS Spectre terminal output, not a ChatGPT-hosted electrical solve.

**New-run results:** `experiments/e02_zero_bias_pex_hierarchy.py --size 16 --run` generated a fresh 16×16 hierarchy from 16 instances of the existing 4×4 extracted tile (256 physical MTJ sites). Spectre 23.1.0.403.isr6 reported exit code **0** and "spectre completes with 0 errors, 3 warnings, and 9 notices." The exact three warnings require review. No analog read measurements, MTJ P/AP programming, ADC decoding, spatial comparison, or read-disturb test was performed.

**Known limitations:**
- Uses a historical 4×4 PEX *topology* as a verified engineering building block, **not historical 8-cell or single-column measured results**.
- Intra-tile parasitics are present, but inter-tile BL/SL/WL wires have **zero extraction and ideal joins**.
- Zero bias only; no safe read operating point has been frozen.
- This does **not** validate a physically extracted 16×16 or 256×256 macro, read margin, cross-column interference, or any H1/F3/F7 novelty.
- The surrounding Bash script performed `RC=${PIPESTATUS[0]}` after a separate command, producing an empty `RC` despite the simulator printing `E02_SPECTRE_EXIT: 0`. Therefore its subsequent refusal to generate the full 256×256 netlist was **a shell status capture error**, not an electrical simulation failure.

**Next engineering actions:** (1) inspect Spectre warnings and solver output; (2) generate (do not yet simulate) the 256×256 ideal-join hierarchy comprising 4096 extracted 4×4 tiles; (3) independently validate read-bias/model constraints and state programming on a new testbench; (4) add independently justified full-length BL/SL/WL distributed parasitics and verify against newly extracted larger tiles before target-array positional inference.

**Model-size expectation:** direct 4×4 replication uses 4096 tile instances, 65,536 cells, and (before hierarchy optimization) nominally 6,012,928 capacitor instances + 1,662,976 resistor instances + 196,608 subordinate instance cards based on source-tile card counts; this is an elaboration budget, not a completed full-array Spectre run.
