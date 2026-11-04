#!/usr/bin/env python3
"""E24A: Nested-ADC falsification using EXISTING E19 GF Spectre currents.

No Spectre is run. The E19 physical model used an assumed wire R (not PEX).
Two adjacent true count classes (7/8) are available: NOT a full CIM ADC study.
Python 3.6+, standard library only. Keep outputs private, never commit raw data.

Three decision rules per (bit width, full-scale, offset):
  midpoint: recover bin centre and compare with CAL mean-current midpoint.
  cal_fit:  CAL-only best ordered threshold over the ADC output codes.
  inherited: apply the PREVIOUS bit width's fitted threshold to its coarsened
             code; by nesting this MUST reproduce previous cal_fit predictions.
A reported cal_fit or midpoint regression is therefore NOT loss of information.
"""
from __future__ import print_function
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path


def parse_numbers(raw, kind):
    try:
        values = [kind(v.strip()) for v in raw.split(',') if v.strip()]
    except ValueError:
        raise ValueError('Bad comma-separated numeric argument: ' + raw)
    if not values or len(values) != len(set(values)):
        raise ValueError('Empty or repeated argument values: ' + raw)
    return values


def quantize(current_a, bits, offset_a, fullscale_a):
    if not math.isfinite(current_a):
        raise ValueError('Non-finite measured current')
    ncode = 1 << bits
    x = int(math.floor((current_a - offset_a) * ncode / fullscale_a))
    return min(ncode - 1, max(0, x))


def oriented(code, bits, polarity):
    return code if polarity == 1 else (1 << bits) - 1 - code


def classify(code, bits, polarity, threshold, labels):
    return labels[1] if oriented(code, bits, polarity) >= threshold else labels[0]


def analog_mean_midpoint(cal, labels):
    means = []
    for n in labels:
        xs = [c['current_A'] for c in cal if c['true_n'] == n]
        if not xs:
            raise ValueError('CAL missing class ' + str(n))
        means.append(sum(xs) / len(xs))
    if means[1] == means[0]:
        raise ValueError('Equal CAL means: cannot choose current polarity')
    return (means[0] + means[1]) / 2., 1 if means[1] > means[0] else -1


def midpoint_predict(code, bits, offset, fs, midpoint, polarity, labels):
    # Reconstructed code centre, not analogue truth; fixed CAL threshold.
    reconstructed = offset + (code + 0.5) * fs / float(1 << bits)
    return labels[1] if polarity * (reconstructed - midpoint) >= 0. else labels[0]


def fit_code_threshold(cal, bits, offset, fs, labels, midpoint, polarity):
    size = 1 << bits
    calcodes = [(quantize(c['current_A'], bits, offset, fs), c['true_n']) for c in cal]
    # A threshold 0 or size represents always-high / always-low, respectively.
    def physical_edge(k):
        return offset + (k if polarity == 1 else size - k) * fs / size
    candidates = []
    for k in range(size + 1):
        err = sum(classify(q, bits, polarity, k, labels) != n for q, n in calcodes)
        candidates.append((err, abs(physical_edge(k) - midpoint), k))
    err, _, k = min(candidates)
    return {'k': k, 'cal_errors': err, 'physical_boundary_uA': physical_edge(k) * 1e6}


def score(cases, bits, offset, fs, labels, midpoint, polarity, fitted, prior):
    counts = {'midpoint': 0, 'cal_fit': 0, 'inherited': 0}
    fails = {'midpoint': [], 'cal_fit': [], 'inherited': []}
    sat_lo = sat_hi = 0
    adc_margin = []
    for c in cases:
        cur = c['current_A']
        q = quantize(cur, bits, offset, fs)
        sat_lo += cur < offset
        sat_hi += cur >= offset + fs
        pred = {
            'midpoint': midpoint_predict(q, bits, offset, fs, midpoint, polarity, labels),
            'cal_fit': classify(q, bits, polarity, fitted['k'], labels),
        }
        if prior is not None:
            old_bits, old_fit = prior
            old_q = q >> (bits - old_bits)
            direct_old_q = quantize(cur, old_bits, offset, fs)
            if old_q != direct_old_q:
                raise AssertionError('Nested-quantizer identity broken')
            pred['inherited'] = classify(old_q, old_bits, polarity, old_fit['k'], labels)
        else:
            pred['inherited'] = pred['cal_fit']
        for name, value in pred.items():
            if value != c['true_n']:
                counts[name] += 1
                fails[name].append(c['case_id'])
        if offset < cur < offset + fs:
            z = (cur - offset) * (1 << bits) / fs
            adc_margin.append(min(z - math.floor(z), math.ceil(z) - z) *
                              fs * 1e6 / (1 << bits))
    return {'errors': counts, 'failing_case_ids': fails, 'dev_n': len(cases),
            'dev_saturated_low': sat_lo, 'dev_saturated_high': sat_hi,
            'min_distance_to_any_adc_edge_uA':
                min(adc_margin) if adc_margin else None}


