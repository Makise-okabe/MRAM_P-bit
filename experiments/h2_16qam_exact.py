#!/usr/bin/env python3
"""16-QAM, 16-spin H2: exact encoding-aware coupling quantization experiment.

E0/E1 software only. No stochastic p-bit, no measured MRAM device, no RTL.
Three PRESELECTED candidates: FP4_fn J + FP6_fn h; INT4 J + INT6 h;
BFP6 J+h. Same CAL-fitted frozen group policy, identical heldout frames.
All 2^(4*tx) states are enumerated by a vectorized split-energy oracle.
Requires numpy and existing m1_coupling_formats.py in this directory.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np

import m1_coupling_formats as qfmt

CANDIDATES = {
    "mixed_fp": ("fp4_fn", "fp6_fn"),
    "mixed_int": ("int4", "int6"),
    "bfp6": ("bfp6", "bfp6"),
}
GROUPINGS = ("global", "tile", "significance")
NUM_TOL = 1e-8


def weights(tx):
    return np.tile(np.array([2, 1, 2, 1], dtype=int), tx)


def mapper(tx):
    """Map (a,b,c,d) spins to ((2a+b)+1j*(2c+d))/sqrt(10)."""
    B = np.zeros((tx, 4 * tx), dtype=np.complex128)
    for k in range(tx):
        B[k, 4*k:4*k+4] = [2, 1, 2j, 1j]
    return B / math.sqrt(10.0)


def gray_bits(spins):
    """Gray data labeling of PAM: -3:00, -1:01, +1:11, +3:10."""
    a = np.asarray(spins, dtype=np.int8)
    if a.shape[-1] % 4:
        raise ValueError("a complex 16-QAM symbol requires four spins")
    out = np.zeros(a.shape, dtype=np.uint8)
    out[..., 0::2] = (a[..., 0::2] == 1)
    out[..., 1::2] = (a[..., 0::2] != a[..., 1::2])
    return out


def frame(tx, rx, snr_db, seed):
    if not (1 <= tx <= 4 and rx >= 1 and math.isfinite(snr_db)):
        raise ValueError("this exact pilot supports 1..4 Tx and rx>=1")
    rng = np.random.default_rng(seed)
    H = (rng.standard_normal((rx, tx)) +
         1j * rng.standard_normal((rx, tx))) / math.sqrt(2 * rx)
    transmitted = rng.choice(np.array([-1, 1], dtype=np.int8), size=4*tx)
    B = mapper(tx)
    x = B @ transmitted
    sigma2 = (tx/rx) * 10 ** (-snr_db/10)
    noise = (rng.standard_normal(rx) +
             1j*rng.standard_normal(rx)) * math.sqrt(sigma2/2)
    y = H @ x + noise
    A = H @ B
    G = np.real(A.conj().T @ A)
    b = np.real(A.conj().T @ y)
    J = -2 * (G - np.diag(np.diag(G)))
    h = 2 * b
    C = float(np.vdot(y, y).real + np.trace(G))
    if not np.allclose(J, J.T, rtol=0, atol=1e-12):
        raise AssertionError("mapped Ising couplings are not symmetric")
    return dict(H=H, y=y, A=A, B=B, J=J, h=h, C=C,
                transmitted=transmitted, tx=tx, rx=rx,
                snr_db=snr_db, seed=seed, noise_variance=sigma2)


def j_groups(tx, grouping, tile):
    if grouping not in GROUPINGS or tile < 1:
        raise ValueError("unsupported grouping or invalid tile")
    n = tx*4
    w = weights(tx)
    groups = {}
    for i in range(n):
        for j in range(i+1, n):
            if grouping == "global":
                key = "J_all"
            elif grouping == "tile":
                key = f"J_tile_{i//tile}_{j//tile}"
            else:
                lo, hi = sorted((int(w[i]), int(w[j])))
                key = f"J_sig_{lo}_{hi}"
            groups.setdefault(key, []).append((i,j))
    return groups


def calibrate(tx, rx, snr_db, cal_frames, cal_seed, tile):
    """No original ML labels or HELDOUT data are seen during calibration."""
    groups = {g:j_groups(tx,g,tile) for g in GROUPINGS}
    pools = {g:{name:[] for name in edges} for g,edges in groups.items()}
    for g in GROUPINGS:
        pools[g]["h"] = []
    for k in range(cal_frames):
        f = frame(tx,rx,snr_db,cal_seed+k)
        for g in GROUPINGS:
            for key,edges in groups[g].items():
                pools[g][key].extend(float(f["J"][i,j]) for i,j in edges)
            pools[g]["h"].extend(float(v) for v in f["h"])
    fitted = {}
    for grouping in GROUPINGS:
        for label,(jf,hf) in CANDIDATES.items():
            vals=pools[grouping]
            scales={}
            for key in groups[grouping]:
                scales[key] = qfmt.tune_scale(vals[key],jf)[0]
            scales["h"] = qfmt.tune_scale(vals["h"],hf)[0]
            fitted[f"{label}|{grouping}"] = scales
    return fitted


def represent(f, grouping, tile, label, scales):
    n=4*f["tx"]
    jf,hf=CANDIDATES[label]
    groups=j_groups(f["tx"],grouping,tile)
    if set(scales) != set(groups)|{"h"}:
        raise ValueError("scale keys do not match group definition")
    J=np.zeros((n,n),dtype=np.float64)
    for key,edges in groups.items():
        sc=scales[key]
        for i,j in edges:
            v=qfmt.quantized_level(float(f["J"][i,j]),sc,jf)
            J[i,j]=J[j,i]=v
    h=np.array([qfmt.quantized_level(float(v),scales["h"],hf)
                for v in f["h"]],dtype=np.float64)
    jbits=qfmt.format_bits(jf)
    hbits=qfmt.format_bits(hf)
    scale_bits=8 if label=="bfp6" else 32
    encoded_bits=(n*(n-1)//2)*jbits + n*hbits
    metadata_bits=(len(groups)+1)*scale_bits
    if not np.allclose(J,J.T,rtol=0,atol=0):
        raise AssertionError("quantization broke J symmetry")
    return dict(J=J,h=h,bits=encoded_bits+metadata_bits,
                coefficient_bits=encoded_bits,metadata_bits=metadata_bits,
                jmse=float(np.sum(np.triu((f["J"]-J)**2,k=1))),
                hmse=float(np.sum((f["h"]-h)**2)))


class ExactOracle:
    """Split 2^n energy evaluation; direct channel residual as independent ML."""
    def __init__(self, tx):
        self.tx=tx
        n=4*tx
        nleft=n//2
        nright=n-nleft
        left_int=np.arange(1<<nleft, dtype=np.uint32)
        right_int=np.arange(1<<nright, dtype=np.uint32)
        self.left=(2*((left_int[:,None] >> np.arange(nleft)) & 1)-1).astype(np.int8)
        self.right=(2*((right_int[:,None] >> np.arange(nright)) & 1)-1).astype(np.int8)
        self.states=np.concatenate([
            np.repeat(self.left,len(self.right),axis=0),
            np.tile(self.right,(len(self.left),1))
        ],axis=1)
        self.X=self.states @ mapper(tx).T
        self.gray=gray_bits(self.states)
        self.nleft=nleft

    def energies(self,J,h):
        """Return flattened energies in the same order as self.states."""
        k=self.nleft
        J=np.asarray(J,dtype=np.float64)
        h=np.asarray(h,dtype=np.float64)
        l=self.left.astype(np.float64,copy=False)
        r=self.right.astype(np.float64,copy=False)
        el=-.5*np.sum((l@J[:k,:k])*l,axis=1)-l@h[:k]
        er=-.5*np.sum((r@J[k:,k:])*r,axis=1)-r@h[k:]
        cross=-(l@J[:k,k:])@r.T
        return (el[:,None]+er[None,:]+cross).ravel()

    def original(self,f,verify=True):
        residuals=np.sum(np.abs(self.X@f["H"].T-f["y"])**2,axis=1).real
        if verify:
            q=self.energies(f["J"],f["h"])+f["C"]
            difference=float(np.max(np.abs(residuals-q)))
            if not difference<3e-9:
                raise AssertionError(f"16-QAM Ising/direct residual mismatch: {difference}")
            expected_intrasymbol=-4*float(np.vdot(f["H"][:,0],f["H"][:,0]).real)/10
            if abs(float(f["J"][0,1])-expected_intrasymbol)>1e-10:
                raise AssertionError("missing intra-4PAM significance coupling")
        return residuals


def readouts(oracle,f,original,represented,epsilon=NUM_TOL):
    ener=oracle.energies(represented["J"],represented["h"])
    emin=float(np.min(ener))
    minima=np.flatnonzero(ener<=emin+epsilon)
    ml=float(np.min(original))
    gaps=np.maximum(0,original[minima]-ml)
    truth=gray_bits(f["transmitted"])
    errors=np.count_nonzero(oracle.gray[minima] != truth[None,:],axis=1)
    ml_indices=np.flatnonzero(original <= ml+epsilon)
    ml_error=np.count_nonzero(oracle.gray[ml_indices[0]] != truth)
    return {
        "ml_preserved":int(float(np.min(gaps))<=epsilon),
        "ground_degeneracy":len(minima),
        "best_original_gap":float(np.min(gaps)),
        "mean_original_gap":float(np.mean(gaps)),
        "worst_original_gap":float(np.max(gaps)),
        "gray_ber_tie_mean":float(np.mean(errors)/(4*f["tx"])),
        "gray_ber_tie_min":float(np.min(errors)/(4*f["tx"])),
        "gray_ber_tie_max":float(np.max(errors)/(4*f["tx"])),
        "gray_ber_true_ml":float(ml_error/(4*f["tx"])),
        "original_ml_residual":ml,
    }


def selftest():
    """Independent exhaustive original channel objective and Gray label checks."""
    pam=[]
    for high,low in ((-1,-1),(-1,1),(1,-1),(1,1)):
        spin=np.array([high,low,-1,-1],dtype=np.int8)
        x=float(2*high+low)
        pam.append((x,tuple(gray_bits(spin)[:2])))
    assert pam==[(-3.0,(0,0)),(-1.0,(0,1)),(1.0,(1,1)),(3.0,(1,0))]
    for tx in (1,2,3,4):
        f=frame(tx,tx,12,seed=102+tx)
        ex=ExactOracle(tx)
        r=ex.original(f,verify=True)
        assert len(r)==2**(4*tx)
        assert abs(min(r)-min(ex.energies(f["J"],f["h"])+f["C"]))<1e-9
        # A symmetric toy grouping must preserve all undirected interactions.
        for grouping in GROUPINGS:
            gr=j_groups(tx,grouping,4)
            edges=[edge for es in gr.values() for edge in es]
            assert len(edges)==(4*tx)*(4*tx-1)//2
            assert len(set(edges))==len(edges)
    # One small frozen-calibration-to-heldout integration smoke.
    frozen=calibrate(2,2,10,2,20001,4)
    f=frame(2,2,10,30001)
    ex=ExactOracle(2)
    resid=ex.original(f)
    for g in GROUPINGS:
        for label in CANDIDATES:
            represented=represent(f,g,4,label,frozen[f"{label}|{g}"])
            stats=readouts(ex,f,resid,represented)
            assert stats["ground_degeneracy"]>=1
            assert represented["bits"]>0
    print("SELFTEST PASS: 4-,8-,12-,16-spin exact QAM mapping, Gray BER, symmetry, calibrated representation")


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest",action="store_true")
    ap.add_argument("--tx",type=int,default=4)
    ap.add_argument("--rx",type=int,default=4)
    ap.add_argument("--snr-db",type=float,default=12.0)
    ap.add_argument("--cal-frames",type=int,default=100)
    ap.add_argument("--heldout-frames",type=int,default=300)
    ap.add_argument("--cal-seed",type=int,default=2026114000)
    ap.add_argument("--heldout-seed",type=int,default=2026115000)
    ap.add_argument("--tile",type=int,default=4)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    if args.selftest:
        selftest()
        return
    if args.output is None:
        ap.error("--output is required outside --selftest")
    if args.output.exists():
        ap.error("output already exists; use a fresh non-overwriting folder")
    if not (1<=args.tx<=4 and args.rx>=1 and
            args.cal_frames>=1 and args.heldout_frames>=1 and
            args.tile>=1 and math.isfinite(args.snr_db)):
        ap.error("invalid dimensions or frame count")
    if set(range(args.cal_seed,args.cal_seed+args.cal_frames)) & set(
            range(args.heldout_seed,args.heldout_seed+args.heldout_frames)):
        ap.error("CAL/HELDOUT seeds overlap")

    frozen=calibrate(args.tx,args.rx,args.snr_db,args.cal_frames,args.cal_seed,args.tile)
    oracle=ExactOracle(args.tx)
    entries=[]
    for k in range(args.heldout_frames):
        f=frame(args.tx,args.rx,args.snr_db,args.heldout_seed+k)
        residual=oracle.original(f,verify=True)
        for grouping in GROUPINGS:
            for label in CANDIDATES:
                represented=represent(f,grouping,args.tile,label,
                                      frozen[f"{label}|{grouping}"])
                stats=readouts(oracle,f,residual,represented)
                entries.append(dict(frame_index=k,channel_seed=args.heldout_seed+k,
                        format=label,grouping=grouping,snr_db=args.snr_db,
                        nominal_bits=represented["bits"],
                        coefficient_bits=represented["coefficient_bits"],
                        metadata_bits=represented["metadata_bits"],
                        J_mse=represented["jmse"],h_mse=represented["hmse"],**stats))

    group_summaries=[]
    for grouping in GROUPINGS:
        for label in CANDIDATES:
            subset=[r for r in entries if r["grouping"]==grouping and r["format"]==label]
            n=len(subset)
            group_summaries.append(dict(
                format=label,grouping=grouping,frames=n,
                original_ml_preserved=sum(r["ml_preserved"] for r in subset),
                mean_best_original_gap=sum(r["best_original_gap"] for r in subset)/n,
                mean_worst_original_gap=sum(r["worst_original_gap"] for r in subset)/n,
                uniform_ground_tie_gray_ber=sum(r["gray_ber_tie_mean"] for r in subset)/n,
                full_precision_ml_gray_ber=sum(r["gray_ber_true_ml"] for r in subset)/n,
                degenerate_frames=sum(r["ground_degeneracy"]>1 for r in subset),
                nominal_bits=subset[0]["nominal_bits"]))

    args.output.mkdir(parents=True,exist_ok=False)
    with (args.output/"per_frame.csv").open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=list(entries[0]))
        writer.writeheader()
        writer.writerows(entries)
    with (args.output/"summary.csv").open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=list(group_summaries[0]))
        writer.writeheader()
        writer.writerows(group_summaries)
    record=dict(config=dict(tx=args.tx,rx=args.rx,snr_db=args.snr_db,
             cal_frames=args.cal_frames,heldout_frames=args.heldout_frames,
             cal_seed=args.cal_seed,heldout_seed=args.heldout_seed,
             tile=args.tile,format_candidates=CANDIDATES,groupings=GROUPINGS),
             scales=frozen,
             scope="E0/E1 16-QAM exhaustive exact representation, not stochastic MRAM or synthesized hardware",
             limits="Unrounded float64 scale values counted as provisional 32-bit real words for FP/INT, and 8-bit PoT exponent words for BFP. No extra costs of exponent alignment, accumulator, access network or calibration engine included. BER averaged uniformly over mathematical quantized-ground ties, NOT finite-budget p-bit BER.",
             software_sha256={
                "experiment":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "format":hashlib.sha256(Path(qfmt.__file__).read_bytes()).hexdigest()
             })
    (args.output/"setup.json").write_text(
        json.dumps(record,indent=2,allow_nan=False,sort_keys=True)+"\n",encoding="utf-8")
    print("=== 16-QAM EXACT H2: frozen CAL, both J+h quantized, 2^(4tx) states ===")
    print("Format    Group          ML-retained   Mean gap    Tie BER   Bits")
    for x in group_summaries:
        print(f'{x["format"]:9s} {x["grouping"]:13s} '
              f'{x["original_ml_preserved"]:3d}/{x["frames"]:3d}    '
              f'{x["mean_best_original_gap"]:.5f}    '
              f'{x["uniform_ground_tie_gray_ber"]:.5f}  {x["nominal_bits"]}')
    print("Saved: "+str(args.output))


if __name__=="__main__":
    main()
