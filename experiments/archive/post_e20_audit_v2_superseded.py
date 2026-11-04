#!/usr/bin/env python3
"""Within-read-group ordering after cheap calibration: bounded discovery screen.

Real private frozen MNIST bitplanes; ASSUMED passive 256-row column. NOT GF/PEX.
Every candidate preserves each read's m, k, true n and skip/read budget exactly.
No neural classification outcome, energy, latency or novelty is inferred.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import time
import zipfile

import numpy as np

EXPECTED_PACKET='400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a'
B=32
ROWS=256
COLS=32                  # First eight complete W4 output channels
FIT_PARENTS=64
SEARCH_PARENTS=64
DEV_PARENTS=256          # Previously inspected development, NOT untouched TEST
SEED=2026110420
RPS=5000.0
RAPS=10000.0
ADC_BITS=8
ADC_HEADROOM=1.1
RIDGE=1e-3


def read_packet(path):
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=EXPECTED_PACKET:
        raise ValueError('Unexpected source packet hash')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        with np.load(io.BytesIO(z.read('rows_0000/array_0/traces.npz')),allow_pickle=False) as a:
            d={k:a[k].copy() for k in a.files}
        with np.load(io.BytesIO(z.read('rows_0000/array_1/traces.npz')),allow_pickle=False) as a:
            other={k:a[k].copy() for k in a.files}
        meta=json.loads(z.read('rows_0000/array_0/metadata.json'))
        screen=json.loads(z.read('rows_0000/array_0/screen.json'))
    if d['W'].shape!=(ROWS,256):raise ValueError('Unexpected first-block shape')
    for k in ['X_cal','X_eval','cal_parent_ids','eval_parent_ids','cal_activation_bits','eval_activation_bits']:
        np.testing.assert_array_equal(d[k],other[k])
    d['W']=np.concatenate([d['W'],other['W']],axis=1)
    for k in ['output_channels','weight_bits','coefficients']:
        d[k]=np.concatenate([d[k],other[k]])
    take=np.isin(d['output_channels'],np.unique(d['output_channels'])[:COLS//4])
    d['W']=d['W'][:,take]
    for k in ['output_channels','weight_bits','coefficients']:d[k]=d[k][take]
    channels=np.unique(d['output_channels'])
    for c in channels:
        idx=d['output_channels']==c
        if sorted(d['weight_bits'][idx].tolist())!=[0,1,2,3]:
            raise ValueError('Must include complete signed W4 channels')
        if sorted(d['coefficients'][idx].tolist())!=[-8,1,2,4]:
            raise ValueError('Signed reconstruction contract failed')
    ci=np.unique(d['cal_parent_ids']); ei=np.unique(d['eval_parent_ids'])
    if set(ci)&set(ei):raise ValueError('CAL/DEV parent leakage')
    fit_ids=ci[:FIT_PARENTS]; search_ids=ci[FIT_PARENTS:FIT_PARENTS+SEARCH_PARENTS]
    dev_ids=ei[:DEV_PARENTS]
    pick=lambda key,ids:d[key][np.isin(d['cal_parent_ids'] if key=='X_cal' else d['eval_parent_ids'],ids)]
    splits={'fit':pick('X_cal',fit_ids),'search':pick('X_cal',search_ids),'dev':pick('X_eval',dev_ids)}
    d['split_labels']={}
    for split,source,parents in [('fit','cal',fit_ids),('search','cal',search_ids),('dev','eval',dev_ids)]:
        mask=np.isin(d[source+'_parent_ids'],parents)
        pid=d[source+'_parent_ids'][mask]; ab=d[source+'_activation_bits'][mask]
        d['split_labels'][split]=(pid,ab)
        for parent in np.unique(pid):
            np.testing.assert_array_equal(np.sort(ab[pid==parent]),np.arange(8))
    found=[j for j in screen['runs'] if j['mapping']=='zero_rate_sorted' and j['evaluation']['proposed_group_rows']==B]
    if len(found)!=1:raise ValueError('Missing frozen E01 zero-rate group membership')
    d['base_order']=np.array(found[0]['order'],dtype=np.int64)
    for key,x in splits.items():
        if not np.all((x==0)|(x==1)):raise ValueError('Nonbinary trace')
    return d,splits,meta,{'fit_CAL':fit_ids.tolist(),'search_CAL':search_ids.tolist(),'DEV':dev_ids.tolist()}


def ladder(x,w,group,rho):
    # Each row has dimensionless AP=1 or P=2 conductance when selected.
    # Inactive rows are ideal OFF; the full column's upstream wire is retained.
    g=x[:,:,None]*(1+w[None,:,:])
    y=g[:,-1,:].astype(float)
    for j in range(B-2,-1,-1):y=g[:,j,:]+y/(1+rho*y)
    prefix=rho*(group*B+1)
    current=y/(1+prefix*y)
    # Predeclared, separately ranged ideal ADC at each physical group, common to all maps.
    fs_y=2.*B
    fs=ADC_HEADROOM*fs_y/(1+prefix*fs_y)
    step=fs/(2**ADC_BITS-1)
    if np.any(current>fs+1e-12):raise ValueError('Unexpected ADC clipping')
    digitized=np.rint(current/step)*step
    # Give every comparator this strong, exact assumed-prefix deembedding baseline.
    # It is oracle knowledge of the assumed ladder, NOT extracted device calibration.
    denom=1-prefix*digitized
    if np.min(denom)<=0:raise ValueError('Deembedding singularity')
    deembedded=digitized/denom
    return current,deembedded


def prepare(x,order,w,rho):
    parts=[]
    for group in range(ROWS//B):
        ix=order[group*B:(group+1)*B]
        a=x[:,ix].astype(float); bits=w[ix].astype(float)
        m=a.sum(axis=1); n=a@bits
        current,y=ladder(a,bits,group,rho)
        near=a[:,:B//2].sum(axis=1)
        centroid=a@np.arange(1,B+1)
        # Five coefficient slots, all features available from I and input mask only.
        z=np.stack([np.ones_like(y), y/B,
                    np.broadcast_to(m[:,None]/B,y.shape),
                    np.broadcast_to(near[:,None]/B,y.shape),
                    np.broadcast_to(centroid[:,None]/B**2,y.shape)],axis=-1)
        k=bits.sum(axis=0)
        lo=np.maximum(0,m[:,None]+k[None,:]-B)
        hi=np.minimum(m[:,None],k[None,:])
        parts.append({'z':z,'n':n,'current':current,'m':m,'lo':lo,'hi':hi})
    return parts


def fit_calibration(parts):
    all_coef=[]
    for p in parts:
        baseline=p['z'][:,:,1]*B-p['m'][:,None]
        residual=p['n']-baseline
        # Fit a bounded residual about the nominal physics; an unseen CAL group
        # retains that physics instead of an arbitrary zero-valued least-squares fit.
        coefs=[]
        for c in range(COLS):
            z=p['z'][:,c,:]
            coefs.append(np.linalg.solve(z.T@z+RIDGE*np.eye(z.shape[1]),z.T@residual[:,c]))
        all_coef.append({'beta':np.stack(coefs),'cap':np.max(np.abs(residual),axis=0)})
    return all_coef


def evaluate(parts,coef,d,split,with_parent=False):
    decoded=[]; continuous=[]; true=[]; raw=[]
    for p,params in zip(parts,coef):
        delta=np.einsum('ncq,cq->nc',p['z'],params['beta'])
        delta=np.clip(delta,-params['cap'],params['cap'])
        pred=p['z'][:,:,1]*B-p['m'][:,None]+delta
        pred=np.clip(pred,p['lo'],p['hi'])
        continuous.append(pred); decoded.append(np.rint(pred)); true.append(p['n'])
        # Raw ideal-current count estimate, no correction; fit/search use same available physics.
        raw.append(p['current']-p['m'][:,None]-p['n'])
    ct=np.stack(true,axis=1); de=np.stack(decoded,axis=1); co=np.stack(continuous,axis=1)
    err=de-ct
    chans=np.unique(d['output_channels'])
    def reconstruct(a):
        return np.stack([np.sum(a[:,:,d['output_channels']==c]*d['coefficients'][d['output_channels']==c],axis=(1,2))
                         for c in chans],axis=1)
    out_err=reconstruct(err)
    out_float=reconstruct(co-ct)
    pid,ab=d['split_labels'][split]
    def activation_reconstruct(values):
        return np.stack([np.sum(values[pid==parent]*(2.**ab[pid==parent,None]),axis=0)
                         for parent in np.unique(pid)],axis=0)
    full_err=activation_reconstruct(out_err)
    full_float=activation_reconstruct(out_float)
    met={'raw_current_mse':float(np.mean(np.stack(raw)**2)),
            'postcal_continuous_count_mse':float(np.mean((co-ct)**2)),
            'postcal_decoded_count_mse':float(np.mean(err**2)),
            'postcal_count_error_rate':float(np.mean(err!=0)),
            'postcal_signed_block_output_mse':float(np.mean(out_err**2)),
            'postcal_continuous_signed_output_mse':float(np.mean(out_float**2)),
            'postcal_W4A8_block_MSE':float(np.mean(full_err**2)),
            'postcal_continuous_W4A8_block_MSE':float(np.mean(full_float**2)),
            'read_events_including_skips':int(ct.size),
            'nonempty_vector_reads':int(sum(np.count_nonzero(p['m']) for p in parts))}
    if with_parent:met['parent_W4A8_squared_error']=np.mean(full_err**2,axis=1).tolist()
    return met


def greedy_pair_order(S):
    # Same seven best-pair swaps as E22, including the independent-activation ablation.
    pos=np.minimum.outer(np.arange(1,B+1),np.arange(1,B+1))
    order=np.argsort(-S.sum(axis=1),kind='stable')
    cost=lambda q:float(np.sum(S[np.ix_(q,q)]*pos))
    total=cost(order)
    for _ in range(7):
        best=total;pair=None
        for p in range(B):
            for q in range(p+1,B):
                order[p],order[q]=order[q],order[p]
                v=cost(order)
                order[p],order[q]=order[q],order[p]
                if v<best-1e-12:best=v;pair=(p,q)
        if pair is None:break
        order[pair[0]],order[pair[1]]=order[pair[1]],order[pair[0]]
        total=best
    return order


def candidate_orders(d,splits,count):
    # Fix read-group membership by a single CAL-only zero-rate order.
    xcal=np.concatenate([splits['fit'],splits['search']],axis=0).astype(float)
    rate=np.mean(xcal,axis=0)
    base=d['base_order'].copy()
    out=[('fixed_group_base',base.copy())]
    rev=base.reshape(-1,B)[:,::-1].ravel();out.append(('within_group_reverse',rev.copy()))
    density=d['W'].mean(axis=1)
    joint=base.copy(); camp=base.copy(); indep=base.copy()
    for g in range(ROWS//B):
        sl=slice(g*B,(g+1)*B);ids=base[sl]
        p=rate[ids];gbar=1+density[ids]
        joint[sl]=ids[np.argsort(-(p*gbar),kind='stable')]
        C=xcal[:,ids].T@xcal[:,ids]/len(xcal)
        camp[sl]=ids[greedy_pair_order(C*np.outer(gbar,gbar))]
        indep[sl]=ids[greedy_pair_order(np.outer(p*gbar,p*gbar))]
    out.extend([('joint_activity_conductance_sort',joint),('CAMP_light',camp),('independent_activation_pair_optimizer',indep)])
    for direction in [1,-1]:
        q=base.copy()
        for g in range(ROWS//B):
            sl=slice(g*B,(g+1)*B); ids=base[sl]
            q[sl]=ids[np.argsort(direction*density[ids],kind='stable')]
        out.append(('weight_density_'+('ascending' if direction==1 else 'descending'),q))
    rng=np.random.default_rng(SEED)
    for i in range(count):
        q=base.copy()
        for g in range(ROWS//B):rng.shuffle(q[g*B:(g+1)*B])
        out.append((f'within_group_random_{i:03d}',q))
    for name,q in out:
        np.testing.assert_array_equal(np.sort(q),np.arange(ROWS))
        for g in range(ROWS//B):
            np.testing.assert_array_equal(np.sort(q[g*B:(g+1)*B]),np.sort(base[g*B:(g+1)*B]))
    return out


def checks(d,splits,orders):
    base=orders[0][1]
    for _,order in orders:
        for x in splits.values():
            for g in range(ROWS//B):
                a=base[g*B:(g+1)*B];b=order[g*B:(g+1)*B]
                np.testing.assert_array_equal(x[:,a].sum(1),x[:,b].sum(1))
                np.testing.assert_array_equal(x[:,a].astype(np.int64)@d['W'][a],x[:,b].astype(np.int64)@d['W'][b])
    # Independent 256-node dense nodal solve vs collapsed-group exact recurrence.
    rng=np.random.default_rng(SEED+1)
    maxerr=0.
    for r in [1.,5.]:
        rho=r/RAPS
        for group in [0,3,7]:
            x=rng.integers(0,2,(1,B)).astype(float)
            w=rng.integers(0,2,(B,1)).astype(float)
            cur,_=ladder(x,w,group,rho)
            full=np.zeros(ROWS);full[group*B:(group+1)*B]=x[0]*(1+w[:,0])
            A=np.diag(full+2/rho);A[-1,-1]-=1/rho
            A+=np.diag(np.full(ROWS-1,-1/rho),1)+np.diag(np.full(ROWS-1,-1/rho),-1)
            rhs=np.zeros(ROWS);rhs[0]=1/rho
            nodes=np.linalg.solve(A,rhs)
            current=(1-nodes[0])/rho
            maxerr=max(maxerr,abs(current-cur[0,0]))
            np.testing.assert_allclose(current,cur[0,0],atol=1e-9,rtol=1e-9)
    return {'arithmetic_and_group_invariance':'PASS','dense_256_node_KCL':'PASS',
            'max_normalized_current_difference':float(maxerr)}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--packet',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--random-orders',type=int,default=24)
    args=ap.parse_args()
    if args.out.exists():ap.error('Choose a new, non-overwriting output directory')
    d,splits,metadata,ids=read_packet(args.packet)
    orders=candidate_orders(d,splits,args.random_orders)
    qa=checks(d,splits,orders)
    args.out.mkdir(parents=True)
    records=[]
    for r in [0.,1.,5.]:
        cal=[];params=[]
        start=time.perf_counter()
        for name,order in orders:
            fit=prepare(splits['fit'],order,d['W'],r/RAPS)
            beta=fit_calibration(fit)
            search=prepare(splits['search'],order,d['W'],r/RAPS)
            met=evaluate(search,beta,d,'search')
            cal.append({'name':name,'metrics':met});params.append(beta)
        selected={'fixed_group_base':0,
                  'joint_activity_conductance_sort':next(i for i,o in enumerate(orders) if o[0]=='joint_activity_conductance_sort'),
                  'CAMP_light':next(i for i,o in enumerate(orders) if o[0]=='CAMP_light'),
                  'independent_activation_pair_optimizer':next(i for i,o in enumerate(orders) if o[0]=='independent_activation_pair_optimizer'),
                  'raw_current_MSE':min(range(len(cal)),key=lambda i:cal[i]['metrics']['raw_current_mse']),
                  'postcal_continuous_count_MSE':min(range(len(cal)),key=lambda i:cal[i]['metrics']['postcal_continuous_count_mse']),
                  'postcal_decoded_count_MSE':min(range(len(cal)),key=lambda i:cal[i]['metrics']['postcal_decoded_count_mse']),
                  'candidate_signed_decoded_MSE':min(range(len(cal)),key=lambda i:cal[i]['metrics']['postcal_signed_block_output_mse']),
                  'strong_signed_continuous_MSE':min(range(len(cal)),key=lambda i:cal[i]['metrics']['postcal_continuous_signed_output_mse'])}
        selected['candidate_W4A8_decoded_MSE']=min(range(len(cal)),key=lambda i:cal[i]['metrics']['postcal_W4A8_block_MSE'])
        selected['strong_W4A8_continuous_MSE']=min(range(len(cal)),key=lambda i:cal[i]['metrics']['postcal_continuous_W4A8_block_MSE'])
        cal_time=time.perf_counter()-start
        dev={}
        for policy,i in selected.items():
            name,order=orders[i]
            met=evaluate(prepare(splits['dev'],order,d['W'],r/RAPS),params[i],d,'dev',with_parent=True)
            if r==0 and met['postcal_count_error_rate']!=0:
                raise AssertionError('Zero-wire null must decode every count correctly')
            dev[policy]={'selected_order':name,'metrics':met}
        records.append({'r_segment_assumed_ohm':r,'CAL_scores':cal,'selected':selected,'DEV':dev,
                        'CAL_all_candidates_wall_seconds':cal_time})
        print(json.dumps({'r_ohm':r,'DEV':{k:{'order':v['selected_order'],
                         'count_error':v['metrics']['postcal_count_error_rate'],
                         'W4A8_MSE':v['metrics']['postcal_W4A8_block_MSE']} for k,v in dev.items()}}),flush=True)
    result={'evidence_class':'real workload + assumed passive-network algorithm screen',
            'not_evidence_for':['GF response','validated surrogate','physical 256x256 macro','energy','latency','neural accuracy','novelty'],
            'timestamp_UTC':datetime.now(timezone.utc).isoformat(),
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'packet_sha256':EXPECTED_PACKET,'source_metadata':metadata,'split_parent_ids':ids,
            'settings':{'physical_column_rows_in_assumed_ladder':ROWS,'read_group_rows':B,'weight_columns_used':COLS,
                        'source_row_block':'first 256 FC1 rows only','seed':SEED,'candidate_count':len(orders),
                        'Rp_ohm':RPS,'Rap_ohm':RAPS,'ADC_bits':ADC_BITS,'ADC_headroom':ADC_HEADROOM,
                        'device_mismatch':False,'transistor':False,'temporal_noise':False,
                        'calibration':'nominal count plus bounded ridge residual, 5 coefficients and one bound per group/weight-bit column, CAL-only; ridge=0.001',
                        'strong_baseline':'exact assumed upstream-wire deembedding given to every method',
                        'control_scope':'same candidate pool scored by all objectives; no greedy mapper claimed',
                        'output_metric':'signed W4A8 first-256-row partial dot-product error, parent and activation-bit identities retained; NOT full-layer or inference'},
            'checks':qa,'orders':{name:order.tolist() for name,order in orders},'results':records}
    (args.out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('CHECKS',json.dumps(qa),flush=True)


if __name__=='__main__':main()
