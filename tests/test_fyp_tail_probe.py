"""Checks that can falsify passivity, buffer retention and factorial semantics."""
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from experiments.biqmac_maxcut import load_rudy
from experiments.fyp_ideal_solver import solve_logged
from experiments.fyp_tail_probe import (
    ARMS, PassiveBuffer, build_arms, common_bank, generate_source, lattice_codes,
    legacy_fields, solve_buffered, solver_seed,
)
from experiments.fyp_tail_analysis import METRICS, registry, scientific_analysis
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph, represented_energy


class FakeRandom:
    def __init__(self):
        self.choices = iter([1, 1, 1])
    def randrange(self, n):
        return next(self.choices)
    def random(self):
        return 0.9


class TestTailProbe(unittest.TestCase):
    def graph(self, text="4 6\n1 2 100000\n1 3 4000\n1 4 1200\n2 3 190\n2 4 13\n3 4 -3\n"):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name)/"synthetic.rudy"
        path.write_text(text)
        return load_rudy(path)

    def test_factorial_arrays_keep_scales_and_edge_order(self):
        graph = self.graph()
        reps = build_arms(graph)
        tails = 0
        for f, i, fm, it, keep, original in zip(*(reps[a]["edges"] for a in
                 ("fp6", "int6", "fp6_mask", "int6_tail", "int6_keep")), graph.edges):
            self.assertEqual(f[:2], original[:2])
            self.assertEqual(f[2]-fm[2], it[2]-i[2])
            if i[2]:
                self.assertEqual(fm[2], f[2])
                self.assertEqual(it[2], i[2])
            else:
                self.assertEqual(fm[2], 0)
                self.assertEqual(it[2], f[2])
                tails += f[2] != 0
            self.assertNotEqual(keep[2], 0)
            for a in ARMS:
                u, v = original[:2]
                q = next(q for j, q in reps[a]["adjacency"][u] if j == v)
                self.assertEqual(q, next(q for j, q in reps[a]["adjacency"][v] if j == u))
        self.assertGreater(tails, 0)

    def test_buffer_uses_energy_and_first_visit_not_original_cut(self):
        b = PassiveBuffer(2)
        b.observe(1, 10, 0, 5)
        b.observe(2, 10, 1, 999999)
        b.observe(3, 9, 2, -100)
        b.observe(2, 10, 3, 999999)
        self.assertEqual([r["state_hex"] for r in b.rows()], ["3", "1"])
        self.assertEqual(len(b.first_seen), 3)

    def test_passive_buffer_matches_all_legacy_fields(self):
        graph = self.graph()
        beta = beta_from_original_graph(graph)
        reps = build_arms(graph)
        for arm in ("ref64", "fp6", "int6"):
            for seed in (5, 70, 777):
                old = solve_logged(graph, reps[arm], beta, 400, seed, checkpoints=(100, 400))
                for k in (1, 16):
                    new = solve_buffered(graph, reps[arm], beta, 400, seed,
                                         checkpoints=(100, 400), capacity=k)
                    self.assertEqual(legacy_fields(new), old, (arm, seed, k))

    def test_tied_minimum_oracle_may_exceed_buffer(self):
        graph = self.graph("2 1\n1 2 9\n")
        zero = {"edges": [(0, 1, 0.0)], "adjacency": [[(1, 0.0)], [(0, 0.0)]]}
        for k, gain in ((1, 0), (16, 9)):
            with patch("experiments.fyp_tail_probe.random.Random", return_value=FakeRandom()):
                r = solve_buffered(graph, zero, 1, 1, 1, checkpoints=(1,), capacity=k)
            self.assertEqual(r["minimum_distinct_states"], 2)
            self.assertEqual(r["M"], 9)
            self.assertEqual(r["buffer_best_original_cut"]-r["R"], gain)

    def test_exact_energy_keys_and_common_bank_match_enumeration(self):
        graph = self.graph()
        reps = build_arms(graph)
        states = [tuple(s) for s in itertools.product((-1, 1), repeat=4)]
        from experiments.fyp_first_block_20261120 import hex_state
        from experiments.fyp_ideal_solver import exact_original_cut
        bank_records = [{"buffer": [{"state_hex": hex_state(s), "original_cut": exact_original_cut(graph, s)}
                                     for s in states]}]
        bank = common_bank(graph, reps, bank_records)
        for arm, result in zip(ARMS, bank["results"]):
            denom, codes = lattice_codes(reps[arm])
            expected = min(states, key=lambda s: (represented_energy(reps[arm]["edges"], s), int(hex_state(s), 16)))
            self.assertEqual(result["selected_state_hex"], hex_state(expected))
            self.assertEqual(result["energy_integer_key"]/denom, represented_energy(reps[arm]["edges"], expected))
        self.assertEqual(bank["results"][0]["total_loss_cut"], 0)

    def test_fresh_source_generation_is_deterministic_and_distinct(self):
        for family in (0, 1):
            a, ma = generate_source(family, 0)
            b, mb = generate_source(family, 0)
            c, _ = generate_source(family, 1)
            self.assertEqual(a, b)
            self.assertNotEqual(a, c)
            self.assertEqual(ma, mb)
            self.assertEqual(ma["seed_sequence"], [20261121, 910, family, 0])
            self.assertEqual(ma["raw_edges"], 4950 if family == 0 else 200)
        with self.assertRaises(ValueError):
            solver_seed(0, 24, 0)


class TestTailAnalysis(unittest.TestCase):
    def rows(self):
        rows = []
        for family in ("ring", "torus"):
            for g in range(24):
                losses = {"ref64": 0, "fp6": .02+.001*g, "int6": .2+.002*g,
                          "fp6_mask": .07+.002*g, "int6_tail": .1, "int6_keep": .4+.001*g}
                for arm in ARMS:
                    r = {"family": family, "index": g, "graph": f"{family}_{g:03d}", "representation": arm}
                    r.update({key: .001*g for key in METRICS})
                    r["Rz_pp"] = losses[arm]
                    r["A_pp"] = .01+.0005*g
                    r["extra_pp"] = r["Rz_pp"]+r["A_pp"]
                    rows.append(r)
        return rows

    def test_registry_has_only_two_confirmatory_contrasts(self):
        r = registry()
        self.assertEqual(len(r["confirmatory"]), 2)
        self.assertEqual(sum(c["one_sided_alpha"] for c in r["confirmatory"]), .025)
        self.assertNotIn("int6_keep", [c["left"] for c in r["confirmatory"]])

    def test_directional_signs_multiplicity_and_non_support(self):
        with tempfile.TemporaryDirectory() as d:
            r = scientific_analysis(self.rows(), d, resamples=2000)
        self.assertTrue(all(c["decision"] == "SUPPORTED" for c in r["confirmatory"]))
        self.assertTrue(all(c["q"] == .0125 for c in r["confirmatory"]))
        rows = self.rows()
        for r in rows:
            if r["representation"] == "fp6_mask":
                r["Rz_pp"] = -.08-.003*r["index"]
        with tempfile.TemporaryDirectory() as d:
            r = scientific_analysis(rows, d, resamples=2000)
        self.assertEqual(r["confirmatory"][0]["decision"], "NOT_ESTABLISHED")
        self.assertLess(r["confirmatory"][0]["high"], 0)

    def test_incomplete_ensemble_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "48 complete"):
                scientific_analysis(self.rows()[:-1], d, resamples=100)


if __name__ == "__main__":
    unittest.main()
