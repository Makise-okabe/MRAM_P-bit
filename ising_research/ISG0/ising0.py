#!/usr/bin/env python3
"""Independent ISG-0 four-spin readout/Ising compatibility diagnostic.

IMPORTANT: demo data are deliberately SYNTHETIC mathematical fixtures,
not GF, Spectre, PEX, device-noise, energy, or hardware results.
Requires Python >=3.9 and NumPy. No repo/API/network dependencies.
"""
import argparse
import csv
import itertools
import json
import math
from pathlib import Path
import numpy as np

N = 4
STATES = list(itertools.product([-1, 1], repeat=N))
IDX = {s: i for i, s in enumerate(STATES)}
PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]


def check_config(cfg):
    if cfg.get('n') != N: raise ValueError('ISG-0 requires exactly n=4')
    if cfg.get('field_units') != 'dimensionless_Ising_field':
        raise ValueError('Expected field_units=dimensionless_Ising_field. Convert raw currents using a validated signed read operator first.')
    J = np.asarray(cfg['J'], dtype=float)
    b = np.asarray(cfg['b'], dtype=float)
    beta = float(cfg['beta'])
    if J.shape != (N, N) or b.shape != (N,) or not np.all(np.isfinite(J)) or not np.all(np.isfinite(b)):
        raise ValueError('Expected finite 4x4 J and four biases')
    if beta <= 0 or not math.isfinite(beta): raise ValueError('beta must be finite and positive')
    if not np.allclose(J, J.T, atol=1e-12) or not np.allclose(np.diag(J), 0, atol=1e-12):
        raise ValueError('Intended J must be symmetric with zero diagonal')
    return J, b, beta


def h_ideal(J, b, s, i):
    return float(b[i] + np.dot(J[i], np.asarray(s, dtype=float)))


def q_feature(s, i):
    # Illustrative, predeclared spatial pair-interaction feature (not GF-calibrated).
    js = [j for j in range(N) if j != i]
    return sum(s[j]*s[k]/(1.0+abs(j-k)) for j, k in itertools.combinations(js, 2))


def sig(x):
    if x >= 0:
        z = math.exp(-x)
        return 1/(1+z)
    z = math.exp(x)
    return z/(1+z)


