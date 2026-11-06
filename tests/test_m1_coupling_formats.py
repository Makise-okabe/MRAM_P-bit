import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import m1_coupling_formats as f


class FormatTests(unittest.TestCase):
    def test_positive_finite_levels(self):
        self.assertEqual(f.fp_positive_levels(2,1),[0.0,0.5,1.0,1.5,2.0,3.0])
        self.assertEqual(max(f.fp_positive_levels(4,3)),240.0)
        self.assertEqual(len(f.fp_positive_levels(3,2)),1+3+6*4)

    def test_saturation_and_zero(self):
        self.assertEqual(f.quantized_level(200,1,"fp4"),3.0)
        self.assertEqual(f.quantized_level(-200,1,"fp4"),-3.0)
        self.assertEqual(f.quantized_level(0,1,"fp4"),0)
        self.assertEqual(f.quantized_level(200,1,"int4"),7.0)
        self.assertEqual(f.quantized_level(-200,1,"int4"),-7.0)

    def test_fp_and_integer_have_different_codebooks(self):
        self.assertEqual(f.quantized_level(0.75,1,"fp4"),0.5)
        self.assertEqual(f.quantized_level(0.75,1,"int4"),1.0)

    def test_scale_optimizes_mse_over_naive(self):
        values=[0.01,.03,.08,1.0,1.2,1.25]
        for fmt in ("fp4","fp6","fp8","int4","int6","bfp4"):
            scale,q=f.tune_scale(values,fmt)
            self.assertTrue(scale>0)
            self.assertEqual(len(q),len(values))
            self.assertTrue(all(x>=0 for x in q))

    def test_symmetric_tile_groups_and_cost(self):
        J=[[0,.1,.3,.5],[.1,0,.7,.2],[.3,.7,0,2.0],[.5,.2,2.0,0]]
        h=[.02,.3,.6,4.]
        for fmt in f.FORMATS:
            r=f.quantize_couplings(J,h,fmt,tile=2)
            self.assertEqual(r["format"],fmt)
            self.assertEqual(r["J"][0][3],r["J"][3][0])
            self.assertTrue(all(r["J"][i][i]==0 for i in range(4)))
            self.assertEqual(len(r["h"]),4)
            self.assertGreater(r["coefficient_bits"],0)
            self.assertGreaterEqual(r["metadata_bits"],0)
            if fmt=="fp64_ref":
                self.assertEqual(r["J"],J)
                self.assertEqual(r["h"],h)
            if fmt=="fp32":
                self.assertNotEqual(r["J"][0][1],J[0][1])
                self.assertNotEqual(r["h"][0],h[0])
        self.assertEqual(f.quantize_couplings(J,h,"int4")["coefficient_bits"],40)
        self.assertGreater(f.quantize_couplings(J,h,"bfp4",tile=2)["metadata_bits"],0)

    def test_fp32_is_binary32_and_fp64_reference_remains_exact(self):
        self.assertNotEqual(f.f32(0.1),0.1)
        self.assertEqual(f.f32(0.5),0.5)
        J=[[0.0,.1],[.1,0.0]]
        h=[.01,-.1]
        a=f.quantize_couplings(J,h,"fp32")
        b=f.quantize_couplings(J,h,"fp64_ref")
        self.assertEqual(a["coefficient_bits"],96)
        self.assertEqual(b["coefficient_bits"],192)
        self.assertGreater(a["mse_J"],0)
        self.assertEqual(b["mse_J"],0)
        self.assertEqual(a["J"][0][1],a["J"][1][0])

    def test_input_rejects_asymmetry(self):
        with self.assertRaises(ValueError):
            f.quantize_couplings([[0,1],[2,0]],[0,0],"fp4")
        with self.assertRaises(ValueError):
            f.quantize_couplings([[0,1],[1,0]],[0,0],"fake")


if __name__=="__main__":
    unittest.main()
