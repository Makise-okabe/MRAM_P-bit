#!/usr/bin/env python3
"""E28S: ACTUAL GF NFET simultaneous 4-column electrical coupling pilot.

This is a deliberately *assumed shared-return-resistance* circuit experiment,
NOT extracted 1T1MTJ PEX, silicon data, verified GF-MRAM macro, or novel algorithm.
Unlike E27B's separate circuits, four columns of each scenario simultaneously
share one source-line resistor to ground in ONE Spectre DC deck. It measures
whether neighbor weight states alter C0 current while C0's own state/mask stays
fixed. Only the verified existing GF E19 one-FET + static MTJ generator is used.

No PDK/model source text is printed or committed. All decks/results stay in
~/mram_private/E28_1T1/. No guessed topology: rewrite is blocked unless exactly
one safe 0-return per branch is located and all 4 branches per case are found.
Python >=3.6, stdlib only.
"""
from __future__ import print_function
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

E19_SHA="b6bec40bc234fac406d191229146354a5fe47c6969fb6db6a672e607ddf83e54"
MTJ_SHA="1d22984b7be5135c07bb5e392d73aa53e1ad42b7c4bdc6d2fc11bb3f313b9a88"
SHARED_OHMS=[0.01,5.0,20.0]
SCENARIOS=[
    ("NEAR_LOW",(0,1),(1,0,0,0)),
    ("NEAR_MID",(0,1),(1,1,1,1)),
    ("NEAR_HIGH",(0,1),(1,2,2,2)),
    ("NEAR_MIX_A",(0,1),(1,2,0,1)),
    ("NEAR_MIX_B",(0,1),(1,0,2,1)),
    ("FAR_LOW",(2,3),(1,0,0,0)),
    ("FAR_HIGH",(2,3),(1,2,2,2)),
]
# The four physical columns can be interpreted as a signed W4 bitplane toy block
# for reporting only, NOT as the user's full frozen MNIST inference.
SIGNED_W4_COEFF=[1,2,4,-8]
DEVICE_RE=re.compile(r'^\s*(\w+)\s*\(([^)]*)\)\s*(\w+)(.*)$')
SOURCE_RE=re.compile(r'^VC(\d{4})$',re.I)
ANALYSIS_RE=re.compile(r'^\s*(?:dcOp|dc|tran|ac)\s+',re.I)

def die(s):
    raise SystemExit("E28S_BLOCKED: "+str(s))

