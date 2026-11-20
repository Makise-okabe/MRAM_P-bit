"""Finite synthetic checks; official SHA/archive replays gate freeze before science."""
import json
import math
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph,prepare
from experiments.m1_precision_codebooks import build_global, scalar_quantize,WIDTHS,describe_codebook
from experiments.fyp_first_block_20261120 import (
    ARMS, GRAPH_INFO, projection, solve_logged, compare_solver,
    field_fidelity, hex_state, state_from_hex, append_jsonl, read_jsonl,
)
from experiments.fyp_first_block_stats import (
    CORE_REGISTRY,DEVICE_REGISTRY, CORE_TAIL_Q,DEVICE_TAIL_Q,
    paired_t_interval,claims,
)


class TestFirstBlock(unittest.TestCase):
    def toy(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        path=Path(tmp.name)/"toy.rudy"
        path.write_text("4 6\n1 2 9\n1 3 -7\n1 4 4\n2 3 12\n2 4 -3\n3 4 5\n")
        return load_rudy(path)

    def test_locked_registry_and_seeds(self):
        self.assertEqual(len(CORE_REGISTRY),18)
        self.assertEqual(len(set(CORE_REGISTRY)),18)
        self.assertEqual(len(DEVICE_REGISTRY),6)
        self.assertAlmostEqual(CORE_TAIL_Q,0.04/36)
        self.assertAlmostEqual(DEVICE_TAIL_Q,0.01/12)
        self.assertEqual([x[0] for x in ARMS],["ref64","fp5_raw","int6_raw","fp5_cal","int6_cal"])
        self.assertEqual([g[3] for g in GRAPH_INFO],[3000000000000,3000000020000])

    def test_int7_existing_semantics(self):
        self.assertEqual(WIDTHS,(4,5,6,8))
        self.assertEqual(describe_codebook("int",7)["min_code_unused"],-64)
        self.assertEqual(scalar_quantize(63.5,"int",7,1),63)
        self.assertEqual(scalar_quantize(-2.5,"int",7,1),-2)

    def test_instrumentation_parity_small_original_and_quantized(self):
        g=self.toy(); b=beta_from_original_graph(g)
        for rep in [prepare(g,"ref64","source"),build_global(g,"fp",5),build_global(g,"int",6)]:
            for seed in (5,70,777):
                got=compare_solver(g,rep,b,600,seed)
                self.assertGreaterEqual(got["V"],got["M"])
                self.assertGreaterEqual(got["M"],got["R"])
                cstar=100
                self.assertAlmostEqual(cstar-got["R"],(cstar-got["V"])+(got["V"]-got["M"])+(got["M"]-got["R"]))
                self.assertEqual(len(got["checkpoints"]),1)

    def test_source_projection_and_beta_control(self):
        g=self.toy();src=prepare(g,"ref64","source")
        doubled={"edges":[(i,j,2*q) for i,j,q in src["edges"]],
                 "adjacency":[[(j,2*q) for j,q in row] for row in src["adjacency"]]}
        self.assertEqual(projection(g,doubled),2.0)
        beta=beta_from_original_graph(g)
        for seed in (3,11,177):
            a=solve_logged(g,src,beta,350,seed,checkpoints=(200,350))
            b=solve_logged(g,doubled,beta/2,350,seed,checkpoints=(200,350))
            for key in ("returned_state_hex","actual_flips","improvements","V","M","R"):
                self.assertEqual(a[key],b[key])

    def test_fidelity_same_rep_is_zero(self):
        g=self.toy();rep=prepare(g,"ref64","source")
        state=hex_state((1,-1,1,-1))
        self.assertEqual(state_from_hex(state,4),(1,-1,1,-1))
        f=field_fidelity(g,state,rep,0.1)
        self.assertEqual(f,{"field_rms":0.0,"logit_rms":0.0,"probability_mae":0.0})

    def test_record_checksums_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"file.jsonl"
            append_jsonl(p,{"graph":"toy","seed":2})
            self.assertEqual(read_jsonl(p),[{"graph":"toy","seed":2}])
            with p.open("a") as f: f.write('{"malformed":')
            with self.assertRaisesRegex(ValueError,"corrupt"):
                read_jsonl(p)

    def test_studentized_intervals_and_decisions(self):
        self.assertEqual(paired_t_interval([1.5]*128,resamples=500,seed=1),(1.5,1.5,1.5))
        a=[((i*23)%131-65)/10 for i in range(128)]
        r=paired_t_interval(a,resamples=12000,seed=707)
        self.assertEqual(r,paired_t_interval(a,resamples=12000,seed=707))
        self.assertLess(r[1],r[0]); self.assertGreater(r[2],r[0])
        self.assertTrue(claims(-0.8,-1.2,-0.6)["true_benefit_gt_0p5pp"])
        self.assertTrue(claims(-0.1,-0.3,0.2)["practically_equivalent"])
        self.assertFalse(claims(-0.6,-1.1,0.1)["statistical_superiority"])
        # A change in significance labels alone cannot establish interaction.
        self.assertFalse(claims(0.0,-0.2,0.2)["statistical_superiority"])


if __name__=="__main__":unittest.main()
