#!/usr/bin/env python3
"""M3 bridge: official original Biq Mac J -> frozen M1 six-bit bits -> row RTL.

Exports ONE original 100-spin graph's one off-diagonal 99-term row, for
FP6/INT6/BFP6 with identical source spins. No Max-Cut solver or model
retuning. Intended to feed existing rtl/tb_m3_row.v via +VEC.
Graph file and published optimum are SHA-checked against official E0 JSON.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
from pathlib import Path

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_precision_sweep import GRAPH_NAMES
from experiments.m1_biqmac_reference_quality_gate import official_reference
from experiments.m1_precision_codebooks import build_global
from experiments.m3_sixbit_encoding import (
    decode_raw_sixbit, encode_quantized_sixbit, row_coupling_value
)

SPIN_SEED = 20261107
ROW_INDEX = 0
REFS = Path("docs/BIQMAC_OFFICIAL_OPTIMA_2007.json")


def build_one_graph_vectors(graph_path: Path, output: Path, *,
                            row_index: int = ROW_INDEX, seed: int = SPIN_SEED):
    if output.exists():
        raise ValueError("refuse overwrite of existing vector directory")
    if graph_path.name not in GRAPH_NAMES:
        raise ValueError("only three frozen M1 Biq Mac Mac CAL graphs supported")
    graph = load_rudy(graph_path)
    if graph.n != 100 or not 0 <= row_index < graph.n:
        raise ValueError("frozen 100-spin graph and valid row required")
    sources = json.loads(REFS.read_text(encoding="utf-8"))
    if sources.get("reference_type") != "PUBLISHED_OPTIMUM":
        raise ValueError("unverified optimum type")
    optimum = official_reference(graph,sources["graphs"][graph_path.name],sources)
    rng = random.Random(seed)
    spins = [1 if rng.randrange(2) else -1 for _ in range(graph.n)]
    output.mkdir(parents=True,exist_ok=False)
    out = dict(
        evidence="M3 CODE/RTL INTEGRITY INPUT ONLY, NOT MAX-CUT SOLVER OR PHYSICAL DEVICE",
        graph=graph_path.name, graph_sha256=graph.sha256,
        reference_type="PUBLISHED_OPTIMUM",published_optimum=optimum,
        n_spins=graph.n,row_index=row_index,spin_seed=seed,
        spins_state_hex=format(sum(1<<i for i,s in enumerate(spins) if s>0),"x"),
        original_J="J_ij=-w_ij mirrored, J_ii=0, h_i=0",
        rows={},
        frozen_m1_codebook="finite-only FP6 E3M2, symmetric INT6, global BFP6",
        scope="coefficient decode and integer accumulator only, global scale applied Python-side",
    )
    for family in ("fp","int","bfp"):
        rep = build_global(graph,family,6)
        neighbors = dict(rep["adjacency"][row_index])
        vector_path = output/f"m3_{family}6_vectors.txt"
        acc = 0
        expected_h = 0.0
        with vector_path.open("x",encoding="ascii") as fp:
            for j in range(graph.n):
                if j == row_index:
                    continue
                q = neighbors.get(j,0.0)
                raw = encode_quantized_sixbit(q,rep["scale"],family)
                s = spins[j]
                acc += decode_raw_sixbit(raw,family)*s
                expected_h += q*s
                fp.write(f"{raw:02x} {int(s==1)} {acc}\n")
        got_h = row_coupling_value(acc,family,rep["scale"])
        if not math.isclose(expected_h,got_h,rel_tol=2e-11,abs_tol=1e-7):
            raise AssertionError(f"{family} original represented J vs decoded row mismatch: {expected_h} {got_h}")
        if vector_path.read_text(encoding="ascii").count("\n") != graph.n-1:
            raise AssertionError("not a full off-diagonal row")
        out["rows"][family+"6"] = dict(
            source_only_scale=rep["scale"],
            scale_metadata_bits=rep["scale_metadata_bits"],
            signed_integer_accum=acc,
            fp6_q4=(family=="fp"),
            represented_J_local_field_from_M1=expected_h,
            represented_J_local_field_from_bits=got_h,
            absolute_roundtrip_difference=abs(expected_h-got_h),
            vector_file=vector_path.name,
            vector_sha256=hashlib.sha256(vector_path.read_bytes()).hexdigest(),
            n_terms=graph.n-1,
        )
    (output/"manifest.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--graph",type=Path,required=True,help="original NUS Mac source file; 100 nodes")
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--row",type=int,default=ROW_INDEX)
    args=ap.parse_args()
    data=build_one_graph_vectors(args.graph,args.out,row_index=args.row)
    print("M3 ORIGINAL GRAPH CODEBOOK BRIDGE PASSED",data["graph"],
          "row",data["row_index"],"sha",data["graph_sha256"])
    for fmt,v in data["rows"].items():
        print(fmt,"H_M1",v["represented_J_local_field_from_M1"],
              "H_integer+scale",v["represented_J_local_field_from_bits"])


if __name__=="__main__":
    main()
