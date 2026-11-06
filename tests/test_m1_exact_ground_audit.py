import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import m0_ising_math as core
import m0_mimo_reference as mimo
import m1_coupling_formats as formats
import m1_exact_ground_audit as audit


class GroundAuditTests(unittest.TestCase):
    @staticmethod
    def controlled_frame(y):
        # Independent diagonal MIMO frame: original residual is sum((y_i-s_i)^2).
        return dict(tx=2,rx=2,H=[[[1.,0.],[0.,0.]],[[0.,0.],[1.,0.]]],
                    y=[[v,0.] for v in y],transmitted=[1,1],
                    J=[[0.,0.],[0.,0.]],h=[2*v for v in y],
                    C=2+sum(v*v for v in y))

    def controlled_audit(self, y, quant_h, selected):
        ins=self.controlled_frame(y)
        quant=dict(J=[[0.,0.],[0.,0.]],h=quant_h)
        oracle=mimo.exact_ml(ins)
        gap=mimo.original_residual(ins,selected)-oracle["residual"]
        row=dict(frame_index="0",snr_db="0.0",format="fp4",response="ideal",
                 selected_state="".join("1" if v>0 else "0" for v in selected),
                 quantized_selection_energy=str(core.energy(quant["J"],quant["h"],selected)),
                 original_residual_gap=str(gap),ml_hit=str(int(gap<=audit.ATOL)))
        # Control only the represented coefficients, not either exact oracle.
        with patch.object(formats,"quantize_couplings",return_value=quant):
            return audit.audit([row],{(0,0.0):ins})

    def test_quantized_tie_is_not_sampling_miss(self):
        unique,checked,summary=self.controlled_audit([.1,1.],[0.,2.],(-1,1))
        self.assertEqual(unique[0]["quantized_ground_degeneracy"],2)
        self.assertEqual(unique[0]["original_ml_minimizers_in_quantized_ground"],1)
        self.assertEqual(unique[0]["non_ml_minimizers_in_quantized_ground"],1)
        self.assertEqual(checked[0]["selected_is_quantized_minimum"],1)
        self.assertEqual(checked[0]["selection_outcome"],"quantized_tie_non_ml")
        self.assertEqual(summary[0]["missed_original_ml_at_quantized_tie"],1)
        self.assertEqual(summary[0]["missed_original_ml_not_at_quantized_minimum"],0)

    def test_changed_optimum_is_separate_from_sampling(self):
        _,checked,summary=self.controlled_audit([.1,1.],[-.2,2.],(-1,1))
        self.assertEqual(checked[0]["selection_outcome"],"changed_quantized_optimum")
        self.assertEqual(summary[0]["original_ml_not_preserved"],1)
        self.assertEqual(summary[0]["missed_original_ml_at_changed_quantized_optimum"],1)
        self.assertEqual(summary[0]["missed_original_ml_not_at_quantized_minimum"],0)

    def test_selected_state_above_quantized_minimum(self):
        _,checked,summary=self.controlled_audit([.1,1.],[.2,2.],(-1,1))
        self.assertEqual(checked[0]["selection_outcome"],"sampling_miss")
        self.assertGreater(checked[0]["quantized_energy_gap"],0)
        self.assertEqual(summary[0]["missed_original_ml_not_at_quantized_minimum"],1)

    def test_any_degenerate_original_ml_state_counts_as_preserved(self):
        # exact_ml picks (-1,+1), while quantization prefers (+1,+1).
        # Both are ORIGINAL ML states because the first original bias is zero.
        unique,checked,summary=self.controlled_audit([0.,1.],[.2,2.],(1,1))
        self.assertEqual(unique[0]["original_ml_is_quantized_minimizer"],1)
        self.assertEqual(checked[0]["selection_outcome"],"original_ml_hit")
        self.assertEqual(summary[0]["original_ml_hits"],1)

    def test_original_ml_hit_can_coexist_with_missing_quantized_minimum(self):
        _,checked,summary=self.controlled_audit([.1,1.],[-.2,2.],(1,1))
        self.assertEqual(checked[0]["selected_is_quantized_minimum"],0)
        self.assertEqual(checked[0]["selection_outcome"],"original_ml_hit")
        self.assertEqual(summary[0]["original_ml_not_preserved"],1)
        self.assertEqual(summary[0]["missed_original_ml_not_at_quantized_minimum"],0)

    def test_unrounded_fp32_historical_compatibility(self):
        ins=mimo.frame(tx=3,rx=3,snr_db=5,seed=12)
        a=audit.quantized_minima(ins,"fp32",tile=2,legacy_fp32=True)
        b=formats.quantize_couplings(ins["J"],ins["h"],"fp64_ref",tile=2)
        self.assertEqual(a["quant"]["J"],b["J"])
        self.assertEqual(a["quant"]["h"],b["h"])
        self.assertEqual(len(a["minima"])>=1,True)

    def test_true_fp32_current_mode_differs_from_original(self):
        ins=mimo.frame(tx=3,rx=3,snr_db=5,seed=12)
        rounded=audit.quantized_minima(ins,"fp32",tile=2)
        unrounded=audit.quantized_minima(ins,"fp32",tile=2,legacy_fp32=True)
        self.assertNotEqual(rounded["quant"]["J"],unrounded["quant"]["J"])

    def test_exact_audit_recovers_pilot_state_and_ground(self):
        ins=mimo.frame(tx=3,rx=3,snr_db=0,seed=12)
        oracle=mimo.exact_ml(ins)
        selected=tuple(oracle["state"])
        txt="".join("1" if x>0 else "0" for x in selected)
        fmt=formats.quantize_couplings(ins["J"],ins["h"],"fp4",tile=2)
        qenergy=core.energy(fmt["J"],fmt["h"],selected)
        row={"frame_index":"0","snr_db":"0.0","format":"fp4",
             "response":"ideal","selected_state":txt,
             "quantized_selection_energy":str(qenergy),
             "original_residual_gap":"0.0","ml_hit":"1"}
        unique,checked,sums=audit.audit([row],{(0,0.0):ins},tile=2)
        self.assertEqual(len(unique),1)
        self.assertEqual(sums[0]["original_ml_hits"],1)
        self.assertEqual(checked[0]["selected_is_original_ml"],1)

    def test_corrupted_energy_rejected(self):
        ins=mimo.frame(tx=2,rx=2,snr_db=5,seed=10)
        selected=tuple(mimo.exact_ml(ins)["state"])
        row={"frame_index":"0","snr_db":"5.0","format":"fp4",
             "response":"ideal","selected_state":"".join("1" if x>0 else "0" for x in selected),
             "quantized_selection_energy":"12345",
             "original_residual_gap":"0.0","ml_hit":"1"}
        with self.assertRaisesRegex(ValueError,"reconstructed Hamiltonian"):
            audit.audit([row],{(0,5.0):ins},tile=2)


if __name__=="__main__":
    unittest.main()
