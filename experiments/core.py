"""Exact array arithmetic and workload-only mapping screens.

All operations refer to one 256-row, 256-column binary physical bit-plane.
Grouping is a proposed schedule, not electrically isolated hardware. No current,
count-error probability, inference accuracy, energy or latency is synthesized.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import numpy as np

ROWS = COLS = 256
GROUP_SIZES = (16, 32, 64, 128, 256)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_new(path, data):
    path = Path(path)
    if 'archive' in path.parts:
        raise ValueError('Active tools must not write into archive/')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write('\n')


def binary(a, name, *, columns=ROWS):
    a = np.asarray(a)
    if a.ndim != 2 or a.shape[1] != columns or not len(a):
        raise ValueError(f'{name}: require a nonempty matrix with {columns} columns')
    if not np.isin(a, (0, 1)).all():
        raise ValueError(f'{name}: values must be exactly binary and finite')
    return a.astype(np.int64)


def validate_order(order):
    order = np.asarray(order)
    if order.shape != (ROWS,) or not np.array_equal(np.sort(order), np.arange(ROWS)):
        raise ValueError('Row order must be a permutation of 0..255')
    return order.astype(np.int64)


def validate_group_size(size):
    if size not in GROUP_SIZES:
        raise ValueError(f'Prospective group size must be in {GROUP_SIZES}')


def car_order(cal, size, alpha=0.25):
    """Independent implementation of VARA v1 Algorithm 1, with stable ties.

    Source: Dang et al., arXiv:2609.00421v1, section 3.3. Uses zero
    rates and pairwise co-zero affinity. This is a prior-art comparator.
    No training-time VAT or crossbar pruning is reproduced here.
    """
    cal = binary(cal, 'calibration activations')
    validate_group_size(size)
    if not np.isfinite(alpha) or alpha < 0:
        raise ValueError('alpha must be finite and nonnegative')
    z = 1.0 - cal
    rate = z.mean(axis=0)
    affinity = z.T @ z / len(cal)
    unused = np.ones(ROWS, dtype=bool)
    result = []
    while unused.any():
        available = np.flatnonzero(unused)
        seed = available[np.argmax(rate[available])]
        block = [int(seed)]
        unused[seed] = False
        running = affinity[seed].copy()
        while len(block) < size:
            available = np.flatnonzero(unused)
            score = running[available] / len(block) + alpha * rate[available]
            nxt = available[np.argmax(score)]
            block.append(int(nxt))
            unused[nxt] = False
            running += affinity[nxt]
        result.extend(block)
    return validate_order(result)


def balanced_order(cal, size, fixed_quiet_groups=0):
    """Simple zero-rate packing + activity balancing comparator.

    This heuristic has no reliability guarantee and is not claimed novel.
    Parameters are frozen using calibration only; evaluation is never fitted.
    """
    cal = binary(cal, 'calibration activations')
    validate_group_size(size)
    groups = ROWS // size
    if not 0 <= fixed_quiet_groups < groups:
        raise ValueError('Quiet groups must leave at least one other group')
    activity = cal.mean(axis=0)
    sorted_rows = np.argsort(activity, kind='stable')
    quiet_count = fixed_quiet_groups * size
    prefix = sorted_rows[:quiet_count].tolist()
    rest = sorted_rows[quiet_count:]
    rest = rest[np.argsort(-activity[rest], kind='stable')]
    bins = [[] for _ in range(groups - fixed_quiet_groups)]
    loads = np.zeros(len(bins))
    for row in rest:
        choices = [i for i, b in enumerate(bins) if len(b) < size]
        target = min(choices, key=lambda i: (loads[i], i))
        bins[target].append(int(row))
        loads[target] += activity[row]
    return validate_order(prefix + [v for b in bins for v in b])


def candidate_orders(cal, size, seed=20261103):
    cal = binary(cal, 'calibration activations')
    validate_group_size(size)
    out = {
        'original': np.arange(ROWS),
        'random': np.random.default_rng(seed).permutation(ROWS),
        'zero_rate_sorted': np.argsort(cal.mean(axis=0), kind='stable'),
        'activity_balanced': balanced_order(cal, size),
    }
    for alpha in (0.0, 0.25, 1.0):
        out[f'car_alpha_{alpha:g}'] = car_order(cal, size, alpha)
    # A bounded comparator set, not a tuned reliability-aware algorithm.
    for q in sorted({1, (ROWS // size) // 4}):
        if 0 < q < ROWS // size:
            out[f'quiet_then_balanced_q{q}'] = balanced_order(cal, size, q)
    return out


def activity_metrics(x, order, size):
    x = binary(x, 'activations')
    order = validate_order(order)
    validate_group_size(size)
    m = x[:, order].reshape(len(x), ROWS // size, size).sum(axis=2)
    active = m > 0
    total = int(m.sum())
    reads = int(active.sum())
    histogram = np.bincount(m.ravel(), minlength=size + 1)
    return {
        'samples': len(x), 'proposed_group_rows': size,
        'potential_group_reads': int(m.size), 'nonempty_group_reads': reads,
        'zero_group_fraction': float(1 - active.mean()),
        'active_rows_total_invariant': total,
        'active_rows_per_nonempty_read': total / reads if reads else None,
        'occupancy_histogram': histogram.tolist(),
        'mean_sum_squared_activity_proxy': float(np.square(m).sum(axis=1).mean()),
        'metric_scope': 'workload structure only; squared activity is not physical error or energy',
    }


def validate_contract(contract, physical=False):
    if (contract.get('physical_rows'), contract.get('physical_columns')) != (ROWS, COLS):
        raise ValueError('Target contract must declare a physical 256 x 256 array')
    if contract.get('representation') != 'binary_01_bitplane':
        raise ValueError('These tools require an explicitly declared 0/1 bit-plane mapping')
    missing = []
    if physical:
        for key in ('cell_model_reference', 'access_device_reference', 'array_topology',
                    'wire_model_reference', 'driver_reference', 'readout_reference',
                    'calibration_protocol', 'variation_protocol', 'validated_max_active_rows',
                    'validation_artifact_sha256'):
            if contract.get(key) is None or contract.get(key) == '':
                missing.append(key)
        cap = contract.get('validated_max_active_rows')
        if cap is not None and (isinstance(cap, bool) or not isinstance(cap, int) or not 1 <= cap <= ROWS):
            raise ValueError('Validated active-row limit must be an integer in 1..256')
        if contract.get('evidence_status') != 'validated_target_model':
            missing.append('evidence_status=validated_target_model')
    return missing


def load_trace_bundle(bundle, metadata):
    meta = json.loads(Path(metadata).read_text())
    if meta.get('evidence_class') != 'workload_trace':
        raise ValueError('A real workload trace declaration is required; fixtures belong in tests')
    for key in ('dataset', 'model_sha256', 'quantization_sha256', 'layer',
                'source_export_command', 'split_purpose', 'previously_inspected'):
        if key not in meta or meta[key] is None or meta[key] == '':
            raise ValueError(f'Missing workload provenance field: {key}')
    if meta['split_purpose'] not in ('development', 'held_out'):
        raise ValueError('Declare development or held_out split purpose')
    if meta['previously_inspected'] is True and meta['split_purpose'] == 'held_out':
        raise ValueError('Previously inspected data cannot be relabelled held_out')
    with np.load(bundle, allow_pickle=False) as f:
        required = ('X_cal', 'X_eval', 'W', 'cal_ids', 'eval_ids')
        if any(k not in f for k in required):
            raise ValueError(f'Trace NPZ must contain {required}')
        cal = binary(f['X_cal'], 'X_cal')
        evaluation = binary(f['X_eval'], 'X_eval')
        w = binary(f['W'], 'W')
        if w.shape != (ROWS, COLS):
            raise ValueError('W must represent exactly one 256 x 256 physical bit-plane')
        cal_ids, eval_ids = f['cal_ids'].astype(str), f['eval_ids'].astype(str)
    if cal_ids.shape != (len(cal),) or eval_ids.shape != (len(evaluation),):
        raise ValueError('One stable ID is required per trace row')
    if len(set(cal_ids)) != len(cal_ids) or len(set(eval_ids)) != len(eval_ids):
        raise ValueError('Trace IDs must be unique inside each split')
    if set(cal_ids) & set(eval_ids):
        raise ValueError('Calibration and evaluation trace IDs overlap')
    return cal, evaluation, w, meta


def screen(bundle, metadata, sizes=GROUP_SIZES, seed=20261103):
    cal, evaluation, w, meta = load_trace_bundle(bundle, metadata)
    result = {
        'schema_version': 1, 'experiment_id': 'E01',
        'evidence_class': 'workload_structure', 'physical_validation': False,
        'trace_sha256': sha256(bundle), 'metadata_sha256': sha256(metadata),
        'source': meta, 'seed': seed,
        'energy_j': None, 'latency_s': None, 'count_error_rate': None,
        'inference_failure_rate': None, 'runs': [],
    }
    exact = evaluation @ w
    for size in sizes:
        for name, order in candidate_orders(cal, size, seed).items():
            if not np.array_equal(evaluation[:, order] @ w[order], exact):
                raise AssertionError('Permutation changed the exact dot product')
            cal_metrics = activity_metrics(cal, order, size)
            eval_metrics = activity_metrics(evaluation, order, size)
            result['runs'].append({
                'mapping': name, 'order': order.tolist(),
                'order_sha256': hashlib.sha256(order.astype('<i8').tobytes()).hexdigest(),
                'calibration': cal_metrics, 'evaluation': eval_metrics,
                'integer_equivalence': True,
            })
    return result


def mathematical_checks(seed=20261103):
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, (5, ROWS), dtype=np.int64)
    w = rng.integers(0, 2, (ROWS, COLS), dtype=np.int64)
    direct = x @ w
    p = rng.permutation(ROWS)
    assert np.array_equal(x[:, p] @ w[p], direct)
    assert np.array_equal(w.sum(axis=0) - (1 - x) @ w, direct)
    for size in GROUP_SIZES:
        split = sum(x[:, i:i+size] @ w[i:i+size] for i in range(0, ROWS, size))
        assert np.array_equal(split, direct)
    xa = rng.integers(0, 256, (3, ROWS), dtype=np.int64)
    ws = rng.integers(-8, 8, (ROWS, COLS), dtype=np.int64)
    ws[0, 0] = -8
    reconstructed = np.zeros((len(xa), COLS), dtype=np.int64)
    for ab in range(8):
        for wb in range(4):
            coeff = (1 << ab) * ((1 << wb) if wb < 3 else -8)
            reconstructed += coeff * (((xa >> ab) & 1) @ ((ws >> wb) & 1))
    assert np.array_equal(reconstructed, xa @ ws)
    hbase = rng.normal(size=(4, ROWS))
    h = hbase.T @ hbase
    a = x[0]
    assert np.allclose(a @ h @ a - (1-a) @ h @ (1-a), (2*a-1) @ h @ np.ones(ROWS))
    for m in range(ROWS + 1):
        for k in range(ROWS + 1):
            support = min(m, k) - max(0, m+k-ROWS) + 1
            assert support == 1 + min(m, ROWS-m, k, ROWS-k)
    return {
        'schema_version': 1, 'experiment_id': 'E00',
        'evidence_class': 'software_mathematical_verification', 'seed': seed,
        'target_rows': ROWS, 'target_columns': COLS,
        'checks': {k: 'PASS' for k in (
            'consistent_row_permutation', 'complement_reconstruction',
            'partial_sum_reconstruction_all_proposed_group_sizes',
            'W4A8_signed_bitplane_reconstruction', 'quadratic_polarity_identity',
            'conditional_count_cardinality_all_m_K')},
        'physical_validation': False, 'inference_evaluation': False,
        'scope': 'Exact software checks only; no claimed MRAM performance or novelty',
    }
