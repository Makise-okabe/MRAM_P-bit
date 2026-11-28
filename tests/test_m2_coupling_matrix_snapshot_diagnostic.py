"""Read-only coupling-matrix snapshot diagnostic: small numerical checks.

Never launches the 50k-update solver.
"""
import math
import unittest
from types import SimpleNamespace

from experiments.m1_biqmac_ideal_pilot import prepare
from experiments.m1_precision_codebooks import build_global
from experiments.m2_stt_pbit_transfer_preflight import logistic
from experiments.m2_coupling_matrix_snapshot_diagnostic import (
    ALL_FORMATS, PHASES, RESPONSE_LEVELS, EXPECTED_REFERENCE_STATES,
    EXPECTED_DIAGNOSTIC_ROWS, EXPECTED_EXISTING_GAPS,
    decode_spins, check_cut, local_fields, snapshot_metrics
)


class TestCouplingMatrixSnapshots(unittest.TestCase):
    def test_exact_analysis_scope_zero_solver_runs(self):
        self.assertEqual(ALL_FORMATS,
            ("ref64","fp4","fp5","fp6","int4","int5","int6","fp8","int8"))
        self.assertEqual(RESPONSE_LEVELS,(0.0,0.8,1.6))
        self.assertEqual(PHASES,(0.5,1.0,2.0))
        self.assertEqual(EXPECTED_REFERENCE_STATES,144)
        self.assertEqual(EXPECTED_EXISTING_GAPS,1296)
        self.assertEqual(EXPECTED_DIAGNOSTIC_ROWS,3888)

    def test_spin_hex_decode_and_original_cut_are_not_quantized(self):
        self.assertEqual(decode_spins("5",3),(1,-1,1))
        self.assertEqual(decode_spins("0",3),(-1,-1,-1))
        with self.assertRaises(ValueError):
            decode_spins("8",3)
        g=SimpleNamespace(n=3,edges=((0,1,4.0),(0,2,-1.0),(1,2,2.0)))
        spins=check_cut(g,6.0,"5",6.0,0.0)
        self.assertEqual(spins,(1,-1,1))
        with self.assertRaises(ValueError):
            check_cut(g,6.0,"5",5.0,100.0/6.0)

    def test_symmetric_j_and_delta_h_identity(self):
        graph=SimpleNamespace(n=3,edges=((0,1,4.0),(0,2,-1.0),(1,2,2.0)))
        ref=prepare(graph,"ref64","source")
        quant=build_global(graph,"fp",4)
        spin=(1,-1,1)
        exact=local_fields(ref,spin)
        q=local_fields(quant,spin)
        self.assertEqual(len(exact),3)
        for i,j,jij in quant["edges"]:
            self.assertIn((j,jij),quant["adjacency"][i])
            self.assertIn((i,jij),quant["adjacency"][j])
            self.assertEqual(jij,dict(quant["adjacency"][i])[j])
        for i in range(3):
            d=sum((dict(quant["adjacency"][i])[j]-
                   dict(ref["adjacency"][i])[j])*spin[j]
                  for j,_ in ref["adjacency"][i])
            self.assertAlmostEqual(q[i]-exact[i],d,places=10)

    def test_switching_probability_is_same_state_and_same_offset(self):
        href=[-2.0,0.0,1.0,4.0]
        hquant=[-2.5,0.2,0.7,4.3]
        off=[0.8,-0.2,0.4,-1.6]
        b,phase=0.2,1.5
        got=snapshot_metrics(href,hquant,off,b,phase)
        expected=sum(abs(logistic(2*b*phase*q+o)-
                         logistic(2*b*phase*r+o))
                     for r,q,o in zip(href,hquant,off))/4
        self.assertAlmostEqual(got["mean_abs_switch_prob_distortion"],expected,places=14)
        dlogits=[2*b*phase*(q-r) for r,q in zip(href,hquant)]
        self.assertAlmostEqual(got["mean_abs_quantization_logit_error"],
                               sum(map(abs,dlogits))/4,places=14)
        ref=snapshot_metrics(href,href,off,b,phase)
        self.assertEqual(ref["mean_abs_switch_prob_distortion"],0.0)
        self.assertEqual(ref["rms_dH"],0.0)
        self.assertGreater(ref["mean_abs_fp64_offset_only_prob_shift"],0)
        ideal=snapshot_metrics(href,href,[0.0]*4,b,phase)
        self.assertEqual(ideal["mean_abs_fp64_offset_only_prob_shift"],0.0)


if __name__=="__main__":
    unittest.main()
