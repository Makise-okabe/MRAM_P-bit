"""E0 source-weight diagnostics are NOT solver results."""
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from experiments.biqmac_maxcut import load_rudy
from experiments.biqmac_weight_audit import weight_statistics


class TestWeightAudit(unittest.TestCase):
    def graph(self, source):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        path=Path(d.name)/"toy.rudy"
        path.write_text(source)
        return load_rudy(path)

    def test_tiny_wide_range_and_zeroed_edges(self):
        g=self.graph("4 4\n1 2 1\n2 3 -100000\n3 4 3\n1 4 0\n")
        st=weight_statistics(g)
        self.assertEqual(st["min_nonzero_abs"],"1")
        self.assertEqual(st["max_nonzero_abs"],"100000")
        self.assertEqual(st["abs_weight_ratio"],"100000")
        self.assertEqual(st["positive_nonzero_edges"],2)
        self.assertEqual(st["negative_nonzero_edges"],1)
        self.assertEqual(st["naive_int6_zeroed_edges"],2)
        self.assertTrue(st["all_original_nonzero_weights_integral"])

    def test_small_integer_exact_int6_unit_scale(self):
        g=self.graph("3 2\n1 2 -10\n2 3 10\n")
        st=weight_statistics(g)
        self.assertEqual(st["naive_int6_zeroed_edges"],0)
        # maxabs/31=10/31; all coefficients reconstructed exactly.
        self.assertEqual(Decimal(st["naive_int6_normalized_abs_error"]),0)

    def test_zero_edges_and_decimal(self):
        g=self.graph("3 2\n1 2 -0.5\n2 3 0\n")
        st=weight_statistics(g)
        self.assertFalse(st["all_original_nonzero_weights_integral"])
        self.assertEqual(st["min_nonzero_abs"],"0.5")
        self.assertEqual(st["max_nonzero_abs"],"0.5")
        self.assertEqual(st["abs_weight_ratio"],"1")

    def test_no_nonzero_edges(self):
        g=self.graph("2 1\n1 2 0\n")
        st=weight_statistics(g)
        self.assertIsNone(st["abs_weight_ratio"])
        self.assertIsNone(st["naive_int6_zeroed_fraction"])


if __name__=="__main__":
    unittest.main()
