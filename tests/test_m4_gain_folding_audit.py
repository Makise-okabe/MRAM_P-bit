"""M4 pure arithmetic and accounting checks; no Graph or device model needed."""
import math
import unittest

from experiments.m4_gain_folding_audit import (effective_scale, folded_gain,
                                                memory_budget, sigmoid)


class TestM4GainFolding(unittest.TestCase):
    def test_formal_logit_factorization(self):
        for family, scale in (("fp", 4.25), ("int", 4.25), ("bfp", 8.0)):
            for acc in (-44352, -3069, -37, 0, 28, 3069, 44352):
                for beta in (0.00001, 0.015, 1.5):
                    h = acc * effective_scale(family, scale)
                    ref = 2 * beta * h
                    folded = folded_gain(family, scale, beta) * acc
                    self.assertTrue(math.isclose(ref, folded, rel_tol=2e-15, abs_tol=2e-10))
                    self.assertAlmostEqual(sigmoid(ref), sigmoid(folded), places=12)

    def test_bfp_scale_is_power_of_two(self):
        self.assertEqual(effective_scale("bfp", 0.125), 0.125)
        for bad in (0.0, -1.0, float("inf"), 1.25, 2.0**128, 2.0**-129):
            with self.assertRaises(ValueError):
                effective_scale("bfp", bad)
        with self.assertRaises(ValueError):
            folded_gain("fp", 1.0, 0.0)

    def test_sigmoid_is_stable(self):
        self.assertEqual(sigmoid(1000), 1.0)
        self.assertEqual(sigmoid(-1000), 0.0)
        self.assertAlmostEqual(sigmoid(0), 0.5)

    def test_100_spin_memory_accounting_is_not_silicon_area(self):
        cost = memory_budget()
        self.assertEqual(cost["coefficient_issue_slots_for_frozen_attempts"], 4_950_000)
        self.assertEqual(cost["formats"]["fp"]["one_copy_plus_metadata_bits"], 29_732)
        self.assertEqual(cost["formats"]["int"]["mirrored_plus_metadata_bits"], 59_432)
        self.assertEqual(cost["formats"]["bfp"]["one_copy_plus_metadata_bits"], 29_708)
        with self.assertRaises(ValueError):
            memory_budget(99)


if __name__ == "__main__":
    unittest.main()
