import ast
import gzip
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock
from types import SimpleNamespace

import numpy as np

from experiments.frozen_mnist import (SHAPES, exact_binary_dot, forward_export,
    pack_weights, quantized_layers, read_idx, trace_planes, validate_splits,
    verify_packed_reconstruction)
from experiments.nus_first_run import checked_golden_functions, execute, inspect_resources, screen_block, write_packet


class FrozenMNISTTests(unittest.TestCase):
    def test_all_signed_weight_planes_and_partial_rows(self):
        rng = np.random.default_rng(20261104)
        x = rng.integers(0, 256, (3, 784), dtype=np.int64)
        w = rng.integers(-8, 8, (128, 784), dtype=np.int64)
        w[0, 0], w[1, 783] = -8, 7
        total = np.zeros((3, 128), dtype=np.int64)
        for start in (0, 256, 512, 768):
            arrays = pack_weights(w, start)
            self.assertEqual(len(arrays), 2)
            self.assertEqual(sum(a['used_columns'] for a in arrays), 512)
            self.assertEqual(arrays[0]['used_rows'], 16 if start == 768 else 256)
            total += verify_packed_reconstruction(x, w, start, arrays)
        np.testing.assert_array_equal(total, x @ w.T)
        self.assertEqual(pack_weights(w, 0)[1]['coefficients'][-1], -8)

    def test_parent_bit_associations_reconstruct_inputs(self):
        x = np.zeros((2, 784), dtype=np.int64)
        x[0, 768:784] = np.arange(16)
        x[1, 768:784] = 255
        traces, ids, parents, bits = trace_planes(x, np.array([43, 91]), 768)
        self.assertEqual(len(set(ids)), 16)
        self.assertEqual(set(parents), {43, 91})
        restored = (traces.reshape(2, 8, 256).astype(np.int64) * (1 << np.arange(8))[None, :, None]).sum(1)
        np.testing.assert_array_equal(restored[:, :16], x[:, 768:784])
        self.assertFalse(restored[:, 16:].any())
        np.testing.assert_array_equal(bits, np.tile(np.arange(8), 2))
        with self.assertRaises(ValueError):
            trace_planes(x, np.array([43, 43]), 768)

    def test_binary_gemm_does_not_overflow_at_256(self):
        x = np.ones((4, 256), dtype=np.uint8)
        w = np.ones((256, 256), dtype=np.uint8)
        np.testing.assert_array_equal(exact_binary_dot(x, w), np.full((4, 256), 256))
        rng = np.random.default_rng(3)
        x, w = rng.integers(0, 2, (7, 256)), rng.integers(0, 2, (256, 256))
        np.testing.assert_array_equal(exact_binary_dot(x, w), x.astype(np.int64) @ w.astype(np.int64))
        x[0, 0] = 2
        with self.assertRaises(ValueError):
            exact_binary_dot(x, w)

    def test_saved_split_and_parent_leakage(self):
        perm = np.random.default_rng(4).permutation(60000)
        config = {'split_seed': 4, 'val_size': 5000, 'calibration_size': 2048}
        splits = {'train': perm[5000:], 'validation': perm[:5000], 'calibration': perm[5000:7048]}
        validate_splits(splits, config)
        changed = {k: v.copy() for k, v in splits.items()}
        changed['calibration'][0] = changed['validation'][0]
        with self.assertRaises(ValueError):
            validate_splits(changed, config)
        changed = {k: v.copy() for k, v in splits.items()}
        changed['calibration'] = changed['calibration'][::-1]
        with self.assertRaises(ValueError):
            validate_splits(changed, config)

    def test_idx_raw_gzip_and_truncation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            image = np.arange(784, dtype=np.uint8).reshape(1, 28, 28)
            raw = struct.pack('>IIII', 2051, 1, 28, 28) + image.tobytes()
            p = root/'images';p.write_bytes(raw)
            np.testing.assert_array_equal(read_idx(p, 2051), image)
            z = root/'images.gz';z.write_bytes(gzip.compress(raw))
            np.testing.assert_array_equal(read_idx(z, 2051), image)
            p.write_bytes(raw[:-1])
            with self.assertRaises(ValueError):
                read_idx(p, 2051)
            p.write_bytes(struct.pack('>II', 2049, 2) + bytes([0, 11]))
            with self.assertRaises(ValueError):
                read_idx(p, 2049)

    def test_quantizer_signed_ties_and_checkpoint_contract(self):
        state = {}
        for i, (nout, nin) in enumerate(SHAPES, 1):
            state[f'fc{i}.weight'] = np.zeros((nout, nin), np.float32)
            state[f'fc{i}.bias'] = np.zeros(nout, np.float32)
        state['fc1.weight'][0, :7] = [7, .5, 1.5, 2.5, -.5, -1.5, -2.5]
        layers = quantized_layers(state, [1, 2, 3])
        np.testing.assert_array_equal(layers[0]['weight'][0, :7], [7, 0, 2, 2, 0, -2, -2])
        images = np.zeros((2, 28, 28), np.uint8)
        inputs, logits = forward_export(images, layers)
        self.assertEqual([v.shape for v in inputs], [(2, 784), (2, 128), (2, 64)])
        self.assertFalse(logits.any())
        state['fc1.weight'][0, 0] = np.nan
        with self.assertRaises(ValueError):
            quantized_layers(state, [1, 2, 3])

    def test_resource_receipt_and_packet_exclude_private_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder);legacy = root/'legacy';model = legacy/'outputs/mnist_stage4a_v3_15ep'
            model.mkdir(parents=True)
            for name in ('fp32_checkpoint.pt', 'frozen_quantization.json', 'split_indices.npz'):
                (model/name).write_bytes(b'fixture only')
            software = legacy/'research/software';software.mkdir(parents=True)
            (software/'mnist_precision_stage4a.py').write_text('# fixture')
            data = legacy/'data/mnist/MNIST/raw';data.mkdir(parents=True)
            for name in ('train-images-idx3-ubyte', 'train-labels-idx1-ubyte'):
                (data/name).write_bytes(b'fixture only')
            circuit = root/'circuit';circuit.mkdir()
            (circuit/'mtj_read_v0.va').write_text('module mtj_read_v0(p,n); parameter real private_value=123; endmodule')
            with mock.patch('experiments.nus_first_run.shutil.which', return_value=None):
                _, private, public = inspect_resources(legacy, circuit_root=circuit)
            self.assertTrue(public['ready_for_neural_export'])
            text = json.dumps(public)
            self.assertNotIn(str(root), text)
            self.assertNotIn('private_value', text)
            self.assertEqual(public['student_mtj_declarations'][0]['ports'], ['p', 'n'])
            out = root/'run';out.mkdir()
            receipt = out/'resource_receipt.json';receipt.write_text(text)
            (out/'private_resource_paths.json').write_text(json.dumps(private))
            packet = write_packet(out, [receipt])
            import zipfile
            with zipfile.ZipFile(packet) as z:
                self.assertEqual(set(z.namelist()), {'resource_receipt.json', 'packet_manifest.json'})
            with self.assertRaises(FileExistsError):
                write_packet(out, [receipt])

    def test_one_resident_mapping_across_arrays_and_no_hardware_metrics(self):
        rng = np.random.default_rng(7)
        cal = rng.integers(0, 2, (8, 256), dtype=np.uint8);cal[:, :32] = 0
        evaluation = rng.integers(0, 2, (8, 256), dtype=np.uint8)
        w = rng.integers(-8, 8, (128, 256), dtype=np.int64)
        results = screen_block(cal, evaluation, pack_weights(w, 0), [64, 256], 9, {})
        self.assertEqual([r['order_sha256'] for r in results[0]['runs']],
                         [r['order_sha256'] for r in results[1]['runs']])
        self.assertIn('dead_feature_packed', {r['mapping'] for r in results[0]['runs']})
        for result in results:
            self.assertIsNone(result['inference_failure_rate'])
            self.assertIsNone(result['energy_j'])
            self.assertFalse(result['physical_validation'])
            self.assertTrue(all(r['integer_equivalence'] for r in result['runs']))

    def test_golden_ast_change_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/'golden.py'
            p.write_text('def q_weight(w, bits):\n    raise RuntimeError("must not execute")\n')
            contract = {'golden_function_ast_sha256': {'q_weight': '0'*64}}
            with self.assertRaisesRegex(ValueError, 'needs review'):
                checked_golden_functions(p, None, contract)

    def test_runner_exports_all_row_blocks_and_auditable_packet(self):
        # The external NUS file/torch loader alone is stubbed; packing, mapping,
        # exact reconstruction, file contracts and ZIP generation run for real.
        rng = np.random.default_rng(11)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = {}
            for name in ('checkpoint', 'quantization'):
                files[name] = root/(name+'.fixture')
                files[name].write_bytes(b'unit fixture; never scientific evidence')
            x = rng.integers(0, 256, (4, 784), dtype=np.int64)
            w = rng.integers(-8, 8, (128, 784), dtype=np.int64)
            args = SimpleNamespace(out=root/'run', legacy_root=root/'legacy', model_dir=None,
                                   data_root=None, circuit_root=None, audit_only=False,
                                   cal_images=2, eval_images=2, layer='fc1',
                                   group_sizes=[256], seed=12)
            public = {'ready_for_neural_export': True, 'resources': {}}
            exported = ([x], [{'weight': w}], np.array([10, 11]), np.array([20, 21]),
                        {'unit_fixture_only': True})
            with mock.patch('experiments.nus_first_run.inspect_resources', return_value=(files, {}, public)), \
                 mock.patch('experiments.nus_first_run.load_neural_inputs', return_value=exported), \
                 mock.patch('builtins.print'):
                self.assertEqual(execute(args), 0)
            summary = json.loads((args.out/'summary.json').read_text())
            self.assertEqual(len(summary['row_blocks']), 4)
            self.assertEqual(summary['row_blocks'][-1]['padding_rows'], 240)
            self.assertFalse(summary['physical_validation'])
            bundles = sorted(args.out.glob('rows_*/array_*/traces.npz'))
            self.assertEqual(len(bundles), 8)
            from experiments.core import load_trace_bundle
            for bundle in bundles:
                cal, evaluation, packed_w, metadata = load_trace_bundle(bundle, bundle.with_name('metadata.json'))
                self.assertEqual(cal.shape, (16, 256))
                self.assertEqual(packed_w.shape, (256, 256))
                self.assertEqual(metadata['split_purpose'], 'development')
                with np.load(bundle, allow_pickle=False) as z:
                    self.assertFalse(set(z['cal_parent_ids']) & set(z['eval_parent_ids']))
            import zipfile
            with zipfile.ZipFile(args.out/'review_packet.zip') as z:
                self.assertNotIn('private_resource_paths.json', z.namelist())
                self.assertNotIn('private_run.json', z.namelist())
                manifest = json.loads(z.read('packet_manifest.json'))
                for name, record in manifest['files'].items():
                    self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(), record['sha256'])
            with self.assertRaises(FileExistsError):
                execute(args)

    def test_runner_cannot_write_into_legacy_or_archive(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder);legacy = root/'legacy';legacy.mkdir()
            for out in (legacy/'new_run', root/'archive/new_run'):
                args = SimpleNamespace(out=out, legacy_root=legacy)
                with self.assertRaisesRegex(ValueError, 'read-only legacy'):
                    execute(args)
                self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
