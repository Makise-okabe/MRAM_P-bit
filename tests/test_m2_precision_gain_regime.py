"""Small E2-GAIN-01 correctness checks; NO solver quality claim or parameter fitting."""
from types import SimpleNamespace
import tempfile
from pathlib import Path
import unittest

from experiments.m1_biqmac_reference_quality_gate import solve_reference
from experiments.m2_e2_response_gate import solve_with_response
from experiments.m2_precision_gain_regime import (
    FORMATS, STRESSES, SEEDS, classify_gap, build_gain_models, load_paired_ideal,
)


class TestGainOnlyPrecision(unittest.TestCase):
    def test_frozen_matrix_exact(self):
        self.assertEqual(len(FORMATS),13)
        self.assertEqual(len(SEEDS),24)
        self.assertEqual(STRESSES,(
            ("ideal",0.0),("gain_025",0.025),("gain_050",0.05)
        ))
        self.assertEqual(13*24*(len(STRESSES)-1),624)

    def test_one_persistent_gain_population_zero_offsets(self):
        a=build_gain_models(100)
        b=build_gain_models(100)
        self.assertEqual(a,b)
        lo,hi=a["gain_025"],a["gain_050"]
        self.assertEqual(lo["per_device_offset_logit"],[0.0]*100)
        self.assertEqual(hi["per_device_offset_logit"],[0.0]*100)
        for x,y in zip(lo["per_device_gain"],hi["per_device_gain"]):
            self.assertLessEqual(abs(x-1),0.0250000001)
            self.assertLessEqual(abs(y-1),0.0500000001)
            self.assertAlmostEqual(y-1,2*(x-1),places=14)

    def test_absolute_ci_classification(self):
        self.assertEqual(classify_gap(2,4.9),"acceptable")
        self.assertEqual(classify_gap(5.01,7.4),"degraded")
        self.assertEqual(classify_gap(7.51,8),"failure")
        self.assertEqual(classify_gap(4.9,5.1),"uncertain")
        self.assertEqual(classify_gap(7.4,7.6),"uncertain")

    def test_ideal_transfer_bit_identical_to_original_software(self):
        g=SimpleNamespace(n=3, edges=[(0,1,3.0),(0,2,-2.0),(1,2,1.0)])
        es=[(0,1,-3.0),(0,2,2.0),(1,2,-1.0)]
        adj=[[],[],[]]
        for i,j,w in es:
            adj[i].append((j,w))
            adj[j].append((i,w))
        rep=dict(edges=es,adjacency=adj)
        model=build_gain_models(3)["gain_050"]
        model["per_device_gain"]=[1.0]*3
        for s in (3,31,20261201):
            a=solve_reference(g,rep,0.1,700,s,"linear")
            b=solve_with_response(g,rep,0.1,700,s,model)
            self.assertEqual(a,b)

    def test_reject_nonfrozen_raw_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"fake.csv"
            path.write_text("graph,configuration,seed\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                load_paired_ideal(path,graph_sha="fake",optimum=123.0)


if __name__=="__main__":
    unittest.main()
