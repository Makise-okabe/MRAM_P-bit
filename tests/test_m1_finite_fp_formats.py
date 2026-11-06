import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import m1_coupling_formats as formats


class FiniteFormatTests(unittest.TestCase):
    def test_ocp_fp4_element_value_set(self):
        self.assertEqual(formats.format_positive_levels("fp4_fn"),
                         [0.,.5,1.,1.5,2.,3.,4.,6.])
        self.assertEqual(formats.format_bits("fp4_fn"),4)
        self.assertEqual(formats.quantized_level(100.,1.,"fp4_fn"),6.)
        self.assertEqual(formats.quantized_level(-100.,1.,"fp4_fn"),-6.)

    def test_ocp_fp6_e3m2_element_range(self):
        levels=formats.format_positive_levels("fp6_fn")
        self.assertEqual(len(levels),32)
        self.assertEqual(levels[1],.0625)
        self.assertEqual(levels[-1],28.)
        self.assertEqual(formats.format_bits("fp6_fn"),6)

    def test_finite_format_midpoints_round_to_even_encoding(self):
        for kind in ("fp4_fn","fp6_fn"):
            levels=formats.format_positive_levels(kind)
            for i,(lo,hi) in enumerate(zip(levels,levels[1:])):
                expected=lo if i%2==0 else hi
                middle=(lo+hi)/2
                self.assertEqual(formats.quantized_level(middle,1.,kind),expected)
                self.assertEqual(formats.quantized_level(-middle,1.,kind),-expected)

    def test_historical_labels_are_unchanged(self):
        self.assertEqual(formats.format_positive_levels("fp4"),[0.,.5,1.,1.5,2.,3.])
        self.assertEqual(formats.quantized_level(.75,1.,"fp4"),.5)
        self.assertEqual(formats.quantized_level(.75,1.,"fp4_fn"),1.)
        self.assertEqual(formats.format_positive_levels("fp6")[-1],14.)

    def test_same_storage_and_symmetry_as_historical_format(self):
        J=[[0.,.13,.8],[.13,0.,-.27],[.8,-.27,0.]]
        h=[.01,-.2,1.]
        for old,new in (("fp4","fp4_fn"),("fp6","fp6_fn")):
            a=formats.quantize_couplings(J,h,old)
            b=formats.quantize_couplings(J,h,new)
            self.assertEqual(a["coefficient_bits"],b["coefficient_bits"])
            self.assertEqual(a["metadata_bits"],b["metadata_bits"])
            self.assertEqual(b["J"][0][2],b["J"][2][0])
            self.assertEqual(b["scales"]["J"][0]["group"],["global"])


if __name__=="__main__":
    unittest.main()
