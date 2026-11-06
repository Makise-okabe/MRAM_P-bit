"""M0 exact mathematical checks, including signed weights and Rudy edge cases."""
import itertools
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from experiments.biqmac_maxcut import (
    audit_graph, cut_weight, ising_energy, load_rudy, local_field
)


class TestBiqMacMaxCut(unittest.TestCase):
    def make_graph(self, contents):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p = Path(tmp.name) / "toy.rudy"
        p.write_text(contents, encoding="utf-8")
        return load_rudy(p)

    def test_signed_weighted_triangle_known_optimum(self):
        g = self.make_graph("# signed weighted triangle\n3 3\n"
                            "1 2 3\n2 3 -2\n1 3 5\n")
        assert g.n == 3
        scores = [cut_weight(g, s) for s in itertools.product((-1, 1), repeat=3)]
        self.assertEqual(max(scores), Decimal(8))
        self.assertEqual(cut_weight(g, (1, 1, 1)), Decimal(0))
        self.assertEqual(ising_energy(g, (1, 1, 1)), Decimal(6))
        self.assertEqual(local_field(g, (1, 1, 1), 0), Decimal(-8))
        report = audit_graph(g, n_random_states=12)
        self.assertEqual(report["status"], "E0_PASS")
        self.assertEqual(report["optimum_status"], "NOT_LOADED")

    def test_parallel_edges_zero_and_loops(self):
        g = self.make_graph("3 5\n1 2 3\n2 1 2\n2 2 99\n"
                            "1 3 -1\n1 2 0\n")
        self.assertEqual(g.raw_edge_count, 5)
        self.assertEqual(g.loops_ignored, 1)
        self.assertEqual(g.parallel_entries, 2)
        self.assertEqual(g.edges,
                         ((0, 1, Decimal(5)), (0, 2, Decimal(-1))))
        self.assertEqual(g.sum_weights, Decimal(4))

    def test_decimal_weights_kept_exact(self):
        g = self.make_graph("2 1\n1 2 -0.125\n")
        self.assertEqual(cut_weight(g, (1, -1)), Decimal("-0.125"))
        self.assertEqual(ising_energy(g, (1, -1)), Decimal("0.125"))
        self.assertEqual(audit_graph(g)["status"], "E0_PASS")

    def test_strict_edge_count(self):
        with self.assertRaisesRegex(ValueError, "declares"):
            self.make_graph("3 2\n1 2 1\n")

    def test_invalid_index_and_nonfinite_weight(self):
        with self.assertRaisesRegex(ValueError, "invalid"):
            self.make_graph("2 1\n1 3 4\n")
        with self.assertRaisesRegex(ValueError, "invalid"):
            self.make_graph("2 1\n1 2 NaN\n")

    def test_complement_symmetry(self):
        g = self.make_graph("3 3\n1 2 7\n2 3 -3\n1 3 2\n")
        for spins in itertools.product((-1, 1), repeat=3):
            flip = tuple(-x for x in spins)
            self.assertEqual(cut_weight(g, spins), cut_weight(g, flip))
            self.assertEqual(ising_energy(g, spins), ising_energy(g, flip))


if __name__ == "__main__":
    unittest.main()
