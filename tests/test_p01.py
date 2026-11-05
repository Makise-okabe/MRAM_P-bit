import importlib.util
from pathlib import Path
import random
import unittest

spec = importlib.util.spec_from_file_location("p01", Path(__file__).resolve().parents[1] / "experiments" / "p01_exact_baseline.py")
p01 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p01)

class TestP01(unittest.TestCase):
    def test_exact_ferromagnet(self):
        self.assertEqual(p01.exact_ground_state([[0, 1], [1, 0]]), (-1, 2))

    def test_symmetric_seeded(self):
        J = p01.generate_instance(8, random.Random(9))
        self.assertEqual(J, p01.generate_instance(8, random.Random(9)))
        self.assertTrue(all(J[i][i] == 0 and all(J[i][j] == J[j][i] for j in range(8)) for i in range(8)))

    def test_probability(self):
        self.assertAlmostEqual(p01.sigmoid(0), .5)
        self.assertAlmostEqual(p01.sigmoid(1000), 1)
        self.assertAlmostEqual(p01.sigmoid(-1000), 0)

    def test_fixed_point(self):
        J = [[0,.125,-.9],[.125,0,.4],[-.9,.4,0]]
        Q = p01.fixed_point(J, 4, .1)
        self.assertEqual(Q[0][1], Q[1][0])
        self.assertAlmostEqual(Q[0][2], -.7)

if __name__ == "__main__":
    unittest.main()
