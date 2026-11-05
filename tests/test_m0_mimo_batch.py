import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import m0_mimo_batch as sweep


class MIMOBatchTests(unittest.TestCase):
    def test_independent_frames_and_ber_counts(self):
        rows,instances,summary=sweep.run_batch(
            tx=3,rx=3,snrs=[0.0,10.0],frames=3,
            channel_seed=91000,solver_seed=92000,
            beta=.8,burnin=30,records=10,thin=2)
        self.assertEqual(len(rows),6)
        self.assertEqual(len(instances),6)
        self.assertEqual(len(summary),2)
        self.assertEqual(len(set(r["channel_seed"] for r in rows)),3)
        for s in summary:
            self.assertEqual(s["transmitted_bits"],9)
            self.assertTrue(0<=s["exact_ml_ber"]<=1)
            self.assertTrue(0<=s["gibbs_best_ber"]<=1)
            self.assertTrue(0<=s["gibbs_best_ml_hit_frames"]<=3)
        for ix in range(3):
            pair=[r for r in rows if r["frame_index"]==ix]
            self.assertEqual(len(pair),2)
            self.assertEqual(pair[0]["solver_seed"],pair[1]["solver_seed"])
            self.assertEqual(pair[0]["channel_seed"],pair[1]["channel_seed"])

    def test_reproducible_hash_and_no_overwrite(self):
        args=dict(tx=2,rx=3,snrs=[2.0],frames=2,channel_seed=15,
                  solver_seed=25,beta=.7,burnin=20,records=8,thin=2)
        a=sweep.run_batch(**args)
        b=sweep.run_batch(**args)
        self.assertEqual(a,b)
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"new"
            meta=sweep.write_output(out,*a,args)
            self.assertEqual(meta["summary"][0]["independent_frames"],2)
            self.assertTrue((out/"SHA256SUMS.json").exists())
            with (out/"paired_frames.csv").open(newline="",encoding="utf-8") as fh:
                self.assertEqual(len(list(csv.DictReader(fh))),2)
            with self.assertRaises(FileExistsError):
                sweep.write_output(out,*a,args)

    def test_invalid_snr(self):
        with self.assertRaises(ValueError):
            sweep.run_batch(tx=2,rx=2,snrs=[1.0,1.0],frames=2,
                            channel_seed=1,solver_seed=2,beta=.8,
                            burnin=1,records=1,thin=1)


if __name__=="__main__":
    unittest.main()
