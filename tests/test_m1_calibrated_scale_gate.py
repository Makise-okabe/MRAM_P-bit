import sys
import unittest
from pathlib import Path
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))

import m0_mimo_reference as mimo
import m1_calibrated_scale_gate as g


class CalibratedScaleTests(unittest.TestCase):
    def test_scales_fixed_across_heldout_and_grouping_matched(self):
        ca=g.frames_for(3,4,[0.0,5.0],2,100)
        scales=g.calibrate(ca,["fp4","fp4_fn","fp6_fn","int4","bfp4"],["global","tile"],2)
        self.assertEqual(set(scales[("fp4","global")]),set(scales[("int4","global")]))
        self.assertEqual(set(scales[("fp4","tile")]),set(scales[("int4","tile")]))
        self.assertEqual(set(scales[("fp4_fn","tile")]),set(scales[("fp6_fn","tile")]))
        self.assertGreater(len(scales[("fp4","tile")]),len(scales[("fp4","global")]))
        a=mimo.frame(3,4,7,1000)
        b=mimo.frame(3,4,-3,1001)
        qa=g.quantize_with_frozen(a,"fp4","tile",2,scales[("fp4","tile")])
        qb=g.quantize_with_frozen(b,"fp4","tile",2,scales[("fp4","tile")])
        self.assertEqual(qa["total_nominal_bits"],qb["total_nominal_bits"])
        self.assertEqual(qa["J"],[list(row) for row in zip(*qa["J"])])

    def test_disjoint_seeds_validation_and_repeatability(self):
        opts=dict(tx=3,rx=3,snrs=[0.0],cal_frames=2,held_frames=2,
                  cal_seed=10,held_seed=100,
                  formats=["fp4","int4","bfp4"],granularities=["global","tile"],tile=2)
        out=g.run(**opts)
        self.assertEqual(out,g.run(**opts))
        rows,summary,scales,cal,held=out
        self.assertEqual(len(rows),12)
        self.assertEqual(len(summary),6)
        self.assertTrue(all(0<=r["best_possible_original_gap"]<=r["worst_possible_original_gap"]+1e-8 for r in rows))
        self.assertTrue(all(r["quantized_ground_degeneracy"]>=1 for r in rows))
        with self.assertRaisesRegex(ValueError,"overlap"):
            g.run(**dict(opts,held_seed=11))

    def test_finite_fp_formats_in_heldout_gate(self):
        opts=dict(tx=3,rx=3,snrs=[0.0],cal_frames=2,held_frames=2,
                  cal_seed=10000,held_seed=20000,
                  formats=["fp4_fn","fp6_fn","int4"],granularities=["global","tile"],tile=2)
        rows,summary,scales,cal,held=g.run(**opts)
        self.assertEqual(len(rows),12)
        self.assertEqual(len(summary),6)
        a=next(r for r in rows if r["format"]=="fp4_fn" and r["granularity"]=="global")
        self.assertEqual(a["coefficient_bits"],4*(3*2//2+3))
        self.assertTrue(all(r["original_ml_preserved"] in (0,1) for r in rows))

    def test_ground_comparison_oracle(self):
        frame=mimo.frame(3,3,3,201)
        q=g.quantize_with_frozen(frame,"int4","global",2,{"J_global":.2,"h":.2})
        a=g.exact_ground_compare(frame,q)
        self.assertIn(a["original_ml_preserved"],(0,1))
        self.assertGreaterEqual(a["minimum_positive_quantized_energy_gap"],0)
        self.assertTrue(0<=a["original_ber_lower_bound_among_qground"]<=
                        a["original_ber_upper_bound_among_qground"]<=1)

    def test_persist_and_no_overwrite(self):
        opts=dict(tx=2,rx=3,snrs=[0.0],cal_frames=1,held_frames=1,
                  cal_seed=300,held_seed=400,
                  formats=["fp4","int4"],granularities=["global"],tile=2)
        result=g.run(**opts)
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"new"
            meta=g.write_output(out,*result,configuration=opts)
            self.assertTrue((out/"SHA256SUMS.json").exists())
            self.assertEqual(len(meta["summary"]),2)
            with self.assertRaises(FileExistsError):
                g.write_output(out,*result,configuration=opts)

if __name__=="__main__":
    unittest.main()
