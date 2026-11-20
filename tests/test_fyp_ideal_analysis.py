"""Synthetic verification of the locked estimands and decision implementation."""
import importlib.util
import json
import copy
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

SPEC = importlib.util.spec_from_file_location(
    "fyp_ideal_analysis", Path(__file__).resolve().parents[1]/"experiments/fyp_ideal_analysis.py")
a = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(a)


class LockedRegistryTests(unittest.TestCase):
    def test_exact_registry_and_multiplicity(self):
        r = a.analysis_registry()
        self.assertEqual(len(a.CORE_REGISTRY), 18)
        self.assertEqual(len(set(a.CORE_REGISTRY)), 18)
        self.assertEqual([sum(x[0] == f for x in a.CORE_REGISTRY) for f in a.FAMILIES], [9, 9])
        self.assertEqual(a.CORE_TAIL_Q, .04/36)
        self.assertEqual(r["resamples"], 500000)
        self.assertEqual(r["core_seed_sequences"]["torus"], [20261120, 940, 1])
        self.assertEqual(r["descriptive_seed_sequences"]["ring"], [20261120, 940, 0, 1])
        self.assertIn("[20261120,940,family,2,anchor_label_index]", r["anchor_seed_sequences"])
        self.assertIn("int7", a.CANDIDATES)
        self.assertEqual(r["descriptive"]["alpha_from_core"], 0)
        self.assertEqual(a.PREDICTIONS["fp6-int6"], "none")

    def test_ni_is_at_margin_not_zero(self):
        # Statistically worse is still noninferior within the stated tolerance.
        d = a.decision_labels(.3, .1, .49)
        self.assertEqual(d["qualification"], "PASS")
        self.assertTrue(d["statistical_inferiority"])
        self.assertTrue(d["practically_equivalent"])
        d = a.decision_labels(.47, .18, .75)
        self.assertEqual(d["qualification"], "UNRESOLVED")
        self.assertTrue(d["statistical_inferiority"])
        self.assertEqual(a.decision_labels(.8, .51, 1.1)["qualification"], "FAIL")

    def test_strict_bounds_and_benefit_claims(self):
        self.assertEqual(a.decision_labels(.3, .1, .5)["qualification"], "UNRESOLVED")
        self.assertEqual(a.decision_labels(.7, .5, .9)["qualification"], "UNRESOLVED")
        d = a.decision_labels(-.6, -.9, -.2)
        self.assertTrue(d["estimated_benefit_gt_margin"])
        self.assertFalse(d["true_benefit_gt_margin"])
        self.assertTrue(a.decision_labels(-.8, -1.2, -.51)["true_benefit_gt_margin"])
        self.assertEqual(a.decision_labels(.3, .1, .49, .25)["qualification"], "UNRESOLVED")
        self.assertEqual(a.decision_labels(0, None, None)["qualification"], "UNRESOLVED")
        with self.assertRaises(ValueError):
            a.decision_labels(0, 1, -1)