def make_fixture(out):
    J = np.array([[0,.80,-.50,0], [.80,0,.60,-.70], [-.50,.60,0,.45], [0,-.70,.45,0]],dtype=float)
    b = np.array([.18,-.12,.06,-.16])
    d_sym = np.zeros((N,N))
    for (i,j),v in {(0,1):.07,(0,2):-.05,(0,3):-.02,(1,2):.09,(1,3):-.06,(2,3):.03}.items():
        d_sym[i,j]=d_sym[j,i]=v
    d_asym = np.zeros((N,N))
    for (i,j),v in {(0,1):.15,(0,2):-.10,(0,3):.06,(1,2):-.07,(1,3):.12,(2,3):-.08}.items():
        d_asym[i,j]=v
        d_asym[j,i]=-v
    shift=np.array([.04,-.03,.02,-.05])
    lam=np.array([.20,-.17,.15,-.13])
    cfgbase={'n':4,'beta':1.30,'J':J.tolist(),'b':b.tolist(),
             'source':'SYNTHETIC_MATHEMATICAL_FIXTURE',
             'field_units':'dimensionless_Ising_field',
             'warning':'NOT actual GF MRAM/Spectre data; no physical claims can be drawn.'}
    scenarios = ['ideal','fixed_symmetric','fixed_asymmetric','asymmetric_nonlinear']
    out.mkdir(parents=True,exist_ok=True)
    for name in scenarios:
        cfg=dict(cfgbase,scenario=name)
        (out/f'{name}_config.json').write_text(json.dumps(cfg,indent=2)+'\n')
        with (out/f'{name}_fields.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['state','spin_index','measured_field'])
            w.writeheader()
            for s in STATES:
                for i in range(N):
                    y=h_ideal(J,b,s,i)
                    if name!='ideal':
                        y += shift[i] + float(np.dot(d_sym[i],np.array(s)))
                    if name in ('fixed_asymmetric','asymmetric_nonlinear'):
                        y += float(np.dot(d_asym[i],np.array(s)))
                    if name=='asymmetric_nonlinear':
                        y += lam[i]*q_feature(s,i)
                    w.writerow({'state':'|'.join(map(str,s)), 'spin_index':i,
                                'measured_field':f'{y:.15g}'})
    return scenarios


def read_fields(path):
    raw={}
    with Path(path).open(newline='') as f:
        reader=csv.DictReader(f)
        required={'state','spin_index','measured_field'}
        if not required.issubset(reader.fieldnames or []): raise ValueError(f'CSV needs {required}')
        for row in reader:
            s=tuple(int(x) for x in row['state'].split('|'))
            i=int(row['spin_index'])
            y=float(row['measured_field'])
            if s not in IDX or i not in range(N) or not math.isfinite(y):
                raise ValueError(f'Invalid state/spin/field: {row}')
            if (s,i) in raw: raise ValueError(f'Duplicate row for {s}, spin {i}')
            raw[s,i]=y
    if len(raw)!=64: raise ValueError(f'Expected exactly 64 state/spin rows, got {len(raw)}')
    for s in STATES:
        for i in range(N):
            if (s,i) not in raw: raise ValueError(f'Missing {s} spin {i}')
    ycond={}
    self_delta=[]
    for i in range(N):
        for s in STATES:
            if s[i]!=-1: continue
            t=list(s); t[i]=1; t=tuple(t)
            v0,v1=raw[s,i],raw[t,i]
            self_delta.append(abs(v1-v0))
            ycond[(i,tuple(s[j] for j in range(N) if j!=i))]=(v0+v1)/2
    return raw,ycond,max(self_delta)


def context_to_state(i,context,si=-1):
    it=iter(context)
    return tuple(si if j==i else next(it) for j in range(N))


def yfield(ycond,i,s):
    return ycond[(i,tuple(s[j] for j in range(N) if j!=i))]


def transitions(ycond,beta,order=None):
    P=np.zeros((16,16),dtype=float)
    for s in STATES:
        a=IDX[s]
        indices=range(N) if order is None else order
        for i in indices:
            p=sig(2*beta*yfield(ycond,i,s))
            for sign,prob in [(-1,1-p),(1,p)]:
                t=list(s); t[i]=sign; t=tuple(t)
                P[a,IDX[t]]+=prob/(N if order is None else 1)
    return P


def one_spin_transition(ycond,beta,i):
    P=np.zeros((16,16),dtype=float)
    for s in STATES:
        a=IDX[s]; p=sig(2*beta*yfield(ycond,i,s))
        for sign,prob in [(-1,1-p),(1,p)]:
            t=list(s); t[i]=sign
            P[a,IDX[tuple(t)]]+=prob
    return P


def stationary(P):
    # Dense 16-state, no Monte Carlo estimation error: solve (P^T-I)pi=0, sum(pi)=1.
    A=P.T-np.eye(16)
    rhs=np.zeros(16)
    A[-1,:]=1
    rhs[-1]=1
    p=np.linalg.solve(A,rhs)
    if np.min(p)<-1e-10 or not np.isclose(p.sum(),1) or not np.allclose(p@P,p,atol=1e-10):
        raise AssertionError('Stationary distribution failed validation')
    return np.maximum(0,p)/sum(np.maximum(0,p))


def target_distribution(J,b,beta):
    # H(s)=-sum_{i<j}Jij sisj - sum_i b_i si.
    logw=[]
    for s in STATES:
        energy=-sum(J[i,j]*s[i]*s[j] for i,j in PAIRS)-float(np.dot(b,s))
        logw.append(-beta*energy)
    z=np.exp(np.asarray(logw)-max(logw))
    return z/z.sum()


def tv(p,q): return float(.5*np.abs(p-q).sum())

def kl(p,q): return float(np.sum(p*np.log(p/q)))


def curl_stats(ycond,beta):
    defects=[]
    for i,j in PAIRS:
        others=[k for k in range(N) if k not in (i,j)]
        for other_vals in itertools.product([-1,1],repeat=2):
            s=dict(zip(others,other_vals))
            def f(ii, jj, val):
                ss=[s.get(k,-1) for k in range(N)]
                ss[jj]=val
                return yfield(ycond,ii,tuple(ss))
            dji=2*beta*(f(i,j,1)-f(i,j,-1))
            dij=2*beta*(f(j,i,1)-f(j,i,-1))
            defects.append(dji-dij)
    return float(max(map(abs,defects))),float(np.sqrt(np.mean(np.square(defects))))


def feature_row(model,i,s):
    others=[j for j in range(N) if j!=i]
    if model=='symmetric':
        x=[0.]*(N+len(PAIRS))
        x[i]=1.
        for k,(a,b) in enumerate(PAIRS):
            if a==i:x[N+k]=float(s[b])
            elif b==i:x[N+k]=float(s[a])
        return x
    if model in ('directed','directed_plus_q'):
        x=[0.]*(N*(1+N-1)+(N if model=='directed_plus_q' else 0))
        start=i*N
        x[start]=1.
        for k,j in enumerate(others):x[start+1+k]=float(s[j])
        if model=='directed_plus_q': x[N*N+i]=q_feature(s,i)
        return x
    raise ValueError(model)


def calibration_models(ycond,seed=20261105):
    rng=np.random.default_rng(seed)
    train=[]; test=[]
    for i in range(N):
        contexts=list(itertools.product([-1,1],repeat=N-1))
        # Ensure the 6-context train subset identifies the 5-column nonlinear feature basis.
        for attempt in range(1000):
            shuffled=rng.permutation(len(contexts))
            idx=shuffled[:6]
            contexts_train=[contexts[k] for k in idx]
            A=np.array([feature_row('directed_plus_q',i,context_to_state(i,c))[i*N:(i+1)*N]+
                        [q_feature(context_to_state(i,c),i)] for c in contexts_train])
            if np.linalg.matrix_rank(A)==5: break
        else: raise AssertionError('Could not find full-rank training split')
        for k,c in enumerate(contexts):
            entry=(i,context_to_state(i,c),ycond[(i,c)])
            (train if k in set(idx) else test).append(entry)
    errors={}
    for model in ['symmetric','directed','directed_plus_q']:
        X=np.array([feature_row(model,i,s) for i,s,y in train])
        y=np.array([yy for i,s,yy in train])
        coef,*_=np.linalg.lstsq(X,y,rcond=None)
        T=np.array([feature_row(model,i,s) for i,s,yy in test])
        truth=np.array([yy for i,s,yy in test])
        pred=T@coef
        errors[model]={
            'heldout_MAE':float(np.mean(np.abs(pred-truth))),
            'heldout_max_abs_error':float(np.max(np.abs(pred-truth))),
            'train_MAE':float(np.mean(np.abs(X@coef-y))),
            'train_rank':int(np.linalg.matrix_rank(X)),
            'parameters':int(X.shape[1]),
        }
    return errors, {'train_conditional_measurements':len(train),'test_conditional_measurements':len(test),
                    'split_seed':seed}


def analyze(csv_path,config_path,self_tolerance=1e-7):
    cfg=json.loads(Path(config_path).read_text()); J,b,beta=check_config(cfg)
    raw, ycond, selfdep=read_fields(csv_path)
    if selfdep > self_tolerance:
        raise ValueError(f'Target-spin self-dependence {selfdep:.6g} exceeds tolerance {self_tolerance:.6g}; cannot treat reads as Gibbs conditional fields. Investigate separately, do not average away this effect.')
    pi_target=target_distribution(J,b,beta)
    P=transitions(ycond,beta)
    pi=stationary(P)
    ymax,yrms=curl_stats(ycond,beta)
    errors,split=calibration_models(ycond)
    T_f=np.eye(16);T_r=np.eye(16)
    for i in range(N):T_f=T_f@one_spin_transition(ycond,beta,i)
    for i in reversed(range(N)):T_r=T_r@one_spin_transition(ycond,beta,i)
    pi_f=stationary(T_f);pi_r=stationary(T_r)
    probs=[]; ferr=[]
    for i in range(N):
        for context in itertools.product([-1,1],repeat=3):
            s=context_to_state(i,context)
            hw=yfield(ycond,i,s);ideal=h_ideal(J,b,s,i)
            probs.append(abs(sig(2*beta*hw)-sig(2*beta*ideal)))
            ferr.append(abs(hw-ideal))
    detailed_balance_flow=float(.5*np.abs(pi[:,None]*P-pi[None,:]*P.T).sum())
    summary={
      'source':cfg.get('source','UNSPECIFIED'),
      'scenario':cfg.get('scenario','external'),
      'beta':beta,
      'mean_abs_field_error_vs_intended':float(np.mean(ferr)),
      'mean_abs_transition_probability_error':float(np.mean(probs)),
      'stationary_TV_vs_intended':tv(pi_target,pi),
      'stationary_KL_intended_to_implemented':kl(pi_target,pi),
      'max_conditional_compatibility_defect':ymax,
      'rms_conditional_compatibility_defect':yrms,
      'max_target_spin_self_dependence':selfdep,
      'forward_vs_reverse_fixed_scan_TV':tv(pi_f,pi_r),
      'random_scan_stationary_probability_flow':detailed_balance_flow,
      'calibration':errors,
      'split':split,
      'readout_rows':len(raw),
      'warnings':['Results are diagnostics, not proof of a physically viable MRAM Ising architecture.',
                  'A nonzero defect is not sufficient proof that the target stationary distribution is incorrect.',
                  'The q-feature is a pre-specified synthetic stress-test feature, not a demonstrated MRAM correction.',
                  'Field values must be dimensionless calibrated Ising fields; raw amperes are NOT directly valid.']
    }
    return summary


def print_table(summaries):
    print('\nISG-0 mathematical smoke tests — SYNTHETIC FIXTURES ONLY')
    print('Scenario                 Field MAE   Prob MAE     TV(target)   max curl   sym test MAE    directed MAE     +Q MAE')
    for m in summaries:
        c=m['calibration']
        print(f"{m['scenario']:<24} {m['mean_abs_field_error_vs_intended']:<11.5f} "
              f"{m['mean_abs_transition_probability_error']:<12.5f} "
              f"{m['stationary_TV_vs_intended']:<12.5f} "
              f"{m['max_conditional_compatibility_defect']:<10.5f} "
              f"{c['symmetric']['heldout_MAE']:<15.6f} "
              f"{c['directed']['heldout_MAE']:<16.6f} "
              f"{c['directed_plus_q']['heldout_MAE']:.6f}")


def test_synthetic(summaries):
    by={m['scenario']:m for m in summaries}
    assert by['ideal']['stationary_TV_vs_intended']<1e-10
    assert by['ideal']['max_conditional_compatibility_defect']<1e-10
    assert by['fixed_symmetric']['max_conditional_compatibility_defect']<1e-10
    assert by['fixed_symmetric']['calibration']['symmetric']['heldout_MAE']<1e-10
    assert by['fixed_asymmetric']['max_conditional_compatibility_defect']>1e-3
    assert by['fixed_asymmetric']['calibration']['directed']['heldout_MAE']<1e-10
    assert by['asymmetric_nonlinear']['calibration']['directed']['heldout_MAE']>1e-3
    assert by['asymmetric_nonlinear']['calibration']['directed_plus_q']['heldout_MAE']<1e-10
    assert all(m['max_target_spin_self_dependence']<1e-10 for m in summaries)
    assert all(m['readout_rows']==64 for m in summaries)
    print('\nPASS: 10 mathematical diagnostic checks (NOT physical validation).')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='cmd',required=True)
    demo=sub.add_parser('demo',help='Generate and analyze four known synthetic fixtures')
    demo.add_argument('--out',type=Path,default=Path('results/ISG0_SYNTHETIC'))
    analyze_p=sub.add_parser('analyze',help='Analyze externally provided 64-record field measurements')
    analyze_p.add_argument('--fields',type=Path,required=True)
    analyze_p.add_argument('--config',type=Path,required=True)
    analyze_p.add_argument('--out',type=Path,required=True)
    analyze_p.add_argument('--self-tolerance',type=float,default=1e-7,help='Maximum allowed field dependence on previously stored target spin')
    args=p.parse_args()
    if args.cmd=='demo':
        scenarios=make_fixture(args.out)
        ss=[]
        for name in scenarios:
            summ=analyze(args.out/f'{name}_fields.csv',args.out/f'{name}_config.json')
            (args.out/f'{name}_analysis.json').write_text(json.dumps(summ,indent=2)+'\n')
            ss.append(summ)
        print_table(ss)
        test_synthetic(ss)
        (args.out/'summary.json').write_text(json.dumps(ss,indent=2)+'\n')
        print('Saved CSV, configs and audit JSON to',args.out.resolve())
    else:
        summ=analyze(args.fields,args.config,self_tolerance=args.self_tolerance)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(summ,indent=2)+'\n')
        print(json.dumps(summ,indent=2))
        print('Saved:',args.out.resolve())

if __name__=='__main__':main()
