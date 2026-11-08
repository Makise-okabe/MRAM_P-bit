"""Small fixed-matrix tests for E2 offset precision. No solver sweeps here."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.m2_offset_fp64_scout import GRAPH_SPECS, paired_seed, models
from experiments.m2_offset_precision_primary import (
    LEVELS, FORMATS, COMPARATORS, EXPECTED_NEW, EXPECTED_IDEAL,
    EXPECTED_SCOUT_REFS, summarize, extension_cells, write_svg
)


class TestOffsetPrecisionPrimary(unittest.TestCase):
    def test_exact_fixed_budget_and_original_graph_seeds(self):
        self.assertEqual(LEVELS,(0.8,1.6))
        self.assertEqual(FORMATS,("fp4","fp5","fp6","int4","int5","int6"))
        self.assertEqual(COMPARATORS,("ref64",)+FORMATS)
        self.assertEqual(EXPECTED_NEW,576)
        self.assertEqual(EXPECTED_SCOUT_REFS,96)
        self.assertEqual(EXPECTED_IDEAL,336)
        self.assertEqual(GRAPH_SPECS,(("t2g10_5555",1),("ising2.5-100_5555",2)))
        self.assertEqual(paired_seed(1)[0],20261201+100000)
        self.assertEqual(paired_seed(2)[0],20261201+200000)

    def test_selected_models_are_persistent_offset_only(self):
        m=models(100)
        a,b=m[0.8],m[1.6]
        self.assertEqual(a["per_device_gain"],[1.0]*100)
        self.assertEqual(b["per_device_gain"],[1.0]*100)
        for x,y in zip(a["per_device_offset_logit"],
                       b["per_device_offset_logit"]):
            self.assertAlmostEqual(y,2*x,places=13)

    def test_direct_comparisons_are_different_from_interactions(self):
        ideal={};fp64={};low={}
        for name,index in GRAPH_SPECS:
            for seed in paired_seed(index):
                for fmt in COMPARATORS:
                    ideal[(name,fmt,seed)]={"gap_pct":3.0}
                for d in LEVELS:
                    fp64[(name,d,seed)]={"gap_pct":4.0 if d==0.8 else 5.6}
                    for fmt in FORMATS:
                        # d=0.8 FP6 and INT6 pass, d=1.6 neither passes
                        gap=(4.2 if fmt=="fp6" else 4.5 if fmt=="int6" else 4.0)
                        if d==1.6:
                            gap=5.5 if fmt=="fp6" else 5.7
                        low[(name,d,fmt,seed)]={"gap_pct":gap}
        s,p=summarize({},ideal,fp64,low)
        self.assertEqual(len(s),2*3*7)
        self.assertEqual(len(p),2*3*3)
        p6=next(x for x in p if x["graph"]=="t2g10_5555"
                and x["width_bits"]==6
                and x["offset_logit_halfspan"]==0.8)
        self.assertAlmostEqual(p6["mean_direct_delta_fp_minus_int_pp"],-0.3)
        self.assertAlmostEqual(p6["mean_interaction_D_pp"],-0.3)
        f=next(x for x in s if x["graph"]=="t2g10_5555"
               and x["offset_logit_halfspan"]==1.6
               and x["configuration"]=="fp6")
        # Negative FP64 quantization penalty is NOT enough when absolute
        # original-weight gap fails the fixed 5% CI threshold.
        self.assertLess(f["mean_quantization_loss_pp"],0)
        self.assertFalse(f["absolute_quality_met"])
        self.assertFalse(f["eligible"])
        ext=extension_cells(s)
        self.assertEqual(len(ext),2)
        self.assertEqual(sum(x["additional_solver_runs"] for x in ext),96)
        self.assertTrue(all(x["extension_formats"]=="fp8,int8" and
                            x["status"]=="NOT_RUN" for x in ext))
        with TemporaryDirectory() as folder:
            path=Path(folder)/"test.svg"
            write_svg(path,s)
            svg=path.read_text(encoding="utf-8")
            self.assertIn("<svg",svg)
            self.assertIn("±1.6 logit",svg)
            self.assertIn("t2g10_5555",svg)

    def test_extension_if_just_one_six_bit_fails(self):
        rows=[]
        for name,_ in GRAPH_SPECS:
            for d in LEVELS:
                rows.append({"graph":name,"offset_logit_halfspan":d,
                             "configuration":"fp6","eligible":True})
                rows.append({"graph":name,"offset_logit_halfspan":d,
                             "configuration":"int6","eligible":True})
        self.assertEqual(extension_cells(rows),[])
        rows[-1]["eligible"]=False
        needed=extension_cells(rows)
        self.assertEqual(len(needed),1)
        self.assertEqual(needed[0]["additional_solver_runs"],48)


if __name__=="__main__":
    unittest.main()
