import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import m0_reference as core
import m0_mimo_reference as mimo


class MIMOTests(unittest.TestCase):
    def test_all_states_complex_mapping(self):
        for (nt,nr,snr,seed) in ((2,3,4,10),(3,2,10,11),(4,4,-5,12)):
            inst=mimo.frame(nt,nr,snr,seed)
            core.assert_ising(inst["J"],inst["h"])
            for s in itertools.product((-1,1),repeat=nt):
                self.assertAlmostEqual(
                    core.energy(inst["J"],inst["h"],s,inst["C"]),
                    mimo.original_residual(inst,s),places=9)

    def test_ml_ground_matches_independent_residual(self):
        inst=mimo.frame(4,6,5,22)
        ml=mimo.exact_ml(inst)
        ref=core.exact(inst["J"],inst["h"],0.8,inst["C"])
        self.assertAlmostEqual(ml["residual"],ref["ground_energy"],places=9)
        self.assertAlmostEqual(ml["residual"],mimo.original_residual(inst,ml["state"]),places=9)

    def test_seeds_and_normalization(self):
        a=mimo.frame(3,4,8,99)
        self.assertEqual(a,mimo.frame(3,4,8,99))
        self.assertAlmostEqual(a["sigma2_complex_noise"],(3/4)/(10**0.8))
        self.assertNotEqual(a,mimo.frame(3,4,8,100))

    def test_true_bits_differ_from_ml_when_noise_large(self):
        found=False
        for seed in range(25):
            inst=mimo.frame(2,2,-18,seed)
            ml=mimo.exact_ml(inst)
            if ml["bit_errors"]>0:
                self.assertAlmostEqual(
                    ml["residual"],mimo.original_residual(inst,ml["state"]))
                found=True
                break
        self.assertTrue(found,"need a deterministic noisy frame with ML BER>0")

    def test_sampling_reproducible_and_outputs(self):
        inst=mimo.frame(3,4,6,16)
        a=mimo.solve_one(inst,beta=0.9,sampler_seed=47,burnin=100,
                         records=20,thin=3)
        b=mimo.solve_one(inst,beta=0.9,sampler_seed=47,burnin=100,
                         records=20,thin=3)
        self.assertEqual(a,b)
        self.assertEqual(a["total_spin_update_attempts"],160)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"fresh"
            public=mimo.write_output(inst,a,path)
            self.assertEqual(public["recorded_samples"],20)
            self.assertTrue((path/"SHA256SUMS.json").exists())
            self.assertEqual(len(list(__import__("csv").DictReader((path/"mimo_samples.csv").open()))),20)
            with self.assertRaises(FileExistsError):
                mimo.write_output(inst,a,path)

    def test_dimension_and_beta_validation(self):
        with self.assertRaises(ValueError):
            mimo.frame(17,17,10,4)
        with self.assertRaises(ValueError):
            mimo.frame(2,2,float("nan"),4)
        with self.assertRaises(ValueError):
            mimo.original_residual(mimo.frame(2,2,10,4),(0,1))
        with self.assertRaises(ValueError):
            mimo.solve_one(mimo.frame(2,2,10,4),beta=0)


if __name__=="__main__":
    unittest.main()
