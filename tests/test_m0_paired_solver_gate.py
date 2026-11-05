import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import m0_paired_solver_gate as gate
import m0_reference as base
import m0_parallel_tempering as pt

class PairedGateTests(unittest.TestCase):
    def test_exact_update_budget(self):
        x=base.maxcut_instance(4,13)
        rows=gate.run_case(x,42,5,(.1,.3,.6))
        self.assertEqual({r["total_spin_updates"] for r in rows},{60})
        self.assertEqual([r["method"] for r in rows],["PT","Gibbs"])
        self.assertEqual(rows[0]["swap_attempts"],5)
        self.assertEqual(rows[1]["swap_attempts"],0)

    def test_repeatability(self):
        x=base.maxcut_instance(4,9)
        self.assertEqual(gate.run_case(x,46,8,(.1,.2,.5)),
                         gate.run_case(x,46,8,(.1,.2,.5)))

    def test_feasible_target_and_pairs(self):
        x=base.tsp_instance(3,12)
        r=gate.run_case(x,3,5,(.1,.2,.5))
        for row in r:
            self.assertIsInstance(row["hit"],bool)
            self.assertEqual(row["total_spin_updates"],135)
        pairs=[
          dict(method="PT",instance_seed=1,solver_seed=2,hit=True),
          dict(method="Gibbs",instance_seed=1,solver_seed=2,hit=False),
        ]
        s=gate.summarize(pairs,"tsp",3,1,1,5,(.1,.5))
        self.assertEqual(s["paired_outcome_counts"]["pt_only"],1)

if __name__=="__main__":
    unittest.main()