def sha(path):
    h=hashlib.sha256()
    with open(str(path),"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def weights_for_n(active,n):
    active=list(active)
    unused=[r for r in range(4) if r not in active]
    assert len(active)==2 and len(unused)==2 and 0<=n<=2
    return sorted(active[:n]+unused[:2-n])

def profiles():
    out=[]
    for scenario,active,counts in SCENARIOS:
        for column,n in enumerate(counts):
            p=weights_for_n(active,n)
            out.append(dict(id=len(out),split="CONTROL",true_n=n,
                m=2,k=2,active_rows_0based=list(active),
                weight_P_rows_0based=p,
                mask_hash=hashlib.sha256(repr((scenario,column,active,p)).encode("ascii")).hexdigest()[:16],
                scenario=scenario, column=column))
    return out

def selftest():
    rows=profiles()
    assert len(rows)==28 and len(set(x["mask_hash"] for x in rows))==28
    for k in range(len(SCENARIOS)):
        chunk=rows[k*4:k*4+4]
        assert len(chunk)==4
        assert [x["column"] for x in chunk]==[0,1,2,3]
        assert [x["true_n"] for x in chunk]==list(SCENARIOS[k][2])
        assert all(x["true_n"]==len(set(x["active_rows_0based"])&
                                set(x["weight_P_rows_0based"])) for x in chunk)
        assert chunk[0]["true_n"]==1
    # Synthetic parser fixture: four 1-FET+MTJ branches for case0 and case1.
    lines=['simulator lang=spectre','VC0000 (b0 0) vsource type=dc dc=0.05',
           'VC0001 (b1 0) vsource type=dc dc=0.05']
    for ix in (0,1):
        for j in range(4):
            lines.append("XM{}_{} (b{} d{}_{}) mtj_read_v0 p_state=1".format(ix,j,ix,ix,j))
            lines.append("M{}_{} (d{}_{} w{}_{}, 0 0) hvtnfet l=20n w=80n".format(
                ix,j,ix,j,ix,j).replace(",", ""))
    lines.append("dcOp dc")
    # This mock confirms rewiring mechanics; it is NOT a circuit or PEX result.
    new,stats=rewire("\n".join(lines)+"\n",{0:0,1:0},5.0,
                     expected_rows=4,expected_sources=2)
    assert "RSLGRP0" in new and stats["return_devices_rewired"]==8
    assert "slgrp0 0" in new and new.count("vsource type=dc")==2
    print("E28S_SELFTEST_PASS: 28 case profiles, 7 four-column scenarios, parser mock")
    print("E28S_SELFTEST_MOCK_ONLY_NO_GF_CURRENT_NO_PEX")

class DSU:
    def __init__(self):self.parent={}
    def root(self,x):
        if x not in self.parent:self.parent[x]=x
        if self.parent[x]!=x:self.parent[x]=self.root(self.parent[x])
        return self.parent[x]
    def connect(self,a,b):
        if a=="0" or b=="0":return
        self.parent[self.root(a)]=self.root(b)

def parse_instances(text):
    entries=[]
    for index,line in enumerate(text.splitlines()):
        m=DEVICE_RE.match(line)
        if m:
            name,nodes,model,suffix=m.groups()
            entries.append(dict(idx=index,name=name,nodes=nodes.split(),
                                model=model,suffix=suffix,line=line))
    return entries

def rewire(raw,group_by_case,ohms,expected_rows=4,expected_sources=28):
    if ohms<=0:die("shared return resistance must be positive")
    entries=parse_instances(raw)
    source_by_case={}
    active=[]
    dsu=DSU()
    for e in entries:
        model=e["model"].lower()
        terminals=e["nodes"]
        mi=SOURCE_RE.match(e["name"])
        if mi and model=="vsource":
            ident=int(mi.group(1))
            if ident in source_by_case:die("duplicate VC source "+str(ident))
            if len(terminals)!=2 or (terminals[0]=="0")==(terminals[1]=="0"):
                die("VC source must have exactly one grounded terminal at case "+str(ident))
            # VC may be a current-sensing return or a BL supply; orientation
            # is a model property, NOT assumed from the sign of source current.
            source_by_case[ident]=terminals[1] if terminals[0]=="0" else terminals[0]
        if model=="hvtnfet":
            if len(terminals)!=4:die("GF NFET must have exactly 4 terminals")
            # Conducting path connects D and S, NOT gate or bulk.
            dsu.connect(terminals[0],terminals[2])
            active.append((e,"fet"))
        elif model=="mtj_read_v0":
            if len(terminals)!=2:die("student MTJ must have exactly 2 terminals")
            dsu.connect(terminals[0],terminals[1])
            active.append((e,"mtj"))
        elif model=="resistor":
            if len(terminals)==2:dsu.connect(terminals[0],terminals[1])
    expected=set(group_by_case)
    if set(source_by_case)!=expected or len(expected)!=expected_sources:
        die("VC case IDs mismatch expected={} found={}".format(
            sorted(expected),sorted(source_by_case)))
    root_to_case={}
    for ix,node in source_by_case.items():
        if node=="0":die("VC source positive node ground")
        root=dsu.root(node)
        if root in root_to_case:
            die("two independent cases already electrically connected through devices")
        root_to_case[root]=ix
    per_case={k:[] for k in group_by_case}
    return_contacts={k:[] for k in group_by_case}
    for e,kind in active:
        ns=e["nodes"]
        non_ground=[ns[i] for i in ([0,2] if kind=="fet" else [0,1]) if ns[i]!="0"]
        roots={dsu.root(n) for n in non_ground}
        cases={root_to_case[r] for r in roots if r in root_to_case}
        if len(cases)!=1:die("device cannot be uniquely assigned to VC case: "+e["name"])
        ix=next(iter(cases))
        per_case[ix].append((e,kind))
        pins=([0,2] if kind=="fet" else [0,1])
        for pos in pins:
            if ns[pos]=="0":
                return_contacts[ix].append((e,pos))
    contacts_per_case={str(ix):len(return_contacts[ix]) for ix in sorted(expected)}
    print("E28S_ORIGINAL_RETURN_CONTACT_COUNTS",contacts_per_case,flush=True)
    for ix in sorted(expected):
        devices=per_case[ix]
        if sum(k=="fet" for e,k in devices)!=expected_rows or sum(k=="mtj" for e,k in devices)!=expected_rows:
            die("case {} must contain {} FETs and {} MTJs, found {} and {}".format(
                ix,expected_rows,expected_rows,
                sum(k=="fet" for e,k in devices),sum(k=="mtj" for e,k in devices)))
        if len(return_contacts[ix])!=expected_rows:
            die("case {} must have exactly {} direct ground return contacts, found {}. "
                "No guessed SL rewiring; inspect existing topology locally.".format(
                ix,expected_rows,len(return_contacts[ix])))
    modifications={}
    # One shared return per scenario; all four conceptual columns join at slgrp#.
    for ix in sorted(expected):
        sl="slgrp{}".format(group_by_case[ix])
        for e,pos in return_contacts[ix]:
            ns=list(e["nodes"])
            ns[pos]=sl
            replacement="{} ({}) {}{}".format(e["name"]," ".join(ns),e["model"],e["suffix"])
            if e["idx"] in modifications:die("duplicate modification line")
            modifications[e["idx"]]=replacement
    original=raw.splitlines()
    for index,line in modifications.items():original[index]=line
    # Insert before first analysis statement. resistor names chosen to not collide.
    existing={e["name"].lower() for e in entries}
    groups=sorted(set(group_by_case.values()))
    resist=[]
    for g in groups:
        name="RSLGRP{}".format(g)
        if name.lower() in existing:die("shared resistor name collision")
        resist.append("{} (slgrp{} 0) resistor r={:.12g}".format(name,g,ohms))
    position=next((i for i,s in enumerate(original) if ANALYSIS_RE.match(s)),len(original))
    original[position:position]=["// Assumed shared source-line return, NOT physical PEX"]+resist
    new="\n".join(original)+"\n"
    return new,dict(return_devices_rewired=sum(len(v) for v in return_contacts.values()),
                    individual_cases=len(expected),shared_groups=len(groups),
                    row_devices_per_case=expected_rows,
                    shared_return_assumed_ohms=ohms)

def verify_source():
    import e19_gf_nfet_mtj_nonideal_count_gate_v2 as e19
    source=Path(e19.__file__).resolve()
    if sha(source)!=E19_SHA:die("E19 verified generator SHA mismatch")
    mtj=Path.home()/e19.MODEL_REL
    if not mtj.is_file() or sha(mtj)!=MTJ_SHA or e19.MODEL_SHA!=MTJ_SHA:
        die("student MTJ mismatch")
    template_path=Path(e19.choose_template(None)).resolve()
    template=e19.parse_template(template_path)
    return e19,source,mtj,template_path,template

def run_spectre(deck,work,e19,timeout):
    work.mkdir(mode=0o700)
    target=work/"input.scs"
    target.write_text(deck)
    with (work/"stdout.log").open("w") as f:
        try:
            proc=subprocess.run(["spectre",str(target),"+log",str(work/"spectre.log"),
                                 "-format","psfascii"],cwd=str(work),
                                stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
            rc=proc.returncode
        except subprocess.TimeoutExpired:
            rc=124
    if rc:die("Spectre rc={} at {}, private log retained".format(rc,work))
    raw=work/"input.raw/dcOp.dc"
    if not raw.is_file():die("Spectre DC raw missing at {}".format(work))
    z=e19.parse_sources(raw)
    currents=[]
    for i in range(len(profiles())):
        key="VC%04d:p"%i
        if key not in z:die("missing GF current source "+key)
        currents.append(float(z[key]))
    return currents,sha(raw),sha(target)

def reconstruct_counts(ideal,paired,rows):
    # Statistical decoder benchmark only, no hardware ADC.
    ref={}
    for n in (0,1,2):
        v=[ideal[i] for i,p in enumerate(rows) if p["true_n"]==n]
        if not v:die("cannot calibrate exact P count n={}".format(n))
        ref[n]=sum(v)/len(v)
    vals=sorted(ref.items(),key=lambda x:x[0])
    if not (ref[0]<ref[1]<ref[2] or ref[0]>ref[1]>ref[2]):
        die("ideal GF current levels not monotone vs n; investigate P/AP polarity")
    out=[]
    for i,p in enumerate(rows):
        target=paired[i]
        guess=min(ref,key=lambda n:abs(target-ref[n]))
        # Continuous *software* interpolation/extrapolation of GF current to
        # count. This exposes sub-code compute distortion even when every
        # nearest-count decision stays correct (not an implemented ADC).
        ascending=ref[2]>ref[0]
        use_lower=(target<=ref[1]) if ascending else (target>=ref[1])
        if use_lower:
            continuous=(target-ref[0])/(ref[1]-ref[0])
        else:
            continuous=1.0+(target-ref[1])/(ref[2]-ref[1])
        out.append({"case":p["scenario"],"column":p["column"],"n_true":p["true_n"],
                    "n_decoded":guess,"n_error":guess-p["true_n"],
                    "continuous_count_estimate":continuous,
                    "continuous_count_error":continuous-p["true_n"],
                    "I_independent_A":ideal[i],"I_coupled_A":target,
                    "delta_nA":1e9*(target-ideal[i])})
    signed=[]
    for j in range(len(SCENARIOS)):
        q=out[4*j:4*j+4]
        signed.append({"scenario":SCENARIOS[j][0],
            "ideal_W4_sum":sum(SIGNED_W4_COEFF[c]*r["n_true"] for c,r in enumerate(q)),
            "decoded_W4_sum":sum(SIGNED_W4_COEFF[c]*r["n_decoded"] for c,r in enumerate(q)),
            "signed_W4_MAC_error":sum(SIGNED_W4_COEFF[c]*r["n_error"] for c,r in enumerate(q)),
            "signed_W4_continuous_MAC_error":sum(SIGNED_W4_COEFF[c]*r["continuous_count_error"] for c,r in enumerate(q))})
    return out,signed,ref

def execute(args):
    selftest()
    if not shutil.which("spectre"):die("Spectre not available in authorized NUS shell")
    e19,src,model,tpath,template=verify_source()
    base=Path(args.private).expanduser().resolve()
    base.mkdir(parents=True,exist_ok=True)
    work=base/("E28S_"+dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")+"_"+str(os.getpid()))
    work.mkdir(mode=0o700)
    rows=profiles()
    opts=argparse.Namespace(**vars(args))
    opts.rows=4; opts.m=2; opts.k=2; opts.vread=0.05; opts.vwl=0.8
    initial=work/"construction"
    initial.mkdir()
    original_path=e19.make_deck(initial,rows,0.,template,model,opts)
    original_path=Path(original_path)
    if not original_path.is_file():die("generator failed to create deck")
    independent_deck=original_path.read_text()
    group_by_case={i:i//4 for i in range(len(rows))}
    # Crucial topology gate BEFORE any coupled Spectre run.
    coupled={}
    for resistance in SHARED_OHMS:
        coupled[resistance]=rewire(independent_deck,group_by_case,resistance)
    print("E28S_PRIVATE_ROOT",work,flush=True)
    print("E28S_VERIFIED_E19_SHA256",sha(src),flush=True)
    print("E28S_ORIGINAL_TEMPLATE_SHA256",sha(tpath),flush=True)
    print("E28S_STATIC_MTJ_SHA256",sha(model),flush=True)
    print("E28S_RETURN_CONTACT_REWRITE_GATE_PASS",coupled[SHARED_OHMS[0]][1],flush=True)
    provenance={"experiment":"E28S_ASSUMED_SHARED_SL_FOUR_COLUMN_ACTUAL_GF",
       "status":"INCOMPLETE","real_GF_access_NFET":True,
       "student_static_MTJ":True,"physical_1T1_layout_PEX":False,
       "four_columns_simultaneous_in_single_Spectre_deck":True,
       "coupling_network":"shared return resistance per scenario, explicitly assumed",
       "shared_resistances_ASSUMED_ohms":SHARED_OHMS,
       "read_bias_historical_not_safety_certified":{"vread_V":0.05,"vwl_V":0.8},
       "no_chip_variation":True,"no_measured_covariance":True,
       "no_full_MNIST_inference":True,"software_count_decoder_not_physical_ADC":True,
       "selected_E19_generator_sha256":sha(src),"student_MTJ_sha256":sha(model),
       "selected_Gf_template_sha256":sha(tpath),
       "source_profile":rows,"raw_current_by_arm":{}}
    (work/"manifest.json").write_text(json.dumps(provenance,indent=2)+"\n")
    print("E28S_RUN INDEPENDENT baseline",flush=True)
    baseline,ih,dh=run_spectre(independent_deck,work/"independent",e19,args.timeout_sec)
    provenance["raw_current_by_arm"]["independent"]={"currents_A":baseline,"dc_sha256":ih,"deck_sha256":dh}
    # C0's *entire* active mask and P/AP state are unchanged across the
    # NEAR_LOW / MID / HIGH / MIX scenario family. Reject any baseline drift.
    base_c0=[baseline[4*j] for j in range(5)]
    if max(base_c0)-min(base_c0)>max(1e-14,abs(base_c0[0])*1e-7):
        die("independent C0 current differs despite identical C0 states/mask")
    print("E28S_C0_FIXED_INPUT_NULL_PASS",base_c0,flush=True)
    print("E28S_INDEPENDENT_DONE min_uA {:.9g} max_uA {:.9g}".format(
        1e6*min(baseline),1e6*max(baseline)),flush=True)
    for resistance in SHARED_OHMS:
        key="shared_{:g}_ohm".format(resistance)
        print("E28S_RUN",key,flush=True)
        readings,rh,deckhash=run_spectre(coupled[resistance][0],work/key,e19,args.timeout_sec)
        delta=max(abs(x-y) for x,y in zip(baseline,readings))
        relative=delta/max(max(abs(x) for x in baseline),1e-12)
        if resistance==SHARED_OHMS[0] and relative>0.001:
            die("near-zero return fails baseline-match 0.1% gate; inspect netlist before claiming coupling")
        reconstructed,signed,ref=reconstruct_counts(baseline,readings,rows)
        provenance["raw_current_by_arm"][key]={"currents_A":readings,
                "dc_sha256":rh,"deck_sha256":deckhash,
                "max_delta_nA":1e9*delta,"max_relative_delta":relative,
                "calibrated_ideal_count_currents_A":ref,
                "per_column_results":reconstructed,
                "signed_W4_toy_mac_per_scenario":signed}
        c0={z["case"]:z for z in reconstructed if z["column"]==0}
        near_neighbor_influence=1e9*(c0["NEAR_HIGH"]["I_coupled_A"]-c0["NEAR_LOW"]["I_coupled_A"])
        print("E28S_COUPLED_RESULT",key,
            "C0_NEIGHBOR_HIGH_MINUS_LOW_nA",near_neighbor_influence,
            "MAX_DELTA_nA",1e9*delta,
            "COUNT_WRONG",sum(z["n_error"]!=0 for z in reconstructed),
            "W4_TOY_MAC_ERRORS",[x["signed_W4_MAC_error"] for x in signed],
            "MAX_ABS_CONTINUOUS_W4_ERROR",max(abs(x["signed_W4_continuous_MAC_error"]) for x in signed),
            flush=True)
    provenance["status"]="FINISHED"
    final=work/"E28S_RESULTS.json"
    final.write_text(json.dumps(provenance,indent=2,sort_keys=True)+"\n")
    print("E28S_ACTUAL_GF_MULTI_COLUMN_RESULTS",final,flush=True)
    print("E28S_NOT_1T1_PEX_NOT_PHYSICAL_WIRE_R_NOT_STATISTICAL_CORRELATION_OR_NN_RESULT",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=["selftest","run"])
    p.add_argument("--private",default=str(Path.home()/"mram_private/E28_1T1"))
    p.add_argument("--timeout-sec",type=int,default=240)
    args=p.parse_args()
    if args.mode=="selftest":selftest()
    else:execute(args)

if __name__=="__main__":main()
