#!/usr/bin/env python3
"""2026-11-20 locked viewed-dense first block: 1,280 trials, no device errors.

Commands: --freeze, --run, --analyse. Requires original Biq Mac
Rudy files; never substitutes generated data or reuses historical outcomes.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from pathlib import Path
import random

from experiments.biqmac_maxcut import load_rudy
from experiments.m0_ising_math import sigmoid
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph, original_cut, prepare, represented_energy
from experiments.m1_biqmac_reference_quality_gate import schedule_beta, solve_reference
from experiments.m1_precision_codebooks import build_global

GRAPH_INFO = (
    ("ising2.5-100_5555", "c8fa3ce4df1997b89aad6199525a66e55699c259680483b62cc5fd3cfc1e316e", 2460049, 3000000000000),
    ("ising2.5-100_7777", "109e1ed2edc71d5f43d623367410d9257a72662d665c7a0c71af4cdd8babaf99", 3363230, 3000000020000),
)
ARMS = (("ref64", "ref64", "raw"), ("fp5_raw", "fp5", "raw"),
        ("int6_raw", "int6", "raw"), ("fp5_cal", "fp5", "calibrated"),
        ("int6_cal", "int6", "calibrated"))
SEEDS_PER_GRAPH = 128
UPDATES = 50000
CHECKPOINTS = (5000, 15000, 30000, 50000)
OUT = Path("results/fyp_first_block_20261120")
GRAPH_DIR = Path("data/biqmac/raw/ising")
SOURCE_FILES = ("experiments/fyp_first_block_20261120.py",
                "experiments/fyp_first_block_stats.py",
                "experiments/m1_biqmac_reference_quality_gate.py",
                "experiments/m1_biqmac_ideal_pilot.py",
                "experiments/m1_precision_codebooks.py",
                "experiments/biqmac_maxcut.py",
                "experiments/m0_ising_math.py")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hex_state(spins):
    return format(sum(1 << i for i, s in enumerate(spins) if s > 0), "x")


def state_from_hex(value, n):
    number = int(value, 16)
    if number >> n:
        raise ValueError("state has bits beyond graph size")
    return tuple(1 if (number >> i) & 1 else -1 for i in range(n))


def projection(graph, rep):
    if len(graph.edges) != len(rep["edges"]):
        raise ValueError("source/quantizer edge count mismatch")
    den, num = 0.0, 0.0
    for (i, j, w), (u, v, q) in zip(graph.edges, rep["edges"]):
        if (i, j) != (u, v):
            raise ValueError("source/quantizer edge order mismatch")
        x = -float(w)
        num += x*q
        den += x*x
    if den <= 0 or num <= 0:
        raise ValueError("nonpositive source projection")
    return num/den


def solve_logged(graph, rep, beta, updates, seed, *, source_rep=None, checkpoints=CHECKPOINTS):
    """Passive dual-cache instrumentation of the existing 50k linear controller.

    Original-cut cache is scoring-only. RNG use, represented-field operations,
    strict represented-energy retention and spin mutations mirror solve_reference.
    """
    if not (updates >= 1 and beta > 0 and math.isfinite(beta)):
        raise ValueError("invalid beta/updates")
    if any(t < 1 or t > updates for t in checkpoints):
        raise ValueError("checkpoint outside attempts")
    rng = random.Random(seed)
    spins = [1 if rng.randrange(2) else -1 for _ in range(graph.n)]
    adj = rep["adjacency"]
    fields = [sum(q*spins[j] for j, q in adj[i]) for i in range(graph.n)]
    energy = represented_energy(rep["edges"], spins)
    best_e = energy
    best_state = tuple(spins)
    source_rep = source_rep or prepare(graph, "ref64", "source")
    src_adj = source_rep["adjacency"]
    src_field = [sum(q*spins[j] for j, q in src_adj[i]) for i in range(graph.n)]
    current_cut = original_cut(graph, spins)
    V = M = R = current_cut
    V_state = M_state = best_state
    flips = 0
    improvements = 0
    snaps = []
    checkpoint_set = set(checkpoints)
    for step in range(updates):
        i = rng.randrange(graph.n)
        u = rng.random()
        b = schedule_beta(beta, "linear", step, updates)
        old = spins[i]
        nxt = 1 if u < sigmoid(2*b*fields[i]) else -1
        if nxt != old:
            delta = nxt-old
            # For J=-w and h=0, delta(original cut) = -s_old * H_original.
            current_cut -= old*src_field[i]
            energy += 2*old*fields[i]
            spins[i] = nxt
            flips += 1
            for j,q in adj[i]:
                fields[j] += q*delta
            for j,q in src_adj[i]:
                src_field[j] += q*delta
        if current_cut > V:
            V, V_state = current_cut, tuple(spins)
        if energy < best_e:
            best_e = energy
            best_state = tuple(spins)
            improvements += 1
            R = M = current_cut
            M_state = best_state
        elif energy == best_e and current_cut > M:
            M, M_state = current_cut, tuple(spins)
        if step+1 in checkpoint_set:
            if not math.isclose(current_cut, original_cut(graph, spins), rel_tol=0, abs_tol=1e-6):
                raise AssertionError("original-score incremental cache drift")
            snaps.append({"attempt":step+1,"beta":b,
                          "current_state_hex":hex_state(spins),
                          "V":V,"M":M,"R":R,
                          "unreached":None,"selection":V-M,"tie":M-R})
    final_e = represented_energy(rep["edges"], spins)
    saved = represented_energy(rep["edges"], best_state)
    if not math.isclose(final_e, energy, rel_tol=1e-7, abs_tol=1e-7):
        raise AssertionError("final represented energy parity failed")
    if not math.isclose(saved, best_e, rel_tol=1e-7, abs_tol=1e-7):
        raise AssertionError("retained represented energy parity failed")
    for score, st in ((V,V_state),(M,M_state),(R,best_state)):
        if not math.isclose(score,original_cut(graph,st),rel_tol=0,abs_tol=1e-6):
            raise AssertionError("trajectory scored state mismatch")
    if not V+1e-6 >= M >= R-1e-6:
        raise AssertionError("trajectory loss ordering failed")
    return {"seed":seed,"attempted_updates":updates,"actual_flips":flips,
            "improvements":improvements,"returned_original_cut":R,
            "final_original_cut":original_cut(graph,spins),
            "returned_represented_energy":saved,
            "final_represented_energy":final_e,
            "returned_state_hex":hex_state(best_state),
            "V":V,"M":M,"R":R,"V_state_hex":hex_state(V_state),
            "M_state_hex":hex_state(M_state),"checkpoints":snaps}


def compare_solver(graph, rep, beta, updates, seed):
    old = solve_reference(graph, rep, beta, updates, seed, "linear")
    new = solve_logged(graph, rep, beta, updates, seed, checkpoints=(updates,))
    for key in ("returned_state_hex","actual_flips","improvements",
                "returned_original_cut","returned_represented_energy",
                "final_represented_energy","final_original_cut"):
        if old[key] != new[key]:
            raise AssertionError(f"solver parity {key}: {old[key]} != {new[key]}")
    return new


def field_fidelity(graph, ref_state_hex, rep, beta):
    spins = state_from_hex(ref_state_hex, graph.n)
    orig = prepare(graph, "ref64", "source")["adjacency"]
    field_ref = [sum(q*spins[j] for j,q in adj) for adj in orig]
    field_q = [sum(q*spins[j] for j,q in adj) for adj in rep["adjacency"]]
    n = graph.n
    rms = math.sqrt(sum((a-b)**2 for a,b in zip(field_q,field_ref))/n)
    logit_rms = 2*beta*rms
    prob_mae = sum(abs(sigmoid(2*beta*a)-sigmoid(2*beta*b))
                   for a,b in zip(field_q,field_ref))/n
    return {"field_rms":rms,"logit_rms":logit_rms,"probability_mae":prob_mae}


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)


def seal(obj):
    return {**obj,"record_sha256":hashlib.sha256(canonical(obj).encode()).hexdigest()}


def read_jsonl(path):
    if not path.exists():
        return []
    rows=[]
    with path.open(encoding="utf-8") as f:
        for lineno,line in enumerate(f,1):
            try:
                row=json.loads(line)
                tag=row.pop("record_sha256")
                if hashlib.sha256(canonical(row).encode()).hexdigest()!=tag:
                    raise ValueError("record digest mismatch")
                rows.append(row)
            except Exception as e:
                raise ValueError(f"corrupt {path}:{lineno}: {e}") from e
    return rows


def append_jsonl(path, obj):
    with path.open("a",encoding="utf-8") as f:
        f.write(canonical(seal(obj))+"\n")
        f.flush()
        os.fsync(f.fileno())


def get_graphs(graph_dir):
    graphs=[]
    for name,sha,optimum,base in GRAPH_INFO:
        path=graph_dir/name
        if not path.is_file():
            raise FileNotFoundError(f"missing original: {path} (official Biq Mac mac/ising)")
        if digest(path)!=sha:
            raise ValueError(f"original graph SHA256 mismatch: {path}")
        g=load_rudy(path)
        if g.sha256!=sha or g.n!=100:
            raise ValueError("source identity/size mismatch")
        graphs.append((g,optimum,base))
    return graphs


def sha_sources():
    return {p:digest(p) for p in SOURCE_FILES}


def git_head():
    try:
        return subprocess.check_output(["git","rev-parse","HEAD"],text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "UNAVAILABLE"


def settings(graphs):
    return {
        "lock":"docs/FYP_STUDY_LOCK_20261120.md", "protocol_date":"2026-11-20",
        "status":"FROZEN_NOT_EXECUTED","source_commit":git_head(),
        "source_sha256":sha_sources(),"python":platform.python_version(),
        "python_implementation":platform.python_implementation(),
        "platform":platform.platform(), "rng":"random.Random(MT19937)",
        "graph_sources":[{"name":g.source.rsplit("/",1)[-1],"sha256":g.sha256,
                          "published_optimum":optimum,"seed_first":base,
                          "seed_last":base+127,"beta_source":beta_from_original_graph(g)}
                         for g,optimum,base in graphs],
        "seeds":{g.source.rsplit("/",1)[-1]:list(range(base,base+128))
                 for g,_,base in graphs},
        "format":"FP5 E2M2 vs INT6; FP64 reference", "arms":[list(a) for a in ARMS],
        "expected_unique_records":1280,"raw_records":768,"calibrated_controls":512,
        "updates":UPDATES,"schedule":"linear beta_G*(0.5+1.5*t/(49999))",
        "beta_calibration":"same source-MSE Q, beta(t)/a; a=<J,Q>/<J,J>",
        "stochastic_response":"gain=1 offset=0, ideal logistic",
        "retention":"earliest strict minimum incremental represented energy",
        "graph_J":"J_ij=-w_ij, h_i=0, symmetric", "checkpoints":list(CHECKPOINTS),
        "bootstrap":"studentized paired bootstrap-t, 500000 draws, NumPy PCG64 seed, linear quantiles; descriptive 95% per fixed graph",
        "first_block_inference":"paired seeds within each fixed viewed graph only; no family-level width claim"
    }


def archived_parity(graphs):
    """Compare deterministic historical runs as independent parity controls."""
    files = (
       (Path("results/e0_fp64_two_cal_20261112/run_rows.csv"),"ising2.5-100_5555",{"schedule":"linear_legacy","attempted_updates":"50000","configuration":None},"ref64"),
       (Path("results/m2_heldout_dense_fp6_int6_20261109/runs.csv"),"ising2.5-100_7777",{"configuration":"ref64","offset_logit_halfspan":"0.0","attempted_updates":"50000"},"ref64"),
       (Path("results/ex1_m5_fp5_int8_20261115/new_runs.csv"),"ising2.5-100_7777",{"configuration":"fp5","offset_logit_halfspan":"0.0","attempted_updates":"50000"},"fp5"),
    )
    byname={g.source.rsplit("/",1)[-1]:g for g,_,_ in graphs}
    audited=[]
    for file,name,filters,fmt in files:
        if not file.is_file():
            raise FileNotFoundError(f"required deterministic replay source missing: {file}")
        with file.open(newline="",encoding="utf-8") as f:
            eligible=[r for r in csv.DictReader(f)
                      if r.get("graph")==name and all((r.get(k)==v) for k,v in filters.items() if v is not None)]
        if not eligible:
            raise ValueError(f"no matching archival replay {file}")
        historic=eligible[0]
        g=byname[name]
        rep=prepare(g,"ref64","source") if fmt=="ref64" else build_global(g,"fp",5)
        beta=beta_from_original_graph(g)
        seed=int(historic["seed"])
        replay=compare_solver(g,rep,beta,UPDATES,seed)
        for key in ("returned_state_hex","actual_flips","improvements",
                    "returned_original_cut","returned_represented_energy"):
            old=historic[key]
            if key=="returned_state_hex":
                good=(old==replay[key])
            else:
                good=(float(old)==float(replay[key]))
            if not good:
                raise AssertionError(f"archive parity failed {file}:{seed} {key}: {old} != {replay[key]}")
        audited.append({"file":str(file),"file_sha256":digest(file),"graph":name,
                        "seed":seed,"format":fmt,"result":"PASS"})
    return audited


def freeze(graph_dir, out):
    graphs=get_graphs(graph_dir)
    if (out/"frozen_settings.json").exists():
        previous=json.loads((out/"frozen_settings.json").read_text())
        now=settings(graphs)
        if {k:previous[k] for k in now}!=now:
            raise ValueError("existing freeze differs; refusing to overwrite or mix source")
        return previous
    if out.exists() and any(out.iterdir()):
        raise ValueError("nonempty output directory without valid freeze")
    # Verify INT7 implementation without adding it to this block.
    from experiments.m1_precision_codebooks import describe_codebook,scalar_quantize,WIDTHS
    assert WIDTHS==(4,5,6,8) and describe_codebook("int",7)["max_represented"]==63
    assert scalar_quantize(2.5,"int",7,1.0)==2
    for graph,_,_ in graphs:
        beta=beta_from_original_graph(graph)
        reps=[prepare(graph,"ref64","source"),build_global(graph,"fp",5),build_global(graph,"int",6)]
        for rep in reps:
            compare_solver(graph,rep,beta,180,123456789)
    historic=archived_parity(graphs)
    obj=settings(graphs)
    obj["archived_parity"]=historic
    # freeze notes must include library version before any runs
    try:
        import numpy
        obj["numpy_version"]=numpy.__version__
        if numpy.__version__!="2.3.5":
            raise ValueError("NumPy 2.3.5 required for frozen analysis")
    except ImportError as e:
        raise RuntimeError("install NumPy 2.3.5 before freeze") from e
    out.mkdir(parents=True,exist_ok=True)
    (out/"frozen_settings.json").write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    return obj


def run(graph_dir,out):
    graphs=get_graphs(graph_dir)
    frozen=json.loads((out/"frozen_settings.json").read_text())
    if frozen!=freeze(graph_dir,out):
        raise ValueError("frozen settings mismatch")
    if frozen["source_commit"]=="UNAVAILABLE":
        raise ValueError("requires git source commit for provenance")
    rows=read_jsonl(out/"records.jsonl")
    expected={(name,base+r,arm) for name,_,_,base in GRAPH_INFO
              for r in range(SEEDS_PER_GRAPH) for arm,_,_ in ARMS}
    observed={}
    for row in rows:
        key=(row["graph"],row["seed"],row["arm"])
        if key not in expected or key in observed:
            raise ValueError(f"invalid or duplicate existing observation: {key}")
        observed[key]=row
    print(f"PRE-FLIGHT existing valid run records={len(rows)}; expected 1280",flush=True)
    for graph,optimum,base in graphs:
        name=Path(graph.source).name
        beta=beta_from_original_graph(graph)
        source=prepare(graph,"ref64","source")
        representations={"ref64":source,"fp5":build_global(graph,"fp",5),
                         "int6":build_global(graph,"int",6)}
        scales={f:projection(graph,rep) for f,rep in representations.items() if f!="ref64"}
        for arm,fmt,condition in ARMS:
            rep=representations[fmt]
            applied_beta=beta if condition=="raw" else beta/scales[fmt]
            for r in range(SEEDS_PER_GRAPH):
                seed=base+r
                key=(name,seed,arm)
                if key in observed:
                    continue
                sample=solve_logged(graph,rep,applied_beta,UPDATES,seed,source_rep=source)
                returned=sample["returned_original_cut"]
                if returned>optimum+1e-6:
                    raise AssertionError("published optimum exceeded")
                if abs((optimum-returned)-((optimum-sample["V"])+(sample["V"]-sample["M"])+(sample["M"]-sample["R"])))>1e-6:
                    raise AssertionError("decomposition identity failed")
                record={"graph":name,"graph_sha256":graph.sha256,"official_optimum":optimum,
                        "seed":seed,"arm":arm,"representation":fmt,"condition":condition,
                        "source_projection_a":1.0 if fmt=="ref64" else scales[fmt],
                        "source_scale":rep["scale"],"beta_G":beta,
                        "applied_beta_G":applied_beta,"schedule":"linear",
                        **sample,"gap_pct":100*(optimum-returned)/optimum}
                append_jsonl(out/"records.jsonl",record)
                observed[key]=record
            print(f"RUN {name} {arm}: 128/128 complete",flush=True)
    if len(observed)!=1280:
        raise AssertionError(f"expected 1280 unique outcomes, got {len(observed)}")
    # Recompute same-state fidelity only after primary run set is complete.
    fidelity_path=out/"fidelity.jsonl"
    done={}
    for row in read_jsonl(fidelity_path):
        key=(row["graph"],row["seed"],row["attempt"],row["representation"])
        if key in done:
            raise ValueError("duplicate fidelity")
        done[key]=row
    for graph,_,base in graphs:
        name=Path(graph.source).name
        reps={"fp5":build_global(graph,"fp",5),"int6":build_global(graph,"int",6)}
        for r in range(SEEDS_PER_GRAPH):
            seed=base+r
            ref=observed[(name,seed,"ref64")]
            for point in ref["checkpoints"]:
                for fmt,rep in reps.items():
                    key=(name,seed,point["attempt"],fmt)
                    if key in done:
                        continue
                    data={"graph":name,"seed":seed,"attempt":point["attempt"],
                          "representation":fmt,"reference_beta":point["beta"],
                          "reference_state_hex":point["current_state_hex"],
                          **field_fidelity(graph,point["current_state_hex"],rep,point["beta"])}
                    append_jsonl(fidelity_path,data)
                    done[key]=data
    if len(done)!=2048:
        raise AssertionError(f"fidelity expected 2048, got {len(done)}")
    print("FIRST BLOCK RAW COMPLETE: 1280 unique paired runs and 2048 common-state checkpoints",flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--freeze",action="store_true")
    ap.add_argument("--run",action="store_true")
    ap.add_argument("--analyse",action="store_true")
    ap.add_argument("--graph-dir",type=Path,default=GRAPH_DIR)
    ap.add_argument("--out",type=Path,default=OUT)
    args=ap.parse_args()
    if not (args.freeze or args.run or args.analyse):
        ap.error("choose --freeze, --run, --analyse")
    if args.freeze:
        data=freeze(args.graph_dir,args.out)
        print("FROZEN",data["source_commit"],"historical replays",len(data["archived_parity"]),flush=True)
    if args.run:
        run(args.graph_dir,args.out)
    if args.analyse:
        from experiments.fyp_first_block_stats import analyse
        analyse(args.out)


if __name__=="__main__":
    main()
