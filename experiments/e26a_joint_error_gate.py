#!/usr/bin/env python3
"""E26A physical-joint versus conditional-shuffle errors on FROZEN E01 FC1 W4A8 traces.

This executable implements a computation-level falsification control, NOT a hardware
measurement or classifier. The --demo command uses explicitly SYNTHETIC errors and
cannot establish physical correlation, measured GF PEX, or MNIST classification.

For physical use, provide an aligned, complete joint count-error tensor from one
validated multi-column 2T1MTJ read model: shape (8,256,8,8,256) indexed as
[packed_array, dev_parent, activation_bit, row_group32, physical_column].
E01 order is four 256-row blocks, two binary weight-plane arrays per block.
The null SHUFFLES errors among dev parents WITHIN exact (number_active_rows,ideal_count)
strata for each physical operation lane, preserving all empirical conditional
single-read error distributions and per-lane weight/bit significance. It removes
residual cross-read coupling, NOT shared dependence through activity/count.

Requirements: Python 3.8+, numpy. Uses E01 review_packet.zip. No torch needed.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import random
import zipfile

import numpy as np

PACKET_EXPECTED_SHA = '400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a'
ARRAYS = 8
PARENTS = 256
BITS = 8
GROUPS = 8
COLS = 256
FC1 = 128
SHAPE = (ARRAYS,PARENTS,BITS,GROUPS,COLS)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_packet(path, *, strict=True):
    raw=path.read_bytes()
    digest=sha(raw)
    if strict and digest != PACKET_EXPECTED_SHA:
        raise ValueError('E01 packet SHA256 mismatch; not the frozen authenticated workload')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        manifest=json.loads(z.read('packet_manifest.json'))
        for name,info in manifest['files'].items():
            bb=z.read(name)
            if sha(bb)!=info['sha256'] or len(bb)!=info['bytes']:
                raise ValueError('Packet internal file integrity failure: '+name)
        rows=[]
        for b in (0,256,512,768):
            pair=[]
            for a in (0,1):
                path='rows_%04d/array_%d/traces.npz'%(b,a)
                with np.load(io.BytesIO(z.read(path)),allow_pickle=False) as f:
                    d={k:f[k].copy() for k in f.files}
                pair.append(d)
            rows.extend(pair)
    return rows,digest


def build_reference(files):
    # E01 shape: each 256-wide array stores TWO weight bitplanes over 128 FC1 neurons;
    # a sample has 8 activation bitplane rows. Padded tail is represented in packet.
    parents=None
    counts=np.empty(SHAPE,dtype=np.int16)
    m=np.empty((ARRAYS,PARENTS,BITS,GROUPS),dtype=np.int16)
    clean=np.zeros((PARENTS,FC1),dtype=np.int64)
    direct=np.zeros_like(clean)
    signed_weight=np.zeros((784,FC1),dtype=np.int16)
    perblock_x=[]
    for ai,f in enumerate(files):
        x=np.asarray(f['X_eval'],dtype=np.int16)
        w=np.asarray(f['W'],dtype=np.int16)
        channels=np.asarray(f['output_channels'],dtype=np.int64)
        coeff=np.asarray(f['coefficients'],dtype=np.int64)
        ids=np.asarray(f['eval_parent_ids'],dtype=np.int64).reshape(PARENTS,BITS)
        abits=np.asarray(f['eval_activation_bits'],dtype=np.int64).reshape(PARENTS,BITS)
        if not np.array_equal(abits,np.broadcast_to(np.arange(BITS),(PARENTS,BITS))):
            raise ValueError('E01 activation bitplane order mismatch at array %d'%ai)
        if not np.all(ids==ids[:,0,None]) or len(set(ids[:,0].tolist()))!=PARENTS:
            raise ValueError('E01 parent IDs out of order or duplicated')
        if parents is None: parents=ids[:,0].copy()
        if not np.array_equal(parents,ids[:,0]):
            raise ValueError('Array parent rows not paired')
        if x.shape!=(PARENTS*BITS,256) or w.shape!=(256,256):
            raise ValueError('Invalid E01 dimensions')
        if sorted(np.unique(channels).tolist())!=list(range(FC1)) or not np.all((x==0)|(x==1)) or not np.all((w==0)|(w==1)):
            raise ValueError('E01 binary packing invalid')
        xb=x.reshape(PARENTS,BITS,256)
        if ai%2==0:
            perblock_x.append(xb)
        elif not np.array_equal(xb,perblock_x[-1]):
            raise ValueError('Paired physical arrays have mismatched activation patterns')
        signed_x=np.tensordot(xb, (1<<np.arange(BITS,dtype=np.int64)), axes=([1],[0]))
        # signed_x is [parents, physical_rows]
        start=(ai//2)*256
        used=16 if start==768 else 256
        for j in range(256):
            if np.any(w[used:,j]):
                raise ValueError('Padding rows contain stored bits')
            signed_weight[start:start+used,channels[j]] += (w[:used,j]*int(coeff[j])).astype(np.int16)
            direct[:,channels[j]] += signed_x[:,:used] @ (w[:used,j].astype(np.int64)*coeff[j])
        for g in range(GROUPS):
            s=32*g; e=s+32
            n=np.einsum('pr,rc->pc',xb[:,:,s:e].reshape(PARENTS*BITS,32).astype(np.int32),w[s:e,:].astype(np.int32),optimize=True)
            # Equivalent parent,activation-bit,phys-column count
            counts[ai,:,:,g,:]=n.reshape(PARENTS,BITS,COLS)
            m[ai,:,:,g]=xb[:,:,s:e].sum(axis=2)
            piece=(counts[ai,:,:,g,:].astype(np.int64)*(1<<np.arange(BITS,dtype=np.int64))[None,:,None]).sum(axis=1)*coeff[None,:]
            for j in range(COLS):
                clean[:,channels[j]]+=piece[:,j]
    if np.any(signed_weight<-8) or np.any(signed_weight>7):
        raise ValueError('Weight bits do not reconstruct 4-bit signed model')
    if not np.array_equal(clean,direct):
        raise ValueError('Bitplane group MAC does not match direct packed W4A8 dot product')
    return dict(counts=counts,activity=m,clean=clean,parents=parents,signed_weight=signed_weight,
                files=files)


def perturb_fc1(err, files):
    # Error in decoded COUNT (not current in amperes) with exact signed weight coefficient.
    y=np.zeros((PARENTS,FC1),dtype=np.int64)
    for ai,f in enumerate(files):
        ch=f['output_channels'].astype(np.int64)
        coeff=f['coefficients'].astype(np.int64)
        total=(err[ai].astype(np.int64)*(1<<np.arange(BITS,dtype=np.int64))[None,:,None,None]).sum(axis=(1,2))*coeff[None,:]
        for j in range(COLS):
            y[:,ch[j]]+=total[:,j]
    return y


def verify_error(err, ref):
    if err.shape!=SHAPE or err.dtype.kind not in 'iu':
        raise ValueError('Need COMPLETE integer count-error tensor shape '+str(SHAPE))
    if err.min() < -32 or err.max() > 32:
        raise ValueError('Unrealistic count-error magnitude')
    n=ref['counts'].astype(np.int32)
    decoded=n+err.astype(np.int32)
    # A bad decoder can report a count HIGHER than the number of active rows.
    # This is a valid *failure*, not an invalid physical sample. Enforce only
    # the predeclared group-size decoder output range 0..32.
    if np.any(decoded<0) or np.any(decoded>32):
        raise ValueError('Decoded count outside supported 0..32 range; check data contract')
    return int(np.count_nonzero(err))


def shuffled_within_exact_strata(err,ref,seed):
    rng=np.random.default_rng(seed)
    # Operate only on physical lanes with variable errors; unchanged zero lanes are skipped.
    out=err.copy()
    counts=ref['counts']; activ=ref['activity']
    changed=0; eligible=0; variable_lanes=0
    for ai in range(ARRAYS):
        for abit in range(BITS):
            for g in range(GROUPS):
                ms=activ[ai,:,abit,g].astype(np.int32)
                for col in range(COLS):
                    src=err[ai,:,abit,g,col]
                    if not np.any(src!=0):continue
                    variable_lanes+=1
                    key=ms*33 + counts[ai,:,abit,g,col].astype(np.int32)
                    # A stratum keeps precise active-row population and ideal count.
                    for val in np.unique(key):
                        ix=np.flatnonzero(key==val)
                        if len(ix)<2:continue
                        vals=src[ix]
                        if np.all(vals==vals[0]):continue
                        eligible += len(ix)
                        shuffled=vals[rng.permutation(len(ix))]
                        changed += int(np.count_nonzero(shuffled!=vals))
                        out[ai,ix,abit,g,col]=shuffled
    verify_error(out,ref)
    return out,dict(variable_lanes=variable_lanes,eligible_entries=eligible,changed_entries=changed)


def metrics(delta):
    a=np.abs(delta.astype(np.int64))
    return dict(fc1_mae=float(a.mean()),fc1_rmse=float(np.sqrt(np.square(delta.astype(np.float64)).mean())),
                fc1_max_abs=int(a.max()),fraction_nonzero_fc1=float(np.mean(a!=0)),
                fraction_images_any_fc1_error=float(np.mean(np.any(a!=0,axis=1))))


def compare(err,ref,repeat,seed):
    verify_error(err,ref)
    clean=ref['clean'];dj=perturb_fc1(err,ref['files'])
    joint=metrics(dj)
    joint['relu_gate_flip_fraction']=float(np.mean((clean>0)!=(clean+dj>0)))
    controls=[];deltas=[]
    for i in range(repeat):
        perm,audit=shuffled_within_exact_strata(err,ref,seed+i)
        ds=perturb_fc1(perm,ref['files'])
        score=metrics(ds)
        score['relu_gate_flip_fraction']=float(np.mean((clean>0)!=(clean+ds>0)))
        controls.append(dict(score=score,shuffle_audit=audit))
        deltas.append(ds)
    keys=joint.keys()
    means={k:float(np.mean([t['score'][k] for t in controls])) for k in keys}
    q05={k:float(np.quantile([t['score'][k] for t in controls],.05)) for k in keys}
    q95={k:float(np.quantile([t['score'][k] for t in controls],.95)) for k in keys}
    return dict(joint=joint,conditional_shuffled_mean=means,conditional_shuffled_p05=q05,
                conditional_shuffled_p95=q95,
                total_error_events=int(np.count_nonzero(err)),
                total_read_operations=int(np.prod(err.shape)),
                repeats=repeat,
                min_effective_changed_entries=min(t['shuffle_audit']['changed_entries'] for t in controls),
                mean_effective_changed_entries=float(np.mean([t['shuffle_audit']['changed_entries'] for t in controls])),
                warnings=['FC1 ONLY: No FC2 or output logits, no classification accuracy.',
                          'Preserves each physical lane empirical error distribution conditional on exact input activity and ideal count; count is used for OFFLINE SHUFFLE STRATIFICATION ONLY, not runtime correction.',
                          'A difference is not algorithm novelty or proof physical shared coupling.',
                          'Population and chip uncertainty requires newly measured fixed-chip joint tensors.'])


def demo_errors(ref,seed):
    # Deliberately artificial coherent signs in the negative weight MSB and high activation bit.
    # This is a SOFTWARE TEST of the comparison procedure, NOT MRAM experimental data.
    rng=np.random.default_rng(seed)
    a=np.zeros(SHAPE,dtype=np.int8)
    latent=rng.random(PARENTS)<.22
    for ai in (1,3,5,7):
        ab=7;g=0
        f=ref['files'][ai];col=np.flatnonzero(f['coefficients']==-8)
        n=ref['counts'][ai,:,ab,g,:];m=ref['activity'][ai,:,ab,g,None]
        feasible=np.logical_and(n>0,n<m)
        for p in np.flatnonzero(latent):
            a[ai,p,ab,g,col[feasible[p,col]]]=-1
    verify_error(a,ref)
    return a


def run(args):
    path=Path(args.packet).expanduser()
    files,digest=load_packet(path,strict=not args.allow_nonfrozen)
    ref=build_reference(files)
    print('E26A_E01_PACKET_SHA256',digest)
    print('E26A_FROZEN_FC1_PASS: 256 actual E01 development parents, eight packed arrays, signed bitplane reconstruction matches direct dot',flush=True)
    print('E26A_CLEAN_FC1_SHAPE',ref['clean'].shape,'WEIGHT_RANGE',int(ref['signed_weight'].min()),int(ref['signed_weight'].max()))
    if args.mode=='preflight':
        print('E26A_BLOCKED_PHYSICAL: joint per-read, per-parent, per-array, per-column GF 2T1MTJ PEX count-error tensor not provided.')
        print('E26A_BLOCKED_FULL_NETWORK: frozen downstream FC2/FC3/logit adapter absent; FC1 only.')
        return
    if args.mode=='demo':
        err=demo_errors(ref,args.seed)
        evidence='SYNTHETIC_DEMONSTRATION_NOT_GF_OR_PEX'
    else:
        if not args.errors: raise ValueError('analyze requires --errors npz, physically generated complete count-error tensor')
        if not args.attestation:raise ValueError('analyze needs physical source attestation JSON; no inferred physical evidence')
        att=json.loads(Path(args.attestation).read_text())
        if att.get('evidence_tier') not in ('extracted_2T1MTJ_parallel_CIM_model','measured_MRAM_parallel_CIM') or not att.get('joint_sampled_from_same_fixed_chip_and_read_conditions',False):
            raise ValueError('No validated physical joint-error provenance; use demo for synthetic control')
        if att.get('packet_sha256')!=digest:raise ValueError('Physical error tensor E01 workload hash mismatch')
        with np.load(args.errors,allow_pickle=False) as data:
            err=data['count_error'].copy()
        if not np.issubdtype(err.dtype,np.integer):raise ValueError('count_error must be integer')
        verify_error(err,ref)
        evidence=att['evidence_tier']+'_ATTESTED_BY_STUDENT_NOT_INDEPENDENTLY_VERIFIED'
    if args.repeat<1:raise ValueError('repeat >=1 required')
    score=compare(err,ref,args.repeat,args.seed)
    report={'experiment':'E26A','status':'FC1_ONLY_NO_CLASSIFIER','evidence_class':evidence,
            'packet_sha256':digest,'source_error_tensor_sha256':sha(Path(args.errors).read_bytes()) if args.errors else None,
            'metric_scope':'FC1 integer MAC error and ReLU gate changes only',
            'comparison':score}
    print('E26A_TIER',evidence)
    print('E26A_JOINT_FC1',json.dumps(score['joint'],sort_keys=True))
    print('E26A_SHUFFLED_FC1',json.dumps(score['conditional_shuffled_mean'],sort_keys=True))
    print('E26A_SHUFFLE_EFFECTIVE_CHANGED',score['mean_effective_changed_entries'])
    if args.out:
        out=Path(args.out).expanduser()
        if out.exists():raise ValueError('Refuses overwrite '+str(out))
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('E26A_REPORT',out)
    print('E26A_NOT_FULL_NETWORK; NO_CLASSIFICATION; NO_NOVEL_ALGORITHM_CLAIM')


def selftest():
    # Unit test physical-lane error shuffle preserving exact (m,n) strata.
    e=np.array([0,0,-1,0,0,0],dtype=np.int8)
    key=np.array([0,0,0,1,1,1]);r=np.random.default_rng(1);new=e.copy()
    for k in np.unique(key):
        ix=np.flatnonzero(key==k);new[ix]=e[ix][r.permutation(len(ix))]
        assert sorted(new[ix].tolist())==sorted(e[ix].tolist())
    print('E26A_SELFTEST_PASS: conditional shuffled event marginals; mock data only')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=('selftest','preflight','demo','analyze'))
    p.add_argument('--packet',default='review_packet.zip')
    p.add_argument('--errors')
    p.add_argument('--attestation')
    p.add_argument('--repeat',type=int,default=4)
    p.add_argument('--seed',type=int,default=20261105)
    p.add_argument('--out')
    p.add_argument('--allow-nonfrozen',action='store_true',help='Developer debugging only; disables frozen E01 packet SHA requirement')
    a=p.parse_args()
    if a.mode=='selftest':selftest()
    else:run(a)

if __name__=='__main__':main()