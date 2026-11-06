#!/usr/bin/env python3
"""STT-MTJ pulse-p-bit probability interface: source-backed nominal algebra ONLY.

A 2026 experimentally measured STT-MTJ p-bit sigmoid example:
  P(+1|Vin) = logistic(128.8 * (Vin - 1.852 V))
Source: Yang, Grimaldi et al., Nature Communications 17:5368 (2026),
DOI 10.1038/s41467-026-72020-8, Fig. 1e.
The device is pulse-driven (reset + stochastic perturb), not a
continuously fluctuating low-barrier MTJ. These are one literature
illustration's nominal parameters, NOT 100 individual device fits,
GF22FDX characterization or a bounded operating-voltage spec.

For Ising E=-sum_{i<j}J_ij*s_i*s_j, h=0 and ideal Gibbs:
  desired P(s_i=+1) = logistic(2*beta*H_i), H_i=sum_j J_ij*s_j.
Nominal field-to-voltage conversion:
  Vin = V50 + (2*beta*H_i)/slope.
This exactly reproduces ideal Gibbs IF the device is the nominal
sigmoid; it does not create physically meaningful nonideality.

Residual slope/midpoint must be explicitly supplied to inspect an E2
sensitivity example. NEVER invent their distributions or label an
unsourced sweep as E3 device-characterized. NOT a circuit timing model.
"""
from __future__ import annotations

import math

SOURCE_DOI = "10.1038/s41467-026-72020-8"
SOURCE_EQUATION = "Fig. 1e nominal measured sigmoid"
SOURCE_LEVEL = "one published representative transfer example, not device-population evidence"
NOMINAL_LOGIT_PER_V = 128.8
NOMINAL_V50 = 1.852


def logistic(x: float) -> float:
    if not math.isfinite(x):
        raise ValueError("nonfinite logit")
    if x >= 0:
        q = math.exp(-x)
        return 1 / (1 + q)
    q = math.exp(x)
    return q / (1 + q)


def ising_conditional_logit(beta: float, local_field: float) -> float:
    if not all(math.isfinite(z) for z in (beta, local_field)) or beta < 0:
        raise ValueError("finite beta >= 0 and finite local field required")
    x = 2.0 * beta * local_field
    if not math.isfinite(x):
        raise ValueError("nonfinite desired logit")
    return x


def nominal_input_voltage(beta: float, local_field: float) -> float:
    """Illustrative voltage with no validated clipping or DAC limit."""
    return NOMINAL_V50 + ising_conditional_logit(beta, local_field) / NOMINAL_LOGIT_PER_V


def pulse_switch_probability(voltage_v: float, *, slope_per_v: float,
                             midpoint_v: float) -> float:
    """One reset-and-perturb STT-MTJ switching probability from a fit.

    Must pass measured/exploratory slope and center explicitly; caller
    owns provenance and voltage-window validation. No data are sampled.
    """
    if not all(math.isfinite(z) for z in (voltage_v, slope_per_v, midpoint_v)):
        raise ValueError("finite voltage, slope and midpoint required")
    if slope_per_v <= 0:
        raise ValueError("positive switching slope required")
    return logistic(slope_per_v * (voltage_v - midpoint_v))


def nominal_probability(beta: float, local_field: float) -> float:
    return pulse_switch_probability(
        nominal_input_voltage(beta, local_field),
        slope_per_v=NOMINAL_LOGIT_PER_V,
        midpoint_v=NOMINAL_V50,
    )


def explicitly_characterized_or_e2_probability(
    beta: float, local_field: float, *,
    actual_slope_per_v: float, actual_midpoint_v: float,
) -> float:
    """Residual slope/offset are an EXPLICIT caller-supplied assumption.

    E2 unless supported by individually sourced device data, device
    operating window, calibration provenance and population statistics.
    """
    return pulse_switch_probability(
        nominal_input_voltage(beta, local_field),
        slope_per_v=actual_slope_per_v,
        midpoint_v=actual_midpoint_v,
    )


def main() -> None:
    print(f"SOURCE: {SOURCE_DOI} — {SOURCE_EQUATION}")
    print("E0 nominal probability-transfer identity (NOT stochastic MTJ data)")
    for logit in (-6.0, -2.0, 0.0, 2.0, 6.0):
        beta = 1.0
        field = logit / 2.0
        expected = logistic(logit)
        got = nominal_probability(beta, field)
        if abs(got - expected) > 1e-12:
            raise AssertionError(f"mismatched mapping for logit {logit}")
        print(f"logit={logit:+.1f} Vin={nominal_input_voltage(beta,field):.8f} V "
              f"idealP={expected:.9f} mappedP={got:.9f}")
    print("STT-PBIT TRANSFER PRE-FLIGHT PASS — NO DEVICE CHARACTERIZATION")


if __name__ == "__main__":
    main()
