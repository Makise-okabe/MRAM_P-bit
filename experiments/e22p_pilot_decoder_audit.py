#!/usr/bin/env python3
"""E22P: Postprocess E22 pilot currents; decoder-dependence diagnostic.

Python 3.6+ stdlib. No new Spectre, no PDK access. Uses the existing E22
loader and exact source masks. All reference levels / corrections / ADC ranges
fit only on CAL of the current R; none trained on DEV.
E22 is a constructed 32-row line with assumed 0/5 ohm per segment, NOT PEX.
"""
from __future__ import print_function
import argparse
import hashlib
import json
import math
from pathlib import Path
import e22_gf_precision_regime as e22

BITS = (0, 4, 5, 6, 7)
POLICIES = ('nominal_raw', 'nominal_offset', 'nominal_near',
            'perR_centroids', 'perR_near_centroids')
DECODERS = ('reference_code', 'code_center')


def means_by_count(cal, corrected):
    result = []
    for n in range(17):
        vals = [corrected(row) for row in cal if row['n'] == n]
        if len(vals) < 3:
            raise ValueError('Missing 3 CAL masks at n=' + str(n))
        result.append(e22.mean(vals))
    return result


def window(cal, corrected):
    xs = [corrected(r) for r in cal]
    gap = (max(xs) - min(xs)) / 16.
    if gap <= 0 or not math.isfinite(gap):
        raise ValueError('Invalid CAL ADC range')
    return min(xs) - .5 * gap, max(xs) + .5 * gap


def decode(y, references, bits, low, high, decoder):
    if bits == 0:
        return min(range(17), key=lambda n: (abs(references[n] - y), n))
    q = e22.ADC(y, bits, low, high)
    if decoder == 'reference_code':
        return min(range(17),
                   key=lambda n: (abs(e22.ADC(references[n], bits, low, high) - q), n))
    analogue_code_center = low + (q + .5) * (high - low) / float(1 << bits)
    return min(range(17),
               key=lambda n: (abs(references[n] - analogue_code_center), n))


def score(dev, model, bits, decoder):
    refs, low, high, correction = model
    failures = []
    signed = 0
    abs_err = 0
    satlo = sathi = 0
    predictions = {}
    for x in dev:
        y = correction(x)
        if bits:
            satlo += y < low
            sathi += y >= high
        guess = decode(y, refs, bits, low, high, decoder)
        predictions[str(x['id'])] = guess
        signed += guess - x['n']
        abs_err += abs(guess - x['n'])
        if guess != x['n']:
            failures.append(x['id'])
    return {'wrong': len(failures), 'total': len(dev),
            'count_MAE': abs_err / float(len(dev)),
            'signed_count_bias': signed / float(len(dev)),
            'saturated_low': satlo, 'saturated_high': sathi,
            'failed_mask_ids': failures,
            'predictions': predictions}


def compare_predictions(dev, scores4, scores7):
    mistakes4 = set(scores4['failed_mask_ids'])
    mistakes7 = set(scores7['failed_mask_ids'])
    return {'4bit_wrong_7bit_right': len(mistakes4 - mistakes7),
            '4bit_right_7bit_wrong': len(mistakes7 - mistakes4),
            'both_wrong': len(mistakes4 & mistakes7),
            'both_right': len(dev) - len(mistakes4 | mistakes7)}


def selftest():
    levels = [(i + 1) * 1e-6 for i in range(17)]
    lo, hi = .5e-6, 17.5e-6
    for y in (-1e-6, lo, 3.6e-6, 12.78e-6, hi, 20e-6):
        assert e22.ADC(y, 4, lo, hi) == e22.ADC(y, 7, lo, hi) >> 3
    for i, level in enumerate(levels):
        assert decode(level, levels, 0, lo, hi, 'code_center') == i
        assert decode(level, levels, 7, lo, hi, 'code_center') == i
    rows = [{'n': i, 'I': levels[i] + (j - 1) * .01e-6,
             'near': float(j), 'id': 3*i+j} for i in range(17) for j in range(3)]
    assert len(means_by_count(rows, lambda x: x['I'])) == 17
    a, b = window(rows, lambda x: x['I'])
    assert a < min(x['I'] for x in rows) and b > max(x['I'] for x in rows)
    print('E22P_SELFTEST_PASS: 17 CAL levels, ADC nesting, code-centre decoding.')
    print('SELFTEST IS CONSTRUCTED NUMERIC DATA, NOT SPECTRE.')


