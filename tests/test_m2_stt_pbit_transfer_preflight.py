"""Small algebraic transfer tests only: never a device experiment."""
import math
import unittest

from experiments.m2_stt_pbit_transfer_preflight import (
    NOMINAL_LOGIT_PER_V, NOMINAL_V50, SOURCE_DOI,
    logistic, ising_conditional_logit, nominal_input_voltage,
    nominal_probability, pulse_switch_probability,
    explicitly_characterized_or_e2_probability
)


class TestSTTPbitTransferPreflight(unittest.TestCase):
    def test_source_identity_and_midpoint(self):
        self.assertEqual(SOURCE_DOI, "10.1038/s41467-026-72020-8")
        self.assertAlmostEqual(NOMINAL_LOGIT_PER_V, 128.8)
        self.assertAlmostEqual(NOMINAL_V50, 1.852)
        self.assertAlmostEqual(
            pulse_switch_probability(1.852,
                                     slope_per_v=128.8,midpoint_v=1.852),0.5)

    def test_exact_nominal_field_to_voltage_logit_identity(self):
        for beta in (0.001, 0.05, 1, 2):
            for wanted_x in (-10,-4,-1,0,1,4,10):
                h = wanted_x / (2*beta)
                self.assertAlmostEqual(ising_conditional_logit(beta,h), wanted_x)
                self.assertAlmostEqual(
                    nominal_probability(beta,h), logistic(wanted_x), places=12)
                self.assertAlmostEqual(
                    NOMINAL_LOGIT_PER_V*(nominal_input_voltage(beta,h)-NOMINAL_V50),
                    wanted_x, places=11)

    def test_output_monotonicity_and_saturation(self):
        p=[nominal_probability(1.0,float(x)) for x in (-10,-1,0,1,10)]
        self.assertTrue(all(a<b for a,b in zip(p,p[1:])))
        self.assertGreater(p[0],0)
        self.assertLess(p[-1],1)
        self.assertAlmostEqual(logistic(-200),0,places=30)
        self.assertAlmostEqual(logistic(200),1,places=12)

    def test_explicit_residuals_and_no_default_fake_device_parameters(self):
        with self.assertRaises(TypeError):
            explicitly_characterized_or_e2_probability(1,1)
        ideal=nominal_probability(1,0.5)
        mismatch=explicitly_characterized_or_e2_probability(
            1,0.5,actual_slope_per_v=0.95*NOMINAL_LOGIT_PER_V,
            actual_midpoint_v=NOMINAL_V50+0.005)
        self.assertNotAlmostEqual(ideal,mismatch)
        self.assertAlmostEqual(
            explicitly_characterized_or_e2_probability(
                1,0.5,actual_slope_per_v=NOMINAL_LOGIT_PER_V,
                actual_midpoint_v=NOMINAL_V50),ideal)

    def test_bad_inputs_rejected(self):
        for beta,field in ((-1,0),(float("nan"),0),(1,float("inf"))):
            with self.assertRaises(ValueError):
                ising_conditional_logit(beta,field)
        for slope,center in ((0,NOMINAL_V50),(-1,NOMINAL_V50),
                             (128.8,float("nan"))):
            with self.assertRaises(ValueError):
                pulse_switch_probability(1.85,slope_per_v=slope,midpoint_v=center)


if __name__ == "__main__":
    unittest.main()
