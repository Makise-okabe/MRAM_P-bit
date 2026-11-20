"""Independent source/namespace checks; no annealer and no official weight reads."""
import hashlib
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from experiments.fyp_ideal_sources import (
    ANCHORS, CANDIDATES, GRAPHS_PER_FAMILY, NUMPY_VERSION, _round_weights,
    anchor_seed, bootstrap_seed_sequence, graph_name, graph_relative_path,
    graph_seed_sequence, protocol_parameters,
    require_numpy_version, ring_normalization, rudy_bytes, solver_seed,
    source_statistics, torus_edges, distribution_statistics,
)


class TestLockedSources(unittest.TestCase):
    def test_ring_normalization_full_row_independent_formula(self):
        # Independent scalar formula: both ring directions enter the full row.
        expected = 1 / math.sqrt(sum(
            ((100/math.pi)*math.sin(math.pi*j/100))**-5
            for j in range(1, 100)))
        self.assertAlmostEqual(ring_normalization(), expected, places=14)
        self.assertAlmostEqual(ring_normalization(), 0.69407031, places=8)
        self.assertGreater(ring_normalization(), 0)

    def test_torus_is_periodic_unique_degree_four(self):
        edges = torus_edges()
        self.assertEqual(len(edges), 200)
        self.assertEqual(edges, tuple(sorted(set(edges))))
        degree = [0]*100
        for i, j in edges:
            self.assertLess(i,j); degree[i] += 1; degree[j] += 1
        self.assertEqual(degree, [4]*100)
        self.assertIn((0,9), edges)
        self.assertIn((0,90), edges)
        self.assertNotIn((9,10), edges)

    def test_seed_domains_and_counts_are_disjoint(self):
        refs = {solver_seed("reference", f, g, r)
                for f in range(2) for g in range(72) for r in range(128)}
        main = {solver_seed("main", f, g, r)
                for f in range(2) for g in range(72) for r in range(64)}
        anchors = {anchor_seed(h,r) for h in range(6) for r in range(128)}
        self.assertEqual(len(refs), 144*128)
        self.assertEqual(len(main), 144*64)
        self.assertEqual(len(anchors), 6*128)
        self.assertFalse(refs & main or refs & anchors or main & anchors)
        self.assertEqual(anchor_seed(0,0), 3000000000000)
        self.assertEqual(anchor_seed(2,127), 3000000020127)
        self.assertEqual(graph_seed_sequence(1,71), [20261120,910,1,71])
        self.assertEqual(graph_name(0,71), "ring_071")
        self.assertEqual(graph_relative_path(0,71), "ring/071.rudy")
        self.assertEqual(graph_relative_path(1,0), "torus/000.rudy")
        self.assertEqual(bootstrap_seed_sequence(0), [20261120,940,0])
        self.assertEqual(bootstrap_seed_sequence(1,descriptive=True), [20261120,940,1,1])
        with self.assertRaises(ValueError): solver_seed("main",0,0,64)
        with self.assertRaises(ValueError): solver_seed("reference",0,0,128)
        with self.assertRaises(ValueError): graph_name(0,72)
        with self.assertRaises(ValueError): anchor_seed(6,0)

    def test_numpy_version_guard_and_candidate_roster(self):
        require_numpy_version()
        with patch.object(np,"__version__","2.3.4"):
            with self.assertRaisesRegex(RuntimeError, "2.3.5 required"):
                require_numpy_version()
        self.assertEqual(CANDIDATES,("ref64","fp5","fp6","int5","int6","int7","int8"))
        self.assertEqual(GRAPHS_PER_FAMILY,72)
        self.assertEqual([x["name"] for x in ANCHORS], [
            "ising2.5-100_5555","ising2.5-100_6666","ising2.5-100_7777",
            "t2g10_5555","t2g10_6666","t2g10_7777"])

    def test_rounding_is_ties_even_and_raw_zeros_survive_serialization(self):
        self.assertEqual(_round_weights(np.array([-2.5,-1.5,-.5,.5,1.5,2.5])).tolist(),
                         [-2,-2,0,0,2,2])
        edges=((0,1,0),(0,2,-7),(1,2,9))
        expected=b"3 3\n1 2 0\n1 3 -7\n2 3 9\n"
        self.assertEqual(rudy_bytes(edges,n=3),expected)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"toy.rudy";path.write_bytes(expected)
            info=source_statistics(path)
            self.assertEqual(info["zero_count"],1)
            self.assertEqual(info["raw_edge_count"],3)
            self.assertEqual(info["effective_nonzero_edges"],2)
            self.assertEqual(info["max_abs_weight"],9)
            self.assertEqual(info["sum_weights"],2)
            self.assertEqual(info["sum_abs_weights"],16)
            self.assertEqual(info["sha256"],hashlib.sha256(expected).hexdigest())
        with self.assertRaises(ValueError):
            rudy_bytes(((0,2,1),(0,1,2)),n=3)

    def test_metadata_distribution_and_fixed_parameters(self):
        d=distribution_statistics([0,1,2,3,4])
        self.assertEqual((d["minimum"],d["q25"],d["median"],d["q75"],d["maximum"]),
                         (0,1,2,3,4))
        p=protocol_parameters()
        self.assertEqual(p["source_multiplier"],100000)
        self.assertEqual(p["numpy_version"],NUMPY_VERSION)
        self.assertEqual(p["source_root"],"data/fyp_locked_20261120")
        self.assertEqual(p["core_contrasts_total"],18)
        self.assertEqual(p["core_one_sided_tail"],0.04/36)
        self.assertEqual(p["zero_entries"],"retained in raw Rudy sources, omitted by existing loader")


if __name__ == "__main__":
    unittest.main()
