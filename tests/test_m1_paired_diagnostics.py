import csv
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import m1_paired_diagnostics as diag

class PairDiagnosticsTests(unittest.TestCase):
    def _row(self,frame,fmt,response,state,hit,errors,best=20):
        return {"frame_index":str(frame),"channel_seed":str(300+frame),
                "solver_seed":str(400+frame),"snr_db":"0.0",
                "response":response,"format":fmt,"selected_state":state,
                "ml_hit":str(hit),"bit_errors":str(errors),
                "selected_at_update":str(best),"original_residual_gap":str(1-hit)}

    def test_paired_ideal_response_and_fp_int(self):
        rows=[]
        for frame in range(2):
            for fmt in ("fp4","int4"):
                rows.append(self._row(frame,fmt,"ideal","01",1,0))
                rows.append(self._row(frame,fmt,"gain080","01" if frame==0 else "10",
                                      1 if frame==0 else 0,0 if frame==0 else 1))
        result=diag.analyze(rows)
        a=next(x for x in result["response_vs_ideal"] if x["format"]=="fp4")
        self.assertEqual(a["different_final_states"],1)
        self.assertEqual(a["changed_ml_hit"],1)
        self.assertEqual(a["net_bit_error_difference"],1)
        b=next(x for x in result["fp_vs_equal_bit_int"] if x["response"]=="ideal")
        self.assertEqual(b["paired_frames"],2)
        self.assertEqual(b["both_ml_hit"],2)

    def test_requires_matching_control(self):
        with self.assertRaises(ValueError):
            diag.analyze([self._row(0,"fp4","ideal","01",1,0),
                          self._row(1,"fp4","gain080","01",1,0)])

    def test_csv_and_nonoverwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"m1.csv"
            with source.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=list(self._row(0,"fp4","ideal","01",1,0)))
                w.writeheader()
                w.writerow(self._row(0,"fp4","ideal","01",1,0))
                w.writerow(self._row(0,"fp4","gain080","11",0,1))
            rows=diag.read_rows(source)
            self.assertEqual(len(rows),2)
            report=diag.analyze(rows)
            output=Path(tmp)/"evidence"
            diag.write_report(output,source,report)
            self.assertTrue((output/"m1_paired_diagnostics.json").exists())
            with self.assertRaises(FileExistsError):
                diag.write_report(output,source,report)

if __name__=="__main__":
    unittest.main()
