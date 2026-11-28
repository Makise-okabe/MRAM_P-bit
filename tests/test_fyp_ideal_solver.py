"""Meaningful parity and signed-latest-tie checks, using tiny synthetic cases."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.biqmac_maxcut import load_rudy
from experiments.fyp_first_block_20261120 import solve_logged as old_logged
from experiments.fyp_ideal_solver import (
    exact_original_cut, field_fidelity, representation, representation_metrics,
    solve_logged, without_latest,
)
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph, prepare


class FixedRandom:
    def __init__(self, choices, uniforms):
        self.choices = iter(choices)
        self.uniforms = iter(uniforms)

    def randrange(self, n):
        value = next(self.choices)
        assert 0 <= value < n
        return value

    def random(self):
        return next(self.uniforms)


class TestIdealSolver(unittest.TestCase):
    def graph(self, text):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name)/"synthetic.rudy"
        path.write_text(text)
        return load_rudy(path)

    def test_all_seven_codes_preserve_legacy_outputs(self):
        graph = self.graph("4 6\n1 2 90\n1 3 -7\n1 4 4\n2 3 12\n2 4 -3\n3 4 5\n")
        beta = beta_from_original_graph(graph)
        for fmt in ("ref64", "fp5", "fp6", "int5", "int6", "int7", "int8"):
            rep = representation(graph, fmt)
            for seed in (5, 70, 777):
                old = old_logged(graph, rep, beta, 400, seed, checkpoints=(100, 400))
                new = solve_logged(graph, rep, beta, 400, seed, checkpoints=(100, 400))
                self.assertEqual(without_latest(new), old, (fmt, seed))
                self.assertGreaterEqual(new["M"], new["R_last"])

    def test_latest_tie_difference_has_either_sign(self):
        graph = self.graph("2 1\n1 2 9\n")
        zero = {"edges": [(0, 1, 0.0)], "adjacency": [[(1, 0.0)], [(0, 0.0)]]}
        for choices, u, expected_R, expected_last in (
            ([1, 1, 1], 0.9, 0, 9),
            ([1, 0, 1], 0.1, 9, 0),
        ):
            fake = FixedRandom(choices, [u])
            with patch("experiments.fyp_ideal_solver.random.Random", return_value=fake):
                result = solve_logged(graph, zero, 1.0, 1, 1, checkpoints=(1,))
            self.assertEqual(result["R"], expected_R)
            self.assertEqual(result["R_last"], expected_last)
            self.assertEqual(result["improvements"], 0)
            self.assertEqual(result["actual_flips"], 1)
            self.assertEqual(result["checkpoints"][0]["R_last"], expected_last)

    def test_exact_score_and_zeroed_weight_mass(self):
        graph = self.graph("3 3\n1 2 100\n1 3 -3\n2 3 1\n")
        self.assertEqual(exact_original_cut(graph, (1, -1, 1)), 101)
        rep = {"edges": [(0, 1, -100.0), (0, 2, 0.0), (1, 2, 0.0)]}
        metrics = representation_metrics(graph, rep)
        self.assertEqual(metrics["quantized_zero_edges"], 2)
        self.assertEqual(metrics["zeroed_abs_weight_mass_fraction"], 4/104)
        self.assertNotEqual(metrics["zeroed_abs_weight_mass_fraction"], 2/3)

    def test_common_state_self_fidelity_is_exactly_zero(self):
        graph = self.graph("3 3\n1 2 100\n1 3 -3\n2 3 1\n")
        source = prepare(graph, "ref64", "source")
        result = field_fidelity(graph, "5", source, 0.15, source_rep=source)
        self.assertEqual(result, {"field_rms": 0.0, "logit_rms": 0.0, "probability_mae": 0.0})

    def test_noninteger_sources_are_rejected(self):
        graph = self.graph("2 1\n1 2 0.25\n")
        with self.assertRaisesRegex(ValueError, "integer"):
            exact_original_cut(graph, (1, -1))


if __name__ == "__main__":
    unittest.main()
