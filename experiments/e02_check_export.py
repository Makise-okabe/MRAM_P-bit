#!/usr/bin/env python3
"""Summarize genuine E02 exported matched-pattern currents, never fabricate readings.

CSV required:
case_id,matched_family,active_rows,selected_P,selected_AP,sense_column,
sample_time_s,sampled_current_A,source_sha256,array_netlist_sha256,readout_id
"""
import argparse, csv, hashlib, json
from collections import defaultdict
from pathlib import Path

FIELDS = (
    "case_id","matched_family","active_rows","selected_P","selected_AP",
    "sense_column","sample_time_s","sampled_current_A",
    "source_sha256","array_netlist_sha256","readout_id"
)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv_file",type=Path)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():p.error("Refuse overwrite: choose fresh --out")
    with a.csv_file.open(newline="") as f:
        d=csv.DictReader(f)
        missing=[x for x in FIELDS if x not in (d.fieldnames or [])]
        if missing:p.error("Missing: "+", ".join(missing))
        rows=list(d)
    if not rows:p.error("Empty CSV")
    fam=defaultdict(list)
    ids=set()
    for r in rows:
        cid=r["case_id"]
        if not cid or cid in ids:p.error("Missing or duplicate case_id")
        ids.add(cid)
        for x in ("active_rows","selected_P","selected_AP","sense_column"):r[x]=int(r[x])
        for x in ("sample_time_s","sampled_current_A"):r[x]=float(r[x])
        if r["selected_P"]+r["selected_AP"]!=r["active_rows"]:p.error("Inconsistent P/AP count: "+cid)
        if r["sense_column"] not in range(256):p.error("Invalid sense column: "+cid)
        if any(not r[x] for x in ("source_sha256","array_netlist_sha256","readout_id")):p.error("Missing provenance: "+cid)
        fam[r["matched_family"]].append(r)
    valid={};warning=[]
    for k,v in fam.items():
        if len(v)<2:continue
        same={(r["active_rows"],r["selected_P"],r["selected_AP"],r["sense_column"],r["sample_time_s"],r["readout_id"],r["source_sha256"],r["array_netlist_sha256"]) for r in v}
        if len(same)!=1:
            warning.append(k+" is not matched by count/time/readout/netlist")
            continue
        i=[r["sampled_current_A"] for r in v]
        valid[k]={"case_ids":[r["case_id"] for r in v],"difference_max_min_A":max(i)-min(i),"current_range_A":[min(i),max(i)]}
    out={"evidence_class":"EXPORTED_E02_CIRCUIT_RESULTS_NOT_INDEPENDENTLY_VERIFIED",
         "source_file_sha256":hashlib.sha256(a.csv_file.read_bytes()).hexdigest(),
         "num_rows":len(rows),"matched":valid,"warnings":warning,
         "not_claimed":["full-macro PEX","readout validity","physical novelty","energy improvement"]}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+"\n")
    print("Rows:",len(rows),"matched groups:",len(valid),"warnings:",len(warning))
    print("Saved",a.out)
if __name__=="__main__":
    main()
