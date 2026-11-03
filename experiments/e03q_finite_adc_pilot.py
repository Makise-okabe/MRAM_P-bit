#!/usr/bin/env python3
"""E03Q: finite-ADC sensitivity of the constructed 256x256 E03M fixture.

No new GF 22FDX data; normalized illustrative currents only. Deterministic,
fixed chip variation across read cycles; independent calibration/evaluation chips.

Exact E03M geometry and policy masks are reconstructed. Per-policy ADC-offset
selection uses an equal calibration set; held-out chip sampling is paired.
Full-group conditional mean correction is an oracle-like illustrative assumption.
The controller is NOT claimed to be implementable in the target macro.
"""
from __future__ import annotations
import argparse, hashlib, json, platform
from pathlib import Path
import numpy as np

CV=0.03
NROWS=NCOLS=256
TRUE_COUNT=8
GROUP_ROWS=64
COEFF=np.tile(np.array([1.,2.]),4)


def fixture(seed=4107,column=0):
    rng=np.random.default_rng(seed)
    x=np.tile(np.repeat([3,1,2,0],[16,16,16,80]),2)
    w=np.empty((256,256),dtype=np.int8)
    for start in range(0,256,8):
        for j in range(256):
            w[start:start+8,j]=rng.permutation([0]*4+[1]*4)
    concentrated,balanced=[],[]
    for base in (0,128):
        a=list(range(base,base+16));b=list(range(base+16,base+32))
        c=list(range(base+32,base+48));d=list(range(base+48,base+128))
        concentrated+=a+d[:48]+b+c+d[48:]
        balanced+=a[:8]+b[:8]+c[:8]+d[:40]
        balanced+=a[8:]+b[8:]+c[8:]+d[40:]
    orders={'concentrated_overlap':np.array(concentrated), 'balanced_overlap':np.array(balanced)}
    sensitivities={}
    for name,o in orders.items():
        assert np.array_equal(np.sort(o),np.arange(256))
        s=np.zeros((8,256),dtype=float)
        for g in range(4):
            ids=o[g*64:(g+1)*64]
            assert int(w[ids,column].sum())==32
            for b in (0,1):
                mask=(x[ids]>>b)&1
                assert int(mask.sum())==16 and int(mask@w[ids,column])==8
                s[2*g+b,ids]=CV*(1+w[ids,column])*(mask-0.25)
        sensitivities[name]=s
    assert np.array_equal(x[orders['balanced_overlap']]@w[orders['balanced_overlap']],x@w)
    return sensitivities,hashlib.sha256(w.tobytes()).hexdigest()


def read_adc(analog, bits, offset, *, vmin=16.,vmax=32.):
    """Unipolar uniform midrise ADC, B bits. Offset shifts both range endpoints.
    Code k = clip(floor((I - vmin - offset)/LSB), 0, 2**B-1).
    Decoder: nearest *quantized* nominal reference among 0..16 P-counts;
    ties choose the smaller count (argmin's first index). Samples on ties
    use the floor code convention. This is a mathematical decoder design,
    not a GF readout circuit specification.
    """
    levels=1<<bits; step=(vmax-vmin)/levels
    lo=vmin+offset
    codes=np.clip(np.floor((analog-lo)/step),0,levels-1).astype(np.int16)
    refs=np.arange(17,dtype=float)+16.
    refcodes=np.clip(np.floor((refs-lo)/step),0,levels-1).astype(np.int16)
    # One calibrated reference code for each logical count. When references
    # collide, tie breaks to smaller count. No knowledge of the true result.
    decode=np.abs(np.arange(levels)[:,None]-refcodes[None,:]).argmin(axis=1)
    return decode[codes].astype(np.int16)-TRUE_COUNT


def ideal_decode(analog):
    return np.clip(np.rint(analog-16),0,16).astype(np.int16)-TRUE_COUNT


def moments(errors):
    e=errors.astype(float)
    mean=e.mean(axis=0);center=e-mean
    cov=center.T@center/len(e)
    reconstructed=e@COEFF
    return {'per_read_error_probability':float(np.mean(e!=0)),
            'per_read_mean':float(np.mean(e)),
            'per_read_marginal_probs':np.mean(e!=0,axis=0).round(8).tolist(),
            'decoded_pair_covariance_per_group':np.round([cov[2*g,2*g+1] for g in range(4)],9).tolist(),
            'reconstructed_bias':float(np.mean(reconstructed)),
            'reconstructed_mse':float(np.mean(reconstructed**2)),
            'reconstructed_mae':float(np.mean(np.abs(reconstructed))),
            'P_abs_error_ge_1':float(np.mean(np.abs(reconstructed)>=1)),
            'P_abs_error_ge_2':float(np.mean(np.abs(reconstructed)>=2)),
            'P_abs_error_ge_4':float(np.mean(np.abs(reconstructed)>=4))}


def simulate(seed, n, s):
    chips=np.random.default_rng(seed).standard_normal((n,256))
    return 24 + chips@s.T  # fixed theta reused across both activation cycles


def fixed_choice(measured,bit,offset):
    return {k:moments(read_adc(x,bit,offset)) for k,x in measured.items()}


