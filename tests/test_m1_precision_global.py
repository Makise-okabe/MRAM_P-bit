"""Frozen precision codebook tests; all are tiny synthetic graphs, not NUS data."""
import math
import tempfile
import unittest
from pathlib import Path

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph, prepare
from experiments.m1_biqmac_reference_quality_gate import solve_reference
from experiments.m1_precision_codebooks import (
    FAMILIES, WIDTHS, FP_LAYOUTS, levels,
    fullscale, scalar_quantize, candidate_scales, fit_global_scale,
    describe_codebook, build_global
)
from experiments.m1_biqmac_precision_sweep import (
    bootstrap_paired_ci, summarize, ADDITIONAL_GAP_TOLERANCE_PP
)


class TestPrecisionGlobal(unittest.TestCase):
    def graph(self,text="4 4\n1 2 -10\n2 3 7\n3 4 -1\n1 4 9\n"):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p=Path(tmp.name)/"toy.rudy"
        p.write_text(text,encoding="utf-8")
        return load_rudy(p)

    def test_all_codebooks_have_exactly_declared_width(self):
        self.assertEqual(WIDTHS,(4,5,6,8))
        self.assertEqual(FP_LAYOUTS,{4:(2,1),5:(2,2),6:(3,2),8:(4,3)})
        for family in FAMILIES:
            for bits in WIDTHS:
                d=describe_codebook(family,bits)
                self.assertTrue(d["one_quantized_edge_shared_both_directions"])
                self.assertEqual(d["width"],bits)
                self.assertEqual(d["scale_bits"],8 if family=="bfp" else 32)
                if family=="fp":
                    e,m=FP_LAYOUTS[bits]
                    self.assertEqual(e+m+1,bits)
                    self.assertEqual(len(levels(bits)),2**(e+m))
                    self.assertTrue(d["finite_only"])
                    self.assertTrue(d["subnormals"])
                else:
                    self.assertEqual(d["min_represented"]+d["max_represented"],0)

    def test_fp_subnormal_and_ties_to_even(self):
        self.assertEqual(levels(4)[1],0.5)
        self.assertEqual(scalar_quantize(0.25,"fp",4,1.0),0.0)
        self.assertEqual(scalar_quantize(0.75,"fp",4,1.0),1.0)
        self.assertEqual(scalar_quantize(1.25,"fp",4,1.0),1.0)
        self.assertEqual(scalar_quantize(100.0,"fp",4,1.0),6.0)
        self.assertEqual(scalar_quantize(-100.0,"fp",4,1.0),-6.0)
        self.assertEqual(levels(8)[-1],480.0)
        self.assertEqual(scalar_quantize(0.03125,"fp",6,1.0),0.0)

    def test_int_rounding_and_saturation_every_width(self):
        for width in WIDTHS:
            maxq=(1<<(width-1))-1
            self.assertEqual(scalar_quantize(2.5,"int",width,1.0),2.0)
            self.assertEqual(scalar_quantize(-2.5,"int",width,1.0),-2.0)
            self.assertEqual(scalar_quantize(10000,"int",width,1.0),maxq)
            self.assertEqual(scalar_quantize(-10000,"bfp",width,1.0),-maxq)

    def test_exact_small_integer_policy_all_fitting_int_widths(self):
        g=self.graph()
        truth=prepare(g,"ref64","source")["edges"]
        for bits in (5,6,8):
            p=build_global(g,"int",bits)
            self.assertEqual(p["scale"],1.0)
            self.assertEqual(p["edges"],truth)
            self.assertEqual(p["coefficient_mse"],0.0)
        p4=build_global(g,"int",4)
        self.assertNotEqual(p4["edges"],truth)

    def test_exact_int_five_reproduces_reference_per_seed_under_linear(self):
        g=self.graph()
        beta=beta_from_original_graph(g)
        ref=prepare(g,"ref64","source")
        i5=build_global(g,"int",5)
        self.assertEqual(ref["edges"],i5["edges"])
        for seed in (20261201,20261202,20261203):
            a=solve_reference(g,ref,beta,100,seed,"linear")
            b=solve_reference(g,i5,beta,100,seed,"linear")
            self.assertEqual(a,b)

    def test_bfp_one_exponent_global_symmetric(self):
        g=self.graph()
        p=build_global(g,"bfp",4)
        self.assertEqual(p["scale_metadata_bits"],8)
        self.assertTrue(math.log2(p["scale"]).is_integer())
        self.assertEqual(p["nominal_one_copy_dense_coefficient_bits"],4*6)
        self.assertEqual(p["nominal_one_copy_dense_total_bits"],4*6+8)
        for i,j,q in p["edges"]:
            self.assertIn((j,q),p["adjacency"][i])
            self.assertIn((i,q),p["adjacency"][j])

    def test_global_scale_fit_is_source_only_and_repeatable(self):
        data=[-10000.0,5.0,4.0,3.0,2.0,1.0]
        for family in FAMILIES:
            for width in WIDTHS:
                a=fit_global_scale(data,family,width)
                b=fit_global_scale(data,family,width)
                self.assertEqual(a,b)
                self.assertTrue(math.isfinite(a[0]))
                self.assertGreater(a[0],0)
                if family=="bfp":
                    self.assertTrue(math.log2(a[0]).is_integer())
        self.assertIn(1.0,candidate_scales([1.0,9.0,-10.0],"int",5))
        self.assertNotIn(1.0,candidate_scales([1.0,9.0,-10.0],"int",4))

    def test_source_encoding_input_cannot_have_nan(self):
        with self.assertRaises(ValueError):
            fit_global_scale([1.0,math.nan],"int",5)
        with self.assertRaises(ValueError):
            scalar_quantize(1.0,"fp",6,0.0)

    def test_bootstrap_paired_ci_degenerate_and_ordered(self):
        self.assertEqual(bootstrap_paired_ci([0.0]*24,1234),(0.0,0.0))
        low,high=bootstrap_paired_ci([float(i-12) for i in range(24)],1,200)
        self.assertLessEqual(low,high)

    def test_aggregate_checks_exactly_matched_seed_coverage(self):
        rows=[]
        for seed in (1,2):
            for config in ["ref64"]+[f"{f}{b}" for f in FAMILIES for b in WIDTHS]:
                family="ref" if config=="ref64" else config.rstrip("4568")
                width=64 if config=="ref64" else int(config[-1])
                rows.append(dict(seed=seed,configuration=config,graph="toy",graph_sha256="test",
                    official_optimum=100,returned_original_cut=90.0,
                    optimality_gap_pct=10.0,actual_flips=1,family=family,width=width,
                    layout="test",scale=1.0,zeroed_nonzero_edges=0,
                    zeroed_abs_weight_fraction=0,
                    relative_abs_coefficient_error=0,
                    nominal_one_copy_dense_total_bits=48))
        result=summarize(rows,0)
        self.assertEqual(len(result),13)
        self.assertTrue(all(x["mean_additional_gap_pp"]==0 for x in result))
        self.assertTrue(all(x["predeclared_useful_precision_gate"]=="YES_PRELIMINARY_WITHIN_GRAPH" for x in result))
        with self.assertRaisesRegex(ValueError,"missing paired"):
            summarize(rows[:-1],0)


if __name__=="__main__":
    unittest.main()
