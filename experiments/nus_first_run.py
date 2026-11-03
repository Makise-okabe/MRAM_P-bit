"""Run the frozen-MNIST E01 screen on NUS; never read retired electrical results."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import uuid
import zipfile

for _key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ.setdefault(_key, '1')
os.environ.setdefault('ATEN_CPU_CAPABILITY', 'default')

import numpy as np

from .core import activity_metrics, candidate_orders, sha256, write_new
from .frozen_mnist import (SHAPES, array_hash, exact_binary_dot, forward_export,
                           pack_weights, quantized_layers, read_idx, trace_planes,
                           validate_splits, verify_packed_reconstruction)

BASE = Path(__file__).resolve().parents[1]
SOURCE_CONTRACT = BASE / 'experiments/config/frozen_mnist_source.json'


def _dataset_file(root, name):
    candidates = [root/'MNIST/raw'/name, root/'MNIST/raw'/(name+'.gz'),
                  root/name, root/(name+'.gz')]
    return next((p for p in candidates if p.is_file()), candidates[0])


def inspect_resources(legacy_root, model_dir=None, data_root=None, circuit_root=None):
    legacy_root = Path(legacy_root).expanduser().resolve()
    model_dir = Path(model_dir).expanduser().resolve() if model_dir else legacy_root/'outputs/mnist_stage4a_v3_15ep'
    data_root = Path(data_root).expanduser().resolve() if data_root else legacy_root/'data/mnist'
    source_candidates = [legacy_root/'research/software/mnist_precision_stage4a.py',
                         legacy_root/'archive/2026-11-03-pre-reset/research/software/mnist_precision_stage4a.py']
    golden = next((p for p in source_candidates if p.is_file()), source_candidates[0])
    files = {'checkpoint': model_dir/'fp32_checkpoint.pt',
             'quantization': model_dir/'frozen_quantization.json',
             'splits': model_dir/'split_indices.npz', 'golden_source': golden,
             'train_images': _dataset_file(data_root, 'train-images-idx3-ubyte'),
             'train_labels': _dataset_file(data_root, 'train-labels-idx1-ubyte')}
    private = {k: {'path': str(p), 'present': p.is_file(),
                   'sha256': sha256(p) if p.is_file() else None} for k, p in files.items()}
    public = {'schema_version': 1, 'evidence_class': 'resource_inventory',
              'resources': {k: {'filename': p.name, 'present': p.is_file(),
                                 'sha256': private[k]['sha256']} for k, p in files.items()},
              'ready_for_neural_export': all(p.is_file() for p in files.values()),
              'spectre_on_path': shutil.which('spectre') is not None,
              'ocean_on_path': shutil.which('ocean') is not None,
              'physical_validation': False, 'electrical_results_read': False}
    # Only inspect student-model declarations in source directories. No PDK body,
    # simulation deck, old current table or physical coefficient is read/exported.
    root = Path(circuit_root).expanduser() if circuit_root else Path.home()/'mram_fyp/cadence/CIM1_SINGLE_CELL'
    model_sources = []
    if root.is_dir():
        for current, dirs, names in os.walk(root):
            rel = Path(current).relative_to(root)
            dirs[:] = [d for d in dirs if d not in {'simulations', 'simulation', 'psf', 'results', '.git'}]
            if len(rel.parts) >= 4:
                dirs[:] = []
            for name in names:
                if not name.endswith('.va') or 'mtj' not in name.lower():
                    continue
                p = Path(current)/name
                if p.stat().st_size > 1_000_000:
                    continue
                text = p.read_text(errors='replace')
                match = re.search(r'\bmodule\s+(mtj_read_v0)\s*\(([^;]*?)\)\s*;', text, re.S)
                if match:
                    model_sources.append({'filename': p.name, 'sha256': sha256(p),
                                          'module': match.group(1),
                                          'ports': [v.strip() for v in match.group(2).split(',')]})
            if len(model_sources) >= 8:
                break
    public['student_mtj_declarations'] = model_sources
    public['circuit_status'] = 'SOURCE_INVENTORY_ONLY_FRESH_E02_REQUIRED'
    public['note'] = 'No PDK/netlist/current/ADC data are included; no circuit run is performed.'
    return files, private, public


def checked_golden_functions(path, torch, contract):
    """Execute only the three inspected, AST-pinned neural quantizer functions."""
    tree = ast.parse(Path(path).read_text())
    nodes = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    selected = []
    for name, expected in contract['golden_function_ast_sha256'].items():
        if name not in nodes:
            raise ValueError(f'Missing audited golden function: {name}')
        digest = hashlib.sha256(ast.dump(nodes[name], include_attributes=False).encode()).hexdigest()
        if digest != expected:
            raise ValueError(f'Golden function changed and needs review: {name}')
        selected.append(nodes[name])
    namespace = {'torch': torch, 'F': torch.nn.functional}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


def load_neural_inputs(files, ncal, neval):
    import torch
    torch.set_num_threads(1)
    config = json.loads(files['quantization'].read_text())
    if config.get('frozen') is not True or config.get('checkpoint_sha256') != sha256(files['checkpoint']):
        raise ValueError('Frozen checkpoint/quantizer hash mismatch')
    precision = config['quantizer_config']['W4A8']
    if (precision['weight_bits'], precision['activation_bits']) != (4, 8):
        raise ValueError('W4A8 precision declaration mismatch')
    ckpt = torch.load(files['checkpoint'], map_location='cpu', weights_only=True)
    for key in ('split_seed', 'train_seed', 'val_size'):
        if ckpt[key] != config[key]:
            raise ValueError(f'Checkpoint/quantizer metadata mismatch: {key}')
    if ckpt['calib_size'] != config['calibration_size']:
        raise ValueError('Calibration-size metadata mismatch')
    with np.load(files['splits'], allow_pickle=False) as f:
        splits = validate_splits({k: f[k] for k in f.files}, config)
    if not 1 <= ncal <= len(splits['calibration']) or not 1 <= neval <= len(splits['validation']):
        raise ValueError('Requested parent budget exceeds the saved split')
    cal_ids, eval_ids = splits['calibration'][:ncal], splits['validation'][:neval]
    images, labels = read_idx(files['train_images'], 2051), read_idx(files['train_labels'], 2049)
    if len(images) != 60000 or len(labels) != 60000:
        raise ValueError('Require the complete original MNIST training files')
    ids = np.concatenate((cal_ids, eval_ids))
    selected_images, selected_labels = images[ids], labels[ids]
    state = {k: v.detach().cpu().numpy() for k, v in ckpt['model'].items()}
    layers = quantized_layers(state, precision['activation_clips'])
    if len(precision['weight_stats']) != 3:
        raise ValueError('Require frozen weight statistics for all three layers')
    for layer, recorded in zip(layers, precision['weight_stats']):
        if not np.isclose(layer['weight_scale'], recorded['scale'], atol=1e-15, rtol=1e-12):
            raise ValueError('Weight scale differs from the frozen quantizer')
    inputs, logits = forward_export(selected_images, layers)
    golden = checked_golden_functions(files['golden_source'], torch, json.loads(SOURCE_CONTRACT.read_text()))

    class Model(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1, self.fc2, self.fc3 = [torch.nn.Linear(nin, nout) for nout, nin in SHAPES]

    model = Model().eval()
    model.load_state_dict(ckpt['model'], strict=True)
    golden_images = torch.from_numpy(selected_images.copy()).unsqueeze(1).float()/255
    with torch.no_grad():
        reference = golden['ptq_forward'](model, golden_images, 4, 8,
                                          precision['activation_clips']).numpy()
    max_difference = float(np.abs(reference-logits).max())
    if max_difference > 1e-10 or not np.array_equal(reference.argmax(1), logits.argmax(1)):
        raise AssertionError('Export differs from the audited frozen golden forward')
    verification = {'golden_max_logit_abs_difference': max_difference,
                    'golden_predictions_equal': True, 'parents_checked': len(ids),
                    'calibration_clean_W4A8_correct': int((logits[:ncal].argmax(1) == selected_labels[:ncal]).sum()),
                    'development_clean_W4A8_correct': int((logits[ncal:].argmax(1) == selected_labels[ncal:]).sum()),
                    'development_count': neval, 'no_electrical_noise': True,
                    'torch': torch.__version__}
    return inputs, layers, cal_ids, eval_ids, verification


def screen_block(cal, evaluation, arrays, sizes, seed, metadata):
    """One CAL-fitted order serves every A8 cycle and packed weight array."""
    cached = {}
    dead = np.flatnonzero(cal.sum(axis=0) == 0)
    live = np.flatnonzero(cal.sum(axis=0) != 0)
    for size in sizes:
        orders = candidate_orders(cal, size, seed)
        orders['dead_feature_packed'] = np.concatenate((live, dead))
        cached[size] = {name: (order, activity_metrics(cal, order, size),
                                     activity_metrics(evaluation, order, size))
                        for name, order in orders.items()}
    results = []
    for array in arrays:
        w = array['W']
        direct = exact_binary_dot(evaluation, w)
        result = {'schema_version': 1, 'experiment_id': 'E01',
                  'evidence_class': 'workload_structure', 'physical_validation': False,
                  'source': dict(metadata, array_index=array['array_index']),
                  'seed': seed, 'energy_j': None, 'latency_s': None,
                  'count_error_rate': None, 'inference_failure_rate': None, 'runs': []}
        for size, entries in cached.items():
            for name, (order, cm, em) in entries.items():
                if not np.array_equal(exact_binary_dot(evaluation[:, order], w[order]), direct):
                    raise AssertionError('Resident permutation changed ideal counts')
                result['runs'].append({'mapping': name, 'order': order.tolist(),
                                      'order_sha256': array_hash(order.astype('<i8')),
                                      'calibration': cm, 'evaluation': em,
                                      'integer_equivalence': True})
        results.append(result)
    return results


def write_packet(out, members):
    manifest = {'files': {str(p.relative_to(out)): {'sha256': sha256(p), 'bytes': p.stat().st_size}
                          for p in members},
                'excluded': ['checkpoint binary', 'raw model/PDK/netlists', 'private resource paths',
                             'retired electrical measurements'],
                'contains': 'MNIST traces, packed quantized weight planes, results and public-safe provenance'}
    write_new(out/'packet_manifest.json', manifest)
    packet = out/'review_packet.zip'
    with zipfile.ZipFile(packet, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for p in [*members, out/'packet_manifest.json']:
            z.write(p, str(p.relative_to(out)))
    return packet


def execute(args):
    out = args.out
    target, legacy = out.expanduser().resolve(), args.legacy_root.expanduser().resolve()
    if 'archive' in target.parts or target == legacy or legacy in target.parents:
        raise ValueError('Run outputs must stay outside the read-only legacy repository and archive')
    out.mkdir(parents=True, exist_ok=False)
    files, private, public = inspect_resources(args.legacy_root, args.model_dir,
                                               args.data_root, args.circuit_root)
    write_new(out/'private_resource_paths.json', private)
    write_new(out/'resource_receipt.json', public)
    members = [out/'resource_receipt.json']
    if args.audit_only or not public['ready_for_neural_export']:
        packet = write_packet(out, members)
        missing = [k for k, v in public['resources'].items() if not v['present']]
        print(json.dumps({'status': 'RESOURCE_AUDIT_ONLY' if not missing else 'MISSING_RESOURCES',
                          'missing': missing, 'review_packet': str(packet.resolve()),
                          'details_local_only': str((out/'private_resource_paths.json').resolve())}, indent=2), flush=True)
        return 2 if missing else 0
    try:
        inputs, layers, cal_ids, eval_ids, verify = load_neural_inputs(files, args.cal_images, args.eval_images)
        layer_index = int(args.layer[-1])-1
        x, weight = inputs[layer_index], layers[layer_index]['weight']
        meta_base = {'evidence_class': 'workload_trace', 'dataset': 'MNIST original training partition',
                     'model_sha256': sha256(files['checkpoint']),
                     'quantization_sha256': sha256(files['quantization']), 'layer': args.layer,
                     'source_export_command': 'bash scripts/run_first_experiment.sh (exact local argv in private_run.json)',
                     'split_purpose': 'development', 'previously_inspected': True,
                     'resident_order': 'one CAL-fitted order across all activation and weight planes per row block',
                     'no_electrical_results_read': True, 'physical_rows': 256, 'physical_columns': 256,
                     'activation_bits': 8, 'weight_precision': 4}
        all_results, block_info, packed_sum = [], [], np.zeros((len(x), weight.shape[0]), dtype=np.int64)
        for row in range(0, weight.shape[1], 256):
            arrays = pack_weights(weight, row)
            packed_sum += verify_packed_reconstruction(x, weight, row, arrays)
            cal, ci, cp, cb = trace_planes(x[:len(cal_ids)], cal_ids, row)
            evaluation, ei, ep, eb = trace_planes(x[len(cal_ids):], eval_ids, row)
            meta = dict(meta_base, row_start=row, used_rows=arrays[0]['used_rows'],
                        calibration_parent_ids_sha256=array_hash(cal_ids),
                        development_parent_ids_sha256=array_hash(eval_ids))
            results = screen_block(cal, evaluation, arrays, args.group_sizes, args.seed, meta)
            for array, result in zip(arrays, results):
                folder = out/f'rows_{row:04d}'/f'array_{array["array_index"]}'
                folder.mkdir(parents=True)
                bundle = folder/'traces.npz'
                with bundle.open('xb') as f:
                    np.savez_compressed(f, X_cal=cal, X_eval=evaluation, W=array['W'],
                                        cal_ids=ci, eval_ids=ei, cal_parent_ids=cp, eval_parent_ids=ep,
                                        cal_activation_bits=cb, eval_activation_bits=eb,
                                        output_channels=array['output_channels'],
                                        weight_bits=array['weight_bits'], coefficients=array['coefficients'])
                write_new(folder/'metadata.json', dict(result['source'],
                           used_columns=array['used_columns'], trace_sha256=sha256(bundle)))
                result['trace_sha256'] = sha256(bundle)
                write_new(folder/'screen.json', result)
                members.extend([bundle, folder/'metadata.json', folder/'screen.json'])
                all_results.append(result)
            block_info.append({'row_start': row, 'used_rows': arrays[0]['used_rows'],
                               'padding_rows': 256-arrays[0]['used_rows'], 'packed_arrays': len(arrays),
                               'cal_always_zero_real_features': int((cal[:, :arrays[0]['used_rows']].sum(0) == 0).sum()),
                               'mapping_shared_across_all_weight_arrays': True})
            print(f'PASS {args.layer} rows {row}..{row+arrays[0]["used_rows"]-1}: '
                  f'{len(arrays)} packed arrays; all bit-plane and permutation identities', flush=True)
        if not np.array_equal(packed_sum, x @ weight.T):
            raise AssertionError('Complete selected-layer packed sum mismatch')
        totals = {}
        for result in all_results:
            for run in result['runs']:
                key = (run['evaluation']['proposed_group_rows'], run['mapping'])
                totals[key] = totals.get(key, 0) + run['evaluation']['nonempty_group_reads']
        rows = []
        for (size, mapping), count in sorted(totals.items()):
            original, dead = totals[(size, 'original')], totals[(size, 'dead_feature_packed')]
            rows.append({'proposed_group_rows': size, 'mapping': mapping,
                         'nonempty_vector_reads': count,
                         'fraction_saved_vs_original': 1-count/original if original else None,
                         'fraction_saved_vs_dead_packed': 1-count/dead if dead else None})
        try:
            revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=BASE, capture_output=True,
                                      text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            revision = None
        summary = {'schema_version': 1, 'experiment_id': 'E01_FROZEN_MNIST',
                   'status': 'WORKLOAD_ONLY_COMPLETE', 'evidence_class': 'workload_structure',
                   'created_utc': datetime.now(timezone.utc).isoformat(), 'git_revision': revision,
                   'source': meta_base, 'calibration_parents': len(cal_ids),
                   'development_parents': len(eval_ids), 'original_test_read': False,
                   'golden_forward': verify, 'row_blocks': block_info, 'read_counts': rows,
                   'physical_validation': False, 'array_error_model': None, 'energy_j': None,
                   'inference_failure_rate': None, 'python': platform.python_version(), 'numpy': np.__version__,
                   'code_sha256': {p.name: sha256(p) for p in
                                   (Path(__file__), BASE/'experiments/frozen_mnist.py', SOURCE_CONTRACT)},
                   'interpretation': 'CAL-only baseline mappings; all DEV counts reported. No winner selected on DEV; '
                                     'padding/dead features are explicit; fresh E02 still required.'}
        write_new(out/'summary.json', summary)
        write_new(out/'private_run.json', {'argv': sys.argv, 'executable': sys.executable})
        members.append(out/'summary.json')
        packet = write_packet(out, members)
        print(json.dumps({'status': summary['status'], 'review_packet': str(packet.resolve()),
                          'calibration_images': len(cal_ids), 'development_images': len(eval_ids),
                          'packed_arrays': len(all_results), 'physical_validation': False}, indent=2), flush=True)
        return 0
    except Exception as error:
        write_new(out/'failure.json', {'status': 'NOT_COMPLETED', 'error_type': type(error).__name__,
                                      'error': str(error), 'physical_validation': False})
        members.append(out/'failure.json')
        packet = write_packet(out, members)
        print(json.dumps({'status': 'NOT_COMPLETED', 'error': str(error),
                          'review_packet': str(packet.resolve())}, indent=2), flush=True)
        return 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-root', type=Path, default=Path.home()/'MRAM_FYP_Overleaf')
    parser.add_argument('--model-dir', type=Path)
    parser.add_argument('--data-root', type=Path)
    parser.add_argument('--circuit-root', type=Path)
    parser.add_argument('--out', type=Path, default=BASE/'experiments/runs'/
                        ('E01_MNIST_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:6]))
    parser.add_argument('--layer', choices=('fc1', 'fc2'), default='fc1')
    parser.add_argument('--cal-images', type=int, default=128)
    parser.add_argument('--eval-images', type=int, default=256)
    parser.add_argument('--group-sizes', type=int, nargs='+', choices=(16,32,64,128,256), default=(32,64,128,256))
    parser.add_argument('--seed', type=int, default=20261104)
    parser.add_argument('--audit-only', action='store_true')
    args = parser.parse_args()
    if args.cal_images < 1 or args.eval_images < 1 or len(set(args.group_sizes)) != len(args.group_sizes):
        parser.error('Require positive parent budgets and unique proposed group sizes')
    try:
        return execute(args)
    except FileExistsError:
        parser.error('Output directory already exists; choose a new --out')


if __name__ == '__main__':
    raise SystemExit(main())
