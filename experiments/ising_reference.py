"""Exact Ising software controls; no MRAM error kernel or hardware simulator.

Stable binary MRAM and a stochastic spin source are separate components. This
module checks a sequential heat-bath reference, exact incremental field caching,
small-graph optima and a two-flip cache diagnostic before a target noise study.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import sys

import numpy as np

from .core import sha256, write_new


def graph_weights(values):
    a = np.asarray(values)
    if (a.ndim != 2 or a.shape[0] != a.shape[1] or not 2 <= len(a) <= 256
            or not np.isfinite(a).all() or not np.equal(a, np.rint(a)).all()
            or np.any(a < 0) or np.any(a > 1_000_000)
            or not np.array_equal(a, a.T) or np.any(np.diag(a))):
        raise ValueError('Require a symmetric, zero-diagonal nonnegative integer graph')
    return a.astype(np.int64)


def spin_vector(values, n):
    s = np.asarray(values)
    if s.shape != (n,) or not np.isin(s, (-1, 1)).all():
        raise ValueError('Spins must be a vector of -1/+1')
    return s.astype(np.int64).copy()


def cut_value(weights, spins):
    a = graph_weights(weights)
    s = spin_vector(spins, len(a))
    return int(np.triu(a * (s[:, None] != s[None, :]), 1).sum())


def target_energy(weights, spins):
    # J=-A, H=-s^T J s/2 = sum_edges A_ij s_i s_j = W_total-2*cut.
    a = graph_weights(weights)
    s = spin_vector(spins, len(a))
    return int(s @ a @ s // 2)


def exact_maxcut(weights):
    a = graph_weights(weights)
    n = len(a)
    if n > 20:
        raise ValueError('Exact enumeration is limited to 20 spins; use certified targets above that')
    best, best_state = -1, None
    # Fix s_0=+1 to remove the global sign symmetry.
    for first in range(0, 1 << (n - 1), 4096):
        indices = np.arange(first, min(first + 4096, 1 << (n - 1)), dtype=np.int64)
        s = np.ones((len(indices), n), dtype=np.int64)
        s[:, 1:] = 2 * ((indices[:, None] >> np.arange(n - 1)) & 1) - 1
        values = (np.triu(a, 1).sum() - np.einsum('bi,ij,bj->b', s, a, s) // 2) // 2
        k = int(np.argmax(values))
        if int(values[k]) > best:
            best, best_state = int(values[k]), s[k].copy()
    assert cut_value(a, best_state) == best
    return best, best_state


def plus_probability(field, beta):
    if not math.isfinite(float(field)) or not math.isfinite(float(beta)) or beta < 0:
        raise ValueError('Require a finite local field and nonnegative finite inverse temperature')
    return 0.5 * (1.0 + math.tanh(float(beta) * float(field)))


def trajectory(weights, initial, order, uniforms, betas, *, mode, check_cache=False):
    a = graph_weights(weights)
    j = -a
    s = spin_vector(initial, len(a))
    order, uniforms, betas = np.asarray(order), np.asarray(uniforms), np.asarray(betas)
    if (order.ndim != 1 or not np.equal(order, np.rint(order)).all()
            or np.any(order < 0) or np.any(order >= len(a))
            or uniforms.shape != order.shape or betas.shape != order.shape
            or not np.isfinite(uniforms).all() or np.any(uniforms < 0) or np.any(uniforms >= 1)
            or not np.isfinite(betas).all() or np.any(betas < 0)
            or mode not in ('full_field', 'incremental')):
        raise ValueError('Invalid update order, randomness, schedule or reference mode')
    cached = j @ s if mode == 'incremental' else None
    decisions, cuts, flips = [], [], 0
    for k, u, beta in zip(order.astype(int), uniforms, betas):
        field = int(j[k] @ s) if cached is None else int(cached[k])
        old = int(s[k])
        new = 1 if u < plus_probability(field, float(beta)) else -1
        if new != old:
            s[k] = new
            flips += 1
            if cached is not None:
                cached += j[:, k] * (new - old)
        if cached is not None and check_cache:
            np.testing.assert_array_equal(cached, j @ s)
        decisions.append(new)
        cuts.append(cut_value(a, s))
    return {'spins': s, 'decisions': np.asarray(decisions, dtype=np.int8),
            'cuts': np.asarray(cuts, dtype=np.int64), 'flips': flips}


def restart_count(success_probability, target_probability=0.99):
    p, q = float(success_probability), float(target_probability)
    if not 0 <= p <= 1 or not 0 < q < 1:
        raise ValueError('Require p in [0,1] and target in (0,1)')
    if p == 0:
        return None  # No finite restart count justified by p=0.
    if p == 1:
        return 1
    return int(math.ceil(math.log1p(-q) / math.log1p(-p)))


def closed_loop_check():
    # Flip one spin and flip it back. Error eta is in one coupling coefficient.
    # Identical eta cancels; independent eta_1,eta_2 leaves 2*(eta_2-eta_1).
    frozen = [2 * (eta - eta) for eta in (-1, 1)]
    fresh = [2 * (b - a) for a, b in itertools.product((-1, 1), repeat=2)]
    assert frozen == [0, 0]
    assert np.mean(fresh) == 0 and np.var(fresh) == 8
    return {'evidence_class': 'exact_algebra_and_finite_enumeration',
            'frozen_loop_residual': frozen, 'independent_sign_error_loop_residual': fresh,
            'independent_sign_error_variance': 8,
            'interpretation': 'Cache drift is possible with fresh incremental-read errors. No MRAM noise magnitude or solver outcome is inferred.'}


def kernel_preflight(contract):
    missing = []
    for key in ('response_model_sha256', 'target_validation_artifact_sha256',
                'coupling_encoding_sha256', 'calibration_policy_sha256',
                'persistent_variation_source_sha256', 'temporal_noise_source_sha256',
                'fixed_state_marginal_audit_sha256'):
        value = contract.get(key)
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            missing.append(key)
    if contract.get('physical_rows') != 256 or contract.get('physical_columns') != 256:
        missing.append('physical_256x256_target')
    if contract.get('field_operator') not in ('full_field_recomputation', 'incremental_coefficient_read'):
        missing.append('field_operator')
    if contract.get('target_model_validated') is not True:
        missing.append('target_model_validated')
    if contract.get('field_error_units') != 'target_integer_coupling_units':
        missing.append('field_error_units')
    return {'status': 'BLOCKED_TARGET_KERNEL' if missing else 'CONTRACT_COMPLETE_REVIEW_AND_ADAPTER_REQUIRED',
            'missing': missing, 'target_noise_study_implemented': False,
            'note': 'Metadata completeness is not physical validation; the target response adapter remains unimplemented.'}


def verify():
    graphs = {'triangle3': np.ones((3, 3), dtype=int) - np.eye(3, dtype=int)}
    cycle = np.zeros((6, 6), dtype=int)
    for k in range(6):
        cycle[k, (k + 1) % 6] = cycle[(k + 1) % 6, k] = 1
    graphs['cycle6'] = cycle
    rng = np.random.default_rng(20261104)
    upper = np.triu(rng.integers(0, 4, (12, 12)) * (rng.random((12, 12)) < 0.35), 1)
    graphs['weighted12'] = upper + upper.T
    graphs['complete64_parity_only'] = np.ones((64, 64), dtype=int) - np.eye(64, dtype=int)
    records = []
    for name, a in graphs.items():
        optimum = exact_maxcut(a)[0] if len(a) <= 20 else None
        if name == 'triangle3':
            assert optimum == 2
        if name == 'cycle6':
            assert optimum == 6
        for seed in (20261104, 20261105):
            rr = np.random.default_rng(seed)
            n = len(a)
            initial = rr.choice([-1, 1], n)
            order = np.concatenate([rr.permutation(n) for _ in range(8)])
            uniforms = rr.random(len(order))
            betas = np.repeat(np.linspace(0.0, 1.2, 8), n)
            full = trajectory(a, initial, order, uniforms, betas, mode='full_field')
            incremental = trajectory(a, initial, order, uniforms, betas, mode='incremental', check_cache=True)
            for key in ('spins', 'decisions', 'cuts'):
                np.testing.assert_array_equal(full[key], incremental[key])
            total_weight = int(np.triu(a, 1).sum())
            assert target_energy(a, full['spins']) == total_weight - 2 * cut_value(a, full['spins'])
            records.append({'graph': name, 'seed': seed, 'spins': n, 'update_attempts': len(order),
                            'exact_optimum_if_enumerated': optimum,
                            'decision_sha256': hashlib.sha256(full['decisions'].tobytes()).hexdigest(),
                            'graph_sha256': hashlib.sha256(np.asarray(a, dtype=np.int64).tobytes()).hexdigest(),
                            'full_incremental_parity': True})
    assert plus_probability(100, 0) == 0.5
    assert restart_count(0.5) == 7 and restart_count(0) is None and restart_count(1) == 1
    return {'evidence_class': 'software_mathematical_verification', 'experiment_id': 'E09A',
            'target_circuit_results': False, 'temporal_noise_calibrated': False,
            'solver_success_benchmark': False, 'hardware_speed_or_energy_claim': False,
            'checks': {'exact_small_graph_targets': True, 'energy_cut_identity': True,
                       'full_incremental_trajectory_parity': True, 'cache_parity_every_update': True,
                       'beta_zero_heatbath': True, 'restart_probability_boundary_cases': True},
            'trajectory_cases': records, 'closed_loop_diagnostic': closed_loop_check()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    v = sub.add_parser('verify', help='Exact software controls, not a hardware-noise experiment')
    v.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('preflight', help='Check the unresolved target field-kernel contract')
    p.add_argument('--contract', type=Path, default=Path('experiments/config/ising_error_kernel.template.json'))
    p.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    # Fail before calculation if a record already exists.
    if args.out.exists() or 'archive' in args.out.resolve().parts:
        raise SystemExit('Refusing to overwrite evidence or write into archive')
    result = verify() if args.mode == 'verify' else kernel_preflight(json.loads(args.contract.read_text()))
    result.update({'created_utc': datetime.now(timezone.utc).isoformat(), 'argv': sys.argv,
                   'implementation_sha256': sha256(Path(__file__)), 'python': platform.python_version(),
                   'numpy': np.__version__})
    if args.mode == 'preflight':
        result['contract_sha256'] = sha256(args.contract)
    write_new(args.out, result)
    print(json.dumps({'out': str(args.out), 'evidence_class': result.get('evidence_class'),
                      'status': result.get('status', 'PASS_SOFTWARE_ONLY'),
                      'checks': result.get('checks'), 'target_circuit_results': False}, indent=2))
    if args.mode == 'preflight':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
