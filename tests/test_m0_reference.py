import importlib.util
import itertools
from pathlib import Path
import tempfile
import unittest

P=Path(__file__).resolve().parents[1]/"experiments"/"m0_reference.py"
spec=importlib.util.spec_from_file_location("m0_reference",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class M0Tests(unittest.TestCase):
    def test_symmetry_gate(self):
        m.assert_ising([[0,1],[1,0]],[0,0])
        with self.assertRaises(ValueError):
            m.assert_ising([[0,1],[2,0]],[0,0])
        with self.assertRaises(ValueError):
            m.assert_ising([[1,1],[1,0]],[0,0])

    def test_exact_ferromagnet(self):
        x=m.exact([[0,1],[1,0]],[0,0],.7)
        self.assertEqual(x["ground_energy"],-1)
        self.assertEqual(x["ground_degeneracy"],2)
        self.assertAlmostEqual(sum(x["probabilities"]),1)
        self.assertGreater(x["probabilities"][0],x["probabilities"][1])

    def test_sigmoid(self):
        self.assertAlmostEqual(m.sigmoid(0),.5)
        self.assertAlmostEqual(m.sigmoid(1000),1)
        self.assertAlmostEqual(m.sigmoid(-1000),0)

    def test_maxcut_exact_mapping(self):
        inst=m.maxcut_instance(6,41)
        W=inst["weights"]
        total=sum(W[i][j] for i in range(6) for j in range(i+1,6))
        for s in itertools.product((-1,1),repeat=6):
            self.assertAlmostEqual(m.energy(inst["J"],inst["h"],s),
                                   total/2-m.cut_value(W,s))

    def test_tsp_every_state(self):
        inst=m.tsp_instance(3,23)
        for s in itertools.product((-1,1),repeat=9):
            self.assertAlmostEqual(m.energy(inst["J"],inst["h"],s,inst["C"]),
                                   m.tsp_qubo_energy(inst,s))

    def test_tsp_ground_valid(self):
        d=m.tsp_instance(3,32)
        ref=m.exact(d["J"],d["h"],.2,d["C"])
        winners=[s for s,e in zip(ref["states"],ref["energies"])
                 if abs(e-ref["ground_energy"])<1e-8]
        self.assertTrue(winners)
        self.assertTrue(all(m.tsp_objective(d,s)["valid"] for s in winners))

    def test_reproducible(self):
        d=m.maxcut_instance(5,67)
        self.assertEqual(d,m.maxcut_instance(5,67))
        x=m.sample(d["J"],d["h"],.6,42,100,150,3)
        self.assertEqual(x,m.sample(d["J"],d["h"],.6,42,100,150,3))

    def test_small_gibbs_stationarity(self):
        J=[[0,.7],[.7,0]];h=[.1,-.2];beta=.9
        ref=m.exact(J,h,beta)
        draws=m.sample(J,h,beta,11,2000,18000,5)
        count={s:0 for s in ref["states"]}
        for s in draws:
            count[s]+=1
        tv=.5*sum(abs(count[s]/len(draws)-p)
                   for s,p in zip(ref["states"],ref["probabilities"]))
        self.assertLess(tv,.04)

    def test_run_evidence_hash(self):
        d=m.maxcut_instance(3,14)
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/"new"
            r=m.run(d,.4,41,40,20,2,out)
            self.assertEqual(r["sampled_states"],20)
            self.assertTrue((out/"SHA256SUMS.json").exists())
            with self.assertRaises(FileExistsError):
                m.run(d,.4,41,40,20,2,out)

if __name__=="__main__":
    unittest.main()
