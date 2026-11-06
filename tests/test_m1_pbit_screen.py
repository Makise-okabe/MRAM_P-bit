import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import m1_pbit_screen as m
import m1_coupling_formats as fmt


class M1ScreenTests(unittest.TestCase):
    def test_probability_bounds_and_ideal(self):
        for label in m.RESPONSES:
            for x in (-10.,0.,10.):
                p=m.pbit_probability(x,.5,label,offset=.17)
                self.assertTrue(0<p<1)
        self.assertAlmostEqual(m.pbit_probability(0,.8,"ideal"),.5)
        self.assertAlmostEqual(m.pbit_probability(0,.8,"contrast090"),.5)
        self.assertGreater(m.pbit_probability(0,.8,"offset015",.2),.5)

    def test_paired_responses_and_reproducible(self):
        opts=dict(tx=3,rx=4,snrs=[0.0],frames=2,channel_seed=501,
                  solver_seed=601,device_seed=701,beta=.7,burnin=20,
                  records=8,thin=2,tile=2,
                  formats=["fp32","fp4","int4","bfp4"],
                  responses=["ideal","offset015"])
        a=m.run_screen(**opts)
        self.assertEqual(a,m.run_screen(**opts))
        rows,frames,summary,offsets=a
        self.assertEqual(len(rows),16)
        self.assertEqual(len(frames),2)
        self.assertEqual(len(summary),8)
        self.assertEqual(len(offsets),3)
        self.assertEqual(len(set((r["channel_seed"],r["format"],r["response"])
                                 for r in rows)),16)
        self.assertEqual(set(r["attempted_spin_updates"] for r in rows),{36})
        self.assertTrue(all(r["original_residual_gap"]>=0 for r in rows))
        self.assertTrue(all(r["total_coefficient_plus_metadata_bits"]>0 for r in rows))

    def test_evidence_nonoverwrite(self):
        a=m.run_screen(2,2,[0.],1,9,10,11,.8,20,5,2,2,
                       ["fp32","fp4","int4"],["ideal"])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"new"
            meta=m.output_evidence(path,*a,config={"test":True})
            self.assertTrue((path/"m1_paired_runs.csv").exists())
            self.assertTrue((path/"SHA256SUMS.json").exists())
            self.assertEqual(meta["config"]["test"],True)
            with self.assertRaises(FileExistsError):
                m.output_evidence(path,*a,config={})

    def test_reject_unknown_response(self):
        with self.assertRaises(ValueError):
            m.run_screen(2,2,[0.],1,1,2,3,.8,20,5,2,2,
                         ["fp4"],["physical_mram"])


if __name__=="__main__":
    unittest.main()
