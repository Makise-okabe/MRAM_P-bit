#!/usr/bin/env python3
"""E02 zero-bias integration smoke test, NOT new 256x256 physical validation.

Construct a NEW hierarchical array from the existing verified 4x4 DSPF as a
licensed read-only engineering source. PEX is present INSIDE each tile only.
Inter-tile wires are IDEAL and have NO extracted R/C. No old read measurements,
voltage settings, P/AP distributions, Monte Carlo, or ADC data are imported.

Default creates a 16x16 electrically connected 2T1MTJ/PDEX composite and runs
zero-bias Spectre (all BL/SL/WLL/WLR/PW = 0 V). This is an assembly check ONLY.
256x256 deck can be generated with --size 256 but --run is prohibited for it.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

SUBCKT="M047_GF_4x4_TILE_TEST"
EXPECTED=(
    [f"SL[{i}]" for i in range(5)] +
    [pin for i in range(4) for pin in (f"WLL[{i}]",f"WLR[{i}]")] +
    [f"BL[{i}]" for i in range(4)] + ["PW"]
)
PDK_MODEL=Path("/apps/PDK/GF/22FDX-PLUS/V1.0_2.4c/Models/Spectre/models/mtj_fls.scs")
DSPF=Path.home()/(
    "mram_fyp/cadence/calibre/xact/M047_GF_4x4_TILE_TEST_PEX/"
    "M047_GF_4x4_TILE_TEST.pex.dspf"
)
DEFAULT_PRIVATE=Path.home()/"mram_private/E02_256x256"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dspf_pins(path):
    with path.open(errors="replace") as f:
        lines=iter(f)
        for line in lines:
            if re.match(r"^\s*\.subckt\s+",line,re.I):
                chunks=[line.strip()]
                for nxt in lines:
                    if nxt.lstrip().startswith("+"):
                        chunks.append(nxt.lstrip()[1:].strip())
                    else:break
                tokens=" ".join(chunks).split()
                return tokens[1],tokens[2:]
    raise RuntimeError("No subckt header in input DSPF")

def build(n,out,manifest,dspf,wrapper):
    cell_size=4
    nt=n//cell_size
    generated_cells=nt*nt*16
    if not manifest.is_file():
        raise RuntimeError("Missing proposed whole-array manifest: "+str(manifest))
    if n==256:
        seen=0
        with manifest.open(newline="") as f:
            reader=csv.DictReader(f)
            for row in reader:
                r,c=int(row["row"]),int(row["column"])
                if row["BL"]!=f"BL_{c:03d}" or row["SL0"]!=f"SL_{r:03d}" or row["SL1"]!=f"SL_{r+1:03d}":
                    raise RuntimeError("Manifest topology mismatch")
                seen+=1
        if seen!=65536:raise RuntimeError("Manifest count does not equal 65,536")

    lines=[
        "simulator lang=spectre",
        "// E02 ZERO-BIAS integration smoke. NOT a calibrated read experiment.",
        "// Existing 4x4 PEX topology reused; ZERO inter-tile R/C -> NOT full-array PEX.",
        "// Cell states remain DEFAULT in PDK; no P/AP matrix configured.",
        'include "'+str(wrapper)+'" section=tt_pre',
        'include "'+str(PDK_MODEL)+'"',
        'dspf_include "'+str(dspf)+'" port_order=spf',
        ""
    ]
    for c in range(n):
        lines.append(f"VBL{c:03d} (BL_{c:03d} 0) vsource type=dc dc=0")
    for r in range(n+1):
        lines.append(f"VSL{r:03d} (SL_{r:03d} 0) vsource type=dc dc=0")
    for r in range(n):
        lines.append(f"VWLL{r:03d} (WLL_{r:03d} 0) vsource type=dc dc=0")
        lines.append(f"VWLR{r:03d} (WLR_{r:03d} 0) vsource type=dc dc=0")
    lines.append("VPW (PW 0) vsource type=dc dc=0")
    lines.append("")
    tile_n=0
    for rr in range(0,n,4):
        for cc in range(0,n,4):
            sl=[f"SL_{rr+i:03d}" for i in range(5)]
            wl=[v for i in range(4) for v in (
                 f"WLL_{rr+i:03d}",f"WLR_{rr+i:03d}")]
            bl=[f"BL_{cc+i:03d}" for i in range(4)]
            pins=sl+wl+bl+["PW"]
            assert len(pins)==18
            lines.append(f"X_T_R{rr:03d}_C{cc:03d} ({' '.join(pins)}) {SUBCKT}")
            tile_n+=1
    assert tile_n==nt*nt and generated_cells==n*n
    # Not a read pulse; do not infer analog margins from this test.
    lines.extend(["","tran_initial tran stop=1n maxstep=100p",""])
    path=out/"input.scs"
    path.write_text("\n".join(lines))
    return path,tile_n

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--size",type=int,choices=(16,256),default=16)
    p.add_argument("--run",action="store_true")
    p.add_argument("--private",type=Path,default=DEFAULT_PRIVATE)
    args=p.parse_args()
    if args.size==256 and args.run:
        p.error("256x256 full-netlist Spectre run deliberately blocked: inter-tile wires uncharacterized; run 16x16 first.")
    if not DSPF.is_file() or not PDK_MODEL.is_file():
        p.error("Missing authorized PDK MTJ model or local extracted 4x4 cell")
    name,pins=dspf_pins(DSPF)
    if name!=SUBCKT or pins!=EXPECTED:
        p.error("4x4 extracted header differs from required 18-pin topology: "+
                repr((name,pins)))
    model_root=os.getenv("SPECTRE_MODEL_PATH","")
    wrapper=Path(model_root)/"design_wrapper.lib.scs" if model_root else None
    if not wrapper or not wrapper.is_file():
        p.error("SPECTRE_MODEL_PATH/design_wrapper.lib.scs unavailable in this shell. Do not guess model setup.")
    if args.run and not shutil.which("spectre"):
        p.error("Spectre missing; run inside authorized Singularity environment.")
    private=args.private.resolve()
    if not private.is_dir():p.error("Private E02 workspace not found")
    private.joinpath("raw").mkdir(exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    folder=private/"raw"/f"E02_{args.size}x{args.size}_zero_bias_{stamp}_{os.getpid()}"
    folder.mkdir(mode=0o700)
    input_file,tile_n=build(args.size,folder,
        private/"config/E02_256x256_connectivity_PROPOSAL.csv",DSPF,wrapper)
    provenance={
        "experiment":"E02_zero_bias_PEX_inside_4x4_tile_integration",
        "evidence_class":"ELECTRICAL_ASSEMBLY_SMOKE_IF_SPECTRE_COMPLETES",
        "array_size":args.size,"n_tiles":tile_n,"MTJ_sites":args.size**2,
        "source_pex_sha256":sha(DSPF),
        "generated_netlist_sha256":sha(input_file),
        "whole_array_pex":False,"intertile_wire_RC":"ABSENT_IDEAL_JOIN",
        "active_read_bias":"NONE_ALL_ZERO",
        "P_AP_programmed":"NO_DEFAULT_MODEL_STATE",
        "historical_read_data_used":False,
        "usable_for_spatial_error_claim":False,
        "user_must_verify_licensed_parameters_locally":True
    }
    (folder/"provenance.json").write_text(json.dumps(provenance,indent=2)+"\n")
    print("E02_INPUT:",input_file,flush=True)
    print("E02_CASE_DIR:",folder,flush=True)
    print(f"E02_ASSEMBLY: {args.size}x{args.size}, {tile_n} extracted 4x4 tiles, {args.size**2} MTJ sites",flush=True)
    print("E02_LIMITATION: zero-bias-only; intra-tile PEX, missing intertile parasitics",flush=True)
    if args.run:
        cmd=["timeout","300s","spectre",str(input_file),"+log",str(folder/"spectre.log"),"-format","psfascii"]
        with (folder/"stdout.log").open("w") as stream:
            rc=subprocess.run(cmd,cwd=folder,stdout=stream,stderr=subprocess.STDOUT).returncode
        txt=(folder/"spectre.log").read_text(errors="replace") if (folder/"spectre.log").exists() else ""
        txt+="\n"+(folder/"stdout.log").read_text(errors="replace")
        matches=[line.strip()[:280] for line in txt.splitlines()
                 if re.search(r"ERROR|FATAL|SPECTRE-[0-9]+|terminated|complete|completed|warnings|successful",line,re.I)]
        print("E02_SPECTRE_EXIT:",rc,flush=True)
        for line in matches[-22:]:print("SPECTRE_LOG:",line,flush=True)
        (folder/"exit_status.json").write_text(json.dumps({
            "spectre_exit_code":rc,"completed_successfully":rc==0,
            "valid_read_measurements":False,"whole_array_PEX":False},indent=2)+"\n")
        if rc:return rc
    return 0

if __name__=="__main__":
    sys.exit(main())
