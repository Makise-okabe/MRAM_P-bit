import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from experiments.core import (activity_metrics, balanced_order, binary, candidate_orders,
                              car_order, load_trace_bundle, mathematical_checks,
                              screen, validate_contract, write_new)


class ResearchToolsTests(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(17)
        self.cal = self.rng.integers(0, 2, (12, 256))

    def test_exact_mathematical_contracts(self):
        self.assertTrue(all(v == 'PASS' for v in mathematical_checks()['checks'].values()))

    def test_every_mapping_preserves_matrix_output(self):
        w = self.rng.integers(0, 2, (256, 256))
        for size in (16, 32, 64, 128, 256):
            for order in candidate_orders(self.cal, size).values():
                np.testing.assert_array_equal(self.cal[:, order] @ w[order], self.cal @ w)

    def test_all_zero_and_all_one_traces_have_correct_read_counts(self):
        for value, reads in ((0, 0), (1, 16)):
            x = np.full((2, 256), value)
            m = activity_metrics(x, np.arange(256), 32)
            self.assertEqual(m['nonempty_group_reads'], reads)
            self.assertEqual(m['active_rows_total_invariant'], value * 512)

    def test_activity_conservation_does_not_imply_error_curve(self):
        x = np.zeros((1, 256), dtype=int); x[0, :26] = 1
        clustered = activity_metrics(x, np.arange(256), 32)
        shuffled = self.rng.permutation(256)
        spread = activity_metrics(x, shuffled, 32)
        self.assertEqual(clustered['active_rows_total_invariant'], spread['active_rows_total_invariant'])
        self.assertGreaterEqual(spread['nonempty_group_reads'], clustered['nonempty_group_reads'])
        self.assertIn('not physical error', clustered['metric_scope'])

    def test_car_is_deterministic_on_ties(self):
        zeros = np.zeros((3, 256))
        np.testing.assert_array_equal(car_order(zeros, 32), np.arange(256))

    def test_invalid_architecture_and_nonbinary_data_rejected(self):
        with self.assertRaises(ValueError):
            validate_contract({'physical_rows': 128, 'physical_columns': 256})
        with self.assertRaises(ValueError):
            binary(np.full((2, 256), np.nan), 'bad')
        with self.assertRaises(ValueError):
            balanced_order(self.cal, 32, fixed_quiet_groups=8)

    def test_unknown_physics_is_blocked(self):
        missing = validate_contract({'physical_rows': 256, 'physical_columns': 256,
                                    'representation': 'binary_01_bitplane'}, physical=True)
        self.assertIn('validated_max_active_rows', missing)
        self.assertIn('validation_artifact_sha256', missing)

    def test_records_are_append_only(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'record.json'
            write_new(p, {'status': 'planned'})
            with self.assertRaises(FileExistsError):
                write_new(p, {'status': 'changed'})

    def bundle(self, directory, *, overlap=False, inspected=True, purpose='development'):
        root = Path(directory)
        trace = root / 'trace.npz'; meta = root / 'meta.json'
        np.savez(trace, X_cal=self.cal, X_eval=self.cal[:3], W=np.zeros((256, 256)),
                 cal_ids=np.arange(12).astype(str),
                 eval_ids=(np.arange(3) + (0 if overlap else 100)).astype(str))
        meta.write_text(json.dumps({'evidence_class': 'workload_trace', 'dataset': 'UNIT_TEST_FIXTURE',
                                  'model_sha256': 'fixture', 'quantization_sha256': 'fixture',
                                  'layer': 'fixture', 'source_export_command': 'test fixture only',
                                  'split_purpose': purpose, 'previously_inspected': inspected}))
        return trace, meta

    def test_cal_eval_overlap_and_relabelling_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            trace, meta = self.bundle(d, overlap=True)
            with self.assertRaises(ValueError): load_trace_bundle(trace, meta)
            trace, meta = self.bundle(d, inspected=True, purpose='held_out')
            with self.assertRaises(ValueError): load_trace_bundle(trace, meta)

    def test_screen_contains_no_invented_hardware_metrics(self):
        with tempfile.TemporaryDirectory() as d:
            trace, meta = self.bundle(d)
            result = screen(trace, meta, sizes=(32,))
            self.assertFalse(result['physical_validation'])
            for key in ('energy_j', 'latency_s', 'count_error_rate', 'inference_failure_rate'):
                self.assertIsNone(result[key])
            for row in result['runs']:
                self.assertEqual(row['evaluation']['active_rows_total_invariant'], int(self.cal[:3].sum()))


if __name__ == '__main__':
    unittest.main()
