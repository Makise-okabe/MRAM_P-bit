# E24A — nested ADC bit-width and full-scale falsification on E19 currents

**Status: SCRIPT PREPARED; NUS execution PENDING.** 2026-11-04.
No measured E24A outcome is asserted. This is an analysis of **existing** E19 GF
access-NFET + student MTJ Spectre currents, with **assumed 0/1/5 ohm/segment**
bitline resistance, NOT physical 256x256 array PEX, ADC hardware, or energy.

## Narrow research question

Can the observed E19 adjacent-count (n=7 vs n=8) decoding accuracy worsen as
ADC bit width increases under a fixed, pre-declared full-scale range and offset?
If so, is this only an effect of a **particular decoding/calibration procedure**,
or is there any evidence relevant to a physical system-design constraint?

Do NOT claim that finer, nested quantization intrinsically loses information:
for matched analogue inputs and fixed range, q_b = floor(q_{b+1}/2). A finer
quantizer can always emulate the prior coarser decoder. Finite-CAL threshold
re-fitting, code-centre assumptions, and fixed hardware decode rules may worsen
observed DEV accuracy even though an inherited decoder preserves it.

## Exact NUS Singularity run

Use the established checkout and the two existing private E19 files:

~~~bash
set -euo pipefail
cd "$HOME/MRAM_Path_Finding"
git pull --ff-only
python3 -m py_compile experiments/e24a_e19_nested_adc_falsifier.py
python3 experiments/e24a_e19_nested_adc_falsifier.py --selftest

OUT="$HOME/mram_private/E02_256x256/E24A/E24A_$(date -u +%Y%m%dT%H%M%S)_$$"
mkdir -p "$OUT"

python3 -u experiments/e24a_e19_nested_adc_falsifier.py \
  "$HOME/mram_private/E02_256x256/E19/E19_GF_NFET_MRAM_20261104T144120_179/e19_results.json" \
  "$HOME/mram_private/E02_256x256/E19/E19_GF_NFET_MRAM_20261104T144132_384/e19_results.json" \
  --bits 3,4,5,6,7,8 \
  --full-scales-uA 28,29 \
  --offsets-uA 0 \
  --out "$OUT/e24a_results.json" | tee "$OUT/e24a_console.log"

echo "=== OUTPUT ==="
echo "$OUT"
~~~

If the 28/29 uA ranges cause code saturation, that is reported explicitly;
do not reinterpret saturated data as an intrinsic precision failure. A
separate CAL-predeclared range sweep may be needed.

## Methods

Every input file and per-R arm is analysed separately, preserving both E19
independent runs and the same mask/current samples across all ADC settings.
Rows and profiles are checked for matching case id, true count, split and
mask hash. Files must have run_state=FINISHED. Input hashes are recorded.

- Uniform, nested, ideal quantizer with ncode=2^bits and saturation.
- Frozen physical range at 28 or 29 uA, offset 0 uA. No actual ADC noise.
- **Midpoint**: CAL mean-current midpoint, apply it to reconstructed ADC
  code-centre currents (no per-bit fit).
- **CAL-fit**: best monotone code threshold fitted exclusively on CAL.
- **Inherited**: re-use the previous bit width's CAL-fitted threshold on the
  current bit width's coarsened digital code. This is an exact nesting control
  and must have identical DEV predictions to prior width CAL-fit.
- Report DEV errors for all three methods, CAL training errors, saturation,
  and (diagnostic only) distance to nearest ADC code edge.

All DEV cases must be scored at every fixed setting, not selected post hoc.
Output is private and must never be committed with raw currents.

## Pass/stop gates

1. **Protocol gate:** Selftest PASS; nesting identity holds; proper CAL/DEV
   separation; zero unreported saturation.
2. **Observation gate:** Does midpoint or independently CAL-fitted threshold
   show worse DEV errors on higher bits at fixed full-scale and offset?
   Compare exactly the same cases. Check both E19 runs and each R arm.
3. **Interpretation gate:** If the inherited coarse decoder restores previous
   accuracy, any observed regression is **calibration/decoder-dependent**, not
   an intrinsic information loss. This alone is NOT algorithmic novelty.
4. **Novelty gate (not tested here):** An inexpensive, physically grounded
   predictor or hardware-constrained design rule must beat calibration-aware
   competitors on many unseen masks/count levels and representative PEX.

E19 includes only n7/n8 at m=k=16, few independent masks, no ADC layout
or actual PEX; no claimed universal error rate, network classification,
energy saving, or innovation.

## Required feedback

Return the NUS console log (or the private E24A JSON with current paths
redacted). The next decision is whether to stop the ADC-edge hypothesis,
or design a more discriminating multi-count physical experiment.
