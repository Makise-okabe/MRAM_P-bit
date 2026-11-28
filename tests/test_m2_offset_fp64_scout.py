"""Tiny offset-scout mathematical tests; no 240-run computation in CI."""
import unittest
from types import SimpleNamespace

from experiments.m1_biqmac_reference_quality_gate import solve_reference
from experiments.m2_e2_response_gate import solve_with_response, validate_device_model
from experiments.m2_offset_fp64_scout import (
    GRAPH_SPECS, LEVELS, paired_seed, models, summary_rows
)


class TestOffsetFP64Scout(unittest.TestCase):
    def test_exact_predeclared_matrix(self):
        self.assertEqual(GRAPH_SPECS,(("t2g10_5555",1),("ising2.5-100_5555",2)))
        self.assertEqual(LEVELS,(0.1,0.2,0.4,0.8,1.6))
        self.assertEqual(len(GRAPH_SPECS)*len(LEVELS)*24,240)
        self.assertEqual(len(GRAPH_SPECS)*24,48)
        self.assertEqual(paired_seed(1)[0],20261201+100000)
        self.assertEqual(paired_seed(2)[0],20261201+200000)

    def test_one_persistent_population_scaled_across_levels(self):
        a=models(100)
        self.assertEqual(a,models(100))
        self.assertTrue(all(g==1.0 for m in a.values() for g in m["per_device_gain"]))
        z=a[0.1]["per_device_offset_logit"]
        self.assertTrue(any(abs(v)>0 for v in z))
        for d in LEVELS:
            self.assertEqual(len(a[d]["per_device_offset_logit"]),100)
            for u,v in zip(z,a[d]["per_device_offset_logit"]):
                self.assertAlmostEqual(v/d,u/0.1,places=12)
            validate_device_model(a[d],100,offset_limit=d)
        with self.assertRaises(ValueError):
            validate_device_model(a[1.6],100)  # old frozen ±0.10 gate stays strict

    def test_unchanged_zero_offset_matches_frozen_ideal_solver(self):
        graph=SimpleNamespace(n=3,edges=[(0,1,3.0),(0,2,-2.0),(1,2,1.0)])
        es=[(0,1,-3.0),(0,2,2.0),(1,2,-1.0)]
        adjacency=[[],[],[]]
        for i,j,q in es:
            adjacency[i].append((j,q))
            adjacency[j].append((i,q))
        rep=dict(adjacency=adjacency,edges=es)
        model=models(3)[1.6]
        model["per_device_offset_logit"]=[0.0]*3
        for seed in (11,20261201):
            old=solve_reference(graph,rep,0.09,600,seed,"linear")
            new=solve_with_response(graph,rep,0.09,600,seed,model,offset_limit=1.6)
            self.assertEqual(old,new)

    def test_bootstrap_summary_uses_paired_ideal(self):
        data={}
        ideal={}
        for gix,(name,index) in enumerate(GRAPH_SPECS):
            for seed in paired_seed(index):
                ideal[(name,seed)]=3.0
                for d in LEVELS:
                    data[(name,d,seed)]={"gap_pct":3.0+d}
        rows=summary_rows(data,ideal)
        self.assertEqual(len(rows),2*6)
        for r in rows:
            d=r["offset_logit_halfspan"]
            self.assertAlmostEqual(r["mean_paired_deterioration_pp"],d)
            self.assertEqual(r["practical_deterioration_above_1pp_supported"],d>1.0)


if __name__=="__main__":
    unittest.main()