def audited_rows(input_path):
    raw = input_path.read_bytes()
    d = json.loads(raw.decode('utf-8'))
    if d.get('run_state') != 'FINISHED':
        raise ValueError('E19 run incomplete: ' + str(input_path))
    if int(d['config']['rows']) != 32:
        raise ValueError('Expected E19 32-row demonstrator, not another array')
    profiles = {int(p['id']): p for p in d['profiles']}
    if len(profiles) != len(d['profiles']):
        raise ValueError('Duplicate E19 profile ids')
    datasets = []
    for name, section in sorted(d['results'].items(),
                                key=lambda kv: float(kv[1]['R_segment_assumed_ohm'])):
        rows = []
        hashes = set()
        for r in section['per_case_currents']:
            ident = int(r['case_id'])
            p = profiles[ident]
            if (r['mask_hash'] != p['mask_hash'] or
                    r['true_n'] != p['true_n'] or
                    r['split'] != p['split']):
                raise ValueError('Current/profile mismatch for case {}'.format(ident))
            if r['mask_hash'] in hashes:
                raise ValueError('Duplicate mask hash within R arm')
            hashes.add(r['mask_hash'])
            n = int(r['true_n'])
            current = float(r['current_A'])
            if not math.isfinite(current):
                raise ValueError('Nonfinite current')
            rows.append({'case_id': ident, 'split': r['split'],
                         'true_n': n, 'current_A': current})
        cal = [x for x in rows if x['split'] == 'CAL']
        dev = [x for x in rows if x['split'] == 'DEV']
        if len(cal) + len(dev) != len(rows):
            raise ValueError('Unsupported split label')
        labels = sorted(set(x['true_n'] for x in rows))
        if len(labels) != 2 or labels[1] - labels[0] != 1:
            raise ValueError('E24A requires two adjacent labels')
        if any(not any(x['true_n'] == n for x in part)
               for part in (cal, dev) for n in labels):
            raise ValueError('Missing a class in CAL or DEV')
        datasets.append((name, section['R_segment_assumed_ohm'],
                         labels, cal, dev))
    if not datasets:
        raise ValueError('No per-R results')
    return hashlib.sha256(raw).hexdigest(), datasets


def evaluate_file(path, bits_list, fs_list, offset_list):
    digest, datasets = audited_rows(path)
    result = {'input_sha256': digest, 'source_run': path.parent.name,
              'resistance_arms': {}}
    for name, resistance, labels, cal, dev in datasets:
        mid, polarity = analog_mean_midpoint(cal, labels)
        item = {'assumed_R_ohm_per_segment': resistance,
                'cal_n': len(cal), 'dev_n': len(dev), 'labels': labels,
                'cal_mean_midpoint_uA': mid * 1e6, 'polarity': polarity,
                'sweeps': []}
        for fs_uA in fs_list:
            for offset_uA in offset_list:
                fs = fs_uA * 1e-6
                off = offset_uA * 1e-6
                previous = None
                widths = []
                for b in bits_list:
                    fitted = fit_code_threshold(cal, b, off, fs, labels, mid, polarity)
                    scores = score(dev, b, off, fs, labels, mid, polarity,
                                   fitted, previous)
                    cal_low = sum(x['current_A'] < off for x in cal)
                    cal_high = sum(x['current_A'] >= off + fs for x in cal)
                    row = {'bits': b, 'cal_fit': fitted,
                           'cal_saturated_low': cal_low,
                           'cal_saturated_high': cal_high}
                    row.update(scores)
                    if previous is not None:
                        prev_err = widths[-1]['errors']['cal_fit']
                        if scores['errors']['inherited'] != prev_err:
                            raise AssertionError('Inherited errors differ from prior width')
                        row['new_fit_minus_prior_fit_dev_errors'] = (
                            scores['errors']['cal_fit'] - prev_err)
                    widths.append(row)
                    previous = (b, fitted)
                item['sweeps'].append({
                    'fullscale_uA': fs_uA, 'offset_uA': offset_uA, 'widths': widths})
        result['resistance_arms'][name] = item
    return result


