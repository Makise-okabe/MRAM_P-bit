import math
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
import m0_reference as base
import m0_parallel_tempering as pt

class PTTests(unittest.TestCase):
    def test_swap_probability_ratio(self):
        self.assertAlmostEqual(pt.swap_log_ratio(.1,.8,2.,0.),-1.4)
        self.assertAlmostEqual(pt.swap_log_ratio(.1,.8,0.,2.),1.4)
        self.assertEqual(pt.swap_log_ratio(.1,.8,2.,2.),0.)

    def test_betas_must_increase(self):
        inst=base.maxcut_instance(3,10)
        for betas in ([.4,.1],[.1,.1],[0.,.5]):
            with self.assertRaises(ValueError):
                pt.pt_run(inst,betas,burnin=0,collect=2)

    def test_cost_count_and_reproducibility(self):
        inst=base.maxcut_instance(3,10)
        a=pt.pt_run(inst,[.2,.4,.6,.8],seed=42,burnin=2,collect=4,sweeps=2)
        b=pt.pt_run(inst,[.2,.4,.6,.8],seed=42,burnin=2,collect=4,sweeps=2)
        self.assertEqual(a,b)
        self.assertEqual(a['all_replica_spin_update_attempts'],6*4*2*3)
        self.assertEqual(a['replica_swap_attempts'],9)
        self.assertEqual(a['cold_checkpoint_count'],6)

    def test_tsp_target_requires_feasibility(self):
        inst=base.tsp_instance(3,11)
        s=tuple([-1]*9)
        self.assertFalse(pt.at_target(inst,s,pt.target_from_exact(inst)))
        ref=base.exact(inst['J'],inst['h'],.2,inst['C'])
        optimal=[s for s in ref['states'] if pt.at_target(inst,s,pt.target_from_exact(inst))]
        self.assertEqual(len(optimal),6)

    def test_stationary_cold_marginal_for_two_spins(self):
        J=[[0.,.7],[.7,0.]]; h=[.12,-.2]
        inst=dict(kind='weighted_maxcut',J=J,h=h,C=0.,weights=[[0.,-1.4],[-1.4,0.]])
        out=pt.pt_run(inst,[.2,.5,.9],seed=418,burnin=2000,collect=18000,sweeps=1)
        self.assertLess(out['cold_sample_tv_to_ideal'],.045)

    def test_saved_manifest_and_no_overwrite(self):
        inst=base.maxcut_instance(3,7)
        result=pt.pt_run(inst,[.3,.6],seed=7,burnin=1,collect=5)
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'new'
            m=pt.write_trial(inst,result,out)
            self.assertTrue((out/'SHA256SUMS.json').exists())
            self.assertEqual(m['cold_sample_count'],5)
            with self.assertRaises(FileExistsError):
                pt.write_trial(inst,result,out)

if __name__=='__main__':
    unittest.main()