def compare_paired(analog_by_mapping, settings):
    """One chip realization per row, same theta across both layouts.

    settings: mapping -> (mode, bits, offset). Compare squared reconstructed
    count error, paired across independent *chips*, not independent reads.
    """
    decoded={}
    for name,(mode,bits,offset) in settings.items():
        x=analog_by_mapping[name]
        e=ideal_decode(x) if mode=='ideal' else read_adc(x,bits,offset)
        decoded[name]=e@COEFF
    a=decoded['concentrated_overlap'];b=decoded['balanced_overlap']
    dif=a*a-b*b
    se=float(np.std(dif,ddof=1)/np.sqrt(len(dif)))
    return {'difference_mse_A_minus_B':float(dif.mean()),
            'paired_se':se,'paired_normal_95pct_ci':[float(dif.mean()-1.96*se),float(dif.mean()+1.96*se)],
            'number_independent_chip_assignments':len(dif)}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',required=True,type=Path)
    p.add_argument('--cal-samples',type=int,default=65536)
    p.add_argument('--eval-samples',type=int,default=131072)
    p.add_argument('--cal-seed',type=int,default=20261110)
    p.add_argument('--eval-seed',type=int,default=20261111)
    args=p.parse_args()
    if args.out.exists():raise SystemExit('Refusing to overwrite existing output')
    sens,whash=fixture()
    cal={k:simulate(args.cal_seed,args.cal_samples,s) for k,s in sens.items()}
    ev={k:simulate(args.eval_seed,args.eval_samples,s) for k,s in sens.items()}
    configs=[(bits,round(phase*(16/(1<<bits)),8),phase) for bits in [4,5,6,7] for phase in [-0.25,0,0.25]]
    out={'experiment':'E03Q_illustrative_finite_adc_sensitivity',
         'evidence_class':'constructed_model_only','new_target_circuit_data':False,
         'new_256x256_PEX':False,'foundry_parameters_used':False,
         'frozen_original_readings_used':False,'physical_validation':False,
         'dataset':{'weight_seed':4107,'weight_sha256':whash,'column':0,'rows':256,'columns':256,
                    'read_groups':4,'rows_per_group':64,'read_cycles':8,'active_rows_per_read':16,
                    'nominal_conductance_values':[1.,2.],'current_CV':CV,
                    'cal_chips':args.cal_samples,'eval_chips':args.eval_samples,
                    'cal_seed':args.cal_seed,'eval_seed':args.eval_seed},
         'decoder':{'type':'uniform midrise ADC then nearest quantized nominal reference',
                    'ranges':'[16+offset,32+offset] normalized current units',
                    'code':'floor & clip','tied_reference':'choose smaller count',
                    'input_count':'16 known selected rows, P count 0..16, nominal I=16+P count',
                    'offset_candidate_phases_in_LSB':[-0.25,0.,0.25],
                    'tuning':'choose offset independently for each mapping/bit-depth by calibration MSE',
                    'calibration':'oracle full-group conditional mean, same for both mappings',
                    'limitations':['not a characterized GF circuit','range conditioned on known 16 selected rows','no shared readout interference','no ADC energy or timing','oracle group calibration assumes full-group mismatch']},
         'ideal':{},'fixed':{},'tuned':{},'paired_tests':{},'note':'All policies see same eval chip random samples. Validation never selects ADC phase.'}
    for name,x in ev.items():out['ideal'][name]=moments(ideal_decode(x))
    out['paired_tests']['ideal']=compare_paired(ev,{k:('ideal',None,None) for k in sens})
    for bits in (4,5,6,7):
        o=fixed_choice(ev,bits,0.0)
        out['fixed'][str(bits)]=o
        out['paired_tests'][f'fixed_{bits}']=compare_paired(ev,{k:('finite',bits,0.) for k in sens})
        choices={}
        for name in sens:
            v=[]
            for b,offset,phase in configs:
                if b!=bits:continue
                m=moments(read_adc(cal[name],b,offset))
                v.append((m['reconstructed_mse'],abs(phase),phase,offset))
            _,_,phase,offset=min(v)
            choices[name]={'offset_phase_LSB':phase,'offset_current':offset,'calibration_mse':min(v)[0],
                           'evaluation':moments(read_adc(ev[name],bits,offset))}
        out['tuned'][str(bits)]=choices
        out['paired_tests'][f'tuned_{bits}']=compare_paired(ev,{k:('finite',bits,choices[k]['offset_current']) for k in sens})
    out['numpy_version']=np.__version__
    out['python_version']=platform.python_version()
    out['interpretation']='No MRAM physical, power, timing, or NN inference claims; finite ADC settings are illustrative.'
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+'\n')
    for mode in ('ideal', 'fixed','tuned'):
        print('\n',mode)
        keys=['ideal'] if mode=='ideal' else ['4','5','6','7']
        for key in keys:
            d=out['ideal'] if mode=='ideal' else out[mode][key]
            a=d['concentrated_overlap'];b=d['balanced_overlap']
            if mode=='tuned':a=a['evaluation'];b=b['evaluation']
            am,bm=a['reconstructed_mse'],b['reconstructed_mse']
            print(key,'A',round(am,6),'B',round(bm,6),'rel_change_pct',round((bm/am-1)*100,3) if am else None,
                  'marg_err',round(a['per_read_error_probability'],6),round(b['per_read_error_probability'],6))
    print('WROTE',args.out)

if __name__=='__main__':main()
