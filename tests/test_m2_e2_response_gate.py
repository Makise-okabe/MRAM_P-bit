"""Tiny deterministic E2 software checks. No benchmark sweep or MTJ data."""
import copy
import math
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest

from experiments.m1_biqmac_reference_quality_gate import solve_reference
from experiments.m2_e2_response_gate import (
    EVIDENCE, GAIN_HALFSPAN, OFFSET_LOGIT_HALFSPAN,
    build_e2_assumption, validate_device_model, e2_probability,
    solve_with_response, load_frozen_e1,
)
from experiments.m0_ising_math import sigmoid


def graph_and_rep():
    graph = SimpleNamespace(n=3, edges=((0, 1, 3.0), (0, 2, -2.0), (1, 2, 1.0)))
    edges = ((0, 1, -3.0), (0, 2, 2.0), (1, 2, -1.0))
    adj = [[], [], []]
    for i, j, q in edges:
        adj[i].append((j, q))
        adj[j].append((i, q))
    return graph, dict(edges=edges, adjacency=adj)


class TestE2Gate(unittest.TestCase):
    def test_fixed_assumed_population_and_constraints(self):
        a = build_e2_assumption(100)
        self.assertEqual(a, build_e2_assumption(100))
        self.assertEqual(a["evidence_level"], EVIDENCE)
        self.assertIn("not extracted from any MTJ", a["source"])
        self.assertEqual(len(a["per_device_gain"]), 100)
        self.assertTrue(all(abs(x-1) <= GAIN_HALFSPAN for x in a["per_device_gain"]))
        self.assertTrue(all(abs(x) <= OFFSET_LOGIT_HALFSPAN for x in a["per_device_offset_logit"]))
        self.assertNotEqual(len(set(a["per_device_gain"])), 1)

    def test_no_silent_parameter_substitution(self):
        x = build_e2_assumption(3)
        for mutation in (
            lambda y: y.update(evidence_level="E3_MEASURED"),
            lambda y: y["per_device_gain"].__setitem__(0, 2.0),
            lambda y: y["per_device_offset_logit"].pop(),
            lambda y: y["per_device_gain"].__setitem__(1, -1.0),
        ):
            y = copy.deepcopy(x)
            mutation(y)
            with self.assertRaises(ValueError):
                validate_device_model(y, 3)

    def test_nominal_is_exact_ideal_probability(self):
        for beta in (0.02, 0.5, 2.0):
            for h in (-10, -2, -0.1, 0, 0.2, 3, 20):
                self.assertEqual(e2_probability(beta, h, 1, 0), sigmoid(2*beta*h))
        with self.assertRaises(ValueError):
            e2_probability(1, 0, -1, 0)
        self.assertAlmostEqual(e2_probability(1, 0, 1, 0.10), sigmoid(0.10))

    def test_zero_residual_reproduces_frozen_solver_entire_return(self):
        graph, rep = graph_and_rep()
        model = build_e2_assumption(3)
        model["per_device_gain"] = [1.0]*3
        model["per_device_offset_logit"] = [0.0]*3
        validate_device_model(model, 3)
        for seed in (2, 11, 208, 20261201):
            expected = solve_reference(graph, rep, 0.08, 1200, seed, "linear")
            got = solve_with_response(graph, rep, 0.08, 1200, seed, model)
            self.assertEqual(expected, got, "zero residual must be bit-identical")

    def test_nonideal_parameters_persistent_and_paired(self):
        graph, rep = graph_and_rep()
        model = build_e2_assumption(3)
        x = solve_with_response(graph, rep, 0.08, 200, 123, model)
        self.assertEqual(x, solve_with_response(graph, rep, 0.08, 200, 123, model))
        self.assertEqual(x["attempted_updates"], 200)
        self.assertTrue(math.isfinite(x["returned_original_cut"]))

    def test_raw_e1_hash_is_mandatory(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"fake_precision_paired_runs.csv"
            p.write_text("graph,configuration,seed\n")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                load_frozen_e1(p)


if __name__ == "__main__":
    unittest.main()
