# E19 — GF access-NFET + custom MTJ adjacent-count nonideal readout gate
Date: 2026-11-04. **STATUS: EXECUTABLE PREPARED; NUS SPECTRE NOT YET EXECUTED. NO physical result is claimed.** This experiment is requested after E17/E18 identified spatial count-current overlap as the make-or-break assumption for E15.

## Specific question
With m=16 selected rows and k=16 stored P-state weights, does the sensed current from a **nominal GF 22FDX+ hvtnfet + student-owned mtj_read_v0** row circuit reliably distinguish n=7 and n=8 true intersections when identical-count weights/activations are placed at different row positions? These are possible adjacent outcomes in the legal [0,16] interval. A one-dimensional threshold decoder on a sense current can only be guaranteed exact for all allowed masks if the current sets are disjoint and correctly ordered.

## New delivered code and QA
User-visible package in current conversation: `E19_GF_NFET_MRAM_nonideal_validation.zip` (11.4 KiB, SHA256 `4d9e4bf628dd2b872d6e2ae7d7990c36a447bdca34105c02cd0409f4818e8a85`). Python script `e19_gf_nfet_mtj_nonideal_count_gate.py` SHA256 `1656e467139c2cd1ce9f1ceaf7673cb57cc3adbe78433f35022eb17793b2451b`. The full executable is in the conversation package, NOT in the GitHub repo. It passed local Python3.6 syntax parsing, mock netlist-generation/unit tests, CAL/DEV pattern distinctness, DC-PSF ASCII parser and scalar-threshold classifier selftest. It has **not** run with the GF simulator from this session; source audit cannot substitute for NUS Spectre.

Script modes: `selftest`, `probe`, `run`. The NUS run locates a *student-origin historical* `input.scs` containing `hvtnfet` and `mtj_read_v0` and uses its nominal MOS instance l=20nm w=80nm and resolved PDK includes **without copying or uploading model content**. The student MTJ two-terminal Verilog-A model is checked against SHA256 `1d22984b7be5135c07bb5e392d73aa53e1ad42b7c4bdc6d2fc11bb3f313b9a88`; P=1 Rp5k and AP=0 Rap10k. Builds 32 nominal transistor+MTJ parallel read branches sharing an explicitly resistive BL, with all inactive WL set to 0 V. The old voltage levels 50mV VREAD and 0.8V WL are preserved as **historical experimental settings**, not requalified nondisturb biases.

## Experimental protocol (pre-registered)
- Two count classes n=7 and n=8, both **m=k=16**, 32 positions, random CAL and DEV spatial assignments with no reused mask pairs. CAL independently fits a scalar threshold from class-mean currents; DEV strictly held out. Default first run 4 CAL +4 DEV per class, repeat with at least 12+12 per class on success.
- NUS parameterized segment resistances r=0,1,5 Ω/segment are *user-chosen hypothetical spatial wiring*, **not extracted GF 22FDX+ PEX**; only the NFET model is GF-native. No macro parasitics, physical sense amplifier, ADC comparator voltage offsets, stochastic MTJ, real read energy or trained-inference metrics.
- Record per-mask `VREAD:p` DC currents, NUS Spectre exit codes, CAL-current class separation, DEV range overlap and DEV error for a CAL-trained midpoint threshold.
- Strong null: r=0 nominal identical NFET/MTJ devices should produce position-invariant count currents, assuming netlist is electrically correct. Distinct n values should be ordered in current. If even the null fails, fix topology and parser, not invent physical effects.
- A verified no-overlap result for finitely many masks is a *feasibility screen*, not universal proof of exact decoding or success for other PVT corners.

## Gate / disposition
This E19 is a **physically motivated diagnostic**: it can establish nominal GF access transistor nonideal response under explicitly assumed BL wiring, unlike E18's passive-only ladder. It is NOT a complete test of E15's lower net ADC energy against DIB. If the real circuit has overlap at realistic independently justified R, E15 cannot claim guaranteed exact-count decoding from one scalar current; either add a distinct calibrated decoder/error fallback and benchmark its cost or reject E15. If it separates, the next E20 must run a calibrated, reference-overhead-aware ADC threshold tree with matched metadata/cost and actual extracted RC, comparing against input-only+support-pruned and a DIB-style controller.

## Reproduce on NUS after transferring .py to experiments/
```bash
cd ~/MRAM_Path_Finding
python3 -m py_compile experiments/e19_gf_nfet_mtj_nonideal_count_gate.py
python3 experiments/e19_gf_nfet_mtj_nonideal_count_gate.py selftest
python3 experiments/e19_gf_nfet_mtj_nonideal_count_gate.py probe
python3 -u experiments/e19_gf_nfet_mtj_nonideal_count_gate.py run \
  --rows 32 --m 16 --k 16 --nlo 7 --nhi 8 \
  --cal-per-count 4 --dev-per-count 4 --rs 0,1,5 \
  --chunk-size 16 --vread .05 --vwl .8 --timeout-sec 240
```
All generated decks, original PDK includes and raw data remain private under `~/mram_private/E02_256x256/E19`. Only summary numbers should be pasted back; do not upload private model files.