class BootstrapTests(unittest.TestCase):
    def test_t_pivot_and_quantile_inversion_against_direct_formula(self):
        x = np.arange(1., 73.)**1.7
        rng = np.random.Generator(np.random.PCG64DXSM(np.random.SeedSequence([20261120,940,0])))
        star = x[rng.integers(0, len(x), size=(2000, len(x)))]
        mean = x.mean()
        se = x.std(ddof=1)/math.sqrt(len(x))
        pivot = (star.mean(axis=1)-mean)/(star.std(axis=1,ddof=1)/math.sqrt(len(x)))
        expected_low = mean-np.quantile(pivot,1-a.CORE_TAIL_Q,method="linear")*se
        expected_high = mean-np.quantile(pivot,a.CORE_TAIL_Q,method="linear")*se
        got = a.bootstrap_t_vectors(x,resamples=2000,batch=361)[0]
        self.assertEqual(got["low"], expected_low)
        self.assertEqual(got["high"], expected_high)

    def test_joint_indices_preserve_exact_linear_relationship(self):
        x = np.linspace(-2, 3, 72)**3
        columns = np.column_stack((x, -x, 2*x+7))
        r = a.bootstrap_t_vectors(columns, resamples=4000, batch=337)
        self.assertTrue(all(v["status"] == "OK" for v in r))
        self.assertAlmostEqual(r[1]["low"], -r[0]["high"], places=12)
        self.assertAlmostEqual(r[1]["high"], -r[0]["low"], places=12)
        self.assertAlmostEqual(r[2]["low"], 2*r[0]["low"]+7, places=12)
        self.assertAlmostEqual(r[2]["high"], 2*r[0]["high"]+7, places=12)

    def test_reproducible_across_batch_sizes(self):
        x = np.arange(72.)**1.5
        r1 = a.bootstrap_t_vectors(x, resamples=1200, batch=77)
        r2 = a.bootstrap_t_vectors(x, resamples=1200, batch=499)
        self.assertEqual(r1, r2)

    def test_more_stringent_tail_is_wider(self):
        x = np.linspace(-1, 1, 72)**3
        ordinary = a.bootstrap_t_vectors(x, q=.025, resamples=4000)[0]
        simultaneous = a.bootstrap_t_vectors(x, q=.04/36, resamples=4000)[0]
        self.assertLess(simultaneous["low"], ordinary["low"])
        self.assertGreater(simultaneous["high"], ordinary["high"])

    def test_observed_constant_is_not_proven_equality(self):
        x = np.column_stack((np.zeros(72), np.full(72, .3)))
        r = a.bootstrap_t_vectors(x, resamples=20)
        self.assertTrue(all(v["low"] is None for v in r))
        self.assertTrue(all(a.decision_labels(v["mean"], v["low"], v["high"])["qualification"] == "UNRESOLVED" for v in r))
        p = a.bootstrap_t_vectors(x, resamples=20, deterministic_equal=[True, False])
        self.assertEqual((p[0]["low"], p[0]["high"]), (0., 0.))
        self.assertEqual(p[0]["status"], "DETERMINISTIC_EQUALITY_PROVEN")
        self.assertIsNone(p[1]["low"])
        with self.assertRaises(ValueError):
            a.bootstrap_t_vectors(x, resamples=20, deterministic_equal=[False, True])

    def test_unstable_studentization_is_not_dropped(self):
        r = a.bootstrap_t_vectors([0., 1.], resamples=200)[0]
        self.assertGreater(r["bad_resamples"], 0)
        self.assertIsNone(r["low"])


class MechanismTests(unittest.TestCase):
    def test_identity_and_signs_with_nonzero_fp64_selection(self):
        c = {"V": 100, "M": 98, "R": 95, "R_last": 93}
        r = {"V": 99, "M": 98, "R": 97}
        z = a.mechanism_values(c, r, 200)
        self.assertEqual(z["A_pp"], -.5)
        self.assertEqual(z["Rz_pp"], 2.5)
        self.assertEqual(z["Rz_reference_pp"], 1.)
        self.assertEqual(z["extra_pp"], 1.)
        self.assertEqual(z["extra_pp"], z["A_pp"]+z["Rz_pp"]-z["Rz_reference_pp"])
        self.assertEqual(z["represented_selection_pp"]+z["earliest_tie_pp"], z["Rz_pp"])
        self.assertEqual(z["R_last_minus_R"], -2.)
        c["R_last"] = 98
        self.assertEqual(a.mechanism_values(c, r, 200)["R_last_minus_R"], 3.)
        del c["R_last"]
        self.assertIsNone(a.mechanism_values(c, r, 200)["R_last_minus_R"])

    def test_invalid_order_or_denominator_rejected(self):
        good = {"V": 100, "M": 100, "R": 99}
        with self.assertRaises(ValueError):
            a.mechanism_values({"V": 98, "M": 100, "R": 99}, good, 100)
        with self.assertRaises(ValueError):
            a.mechanism_values(good, good, 0)

    def test_tied_spearman_and_undefined_cases(self):
        np.testing.assert_array_equal(a.rank_average([3,1,1,5]), [3,1.5,1.5,4])
        self.assertAlmostEqual(a.spearman([1,1,2,3], [8,8,4,1])["rho"], -1.)
        self.assertIsNone(a.spearman([1,1,1], [1,2,3])["rho"])
        self.assertIsNone(a.spearman([1,2,float("nan")], [1,2,3])["rho"])