def selftest():
    off, fs = 0., 29e-6
    for x in [-1e-6, 0., 1e-6, 10e-6, 27e-6, 29e-6, 32e-6]:
        for b in range(2, 8):
            assert quantize(x, b, off, fs) == (
                quantize(x, b + 1, off, fs) >> 1)
    labels = [7, 8]
    cal = [{'current_A': (12.0 + n * 1.5 + i * 0.12) * 1e-6,
            'true_n': n, 'case_id': i + 10 * n}
           for n in labels for i in range(6)]
    dev = [{'current_A': (12.1 + n * 1.5 + i * 0.11) * 1e-6,
            'true_n': n, 'case_id': i + 10 * n + 100}
           for n in labels for i in range(4)]
    mid, pol = analog_mean_midpoint(cal, labels)
    prev = None
    prev_err = None
    for b in range(3, 9):
        fit = fit_code_threshold(cal, b, off, fs, labels, mid, pol)
        s = score(dev, b, off, fs, labels, mid, pol, fit, prev)
        if prev is not None:
            assert s['errors']['inherited'] == prev_err
        prev, prev_err = (b, fit), s['errors']['cal_fit']
    print('E24A_SELFTEST_PASS: nesting, CAL fit, inherited DEV identity')
    print('SELFTEST USES CONSTRUCTED CURRENTS, NOT NUS GF RESULTS')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('e19_json', nargs='*', type=Path)
    p.add_argument('--out', type=Path)
    p.add_argument('--bits', default='3,4,5,6,7,8')
    p.add_argument('--full-scales-uA', default='28,29')
    p.add_argument('--offsets-uA', default='0')
    p.add_argument('--selftest', action='store_true')
    a = p.parse_args()
    if a.selftest:
        selftest()
        return
    if not a.e19_json or a.out is None:
        p.error('Pass E19 e19_results.json paths and --out path')
    try:
        bits = parse_numbers(a.bits, int)
        fs_list = parse_numbers(a.full_scales_uA, float)
        off_list = parse_numbers(a.offsets_uA, float)
        if sorted(bits) != bits or any(x < 2 or x > 12 for x in bits):
            raise ValueError('bits must be ascending within [2,12]')
        if any(y - x != 1 for x, y in zip(bits, bits[1:])):
            raise ValueError('bits must be adjacent for nesting audit')
        if any(not math.isfinite(x) or x <= 0 for x in fs_list):
            raise ValueError('full scales must be positive and finite')
        if any(not math.isfinite(x) for x in off_list):
            raise ValueError('offsets must be finite')
        if a.out.exists():
            raise ValueError('Refusing overwrite: ' + str(a.out))
        outputs = {}
        for path in a.e19_json:
            if not path.is_file():
                raise ValueError('Missing E19 file: ' + str(path))
            if path.parent.name in outputs:
                raise ValueError('Duplicate input run directory name')
            outputs[path.parent.name] = evaluate_file(path, bits, fs_list, off_list)
    except (KeyError, ValueError, TypeError, AssertionError) as exc:
        p.error(str(exc))
    report = {'evidence_class': 'EXISTING_NUS_GF_CURRENTS_POSTPROCESS_ONLY',
              'limitations': ['Assumed wire resistance, NOT physical array PEX',
                              'Only adjacent count classes 7/8',
                              'No actual ADC hardware, timing, noise or energy',
                              'CAL and DEV were used in prior development'],
              'bits': bits, 'full_scales_uA': fs_list,
              'offsets_uA': off_list, 'runs': outputs}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('E24A: E19 currents only; no new GF Spectre; no PEX or ADC circuitry')
    for run, data in outputs.items():
        print('\nRUN:', run, 'SHA256:', data['input_sha256'])
        for _, arm in data['resistance_arms'].items():
            print(' assumed R:', arm['assumed_R_ohm_per_segment'],
                  'CAL:', arm['cal_n'], 'DEV:', arm['dev_n'])
            for sw in arm['sweeps']:
                widths = sw['widths']
                print('  FS={:g}uA offset={:g}uA: {}'.format(
                    sw['fullscale_uA'], sw['offset_uA'],
                    '  '.join('{}b MID={}/{} FIT={}/{} INH={}/{}{}'.format(
                        w['bits'], w['errors']['midpoint'], w['dev_n'],
                        w['errors']['cal_fit'], w['dev_n'],
                        w['errors']['inherited'], w['dev_n'],
                        ' SAT={}'.format(w['dev_saturated_low']+
                                        w['dev_saturated_high'])
                        if (w['dev_saturated_low']+w['dev_saturated_high']) else '')
                        for w in widths)))
                worse = [w['bits'] for w in widths if
                         w.get('new_fit_minus_prior_fit_dev_errors', 0) > 0]
                if worse:
                    print('   CAL-FIT REGRESSION at bits:', worse,
                          '(inherited decoder is a no-regression control)')
    print('\nE24A_OUTPUT:', a.out)
    print('WARNING: This is a two-count postprocessing diagnostic, NOT a new ADC or novelty pass.')


if __name__ == '__main__':
    main()
