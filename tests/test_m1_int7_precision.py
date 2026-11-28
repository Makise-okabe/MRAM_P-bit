"""INT7 extension and frozen-format regression checks."""
import unittest
from decimal import Decimal
from types import SimpleNamespace

from experiments.m1_precision_codebooks import (
    WIDTHS, build_global, describe_codebook, fit_global_scale,
    levels, scalar_quantize,
)


class TestInt7Precision(unittest.TestCase):
    def test_int7_symmetric_range_rounding_and_saturation(self):
        description = describe_codebook("int", 7)
        self.assertEqual(description["min_represented"], -63)
        self.assertEqual(description["max_represented"], 63)
        self.assertEqual(description["min_code_unused"], -64)
        self.assertEqual(description["scale_bits"], 32)
        for value, expected in [(2.5, 2), (3.5, 4), (-2.5, -2),
                                (63, 63), (64, 63), (-64, -63)]:
            self.assertEqual(scalar_quantize(value, "int", 7, 1.0), expected)

    def test_int7_exact_source_scale_and_matrix_symmetry(self):
        graph = SimpleNamespace(n=3, edges=(
            (0, 1, Decimal("63")), (0, 2, Decimal("-62")),
            (1, 2, Decimal("1")),
        ))
        representation = build_global(graph, "int", 7)
        self.assertEqual(representation["scale"], 1.0)
        self.assertEqual(representation["coefficient_mse"], 0.0)
        self.assertEqual(representation["nominal_one_copy_dense_total_bits"], 53)
        for i, j, value in representation["edges"]:
            self.assertIn((j, value), representation["adjacency"][i])
            self.assertIn((i, value), representation["adjacency"][j])

    def test_seven_bits_are_integer_only(self):
        for family in ("fp", "bfp", "unknown"):
            with self.subTest(family=family):
                with self.assertRaises(ValueError):
                    describe_codebook(family, 7)
                with self.assertRaises(ValueError):
                    scalar_quantize(1.0, family, 7, 1.0)
                with self.assertRaises(ValueError):
                    fit_global_scale([1.0, 2.0], family, 7)
        with self.assertRaises(ValueError):
            levels(7)

    def test_legacy_campaign_roster_and_code_values_are_preserved(self):
        self.assertEqual(WIDTHS, (4, 5, 6, 8))
        self.assertEqual(levels(4)[-1], 6.0)
        self.assertEqual(levels(6)[-1], 28.0)
        self.assertEqual(levels(8)[-1], 480.0)
        self.assertEqual(scalar_quantize(0.75, "fp", 4, 1.0), 1.0)
        self.assertEqual(scalar_quantize(-32.0, "int", 6, 1.0), -31.0)
        self.assertEqual(describe_codebook("bfp", 6)["scale_bits"], 8)


if __name__ == "__main__":
    unittest.main()
