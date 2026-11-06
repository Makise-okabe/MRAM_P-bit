import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import m0_ising_math as core
import m0_mimo_reference as mimo
import m1_coupling_formats as formats
import m1_exact_ground_audit as audit


class GroundAuditTests(unittest.TestCase):
    def test_unrounded_fp32_historical_compatibility(self):
        ins=mimo.frame(tx=3,rx=3,snr_db=5,seed=12)
        a=audit.quantized_minima(ins,"fp32",tile=2)
        b=formats.quantize_couplings(ins["J"],ins["h"],"fp64_ref",tile=2)
        self.assertEqual(a["quant"]["J"],b["J"])
        self.assertEqual(a["quant"]["h"],b["h"])
        self.assertEqual(len(a["minima"])>=1,True)

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