def pool_fixture():
    main = [{"representation": f, "seed": s, "V": 100+s, "R": 95,
             "V_state_hex": str(100+s)} for f in a.CANDIDATES for s in (1,2)]
    refs = [{"representation": "ref64", "seed": s, "V": 120+s,
             "R": 110, "V_state_hex": str(120+s)} for s in (10,11,12)]
    return main, refs


class ReferencePoolTests(unittest.TestCase):
    def test_fixed_pool_uses_best_visited_not_returned(self):
        main, refs = pool_fixture()
        main[0].update(V=200, V_state_hex="200")
        b = a.fixed_reference_pool(main, refs, seeds_per_candidate=2, reference_count=3,
                                   verify_cut=lambda state: int(state))
        self.assertEqual(b["B_g"], 200)
        self.assertEqual(b["value_field"], "V")
        self.assertTrue(b["rescore_verified"])
        self.assertEqual(b["pool_main_count"], 14)
        self.assertEqual(b["pool_reference_count"], 3)

    def test_extra_missing_duplicate_and_nonindependent_rows_fail(self):
        main, refs = pool_fixture()
        for mm, rr in ((main[:-1], refs), (main+[main[0]], refs),
                       (main[:-1]+[main[0]], refs), (main, refs[:-1])):
            with self.assertRaises(ValueError):
                a.fixed_reference_pool(mm, rr, seeds_per_candidate=2, reference_count=3)
        refs[0]["seed"] = 1
        with self.assertRaises(ValueError):
            a.fixed_reference_pool(main, refs, seeds_per_candidate=2, reference_count=3)

    def test_exact_rescoring_required_and_empty_fallback(self):
        main, refs = pool_fixture()
        with self.assertRaises(ValueError):
            a.fixed_reference_pool(main, refs, seeds_per_candidate=2, reference_count=3, verify_cut=lambda _: -1)
        for r in main+refs:
            r["V"] = -1
        b = a.fixed_reference_pool(main, refs, seeds_per_candidate=2, reference_count=3)
        self.assertEqual(b["B_g"], 0)
        self.assertFalse(b["normalized_qualification_defined"])


def qualification_rows(passing):
    rows = []
    for left, right in a.CORE_PAIRS:
        low, high = ((-.1,.2) if left in passing else (.2,.8)) if right == "ref64" else (-.3,.3)
        rows.append({"contrast": f"{left}-{right}", "mean": (low+high)/2,
                     "low": low, "high": high, **a.decision_labels((low+high)/2, low, high)})
    return rows


class SelectionTests(unittest.TestCase):
    def test_lowest_certified_is_not_true_minimum(self):
        selected = a.select_pair(qualification_rows({"fp6", "int7", "int8"}))
        self.assertEqual(selected["lowest_tested_certified_FP"], "fp6")
        self.assertEqual(selected["lowest_tested_certified_INT"], "int7")
        self.assertEqual(selected["k_cert"], 1)
        self.assertEqual(selected["smaller_unresolved_FP"], ["fp5"])
        self.assertEqual(selected["smaller_unresolved_INT"], ["int5", "int6"])
        self.assertEqual(selected["selected_pair_bounds"]["method"], "registered_direct_contrast")
        self.assertFalse(selected["offset_run_authorized"])

    def test_either_missing_class_invokes_registered_fallback(self):
        for passing in ({"int5"}, {"fp5"}, set()):
            selected = a.select_pair(qualification_rows(passing))
            self.assertTrue(selected["diagnostic_fallback"])
            self.assertEqual((selected["selected_FP"], selected["selected_INT"]), ("fp6", "int6"))
            self.assertIsNone(selected["k_cert"])

    def test_no_unregistered_pairwise_claim(self):
        selected = a.select_pair(qualification_rows({"fp5", "int5"}))
        bounds = selected["selected_pair_bounds"]
        self.assertEqual(bounds["method"], "conservative_difference_of_simultaneous_bounds")
        self.assertAlmostEqual(bounds["low"], -.3)
        self.assertAlmostEqual(bounds["high"], .3)


