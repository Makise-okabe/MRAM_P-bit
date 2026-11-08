"""Small E2-GAIN-01 correctness checks; NO solver quality claim or parameter fitting."""
from types import SimpleNamespace
import tempfile
from pathlib import Path
import unittest

from experiments.m1_biqmac_reference_quality_gate import solve_reference
from experiments.m2_e2_response_gate import solve_with_response
from experiments.m2_precision_gain_regime import (
    FORMATS, STRESSES, SEEDS, SPARSE_FORMATS, SPARSE_GRAPH_NAME,
    classify_gap, build_gain_models, load_paired_ideal, select_cal_graph,
    paired_fp_int, write_gap_bitwidth_plot,
)


class TestGainOnlyPrecision(unittest.TestCase):
    def test_frozen_matrix_exact(self):
        self.assertEqual(len(FORMATS),13)
        self.assertEqual(len(SEEDS),24)
        self.assertEqual(STRESSES,(
            ("ideal",0.0),("gain_025",0.025),("gain_050",0.05)
        ))
        self.assertEqual(13*24*(len(STRESSES)-1),624)

    def test_sparse_exact_budget_and_frozen_m1_seed_placement(self):
        path, graph_index, formats, seeds=select_cal_graph(SPARSE_GRAPH_NAME)
        self.assertEqual(str(path),"data/biqmac/raw/ising/t2g10_5555")
        self.assertEqual(graph_index,1)
        self.assertEqual(formats,(
            "ref64","fp4","fp5","fp6","int4","int5","int6"
        ))
        self.assertEqual(seeds[0],20261201+100000)
        self.assertEqual(seeds[-1],20261201+100000+23)
        self.assertEqual(len(formats)*len(seeds)*2,336)
        self.assertEqual(len(formats)*len(seeds),168)
        self.assertEqual(len(set(seeds)),24)

    def test_sparse_direct_fp_int_comparison_and_plot(self):
        path, graph_index, formats, seeds=select_cal_graph(SPARSE_GRAPH_NAME)
        gaps={"ref64":4.0,"fp4":7.0,"fp5":5.0,"fp6":4.0,
              "int4":7.3,"int5":5.2,"int6":4.3}
        rows={}
        summary=[]
        for cidx,(condition,alpha) in enumerate(STRESSES):
            for fmt in formats:
                shift=cidx*0.1
                if fmt=="int6":
                    shift=cidx*0.25
                gap=gaps[fmt]+shift
                for seed in seeds:
                    rows[(condition,fmt,seed)]={"optimality_gap_pct":gap}
                summary.append(dict(condition=condition,configuration=fmt,
                    mean_absolute_gap_pct=gap,
                    ci95_abs_gap_lo_pct=gap-0.2,
                    ci95_abs_gap_hi_pct=gap+0.2))
        pairs=paired_fp_int(rows,graph_name=SPARSE_GRAPH_NAME,
                             formats=formats,seeds=seeds)
        self.assertEqual(len(pairs),3*3)
        r=next(v for v in pairs
               if v["condition"]=="gain_050" and v["width_bits"]==6)
        self.assertAlmostEqual(r["mean_direct_delta_fp_minus_int_pp"],-0.6)
        self.assertAlmostEqual(r["mean_interaction_D_pp"],-0.3)
        self.assertAlmostEqual(r["ci95_direct_delta_lo_pp"],-0.6)
        with tempfile.TemporaryDirectory() as td:
            plot=Path(td)/"gap.svg"
            write_gap_bitwidth_plot(plot,summary,
                                    graph_name=SPARSE_GRAPH_NAME,formats=formats)
            data=plot.read_text(encoding="utf-8")
            self.assertIn("<svg",data)
            self.assertIn("t2g10_5555",data)
            self.assertIn("gain_050",data)

    def test_one_persistent_gain_population_zero_offsets(self):
        a=build_gain_models(100)
        b=build_gain_models(100)
        self.assertEqual(a,b)
        lo,hi=a["gain_025"],a["gain_050"]
        self.assertEqual(lo["per_device_offset_logit"],[0.0]*100)
        self.assertEqual(hi["per_device_offset_logit"],[0.0]*100)
        for x,y in zip(lo["per_device_gain"],hi["per_device_gain"]):
            self.assertLessEqual(abs(x-1),0.0250000001)
            self.assertLessEqual(abs(y-1),0.0500000001)
            self.assertAlmostEqual(y-1,2*(x-1),places=14)

    def test_absolute_ci_classification(self):
        self.assertEqual(classify_gap(2,4.9),"acceptable")
        self.assertEqual(classify_gap(5.01,7.4),"degraded")
        self.assertEqual(classify_gap(7.51,8),"failure")
        self.assertEqual(classify_gap(4.9,5.1),"uncertain")
        self.assertEqual(classify_gap(7.4,7.6),"uncertain")

    def test_ideal_transfer_bit_identical_to_original_software(self):
        g=SimpleNamespace(n=3, edges=[(0,1,3.0),(0,2,-2.0),(1,2,1.0)])
        es=[(0,1,-3.0),(0,2,2.0),(1,2,-1.0)]
        adj=[[],[],[]]
        for i,j,w in es:
            adj[i].append((j,w))
            adj[j].append((i,w))
        rep=dict(edges=es,adjacency=adj)
        model=build_gain_models(3)["gain_050"]
        model["per_device_gain"]=[1.0]*3
        for s in (3,31,20261201):
            a=solve_reference(g,rep,0.1,700,s,"linear")
            b=solve_with_response(g,rep,0.1,700,s,model)
            self.assertEqual(a,b)

    def test_reject_nonfrozen_raw_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"fake.csv"
            path.write_text("graph,configuration,seed\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                load_paired_ideal(path,graph_sha="fake",optimum=123.0)


if __name__=="__main__":
    unittest.main()
