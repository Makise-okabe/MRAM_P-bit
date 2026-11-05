import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import m0_ising_math as core

class IsingMathTests(unittest.TestCase):
    def test_symmetry(self):
        core.assert_ising([[0,.3],[.3,0]],[0,0])
        with self.assertRaises(ValueError):
            core.assert_ising([[0,.3],[.4,0]],[0,0])
    def test_exact_ground(self):
        r=core.exact([[0,1],[1,0]],[0,0],.7)
        self.assertEqual(r["ground_energy"],-1)
        self.assertEqual(r["ground_degeneracy"],2)
        self.assertAlmostEqual(sum(r["probabilities"]),1)
    def test_numeric_sigmoid(self):
        self.assertAlmostEqual(core.sigmoid(0),.5)
        self.assertAlmostEqual(core.sigmoid(1000),1)
        self.assertAlmostEqual(core.sigmoid(-1000),0)
    def test_gibbs_seed_reproducibility(self):
        J=[[0,.7],[.7,0]]
        a=core.sample(J,[.1,-.2],.8,43,80,200,2)
        self.assertEqual(a,core.sample(J,[.1,-.2],.8,43,80,200,2))
    def test_gibbs_stationarity_two_spins(self):
        J=[[0,.7],[.7,0]]
        h=[.1,-.2]
        e=core.exact(J,h,.9)
        s=core.sample(J,h,.9,11,2000,16000,5)
        f={state:0 for state in e["states"]}
        for state in s:
            f[state]+=1
        tv=.5*sum(abs(f[state]/len(s)-p) for state,p in zip(e["states"],e["probabilities"]))
        self.assertLess(tv,.05)

if __name__=="__main__":
    unittest.main()
