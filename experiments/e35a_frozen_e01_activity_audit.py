#!/usr/bin/env python3
"""E35A: read-only frozen E01 W4A8 group-read activity schema/occupancy audit.

This is NOT Spectre and NOT a 1T1 physical read, 256x256 PEX or new neural
training run. Strictly verifies frozen E01 packet SHA before interpreting it.
Resolves candidate group occupancy histograms if they are unambiguous numeric
histograms; does not invent missing 256-row activity distribution.
Never publishes raw user checkpoint, activation vectors, foundry data or netlist.
Python 3.6+ stdlib only.
"""
from __future__ import print_function
import argparse, hashlib, json, math, os, pathlib, zipfile

EXPECTED="400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a"
SOURCE=pathlib.Path.home()/"MRAM_Path_Finding/experiments/runs/E01_MNIST_20261104T085558Z_038af9/review_packet.zip"
TRIGGERS=("occupancy","histogram","fanin","fan_in","active_rows","active_count","popcount","group")
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as fp:
        for b in iter(lambda:fp.read(1048576),b""):h.update(b)
    return h.hexdigest()
def stop(msg):raise SystemExit("E35A_BLOCKED: "+msg)

def describe(root,prefix="",depth=0,out=None):
    if out is None:out=[]
    if depth>10:return out
    if isinstance(root,dict):
        for k,v in root.items():
            k=str(k)
            name=(prefix+"."+k).strip(".")
            if any(x in k.lower() for x in TRIGGERS):
                out.append({"path":name,"node_type":type(v).__name__,
                    "dict_keys_first_16":list(v)[:16] if isinstance(v,dict) else None,
                    "length":len(v) if isinstance(v,(dict,list)) else None,
                    "numeric_scalar":float(v) if isinstance(v,(int,float))
                        and not isinstance(v,bool) and math.isfinite(float(v)) else None})
            describe(v,name,depth+1,out)
    elif isinstance(root,list):
        if len(root)>10000:return out
        for i,v in enumerate(root):
            if isinstance(v,(dict,list)):
                describe(v,prefix+"["+str(i)+"]",depth+1,out)
    return out

def histogram_candidates(obj,where=""):
    """Trust only key names containing occupancy/hist and numeric bin->counts."""
    results=[]
    if isinstance(obj,dict):
        for k,v in obj.items():
            name=(where+"."+str(k)).strip(".")
            kl=str(k).lower()
            if any(x in kl for x in ("occupancy_hist","active_rows_hist","fan_in_hist","fanin_hist","popcount_hist")):
                if isinstance(v,dict) and v:
                    try:
                        hist={int(key):int(value) for key,value in v.items()}
                        valid=all(str(int(key))==str(key) for key in v)
                        valid=valid and all(isinstance(value,(int,float))
                          and float(value).is_integer() and value>=0 for value in v.values())
                        valid=valid and all(0<=key<=256 for key in hist)
                    except (TypeError,ValueError):valid=False
                    if valid and sum(hist.values())>0:
                        total=sum(hist.values())
                        results.append({
                            "path":name,"type":"VERIFIED_NUMERIC_OCCUPANCY_HIST",
                            "bin_count":len(hist),"total_group_reads":total,
                            "max_active_rows":max(key for key,count in hist.items() if count>0),
                            "mean_active_rows":sum(key*count for key,count in hist.items())/float(total),
                            "all_bin_counts":{str(key):val for key,val in sorted(hist.items())}})
            results+=histogram_candidates(v,name)
    elif isinstance(obj,list):
        if len(obj)<2000:
            for i,v in enumerate(obj):
                if isinstance(v,(dict,list)):
                    results+=histogram_candidates(v,where+"["+str(i)+"]")
    return results

def selftest():
    x={"screen":{"group_256":{"occupancy_histogram":{"0":2,"1":3,"110":1}}}}
    h=histogram_candidates(x)
    assert len(h)==1 and h[0]["max_active_rows"]==110 and h[0]["mean_active_rows"]==113/6.0
    hints=describe(x)
    assert any("group_256" in j["path"] for j in hints)
    print("E35A_SELFTEST_PASS: packet activity schema, strict histogram bins/mean/max")
    print("E35A_SELFTEST_SOFTWARE_ONLY_NOT_GF_NOT_PEX")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("selftest","audit"))
    p.add_argument("--packet",type=pathlib.Path,default=SOURCE)
    p.add_argument("--out",type=pathlib.Path,default=None)
    args=p.parse_args()
    selftest()
    if args.mode=="selftest":return
    if not args.packet.is_file():stop("E01 frozen packet not present")
    if sha(args.packet)!=EXPECTED:stop("E01 frozen review_packet.zip SHA mismatch; do NOT proceed")
    entries=[]
    hints=[]
    histograms=[]
    with zipfile.ZipFile(str(args.packet),"r") as packet:
        infos=packet.infolist()
        if len(infos)>200:stop("Unusually large packet member count")
        for info in infos:
            if info.is_dir():continue
            path=info.filename.replace("\\","/")
            if path.startswith("/") or ".." in path.split("/"):
                stop("unsafe ZIP member")
            if not path.lower().endswith(".json"):continue
            if info.file_size>8*1024*1024:stop("JSON member too large")
            entries.append({"path":path,"size_bytes":info.file_size})
            if path.endswith("screen.json"):
                raw=packet.read(info)
                try:obj=json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError,ValueError):stop("malformed screen.json")
                hints.extend([dict({"member":path},**x) for x in describe(obj)[:250]])
                histograms.extend([dict({"member":path},**x) for x in histogram_candidates(obj)])
    if not entries:stop("No JSON documents in frozen packet")
    report={
        "status":"E35A_COMPLETED_SCHEMA_AUDIT",
        "source":"frozen E01 W4A8 packet, NUS software traces only",
        "packet_SHA256":EXPECTED,
        "screen_json_count":sum(x["path"].endswith("screen.json") for x in entries),
        "json_entries":entries,
        "activity_related_schema_hints":hints,
        "verified_occupancy_histograms":histograms,
        "full_256row_activity_distribution_verified":any(
          "256" in x["path"] or "256" in x["member"] for x in histograms),
        "caveat":"Histogram labels require physical scheduling review; no GF interconnect/ADC/MTJ failures measured",
        "no_Spectre":True,"no_PEX":True,"no_licensed_model_export":True}
    out=args.out if args.out is not None else (
        pathlib.Path.home()/"mram_private/E35_E01_activity/E35A_schema_audit.json")
    out=out.expanduser().resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():stop("Refuse overwrite "+str(out))
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("E35A_SOURCE_PACKET_SHA256",EXPECTED)
    print("E35A_SCREEN_JSON_COUNT",report["screen_json_count"])
    print("E35A_VERIFIED_HISTOGRAMS",len(histograms))
    for x in histograms:
        print("E35A_HISTOGRAM",x["member"],x["path"],
              "TOTAL",x["total_group_reads"],
              "MEAN_M",x["mean_active_rows"],"MAX_M",x["max_active_rows"])
    if not histograms:
        print("E35A_SCHEMA_ONLY: 256-group histogram NOT inferred; inspect private schema hints")
    print("E35A_SAFE_OUTPUT",out)
    print("E35A_NOT_GF_SPECTRE_NOT_PEX_NOT_PHYSICAL_ARRAY_256x256")
if __name__=="__main__":main()
