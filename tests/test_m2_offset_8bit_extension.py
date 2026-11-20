"""Unit tests for the already-triggered 192-run FP8/INT8 extension (no real sweeps)."""
import unittest

from experiments.m2_offset_fp64_scout import GRAPH_SPECS, paired_seed
from experiments.m2_offset_precision_primary import LEVELS, FORMATS
from experiments.m2_offset_8bit_extension import (
    EXT_FORMATS, report_8bit, final_knee
)


class TestOffsetEightBitExtension(unittest.TestCase):
    def test_exact_extension_count_and_original_pairing(self):
        self.assertEqual(EXT_FORMATS,("fp8","int8"))
        self.assertEqual(FORMATS,("fp4","fp5","fp6","int4","int5","int6"))
        self.assertEqual(LEVELS,(0.8,1.6))
        self.assertEqual(len(GRAPH_SPECS)*len(LEVELS)*len(EXT_FORMATS)*24,192)
        self.assertEqual(paired_seed(1)[0],20261201+100000)
        self.assertEqual(paired_seed(2)[0],20261201+200000)

    def test_extension_ci_comparison_and_absolute_quality_gate(self):
        needed=[dict(graph=name,offset_logit_halfspan=d)
                for name,_ in GRAPH_SPECS for d in LEVELS]
        source={name:(None,index,100) for name,index in GRAPH_SPECS}
        ideal8={}; fp64={}; new={}
        for name,index in GRAPH_SPECS:
            for seed in paired_seed(index):
                ideal8[(name,"fp8",seed)]={"gap_pct":4.0}
                ideal8[(name,"int8",seed)]={"gap_pct":4.0}
                for d in LEVELS:
                    fp64[(name,d,seed)]={"gap_pct":5.6}
                    new[(name,d,"fp8",seed)]={"gap_pct":5.4}
                    new[(name,d,"int8",seed)]={"gap_pct":5.7}
        s,p=report_8bit(source,ideal8,fp64,new,needed)
        self.assertEqual(len(s),8)
        self.assertEqual(len(p),4)
        for r in s:
            self.assertFalse(r["eligible"])
            self.assertFalse(r["absolute_quality_met"])
        self.assertAlmostEqual(p[0]["mean_direct_delta_fp_minus_int_pp"],-0.3)
        self.assertAlmostEqual(p[0]["mean_interaction_D_pp"],-0.3)

    def test_knee_is_lowest_tested_passing_width_and_is_not_monotone(self):
        primary=[]
        for name,_ in GRAPH_SPECS:
            for d in LEVELS:
                for fam in ("fp","int"):
                    for b in (4,5,6):
                        primary.append(dict(graph=name,offset_logit_halfspan=d,
                                            configuration=f"{fam}{b}",
                                            eligible=(fam=="fp" and b==4 and d==0.8)))
        extension=[]
        for name,_ in GRAPH_SPECS:
            for d in LEVELS:
                for fam in ("fp","int"):
                    extension.append(dict(graph=name,offset_logit_halfspan=d,
                                          configuration=f"{fam}8",
                                          eligible=True))
        knees=final_knee(primary,extension)
        self.assertEqual(len(knees),8)
        for r in knees:
            if r["family"]=="fp" and r["offset_logit_halfspan"]==0.8:
                self.assertEqual(r["lowest_eligible_tested_width"],4)
                self.assertEqual(r["eligible_tested_widths"],"4,8")
            else:
                self.assertEqual(r["lowest_eligible_tested_width"],8)


if __name__=="__main__":
    unittest.main()
