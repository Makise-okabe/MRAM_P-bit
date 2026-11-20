"""Mock-only runner, committed-freeze, key-count and immutable-reuse tests."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from experiments.fyp_first_block_20261120 import CHECKPOINTS, digest, seal
import experiments.fyp_ideal_campaign as campaign


class TestIdealCampaign(unittest.TestCase):
    def temp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name)

    def test_registered_counts_and_disjoint_streams(self):
        keys = campaign.expected_keys("generated", 0, 0)
        self.assertEqual(len(keys), 576)
        self.assertEqual(sum(stage == "main" for stage, _, _ in keys), 448)
        main = {seed for stage, _, seed in keys if stage == "main"}
        refs = {seed for stage, _, seed in keys if stage == "reference"}
        self.assertEqual((len(main), len(refs), len(main & refs)), (64, 128, 0))
        self.assertEqual(len(campaign.expected_keys("anchor", 0, 0)), 896)
        rows = [{"stage": s, "representation": f, "seed": seed, "family": 0, "index": 0}
                for s, f, seed in keys]
        campaign.validate_record_keys(rows, "generated", 0, 0)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            campaign.validate_record_keys(rows[:-1]+[rows[0]], "generated", 0, 0)

    def test_deterministic_gzip_and_hash_tamper(self):
        root = self.temp()
        rows = [{"stage": "main", "representation": "fp5", "seed": i, "R": i} for i in (2, 1)]
        a, b = root/"a.jsonl.gz", root/"b.jsonl.gz"
        campaign.write_gzip_rows(a, rows)
        campaign.write_gzip_rows(b, list(reversed(rows)))
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertEqual([r["seed"] for r in campaign.sealed_rows(a)], [1, 2])
        bad = root/"bad.jsonl"
        bad.write_text(json.dumps({**seal(rows[0]), "R": 999})+"\n")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            campaign.sealed_rows(bad)

    def test_reuse_preserves_original_payload_and_missing_latest(self):
        raw = seal({"graph": "ising2.5-100_5555", "condition": "raw",
                    "representation": "fp5", "seed": 3000000000000,
                    "R": 80, "V": 100, "M": 90,
                    "checkpoints": [{"attempt": 5000, "R": 70}]})
        before = deepcopy(raw)
        augmented = campaign.reused_record(raw, family=0, index=0, replicate=0, archive_sha256="archivehash")
        self.assertEqual(raw, before)
        self.assertEqual(augmented["source_record_sha256"], raw["record_sha256"])
        self.assertIsNone(augmented["R_last"])
        self.assertNotIn("R_last", augmented["checkpoints"][0])
        for key, value in raw.items():
            if key != "record_sha256":
                self.assertEqual(augmented[key], value)

    def test_freeze_must_be_committed_and_hashes_match(self):
        root = self.temp()
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        files = {}
        for name in campaign.REQUIRED_FREEZE_SOURCES:
            path = root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic frozen source\n")
            files[name] = digest(path)
        source_manifest = "data/source_manifest.json"
        (root/"data").mkdir()
        (root/source_manifest).write_text('{"synthetic":true}\n')
        files[source_manifest] = digest(root/source_manifest)
        freeze = root/"docs/freeze.json"
        campaign.write_json(freeze, {"source_sha256": files, "source_manifest_path": source_manifest,
                                    "source_manifest_sha256": files[source_manifest]})
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "-c", "user.name=Synthetic Test", "-c", "user.email=test@example.invalid",
                        "commit", "-qm", "synthetic freeze"], cwd=root, check=True)
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        gate = campaign.verify_freeze(freeze, commit, root=root)
        self.assertEqual(gate["freeze_commit"], commit)
        changed = root/campaign.REQUIRED_FREEZE_SOURCES[0]
        changed.write_text("mutated\n")
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            campaign.verify_freeze(freeze, commit, root=root)
        changed.write_text("synthetic frozen source\n")
        freeze.write_text(freeze.read_text()+"\n")
        with self.assertRaisesRegex(ValueError, "differs from committed"):
            campaign.verify_freeze(freeze, commit, root=root)

    def test_mock_bundle_pool_counts_and_completed_resume(self):
        root = self.temp()
        source_dir, graph_dir, out = root/"sources", root/"official", root/"results"
        (source_dir/"ring").mkdir(parents=True)
        source = source_dir/"ring/000.rudy"
        source.write_text("100 1\n1 2 100\n")
        gate = {"freeze_commit": "a"*40, "freeze_manifest_sha256": "b"*64,
                "source_sha256": {"sources/ring/000.rudy": digest(source)}}
        calls = []

        def fake_rep(graph, fmt):
            adjacency = [[(1, -100.0)], [(0, -100.0)]]+[[] for _ in range(98)]
            return {"scale": 1.0, "edges": [(0, 1, -100.0)], "adjacency": adjacency, "_fmt": fmt}

        def fake_solver(graph, rep, beta, updates, seed, **kwargs):
            calls.append((rep["_fmt"], seed))
            return {"seed": seed, "attempted_updates": updates, "actual_flips": 0, "improvements": 0,
                    "returned_original_cut": 100.0, "final_original_cut": 100.0,
                    "returned_represented_energy": -100.0, "final_represented_energy": -100.0,
                    "returned_state_hex": "1", "V_state_hex": "1", "M_state_hex": "1",
                    "V": 100.0, "M": 100.0, "R": 100.0, "R_last": 100.0,
                    "checkpoints": [{"attempt": t, "beta": 0.001, "current_state_hex": "1",
                                     "V": 100.0, "M": 100.0, "R": 100.0, "R_last": 100.0,
                                     "unreached": None, "selection": 0.0, "tie": 0.0} for t in CHECKPOINTS]}

        with patch.object(campaign, "ROOT", root), patch.object(campaign, "representation", side_effect=fake_rep), \
             patch.object(campaign, "solve_logged", side_effect=fake_solver), patch("builtins.print"):
            manifest = campaign.run_bundle("generated", 0, 0, source_dir=source_dir,
                                           graph_dir=graph_dir, out=out, gate=gate)
            self.assertEqual(manifest["stage_counts"], {"main": 448, "reference": 128})
            self.assertEqual(manifest["B_g"], 100)
            self.assertEqual(manifest["fidelity_records"], 1536)
            self.assertEqual(len(calls), 576)
            self.assertEqual(len(set(calls)), 576)
            campaign.run_bundle("generated", 0, 0, source_dir=source_dir,
                                graph_dir=graph_dir, out=out, gate=gate)
            self.assertEqual(len(calls), 576)
            folder = out/"generated/ring/000"
            (folder/"IN_PROGRESS.json").write_text("{}")
            with self.assertRaisesRegex(RuntimeError, "partial bundle"):
                campaign.run_bundle("generated", 0, 0, source_dir=source_dir,
                                    graph_dir=graph_dir, out=out, gate=gate)
            self.assertEqual(len(calls), 576)


if __name__ == "__main__":
    unittest.main()
