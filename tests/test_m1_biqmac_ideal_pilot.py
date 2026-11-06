"""Small exact Max-Cut graph tests for first ideal-Gibbs E1 pilot."""
import tempfile
import unittest
from pathlib import Path

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_ideal_pilot import (
    beta_from_original_graph, original_cut, prepare, represented_energy,
    select_scale, solve
)


class TestMaxCutIdealPilot(unittest.TestCase):
    def make_graph(self, text):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p=Path(tmp.name)/"toy.rudy"
        p.write_text(text)
        return load_rudy(p)

    def test_original_signed_cut_vs_represented_exact_energy(self):
        g=self.make_graph("3 3\n1 2 1\n2 3 -2\n1 3 5\n")
        r=prepare(g,"ref64","source")
        s=(1,1,-1)
        self.assertEqual(original_cut(g,s),3)
        self.assertEqual(represented_energy(r["edges"],s),-2)
        self.assertEqual(r["scale_metadata_bits"],0)
        self.assertEqual(r["zeroed_edges"],0)

    def test_global_fullscale_int6_deletes_small_weight_edges(self):
        g=self.make_graph("4 3\n1 2 1\n2 3 -100000\n3 4 3\n")
        p=prepare(g,"int6","fullscale")
        self.assertEqual(p["zeroed_edges"],2)
        self.assertEqual(p["nominal_dense_coefficient_bits"],36)
        self.assertEqual(p["scale_metadata_bits"],32)
        self.assertGreater(p["relative_abs_coefficient_error"],0)

    def test_mse_source_only_scale(self):
        # No energy or optimum is used in choosing this scale.
        self.assertGreater(select_scale([-1000.0,3.0,1.0],"int6","mse"),0)
        self.assertGreater(select_scale([-1000.0,3.0,1.0],"fp6_fn","mse"),0)
        self.assertGreater(select_scale([-1000.0,3.0,1.0],"bfp6","mse"),0)

    def test_ideal_solver_returns_visited_represented_best(self):
        g=self.make_graph("3 3\n1 2 3\n2 3 -2\n1 3 5\n")
        p=prepare(g,"ref64","source")
        b=beta_from_original_graph(g)
        r=solve(g,p,beta=b,updates=100,seed=20261107)
        self.assertEqual(r["attempted_updates"],100)
        self.assertGreaterEqual(r["returned_original_cut"],r["final_original_cut"])
        self.assertGreaterEqual(r["returned_original_cut"],0)
        self.assertLessEqual(r["returned_original_cut"],8)
        self.assertLessEqual(r["returned_represented_energy"],
                             r["final_represented_energy"]+1e-10)

    def test_same_random_stream_for_identical_representation(self):
        g=self.make_graph("3 2\n1 2 10\n2 3 -10\n")
        base=prepare(g,"ref64","source")
        exact_int=prepare(g,"int6","fullscale")
        self.assertEqual(base["edges"],exact_int["edges"])
        beta=beta_from_original_graph(g)
        a=solve(g,base,beta,100,11)
        b=solve(g,exact_int,beta,100,11)
        self.assertEqual(a["returned_state_hex"],b["returned_state_hex"])
        self.assertEqual(a["returned_original_cut"],b["returned_original_cut"])

if __name__=="__main__":
    unittest.main()
