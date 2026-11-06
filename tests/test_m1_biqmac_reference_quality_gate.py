"""Reference-quality calibration guard tests: no full benchmark or device run."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph, prepare, solve
from experiments.m1_biqmac_reference_quality_gate import (
    examine, official_reference, schedule_beta, solve_reference
)


class TestReferenceQualityGate(unittest.TestCase):
    def toy(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        d = Path(directory.name)
        p = d / "toy.rudy"
        p.write_text("3 3\n1 2 1\n2 3 -2\n1 3 5\n", encoding="utf-8")
        return d, p, load_rudy(p)

    def test_schedule_beta_endpoints(self):
        self.assertEqual(schedule_beta(2.0, "fixed", 10, 20), 2.0)
        self.assertEqual(schedule_beta(2.0, "linear", 0, 5), 1.0)
        self.assertEqual(schedule_beta(2.0, "linear", 4, 5), 4.0)
        with self.assertRaises(ValueError):
            schedule_beta(2.0, "adaptive", 0, 5)

    def test_fixed_is_bit_identical_to_existing_solver(self):
        _, _, g = self.toy()
        rep = prepare(g, "ref64", "source")
        b = beta_from_original_graph(g)
        a = solve(g, rep, b, 200, 19)
        c = solve_reference(g, rep, b, 200, 19, "fixed")
        self.assertEqual(a, c)

    def test_linear_checks_energy_and_returns_original_cut(self):
        _, _, g = self.toy()
        rep = prepare(g, "ref64", "source")
        b = beta_from_original_graph(g)
        r = solve_reference(g, rep, b, 200, 19, "linear")
        self.assertLessEqual(r["returned_original_cut"], 6.0)
        self.assertGreaterEqual(r["returned_original_cut"], -1.0)
        self.assertLessEqual(r["returned_represented_energy"], r["final_represented_energy"] + 1e-8)

    def test_reference_source_hash_must_match(self):
        _, _, g = self.toy()
        self.assertEqual(official_reference(g, {"sha256":g.sha256, "cut":6},None), 6)
        with self.assertRaisesRegex(ValueError, "reference hash mismatch"):
            official_reference(g, {"sha256":"other", "cut":6}, None)

    def test_end_to_end_bounded_probe_toy_and_no_overwrite(self):
        d, p, g = self.toy()
        refs = d / "toy_reference.json"
        refs.write_text(json.dumps({
            "reference_type": "PUBLISHED_OPTIMUM",
            "graphs": {"toy.rudy": {"cut":6, "sha256":g.sha256, "table":0,"pdf_page":0}},
        }),encoding="utf-8")
        output=d/"out"
        rows, summary=examine([p], refs, (10, 25), ("fixed","linear"), 2, 777, output)
        self.assertEqual(len(rows),8)
        self.assertEqual(len(summary),4)
        self.assertTrue((output/"manifest.json").exists())
        with self.assertRaisesRegex(ValueError,"output already exists"):
            examine([p], refs, (10,), ("fixed",), 1, 777, output)

    def test_official_reference_import_is_structured(self):
        p=Path("docs/BIQMAC_OFFICIAL_OPTIMA_2007.json")
        refs=json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(refs["reference_type"],"PUBLISHED_OPTIMUM")
        self.assertEqual(len(refs["graphs"]),10)
        self.assertEqual(refs["graphs"]["w01_100.0"]["cut"],651)
        self.assertEqual(refs["graphs"]["t2g10_5555"]["cut"],6049461)
        self.assertEqual(refs["graphs"]["ising2.5-100_5555"]["cut"],2460049)
        self.assertTrue(all(len(x["sha256"]) == 64 for x in refs["graphs"].values()))


if __name__ == "__main__":
    unittest.main()
