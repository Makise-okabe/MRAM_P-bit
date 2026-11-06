"""Unit tests for E1 paired cut comparison, not evidence of graph quality."""
import unittest
from scripts.m1_biqmac_paired_report import analyze


def make_row(graph,seed,fmt,policy,score,flips=3):
    return {
       "graph":graph,"graph_sha256":"dummy-hash",
       "seed":str(seed),"format":fmt,"scale_policy":policy,
       "returned_original_cut":str(score),
       "final_original_cut":str(score-1),
       "actual_flips":str(flips),"improvements":"2",
       "zeroed_edges":"0","relative_abs_coefficient_error":"0.0",
       "zeroed_abs_weight_fraction":"0.0",
    }


class TestPairedReport(unittest.TestCase):
    def rows(self):
        result=[]
        for seed in (1,2):
            result.extend([
              make_row("toy",seed,"ref64","source",100),
              make_row("toy",seed,"fp6_fn","mse",90 if seed==1 else 105),
              make_row("toy",seed,"int6","mse",100),
              make_row("toy",seed,"bfp6","mse",100),
            ])
        return result

    def test_mean_paired_difference_and_wins(self):
        d=analyze(self.rows())
        fp=next(x for x in d["configuration_summaries"]
                if x["format"]=="fp6_fn")
        self.assertAlmostEqual(fp["mean_paired_delta_cut"],-2.5)
        self.assertEqual(fp["wins_vs_reference"],1)
        self.assertEqual(fp["losses_vs_reference"],1)
        cmp=next(x for x in d["direct_format_comparisons"]
                 if x["candidate_a"]=="fp6_fn:mse" and x["candidate_b"]=="int6:mse")
        self.assertEqual((cmp["a_wins"],cmp["ties"],cmp["b_wins"]),(1,0,1))

    def test_missing_seed_is_rejected(self):
        rows=self.rows()
        rows=[r for r in rows if not
              (r["seed"]=="2" and r["format"]=="fp6_fn")]
        with self.assertRaisesRegex(ValueError,"not all seeds"):
            analyze(rows)

    def test_duplicate_row_is_rejected(self):
        rows=self.rows()
        with self.assertRaisesRegex(ValueError,"duplicate paired"):
            analyze(rows+[rows[0]])

if __name__=="__main__":
    unittest.main()