def audit(path):
    data = json.loads(path.read_text())
    if data.get('status') != 'FINISHED' or data.get('GF_PEX') is not False:
        raise ValueError('Require finished E22 GF non-PEX input')
    allr = e22.nmap(data)
    if 0. not in allr:
        raise ValueError('Must include R0')
    levels0, low0, high0 = e22.calibrate(allr)
    ids0 = {x['id']: x for x in allr[0.]}
    result = {'evidence': 'E22_GF_SPECTRE_CURRENTS_POSTPROCESS_ONLY',
              'input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'original_pilot_R0_reference_window_uA': [low0*1e6, high0*1e6],
              'R0_CAL_nominal_centroids_uA': [v*1e6 for v in levels0],
              'results': {},
              'caveats': [
                  'Single nominal GF access NFET + student MTJ, assumed wire R, no PEX',
                  'Very small 3 CAL and 3 DEV masks per count in pilot',
                  'Per-R 17-level calibration is a strong costly baseline, not free hardware',
                  'DEV had already been analyzed in the E22 pilot; retrospective exploratory',
                  'No ADC analogue noise, settling, device mismatch or energy',
                  'Code-centre decoder versus quantized-reference decoder can differ due to ties']}
    for r in sorted(allr):
        rows = allr[r]
        if {x['id'] for x in rows} != set(ids0):
            raise ValueError('Unpaired E22 mask identities across R')
        for x in rows:
            z = ids0[x['id']]
            if x['n'] != z['n'] or x['split'] != z['split']:
                raise ValueError('Mismatched E22 label/split across R')
        cal = [x for x in rows if x['split'] == 'CAL']
        dev = [x for x in rows if x['split'] == 'DEV']
        if len(cal) < 51 or len(dev) < 51:
            raise ValueError('Expected at least 3 CAL and DEV masks each count')
        slope, near_mean, off = e22.fit_corr(rows, allr[0.])
        functions = {
            'nominal_raw': lambda x: x['I'],
            'nominal_offset': lambda x: x['I']-off,
            'nominal_near': lambda x: x['I']-off-slope*(x['near']-near_mean),
            'perR_centroids': lambda x: x['I'],
            'perR_near_centroids': lambda x: x['I']-slope*(x['near']-near_mean)
        }
        models = {}
        for policy in POLICIES:
            corrected = functions[policy]
            if policy.startswith('nominal_'):
                models[policy] = (levels0, low0, high0, corrected)
            else:
                refs = means_by_count(cal, corrected)
                lo, hi = window(cal, corrected)
                models[policy] = (refs, lo, hi, corrected)
        entry = {
            'R_assumed_ohm_per_segment': r,
            'cal_n': len(cal), 'dev_n': len(dev),
            'CAL_fit_global_offset_uA': off * 1e6,
            'CAL_fit_near_slope_uA': slope * 1e6,
            'policy_results': {}}
        for policy in POLICIES:
            refs, lo, hi, _ = models[policy]
            scores = {}
            for method in DECODERS:
                bybits = {}
                for bits in BITS:
                    bybits[str(bits)] = score(dev, models[policy], bits, method)
                pair = compare_predictions(dev, bybits['4'], bybits['7'])
                scores[method] = {'by_bits': bybits, 'paired_4_vs_7': pair}
                print(' R=%g %-21s %-15s errors (continuous/4/5/6/7): %s' % (
                    r, policy, method, ' '.join('%d/%d' % (
                        bybits[str(b)]['wrong'],len(dev)) for b in BITS)))
                print('    count MAE: %s   SAT(7b)=%d   4right7wrong=%d 4wrong7right=%d' % (
                    ' '.join('%.4f'%bybits[str(b)]['count_MAE'] for b in BITS),
                    bybits['7']['saturated_low']+bybits['7']['saturated_high'],
                    pair['4bit_right_7bit_wrong'],
                    pair['4bit_wrong_7bit_right']))
            entry['policy_results'][policy] = {
                'ADC_window_uA': [lo*1e6, hi*1e6],
                'CAL_centroids_uA': [v*1e6 for v in refs],
                'adjacent_CAL_centroid_inversions': sum(
                    (refs[k+1]-refs[k])*(levels0[-1]-levels0[0]) <= 0
                    for k in range(16)),
                'decoder_results': scores}
        result['results']['R%g'%r] = entry
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', nargs='?', type=Path)
    p.add_argument('--out', type=Path)
    p.add_argument('--selftest', action='store_true')
    args = p.parse_args()
    if args.selftest:
        selftest()
        return
    if not args.source or not args.out:
        p.error('Provide e22_results.json and a unique --out path')
    if not args.source.is_file():
        p.error('Missing E22 JSON: ' + str(args.source))
    if args.out.exists():
        p.error('Refuses overwrite: ' + str(args.out))
    try:
        report = audit(args.source)
    except (ValueError, KeyError, TypeError, AssertionError) as ex:
        p.error(str(ex))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('E22P_OUTPUT', args.out)
    print('Not a novelty result. No PEX/ADC hardware. Do not infer physical BER.')


if __name__ == '__main__':
    main()