class GraphSummaryTests(unittest.TestCase):
    def test_paired_graph_vector_and_signed_last_selection(self):
        rows, fidelity, metrics = [], [], {}
        for k, f in enumerate(a.CANDIDATES):
            metrics[f] = {"zeroed_weight_mass_fraction": k/10, "nonzero_count": 200-k}
            for s in (10,11):
                value = 100+s-k
                rows.append({"representation":f,"seed":s,"V":value+3,"M":value+2,
                             "R":value,"R_last":value+(-1 if s == 10 else 2)})
                if f != "ref64":
                    fidelity.extend({"representation":f,"seed":s,"attempt":t,
                                     "field_rms":1.,"logit_rms":2.,"probability_mae":.03}
                                    for t in a.CHECKPOINTS)
        g = a.summarize_graph(rows, fidelity, metrics, graph="synthetic", family="ring",
                              denominator=200, denominator_label="test_only", reference_B=200,
                              expected_seeds=2, index=0)
        # fp5 has 3 more units of cut than int6: negative contrast favors FP.
        self.assertEqual(g["core"]["fp5-int6"]["mean"], -1.5)
        self.assertEqual(g["candidates"]["fp5"]["mean_R_last_minus_R"], .5)
        self.assertEqual(g["candidates"]["fp5"]["R_last_positive"], 1)
        self.assertEqual(g["candidates"]["fp5"]["R_last_negative"], 1)
        self.assertEqual(g["candidates"]["fp5"]["mean_Rz_pp"], 1.5)
        self.assertEqual(len(g["core"]), 9)
        with self.assertRaises(ValueError):
            a.summarize_graph(rows, fidelity[:-1], metrics, graph="synthetic", family="ring",
                              denominator=200, denominator_label="test", expected_seeds=2)

    def test_synthetic_complete_analysis_exports_eighteen_contrasts(self):
        groups=[]
        for family in a.FAMILIES:
            for index in range(8):
                rows=[]
                fidelity=[]
                metrics={}
                for k,f in enumerate(a.CANDIDATES):
                    metrics[f]={"zeroed_weight_mass_fraction":(index+k)/20,"nonzero_count":200-k}
                    for s in range(4):
                        cut=10000+index*23-s*(k+1)-k*(index+1)
                        rows.append({"representation":f,"seed":s,"V":cut+k+index,"M":cut+k,"R":cut,"R_last":cut+(-1 if s%2 else 1)})
                        if f!="ref64":
                            fidelity.extend({"representation":f,"seed":s,"attempt":t,"field_rms":index+.1,"logit_rms":index+.2,"probability_mae":index/100+.01} for t in a.CHECKPOINTS)
                groups.append(a.summarize_graph(rows,fidelity,metrics,graph=f"synthetic_{family}_{index}",family=family,
                              denominator=11000,denominator_label="SYNTHETIC_ONLY",reference_B=11000,
                              expected_seeds=4,index=index))
        for family, prefix in (("ring","ising2.5-100"),("torus","t2g10")):
            source=next(g for g in groups if g["family"]==family)
            for label in ("5555","6666","7777"):
                anchor=copy.deepcopy(source)
                anchor.update(kind="anchor",graph=f"{prefix}_{label}",index=None)
                groups.append(anchor)
        with tempfile.TemporaryDirectory() as directory:
            got=a.analyse_graph_summaries(groups,directory,resamples=1000,expected_graphs=8)
            self.assertEqual(len(got["core"]),18)
            self.assertEqual(len(got["mechanism"]),12)
            self.assertEqual(len(got["anchors"]),54)
            self.assertTrue((Path(directory)/"RESULTS.md").exists())
            manifest=json.loads((Path(directory)/"analysis_manifest.json").read_text())
            self.assertEqual(manifest["generated_graphs"],16)
            self.assertEqual(manifest["anchors"],6)
            self.assertFalse(manifest["offset_executed"])
            self.assertIn("family_quality_mechanism.csv",manifest["files"])
            self.assertIn("anchor_quality_spread.csv",manifest["files"])


if __name__ == "__main__":
    unittest.main()
