import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import m1_calibrated_scale_gate as gate
import m1_jh_ablation as a


class JHAblationTests(unittest.TestCase):
    def test_heldout_uses_existing_frozen_scales_and_has_mixed_baselines(self):
        cfg=dict(tx=3,rx=3,snrs=[0.0],cal_frames=2,held_frames=2,
                 cal_seed=123,held_seed=1023,tile=2,
                 formats=["fp4","fp4_fn","fp6_fn","int4","int6"],
                 granularities=["global","tile"])
        rows,sums,scales,cal,held=gate.run(**cfg)
        serial={f"{k}|{gr}":v for (k,gr),v in scales.items()}
        frames=[dict(frame_index=i,snr_db=snr,instance=f) for i,snr,f in held]
        results,summary=a.analyze(frames,serial,cfg["formats"],
                                   cfg["granularities"],cfg["tile"])
        self.assertEqual(len(results),2*2*(5*3+2))
        self.assertEqual(len(summary),2*(5*3+2))
        self.assertTrue(all(0<=r["original_ml_preserved"]<=1 for r in results))
        mixed=[r for r in results if r["mode"]=="mixed_both" and r["granularity"]=="global"]
        self.assertEqual(len(mixed),4)
        self.assertEqual(mixed[0]["nominal_stored_bits"],4*3+6*3+64)
        both=[r for r in results if r["mode"]=="both"]
        self.assertTrue(all(isinstance(r["nominal_stored_bits"],int) for r in both))
        diag=[r for r in results if r["mode"]=="J_only"]
        self.assertTrue(all(r["nominal_stored_bits"] is None for r in diag))
        self.assertEqual(a.analyze(frames,serial,cfg["formats"],
                        cfg["granularities"],cfg["tile"]), (results,summary))

    def test_missing_frozen_format_fails_before_false_evidence(self):
        frame=gate.frames_for(3,3,[0.0],1,101)[0]
        with self.assertRaisesRegex(ValueError,"missing required format"):
            a.analyze([dict(frame_index=frame[0],snr_db=frame[1],
                instance=frame[2])],{},["fp4"],["global"],2)

    def test_frozen_manifest_provenance_no_overwrite(self):
        cfg=dict(tx=2,rx=3,snrs=[0.0],cal_frames=1,held_frames=1,
                 cal_seed=123,held_seed=1023,tile=2,
                 formats=["fp4","fp4_fn","fp6_fn","int4","int6"],
                 granularities=["global"])
        rows,sums,scales,cal,held=gate.run(**cfg)
        serial={f"{k}|{gr}":v for (k,gr),v in scales.items()}
        frames=[dict(frame_index=i,snr_db=snr,instance=f) for i,snr,f in held]
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"input"
            gate.write_output(source,rows,sums,scales,cal,held,cfg)
            readframes,frozen,configuration=a.read_m1b(source)
            self.assertEqual(readframes,frames)
            self.assertEqual(frozen,serial)
            rr,ss=a.analyze(readframes,frozen,configuration["formats"],
                configuration["granularities"],configuration["tile"])
            out=Path(tmp)/"new"
            a.save(out,source,rr,ss)
            self.assertTrue((out/"SHA256SUMS.json").exists())
            with self.assertRaises(FileExistsError):
                a.save(out,source,rr,ss)

if __name__=="__main__":
    unittest.main()
