#!/usr/bin/env python3
"""E25: decoded-error row-swap search with exact passive-circuit query controls.

REAL frozen E01 bitplanes + ASSUMED linear shunts and one-ended wire resistance.
No GF, PEX or physical ADC is simulated. Optional neural propagation requires the
hash-pinned student checkpoint on NUS. Circuit search needs NumPy only, Python >=3.6.
Packet bytes remain private. No retraining or DEV fitting.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import platform
import struct
import sys
import time
from types import SimpleNamespace
import zipfile
from pathlib import Path

import numpy as np

PACKET_SHA = '400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a'
GAP = 36.704e-6  # ASSUMED effective shunt conductance, not GF characterization
GP = 2.0 * GAP
ACT = 2.0 ** np.arange(8)
COEF = np.array([1., 2., 4., -8.])


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def direct_seen(a, r):
    """Exact equivalent conductance of the DECLARED passive ladder.

    There is one series wire segment before each shunt, including row zero.
    T_g(y)=(y+g)/(1+r*(y+g)); compose from the farthest row to the source.
    """
    if r == 0:
        return a.sum(axis=1)
    # A contiguous physical-row view is the strong full-recursion control.
    # Charge its transpose/copy cost here; do not rely on pathological strided
    # memory access to manufacture a sparse/tree timing advantage.
    rows = np.ascontiguousarray(a.T)
    y = np.zeros(len(a), dtype=np.float64)
    for row in rows[::-1]:
        y = (y + row) / (1. + r * (y + row))
    return y


def mm(a, b):
    """Batch 2x2 multiplication, row-major coefficients (a,b,c,d)."""
    return np.stack((a[:, 0]*b[:, 0]+a[:, 1]*b[:, 2],
                     a[:, 0]*b[:, 1]+a[:, 1]*b[:, 3],
                     a[:, 2]*b[:, 0]+a[:, 3]*b[:, 2],
                     a[:, 2]*b[:, 1]+a[:, 3]*b[:, 3]), axis=1)


def leaf(q):
    # Dimensionless state z=r*y: T_q(z)=(z+q)/(z+q+1).
    return np.stack((np.ones(len(q)), q, np.ones(len(q)), 1.+q), axis=1)


class SwapOracle:
    """Unmodified circuit samples are skipped; segment backend caches products.

    Per dirty sample: full/sparse recursion O(B); segment update O(log B).
    Tree setup and memory are charged explicitly. Finite precision is tested.
    """
    def __init__(self, a, r, backend):
        if backend not in ('full', 'sparse', 'segment') or r <= 0:
            raise ValueError('Require full/sparse/segment and strictly positive R')
        self.a = np.asarray(a, dtype=np.float64).copy()
        self.r, self.backend = float(r), backend
        self.seen = direct_seen(self.a, r)
        self.size = 1
        while self.size < a.shape[1]:
            self.size *= 2
        self.tree = None
        if backend == 'segment':
            self.tree = [None]*(2*self.size)
            for j in range(self.size):
                if j < a.shape[1]:
                    m = leaf(r*self.a[:, j])
                else:
                    m = np.tile(np.array([1., 0., 0., 1.]), (len(a), 1))
                self.tree[self.size+j] = m
            for j in range(self.size-1, 0, -1):
                self.tree[j] = mm(self.tree[2*j], self.tree[2*j+1])
            y = self.tree[1][:, 1]/self.tree[1][:, 3]/r
            if not np.allclose(y, self.seen, rtol=2e-12, atol=1e-18):
                raise AssertionError('Circuit tree initialization differs from recursion')

    @property
    def cache_bytes(self):
        return 0 if self.tree is None else sum(x.nbytes for x in self.tree[1:])

    def trial(self, p, q):
        dirty = np.flatnonzero(self.a[:, p] != self.a[:, q])
        changed = {}
        if self.backend == 'full':
            aa = self.a.copy()
            aa[:, [p, q]] = aa[:, [q, p]]
            seen = direct_seen(aa, self.r)
        elif not len(dirty):
            seen = self.seen.copy()
        elif self.backend == 'sparse':
            aa = self.a[dirty].copy()
            aa[:, [p, q]] = aa[:, [q, p]]
            seen = self.seen.copy()
            seen[dirty] = direct_seen(aa, self.r)
        else:
            changed[self.size+p] = leaf(self.r*self.a[dirty, q])
            changed[self.size+q] = leaf(self.r*self.a[dirty, p])
            level = {self.size+p, self.size+q}
            while level != {1}:
                parents = sorted(set(j//2 for j in level))
                for j in parents:
                    left = changed.get(2*j)
                    right = changed.get(2*j+1)
                    if left is None:
                        left = self.tree[2*j][dirty]
                    if right is None:
                        right = self.tree[2*j+1][dirty]
                    changed[j] = mm(left, right)
                level = set(parents)
            seen = self.seen.copy()
            seen[dirty] = changed[1][:, 1]/changed[1][:, 3]/self.r
        return {'seen': seen, 'dirty': dirty, 'changed': changed, 'pair': (p, q)}

    def accept(self, proposal):
        p, q = proposal['pair']
        self.a[:, [p, q]] = self.a[:, [q, p]]
        if self.backend == 'segment':
            for j, value in proposal['changed'].items():
                self.tree[j][proposal['dirty']] = value
        self.seen = proposal['seen']


def circuit_data(x, w, order):
    xx = x[:, :, order].astype(np.float64)
    ww = w[:, :, order].astype(np.float64)
    a = xx[:, :, None, None, :] * (GAP + GAP*ww[None, None, :, :, :])
    n = np.einsum('tbr,por->tbpo', xx, ww, optimize=True)
    m, k = xx.sum(-1), ww.sum(-1)
    lo = np.maximum(0., m[:, :, None, None]+k[None, None, :, :]-len(order))
    hi = np.minimum(m[:, :, None, None], k[None, None, :, :])
    centroid = np.einsum('tbr,r->tb', xx, np.arange(1., len(order)+1))
    return {'a': a.reshape(-1, len(order)), 'shape': n.shape, 'n': n,
            'lo': lo, 'hi': hi, 'm': m, 'centroid': centroid,
            'total': a.sum(-1), 'x': xx, 'read_count': int((m > 0).sum())}


def decode(data, seen, centroid, nfit, beta=None):
    """Every arm gets the SAME two-feature, CAL-only, per-group calibrator.

    First CAL half fits beta; second half chooses swaps. No DEV is used here.
    Legal count support is shared optimistic metadata, not free physical circuitry.
    """
    features = np.stack((data['m'], centroid), axis=-1)
    if beta is None:
        # Exact ideal arithmetic is allowed ONLY for fitting on CAL parents.
        droop = (data['total']-seen.reshape(data['shape']))/GAP
        f = features[:nfit].reshape(-1, 2)
        target = droop[:nfit].mean(axis=(2, 3)).reshape(-1)
        beta = np.linalg.lstsq(f, target, rcond=None)[0]
    correction = np.einsum('tbk,k->tb', features, beta)
    # Inference uses sensed admittance and the KNOWN input mask, not true n.
    estimate = seen.reshape(data['shape'])/GAP-data['m'][:, :, None, None]+correction[:, :, None, None]
    count = np.clip(np.floor(estimate+.5), data['lo'], data['hi'])
    err = count-data['n']
    reconstructed = np.einsum('tbpo,b,p->to', err, ACT, COEF, optimize=True)
    return reconstructed, int(np.count_nonzero(err)), beta


def qcost(s, order):
    b = len(order)
    kernel = np.minimum.outer(np.arange(1., b+1), np.arange(1., b+1))
    return float(np.sum(s[np.ix_(order, order)]*kernel))


def graph_orders(x, w, base, b, passes=7):
    acts = x.reshape(-1, 256).astype(np.float64)
    # Mean conductance over ALL evaluated outputs/planes, even if swap fitness
    # samples only a predeclared subset of output channels for bounded runtime.
    mean_g = (GAP+GAP*w.astype(np.float64)).mean(axis=(0, 1))
    orders = {name: base.copy() for name in
              ('activity_sort', 'conductance_sort', 'independent_graph', 'camp_light')}
    graphs = []
    for start in range(0, 256, b):
        ids = base[start:start+b]
        xa = acts[:, ids]
        prob = xa.mean(0)
        c = np.dot(xa.T, xa)/len(xa)
        weight = np.outer(mean_g[ids], mean_g[ids])
        corr = c*weight
        independent = np.outer(prob, prob)*weight
        # Bernoulli self moment is E[x_i^2]=p_i, NOT p_i^2. Only off-diagonal
        # coactivation is removed in the independence control.
        np.fill_diagonal(independent, prob*np.diag(weight))
        graphs.append(corr)
        choices = {'activity_sort': np.argsort(-prob, kind='mergesort'),
                   'conductance_sort': np.argsort(-prob*mean_g[ids], kind='mergesort')}
        for name, s in [('camp_light', corr), ('independent_graph', independent)]:
            order = np.argsort(-s.sum(1), kind='mergesort')
            val = qcost(s, order)
            for unused in range(passes):
                best, pair = val, None
                for p in range(b):
                    for q in range(p+1, b):
                        new = order.copy()
                        new[p], new[q] = new[q], new[p]
                        score = qcost(s, new)
                        if score < best-1e-18:
                            best, pair = score, (p, q)
                if pair is None:
                    break
                order[pair[0]], order[pair[1]] = order[pair[1]], order[pair[0]]
                val = best
            choices[name] = order
        for name, perm in choices.items():
            orders[name][start:start+b] = ids[perm]
    return orders, graphs


def group_errors(x, w, order, b, r, nfit, betas=None):
    errors, beta_out, wrong, reads = [], [], 0, 0
    for gi, start in enumerate(range(0, 256, b)):
        d = circuit_data(x, w, order[start:start+b])
        beta = None if betas is None else betas[gi]
        e, count, beta = decode(d, direct_seen(d['a'], r), d['centroid'], nfit, beta)
        errors.append(e)
        beta_out.append(beta)
        wrong += count
        reads += d['read_count']
    return errors, beta_out, wrong, reads


def search(x, w, base, start_order, graphs, b, r, nfit, proposals, seed, backend,
           objective='decoded_mse'):
    start_time = time.perf_counter()
    order = start_order.copy()
    errors, unused, unused2, reads = group_errors(x, w, order, b, r, nfit)
    total = np.sum(errors, axis=0)
    record = {'backend': backend, 'objective': objective, 'accepted': 0,
              'proposals': 0, 'dirty_fraction_sum': 0., 'max_tree_cache_bytes': 0,
              'oracle_seconds': 0., 'decode_seconds': 0., 'setup_seconds': 0.}
    trajectory = []
    for gi, start in enumerate(range(0, 256, b)):
        ids = order[start:start+b].copy()
        d = circuit_data(x, w, ids)
        ts = time.perf_counter()
        oracle = SwapOracle(d['a'], r, backend)
        record['setup_seconds'] += time.perf_counter()-ts
        record['max_tree_cache_bytes'] = max(record['max_tree_cache_bytes'], oracle.cache_bytes)
        # Independent reproducible candidate stream for every group/backend/objective.
        rng = np.random.RandomState(seed+1009*gi)
        cent = d['centroid'].copy()
        xx = d['x'].copy()
        current_loss = float(np.mean(total[nfit:]**2))
        base_group = base[start:start+b]
        logical_to_local = {int(j): k for k, j in enumerate(base_group)}
        local = np.array([logical_to_local[int(j)] for j in ids])
        current_q = qcost(graphs[gi], local)
        for trial_number in range(proposals):
            p, q = sorted(rng.choice(b, 2, replace=False).tolist())
            newcent = cent+(q-p)*(xx[:, :, p]-xx[:, :, q])
            ts = time.perf_counter()
            prop = oracle.trial(p, q)
            record['oracle_seconds'] += time.perf_counter()-ts
            record['dirty_fraction_sum'] += len(prop['dirty'])/max(1., len(d['a']))
            record['proposals'] += 1
            ts = time.perf_counter()
            newerr, wrong, beta = decode(d, prop['seen'], newcent, nfit)
            proposed_total = total-errors[gi]+newerr
            loss = float(np.mean(proposed_total[nfit:]**2))
            record['decode_seconds'] += time.perf_counter()-ts
            newlocal = local.copy()
            newlocal[p], newlocal[q] = newlocal[q], newlocal[p]
            qq = qcost(graphs[gi], newlocal)
            accept = (loss < current_loss-1e-9 if objective == 'decoded_mse'
                      else qq < current_q-1e-18)
            if accept:
                oracle.accept(prop)
                cent = newcent
                xx[:, :, [p, q]] = xx[:, :, [q, p]]
                ids[p], ids[q] = ids[q], ids[p]
                total, errors[gi], local = proposed_total, newerr, newlocal
                current_loss, current_q = loss, qq
                record['accepted'] += 1
                trajectory.append([gi, trial_number, p, q, loss])
        order[start:start+b] = ids
        # Re-evaluate accepted state with full recursion to catch stale tree/cache errors.
        check = circuit_data(x, w, ids)
        if not np.allclose(oracle.seen, direct_seen(check['a'], r), rtol=2e-12, atol=1e-18):
            raise AssertionError('Accepted sparse state does not match full recomputation')
    if not all(np.array_equal(np.sort(order[s:s+b]), np.sort(base[s:s+b]))
               for s in range(0, 256, b)):
        raise AssertionError('A row escaped its fixed read group')
    record['search_seconds_including_setup'] = time.perf_counter()-start_time
    record['mean_dirty_fraction'] = record.pop('dirty_fraction_sum')/max(1, record['proposals'])
    record['cal_selection_mse'] = float(np.mean(total[nfit:]**2))
    record['read_count'] = reads
    record['accepted_trajectory'] = trajectory
    return order, record


def load_packet(packet, row_start, outputs, ncal, ndev, grouping):
    with zipfile.ZipFile(str(packet)) as z:
        names = ['rows_%04d/array_%d/traces.npz' % (row_start, i) for i in (0, 1)]
        arrays = [np.load(io.BytesIO(z.read(n)), allow_pickle=False) for n in names]
        screen = json.loads(z.read('rows_%04d/array_0/screen.json' % row_start).decode())
        a, aa = arrays
        nc, nd = len(a['X_cal'])//8, len(a['X_eval'])//8
        if ncal > nc or ndev > nd:
            raise ValueError('Requested more parents than the frozen packet contains')
        xc = a['X_cal'].reshape(nc, 8, 256)[:ncal].copy()
        xd = a['X_eval'].reshape(nd, 8, 256)[:ndev].copy()
        calids = a['cal_parent_ids'].reshape(nc, 8)[:ncal]
        devids = a['eval_parent_ids'].reshape(nd, 8)[:ndev]
        if not (np.all(calids == calids[:, :1]) and np.all(devids == devids[:, :1])):
            raise ValueError('Packet parent/bitplane identities are inconsistent')
        if set(calids[:, 0]) & set(devids[:, 0]):
            raise ValueError('CAL and DEV parents overlap')
        if not (np.array_equal(a['X_cal'], aa['X_cal']) and
                np.array_equal(a['X_eval'], aa['X_eval'])):
            raise ValueError('Packed arrays disagree on activation streams')
        w = np.zeros((4, outputs, 256), dtype=np.uint8)
        seen = set()
        for ar in arrays:
            for j, (p, o) in enumerate(zip(ar['weight_bits'], ar['output_channels'])):
                p, o = int(p), int(o)
                if o < outputs:
                    if (p, o) in seen:
                        raise ValueError('Duplicate packed weight plane/output')
                    seen.add((p, o))
                    w[p, o] = ar['W'][:, j]
        if seen != set((p, o) for p in range(4) for o in range(outputs)):
            raise ValueError('Missing signed weight planes')
        matches = [r for r in screen['runs'] if r['mapping'] == grouping
                   and r['evaluation']['proposed_group_rows'] == 32]
        if len(matches) != 1:
            raise ValueError('Expected exactly one frozen grouping order')
        order = np.asarray(matches[0]['order'], dtype=np.int64)
        if sorted(order.tolist()) != list(range(256)):
            raise ValueError('Invalid saved permutation')
        return xc, xd, w, order, calids[:, 0].copy(), devids[:, 0].copy()


def verify_packet(path):
    if digest(path) != PACKET_SHA:
        raise ValueError('Unexpected frozen E01 packet SHA256')
    with zipfile.ZipFile(str(path)) as z:
        manifest = json.loads(z.read('packet_manifest.json').decode())
        for name, rec in manifest['files'].items():
            if hashlib.sha256(z.read(name)).hexdigest() != rec['sha256']:
                raise ValueError('Packet member hash differs: '+name)


def selftest():
    rng = np.random.RandomState(250511)
    for b in (3, 8, 32, 64, 128, 256):
        a = rng.choice([0., GAP, GP], size=(31, b))
        arms = [SwapOracle(a, 5., be) for be in ('full', 'sparse', 'segment')]
        for j in range(20):
            p, q = rng.choice(b, 2, replace=False)
            pp = [v.trial(int(p), int(q)) for v in arms]
            for proposal in pp[1:]:
                np.testing.assert_allclose(pp[0]['seen'], proposal['seen'], rtol=2e-12, atol=1e-18)
            if j % 3:
                for v, proposal in zip(arms, pp):
                    v.accept(proposal)
    # Independent physical-node KCL, not just two implementations of the recursion.
    for b in (1, 3, 12):
        for r in (1., 5., 25.):
            g = rng.choice([0., GAP, GP], size=b)
            mat = np.diag(g.copy())
            rhs = np.zeros(b)
            mat[0, 0] += 1./r
            rhs[0] += 1./r
            for j in range(b-1):
                mat[j, j] += 1./r
                mat[j+1, j+1] += 1./r
                mat[j, j+1] -= 1./r
                mat[j+1, j] -= 1./r
            voltage = np.linalg.solve(mat, rhs)
            np.testing.assert_allclose(direct_seen(g[None, :], r)[0],
                                       np.dot(g, voltage), rtol=1e-11, atol=1e-16)
    x = rng.randint(0, 2, (12, 8, 32)).astype(np.uint8)
    w = rng.randint(0, 2, (4, 3, 32)).astype(np.uint8)
    d = circuit_data(x, w, np.arange(32))
    err, wrong, beta = decode(d, direct_seen(d['a'], 0.), d['centroid'], 6)
    if wrong or np.any(err):
        raise AssertionError('Zero-wire arithmetic null failed')
    expected = (np.einsum('tbr,b->tr', x.astype(np.float64), ACT) @
                np.einsum('por,p->or', w.astype(np.float64), COEF).T)
    counts = np.einsum('tbpo,b,p->to', d['n'], ACT, COEF)
    np.testing.assert_array_equal(expected, counts)
    # Alter held-out true labels with frozen calibration: predicted arithmetic
    # must remain invariant. Ground truth may score predictions, never form them.
    sense = direct_seen(d['a'], 5.)
    ee, unused, frozen = decode(d, sense, d['centroid'], 6)
    fake = dict(d)
    fake['n'] = d['n']+1.
    ef, unused, unused2 = decode(fake, sense, d['centroid'], 6, frozen)
    fake_truth = np.einsum('tbpo,b,p->to', fake['n'], ACT, COEF)
    np.testing.assert_array_equal(ee+counts, ef+fake_truth)
    perm = rng.permutation(32)
    alternate = circuit_data(x, w, perm)
    np.testing.assert_array_equal(d['n'], alternate['n'])
    if d['read_count'] != alternate['read_count']:
        raise AssertionError('Permutation changed physical group activation count')
    # Neural adapter arithmetic tested independently of any trained checkpoint.
    state = {}
    for i, shape in enumerate(((128, 784), (64, 128), (10, 64)), 1):
        state['fc%d.weight' % i] = rng.normal(0., .1, shape).astype(np.float32)
        state['fc%d.bias' % i] = rng.normal(0., .1, shape[0]).astype(np.float32)
    layers = quantized_state(state, [1., 8., 12.])
    xi = rng.randint(0, 256, (4, 784))
    perturb = rng.randint(-100, 100, (4, 8)).astype(np.float64)
    for error in (None, perturb):
        reference = xi.copy()
        for i, layer in enumerate(layers):
            dot = reference.astype(np.int64).dot(layer['w'].T).astype(np.float64)
            if i == 0 and error is not None:
                dot[:, :8] += error
            y = dot*(layer['a_scale']*layer['ws'])+layer['bias']
            if i < 2:
                reference = np.clip(np.rint(np.maximum(y, 0.)/layers[i+1]['a_scale']),
                                    0., 255.).astype(np.int64)
        np.testing.assert_array_equal(logits_from_fc1(xi, layers, error), y)
    print('E25_SELFTEST_PASS: sparse/segment/full swaps; independent KCL; R0; W4A8', flush=True)
    print('SELFTEST IS CONSTRUCTED SOFTWARE, NOT GF OR INFERENCE', flush=True)


def benchmark(out, events, proposals):
    rng = np.random.RandomState(250512)
    rows = []
    for b in (32, 64, 128, 256):
        # Explicit synthetic sparsity, no claim this is representative of MRAM workload.
        a = rng.choice([0., GAP, GP], size=(events, b), p=[.8, .1, .1])
        pairs = [rng.choice(b, 2, replace=False).tolist() for j in range(proposals)]
        for backend in ('full', 'sparse', 'segment'):
            t0 = time.perf_counter()
            oracle = SwapOracle(a, 5., backend)
            setup = time.perf_counter()-t0
            t0 = time.perf_counter()
            checksum = 0.
            for j, (p, q) in enumerate(pairs):
                prop = oracle.trial(p, q)
                checksum += float(prop['seen'].sum())
                if j % 4 == 0:
                    oracle.accept(prop)
            seconds = time.perf_counter()-t0
            row = dict(rows=b, events=events, proposals=proposals, backend=backend,
                       setup_seconds=setup, query_seconds=seconds,
                       total_seconds=setup+seconds, cache_bytes=oracle.cache_bytes,
                       checksum=checksum)
            rows.append(row)
            print('BENCH', b, backend, 'setup', round(setup, 5), 'queries', round(seconds, 5), flush=True)
        vals = [v['checksum'] for v in rows[-3:]]
        if not np.allclose(vals, vals[0], rtol=2e-12, atol=1e-14):
            raise AssertionError('Benchmark backends disagree')
    write_json(out, {'evidence': 'CONSTRUCTED SOFTWARE BENCHMARK, NOT HARDWARE', 'results': rows})


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def quantized_state(state, clips):
    """Same audited Stage4A W4A8 arithmetic as experiments/frozen_mnist.py."""
    shapes = ((128, 784), (64, 128), (10, 64))
    layers = []
    for i, shape in enumerate(shapes, 1):
        w = state['fc%d.weight' % i]
        bias = state['fc%d.bias' % i]
        if w.shape != shape or bias.shape != (shape[0],) or w.dtype != np.float32:
            raise ValueError('Frozen neural parameter shape/dtype mismatch')
        ws = max(float(np.abs(w).max())/7., 1e-12)
        wi = np.clip(np.rint(w.astype(np.float64)/ws), -7, 7).astype(np.int64)
        layers.append(dict(w=wi, ws=ws, bias=bias.astype(np.float64),
                           a_scale=float(clips[i-1])/255.))
    return layers


def logits_from_fc1(x, layers, error=None):
    layer = layers[0]
    exact = np.dot(x, layer['w'].T).astype(np.float64)
    if error is not None:
        exact[:, :error.shape[1]] += error
    y = exact*(layer['a_scale']*layer['ws'])+layer['bias']
    for layer in layers[1:]:
        y = np.maximum(y, 0.)
        xi = np.clip(np.rint(y/layer['a_scale']), 0., 255.).astype(np.int64)
        y = np.dot(xi, layer['w'].T).astype(np.float64)*(layer['a_scale']*layer['ws'])+layer['bias']
    return y


def task_resources(args, packet):
    if not args.task_auto and not args.task_model_dir:
        return None, {'status': 'NOT_REQUESTED', 'network_result_available': False}
    model_sha = '455662670e868006c0b3d375f850336fc82f036190a493ea236f2b349034d485'
    quant_sha = 'fea186c411a52ee4bd3e5ca62042cfb3393fc8f9f2662478f1749e1bfa6e5adf'
    homes = [Path.home()/'MRAM_FYP_Overleaf', Path.home()/'mram_fyp', Path.home()/'MRAM_Path_Finding']
    candidates = ([Path(args.task_model_dir).expanduser()] if args.task_model_dir else
                  [h/'outputs/mnist_stage4a_v3_15ep' for h in homes])
    directory = next((v for v in candidates if (v/'fp32_checkpoint.pt').is_file() and
                      (v/'frozen_quantization.json').is_file()), None)
    if directory is None:
        if args.task_model_dir:
            raise ValueError('Explicit task model directory lacks checkpoint/quantizer')
        return None, {'status': 'BLOCKED_MISSING_FROZEN_CHECKPOINT',
                      'network_result_available': False,
                      'next_action': 'Rerun saved errors with --task-model-dir; no new mapping search needed.'}
    ck, qq = directory/'fp32_checkpoint.pt', directory/'frozen_quantization.json'
    if digest(ck) != model_sha or digest(qq) != quant_sha:
        raise ValueError('Task resources differ from frozen E01 checkpoint/quantizer')
    try:
        import torch
    except ImportError:
        if args.task_model_dir:
            raise
        return None, {'status': 'BLOCKED_TORCH_UNAVAILABLE', 'network_result_available': False}
    # Only the hash-pinned student checkpoint is loaded; no unsafe fallback.
    checkpoint = torch.load(str(ck), map_location='cpu', weights_only=True)
    state = {k: v.detach().cpu().numpy() for k, v in checkpoint['model'].items()}
    quant = json.loads(qq.read_text())
    if not quant.get('frozen') or quant.get('checkpoint_sha256') != model_sha:
        raise ValueError('Frozen quantization contract mismatch')
    layers = quantized_state(state, quant['quantizer_config']['W4A8']['activation_clips'])
    # Packet itself contains all FC1 integer inputs and all W4 planes. No image
    # download/retraining/resplitting is needed to propagate FC1 errors downstream.
    xdev = np.zeros((args.dev_parents, 784), dtype=np.int64)
    prior_dev_ids = None
    for start in (0, 256, 512, 768):
        xc, xd, w, unused, cids, dids = load_packet(packet, start, 128, args.cal_parents,
                                                  args.dev_parents, args.groupings.split(',')[0])
        if prior_dev_ids is not None:
            np.testing.assert_array_equal(prior_dev_ids, dids)
        prior_dev_ids = dids.copy()
        count = min(256, 784-start)
        ints = np.einsum('tbr,b->tr', xd.astype(np.float64), ACT).astype(np.int64)
        xdev[:, start:start+count] = ints[:, :count]
        wi = np.einsum('por,p->or', w.astype(np.float64), COEF).astype(np.int64)
        np.testing.assert_array_equal(wi[:, :count], layers[0]['w'][:, start:start+count])
    clean = logits_from_fc1(xdev, layers)
    labels = None
    label_candidates = ([Path(args.task_labels).expanduser()] if args.task_labels else
                        [h/'data/mnist/MNIST/raw/train-labels-idx1-ubyte' for h in homes])
    label_file = next((v for v in label_candidates if v.is_file()), None)
    if label_file is not None:
        if digest(label_file) != '65a50cbbf4e906d70832878ad85ccda5333a97f0f4c3dd2ef09a8a9eef7101c5':
            raise ValueError('Labels differ from frozen E01 resource receipt')
        raw = label_file.read_bytes()
        magic, count = struct.unpack('>II', raw[:8])
        if magic != 2049 or len(raw) != count+8:
            raise ValueError('Invalid MNIST label IDX')
        labels = np.frombuffer(raw, np.uint8, offset=8)[dids]
    return dict(x=xdev, layers=layers, clean=clean, labels=labels), {
        'status': 'READY', 'network_result_available': True,
        'checkpoint_sha256': model_sha, 'quantization_sha256': quant_sha,
        'labels_available': labels is not None,
        'scope': 'Only specified FC1 rows/output channels receive constructed circuit errors; FC2/FC3 ideal W4A8.'}


def task_score(task, error):
    clean = task['clean']
    noisy = logits_from_fc1(task['x'], task['layers'], error)
    ref, pred = np.argmax(clean, axis=1), np.argmax(noisy, axis=1)
    correct_margin = noisy[np.arange(len(noisy)), ref]-np.max(
        np.where(np.eye(10, dtype=bool)[ref], -np.inf, noisy), axis=1)
    result = dict(parents=len(error), clean_prediction_disagreements=int(np.count_nonzero(ref != pred)),
                  logit_mse=float(np.mean((noisy-clean)**2)),
                  mean_reference_class_margin=float(correct_margin.mean()))
    if task['labels'] is not None:
        good, after = ref == task['labels'], pred == task['labels']
        result.update(clean_correct=int(good.sum()), perturbed_correct=int(after.sum()),
                      clean_correct_now_wrong=int(np.count_nonzero(good & ~after)),
                      clean_wrong_now_correct=int(np.count_nonzero(~good & after)))
    return result


def task_only(args):
    previous = Path(args.task_only)
    result = json.loads((previous/'results.json').read_text())
    options = result['parameters'].copy()
    for key in ('task_model_dir', 'task_labels', 'packet'):
        if getattr(args, key):
            options[key] = getattr(args, key)
    options['task_auto'] = True
    actual = SimpleNamespace(**options)
    verify_packet(Path(actual.packet))
    task, status = task_resources(actual, Path(actual.packet))
    if task is None:
        raise ValueError('Neural evaluation unavailable: '+status['status'])
    rows = []
    with np.load(str(previous/'dev_fc1_integer_errors.npz'), allow_pickle=False) as errors:
        for rec in result['aggregate']:
            key = '%s__%s__R%s' % (rec['grouping'], rec['method'], str(rec['r_assumed']).replace('.', '_'))
            rows.append(dict(grouping=rec['grouping'], method=rec['method'],
                             r_assumed=rec['r_assumed'], network=task_score(task, errors[key])))
    write_json(args.out, dict(evidence='Constructed passive FC1 read error propagated through frozen W4A8 network',
                             prior_results_sha256=digest(previous/'results.json'),
                             error_arrays_sha256=digest(previous/'dev_fc1_integer_errors.npz'),
                             source_sha256=digest(__file__), task_resources=status, results=rows))
    print('E25_TASK_ONLY_OUTPUT', args.out, flush=True)


def run(args):
    packet, out = Path(args.packet), Path(args.out)
    if out.exists():
        raise ValueError('Output exists; choose a new directory')
    out.mkdir(parents=True)
    verify_packet(packet)
    task, task_status = task_resources(args, packet)
    print('TASK_RESOURCE_STATUS', task_status['status'], flush=True)
    b, r = args.group_rows, args.train_r
    if 256 % b or args.cal_parents < 8 or not (1 <= args.search_outputs <= args.outputs <= 128):
        raise ValueError('Invalid group size/parent/output configuration')
    nfit = args.cal_parents//2
    report = {'experiment': 'E25_INCREMENTAL_DECODED_ERROR_MAPPING',
              'evidence': 'REAL FROZEN E01 FC1 BITPLANES + ASSUMED EXACT PASSIVE LADDER',
              'physical_GF_or_PEX': False, 'network_classification': False,
              'packet_sha256': digest(packet), 'source_sha256': digest(__file__),
              'python': platform.python_version(), 'numpy': np.__version__,
              'parameters': vars(args), 'decoder_fit_cal_parents': nfit,
              'swap_selection_cal_parents': args.cal_parents-nfit,
              'dev_previously_inspected': True,
              'task_resources': task_status,
              'calibration': 'per-group m+centroid; first CAL half only; same all methods',
              'notes': ['No GF-calibrated read law, transistor nonlinearity or physical ADC.',
                        'Equal proposals controls search trajectory; CPU is reported, not assumed equal.',
                        'Wire objective and backend changes are distinct hypotheses.',
                        'No faithful NanoCiM implementation or novelty pass.',
                        'No chip variation; this is deterministic placement, not a reliability probability.'],
              'blocks': [], 'aggregate': []}
    row_starts = [int(v) for v in args.row_starts.split(',')]
    groups = args.groupings.split(',')
    rvals = [float(v) for v in args.eval_rs.split(',')]
    if len(set(row_starts)) != len(row_starts) or not set(row_starts).issubset({0, 256, 512, 768}):
        raise ValueError('Use unique frozen row starts from 0,256,512,768')
    if r <= 0 or any(v < 0 for v in rvals) or args.proposals < 1:
        raise ValueError('Require positive train R/proposals and nonnegative evaluation R')
    aggregate = {}
    parent_rows = []
    saved_errors = {}
    for grouping in groups:
        for row_start in row_starts:
            xc, xd, w, base, calids, devids = load_packet(packet, row_start, args.outputs,
                                                       args.cal_parents, args.dev_parents, grouping)
            begin = time.perf_counter()
            orders, graphs = graph_orders(xc, w, base, b, args.graph_passes)
            graph_seconds = time.perf_counter()-begin
            records = []
            # Candidate prefix is predeclared; output selection NEVER uses DEV.
            trainw = w[:, :args.search_outputs]
            prior_order, prior_rec = None, None
            for backend in args.backends.split(','):
                order, rec = search(xc, trainw, base, orders['camp_light'], graphs,
                                    b, r, nfit, args.proposals, args.seed, backend)
                if prior_order is not None:
                    if not np.array_equal(prior_order, order):
                        raise AssertionError('Backends selected different mappings; inspect floating-point ties')
                    if [t[:4] for t in rec['accepted_trajectory']] != [t[:4] for t in prior_rec['accepted_trajectory']]:
                        raise AssertionError('Backends took different acceptance decisions')
                prior_order, prior_rec = order, rec
                orders['decoded_'+backend] = order
                rec['method'] = 'decoded_'+backend
                records.append(rec)
                print('SEARCH', grouping, row_start, backend, 'accepted', rec['accepted'],
                      'CAL selection MSE', round(rec['cal_selection_mse'], 3),
                      'seconds', round(rec['search_seconds_including_setup'], 3), flush=True)
            qorder, qrec = search(xc, trainw, base, orders['camp_light'], graphs,
                                 b, r, nfit, args.proposals, args.seed, 'sparse', 'wire_q')
            orders['q_continue'] = qorder
            qrec['method'] = 'q_continue'
            records.append(qrec)
            block = dict(grouping=grouping, row_start=row_start,
                         graph_setup_seconds=graph_seconds, searches=records,
                         maps={k: v.tolist() for k, v in orders.items()}, evaluations=[])
            print('EVALUATE', grouping, row_start, 'outputs', args.outputs, flush=True)
            for rr in rvals:
                expected_reads = None
                for method, order in orders.items():
                    if not all(np.array_equal(np.sort(order[s:s+b]), np.sort(base[s:s+b]))
                               for s in range(0, 256, b)):
                        raise AssertionError('Fixed membership violated')
                    ce, beta, cw, cr = group_errors(xc, w, order, b, rr, nfit)
                    de, unused, dw, dr = group_errors(xd, w, order, b, rr, nfit, beta)
                    if expected_reads is None:
                        expected_reads = (cr, dr)
                    if expected_reads != (cr, dr):
                        raise AssertionError('Mapping changed nonempty read count')
                    ctotal, dtotal = np.sum(ce, 0), np.sum(de, 0)
                    if rr == 0 and (np.any(ctotal) or np.any(dtotal)):
                        raise AssertionError('R0 decoded arithmetic is not invariant')
                    result = dict(method=method, r_assumed=rr, cal_reads=cr, dev_reads=dr,
                                  cal_fit_mse=float(np.mean(ctotal[:nfit]**2)),
                                  cal_selection_mse=float(np.mean(ctotal[nfit:]**2)),
                                  dev_arithmetic_mse=float(np.mean(dtotal**2)),
                                  dev_wrong_counts=dw, dev_parent_output_count=int(dtotal.size))
                    block['evaluations'].append(result)
                    key = (grouping, method, rr)
                    if key not in aggregate:
                        aggregate[key] = {'cal': np.zeros_like(ctotal), 'dev': np.zeros_like(dtotal),
                                          'cal_reads': 0, 'dev_reads': 0, 'wrong': 0}
                    ag = aggregate[key]
                    ag['cal'] += ctotal
                    ag['dev'] += dtotal
                    ag['cal_reads'] += cr
                    ag['dev_reads'] += dr
                    ag['wrong'] += dw
                    print('DEV', grouping, row_start, method, 'R', rr,
                          'MSE', round(result['dev_arithmetic_mse'], 3), 'wrong', dw, flush=True)
            report['blocks'].append(block)
            write_json(out/('block_%s_%04d.json' % (grouping, row_start)), block)
    for (grouping, method, rr), ag in aggregate.items():
        rec = dict(grouping=grouping, method=method, r_assumed=rr,
                   rows_included=row_starts, outputs=args.outputs,
                   full_fc1_arithmetic=(set(row_starts) == {0, 256, 512, 768} and args.outputs == 128),
                   cal_selection_mse=float(np.mean(ag['cal'][nfit:]**2)),
                   dev_arithmetic_mse=float(np.mean(ag['dev']**2)),
                   dev_arithmetic_mae=float(np.mean(np.abs(ag['dev']))),
                   dev_wrong_counts=ag['wrong'], cal_reads=ag['cal_reads'], dev_reads=ag['dev_reads'])
        report['aggregate'].append(rec)
        key_text = '%s__%s__R%s' % (grouping, method, str(rr).replace('.', '_'))
        saved_errors[key_text] = ag['dev']
        if task is not None:
            rec['network'] = task_score(task, ag['dev'])
            report['network_classification'] = True
            print('NETWORK', grouping, method, 'R', rr, rec['network'], flush=True)
        for parent, squared in zip(devids, np.mean(ag['dev']**2, axis=1)):
            parent_rows.append([grouping, method, rr, int(parent), float(squared)])
    with (out/'dev_parent_mse.csv').open('x', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['grouping', 'method', 'r_assumed', 'parent_id', 'arithmetic_mse'])
        writer.writerows(parent_rows)
    write_json(out/'results.json', report)
    np.savez_compressed(str(out/'dev_fc1_integer_errors.npz'), **saved_errors)
    print('E25_OUTPUT', out/'results.json', flush=True)
    print('EVIDENCE: constructed passive readout; no GF, PEX or novelty pass.', flush=True)
    print('ACTUAL_FROZEN_NETWORK_EVALUATED', task is not None, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--selftest', action='store_true')
    p.add_argument('--benchmark', action='store_true')
    p.add_argument('--packet')
    p.add_argument('--out', required=False)
    p.add_argument('--events', type=int, default=2048)
    p.add_argument('--proposals', type=int, default=64)
    p.add_argument('--row-starts', default='0')
    p.add_argument('--groupings', default='zero_rate_sorted,car_alpha_0')
    p.add_argument('--group-rows', type=int, default=32)
    p.add_argument('--outputs', type=int, default=8)
    p.add_argument('--search-outputs', type=int, default=8)
    p.add_argument('--cal-parents', type=int, default=128)
    p.add_argument('--dev-parents', type=int, default=256)
    p.add_argument('--graph-passes', type=int, default=7)
    p.add_argument('--train-r', type=float, default=5.)
    p.add_argument('--eval-rs', default='0,1,5,10')
    p.add_argument('--seed', type=int, default=250511)
    p.add_argument('--backends', default='full,sparse,segment')
    p.add_argument('--task-auto', action='store_true')
    p.add_argument('--task-model-dir')
    p.add_argument('--task-labels')
    p.add_argument('--task-only', help='Saved E25 directory; propagate saved errors without repeating search')
    args = p.parse_args()
    if args.selftest:
        selftest()
    elif args.task_only:
        if not args.out:
            p.error('--task-only requires --out JSON')
        task_only(args)
    elif args.benchmark:
        if not args.out:
            p.error('--benchmark requires --out')
        benchmark(args.out, args.events, args.proposals)
    else:
        if not args.packet or not args.out:
            p.error('Run requires --packet and --out')
        run(args)


if __name__ == '__main__':
    main()
