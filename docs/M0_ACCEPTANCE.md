# M0 BPSK MIMO acceptance — OPEN

- [x] Exact ideal Ising enumeration, symmetry, ideal Gibbs correctness from fresh small-N mathematical tests.
- [ ] Implement standalone complex BPSK MIMO and fully specify Rayleigh/AWGN normalization, SNR, channel/noise seeds.
- [ ] Independently verify for ALL 2^Nt bit vectors in tiny 2x2 / 4x4 MIMO that ||y-Hs||² equals Ising E(s), including constant C.
- [ ] Define exact small-N ML bitstring, original residual gap, ground-hit and BER versus TRANSMITTED x separately.
- [ ] Freeze independent channel/noise calibration and held-out frames and SNR/antenna settings; statistical units and nesting.
- [ ] Validate baseline solver against exact ML and correct budget including PT replicas/swaps; Gibbs/PT code has NOT yet been validated for MIMO.
- [ ] Locate relevant p-bit device-response provenance or label any nonideality strictly E2 behavioral.
- [ ] Review prior art on finite precision Ising MIMO, particularly Singh et al. (IEEE TWC, 2022).
- [ ] Predeclare absolute BER/quality floor, time-to-target and paired uncertainty before M1.

**Only BPSK MIMO is an application benchmark.** Retain historical graph/TSP code solely as retired diagnostics or archive; no application evidence from them.

```bash
python3 -m unittest discover -s tests -v
python3 experiments/m0_mimo_reference.py --tx 4 --rx 4 --snr-db 10 --output results/m0_mimo_first
```

The core research remains **low-order FP4/FP6/FP8 coupling**, not the MIMO algorithm itself. No physical device or FP advantage claim is currently established.
