import unittest
import numpy as np

from experiments.ising_reference import (closed_loop_check, cut_value, exact_maxcut,
                                        graph_weights, kernel_preflight, plus_probability,
                                        restart_count, target_energy, trajectory)


class IsingReferenceTests(unittest.TestCase):
    def test_exact_maxcut_and_target_energy(self):
        a = np.ones((5, 5), dtype=int) - np.eye(5, dtype=int)
        best, spins = exact_maxcut(a)
        self.assertEqual(best, 6)  # K5: floor(N^2/4).
        self.assertEqual(cut_value(a, spins), 6)
        self.assertEqual(target_energy(a, spins), 10 - 2 * best)

    def test_incremental_cache_matches_recomputed_trajectory(self):
        a = np.array([[0, 2, 0, 1], [2, 0, 3, 0], [0, 3, 0, 1], [1, 0, 1, 0]])
        order = np.tile([0, 2, 1, 3], 12)
        uniforms = np.random.default_rng(810).random(len(order))
        betas = np.linspace(0, 2, len(order))
        first = trajectory(a, [1, -1, 1, -1], order, uniforms, betas, mode='full_field')
        second = trajectory(a, [1, -1, 1, -1], order, uniforms, betas, mode='incremental', check_cache=True)
        for key in ('spins', 'decisions', 'cuts'):
            np.testing.assert_array_equal(first[key], second[key])

    def test_probability_sign_and_zero_temperature_parameter(self):
        self.assertEqual(plus_probability(10, 0), 0.5)
        self.assertGreater(plus_probability(2, 1), 0.5)
        self.assertLess(plus_probability(-2, 1), 0.5)
        self.assertAlmostEqual(plus_probability(2, 1) + plus_probability(-2, 1), 1)

    def test_two_flip_loop_separates_cache_drift(self):
        result = closed_loop_check()
        self.assertEqual(result['frozen_loop_residual'], [0, 0])
        self.assertEqual(result['independent_sign_error_loop_residual'], [0, 4, -4, 0])
        self.assertEqual(result['independent_sign_error_variance'], 8)

    def test_restart_probability_limits(self):
        self.assertIsNone(restart_count(0))
        self.assertEqual(restart_count(1), 1)
        self.assertEqual(restart_count(0.5), 7)
        with self.assertRaises(ValueError):
            restart_count(0.5, 1)

    def test_invalid_graph_and_unknown_hardware_are_rejected(self):
        with self.assertRaises(ValueError):
            graph_weights([[0, 1], [0, 0]])
        result = kernel_preflight({'physical_rows': 256, 'physical_columns': 256})
        self.assertEqual(result['status'], 'BLOCKED_TARGET_KERNEL')
        self.assertIn('temporal_noise_source_sha256', result['missing'])
        self.assertFalse(result['target_noise_study_implemented'])


if __name__ == '__main__':
    unittest.main()
