#!/usr/bin/env python3
"""Frozen weak-tail mechanism probes; historical codes and solver stay unchanged.

All six arms use one source beta and paired Python Random streams. The passive
top-16 buffer never uses original quality to retain a candidate. Fresh sources
use a new graph namespace, with the original ring/torus generating equations.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import gzip
import hashlib
import heapq
import io
import json
import math
from pathlib import Path
import platform
import random
import time

import numpy as np

from experiments.biqmac_maxcut import load_rudy
from experiments.fyp_first_block_20261120 import canonical, hex_state, state_from_hex
from experiments.fyp_ideal_solver import exact_original_cut, representation
from experiments.fyp_ideal_sources import (
    N, NUMPY_VERSION, SOURCE_MULTIPLIER, ring_normalization, torus_edges,
    rudy_bytes, require_numpy_version,
)
from experiments.m0_ising_math import sigmoid
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph, original_cut, represented_energy
from experiments.m1_biqmac_reference_quality_gate import schedule_beta

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "b8e6f28eab87b40ad97f124837c2e2bcec74a992"
ARMS = ("ref64", "fp6", "int6", "fp6_mask", "int6_tail", "int6_keep")
CONTROLS = ARMS[:3]
GRAPHS = 24
SEEDS = 64
UPDATES = 50_000
K = 16
CHECKPOINTS = (5000, 15000, 30000, 50000)
SOURCE_DIR = ROOT / "data/fyp_tail_probe_20261121"
RESULT_DIR = ROOT / "results/fyp_tail_probe_20261121"
FREEZE = ROOT / "docs/FYP_TAIL_FREEZE_20261121.json"
RECEIPT = ROOT / "results/fyp_tail_preflight_20261121/freeze_receipt.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_bytes(obj):
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False)+"\n").encode()


def save_new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"refuse to replace existing evidence: {path}")
    else:
        path.write_bytes(data)


def save_gzip(path, obj):
    save_new(path, gzip.compress(json_bytes(obj), compresslevel=9, mtime=0))


def seal(row):
    payload = dict(row)
    payload["record_sha256"] = hashlib.sha256(canonical(row).encode()).hexdigest()
    return payload


def solver_seed(family, index, replicate):
    if family not in (0, 1) or not 0 <= index < GRAPHS or not 0 <= replicate < SEEDS:
        raise ValueError("unregistered seed")
    return 4_000_000_000_000 + 100_000*family + 1000*index + replicate


def generate_source(family, index):
    require_numpy_version()
    if family not in (0, 1) or not 0 <= index < GRAPHS:
        raise ValueError("unregistered graph")
    entropy = [20261121, 910, family, index]
    rng = np.random.Generator(np.random.PCG64DXSM(np.random.SeedSequence(entropy)))
    if family == 0:
        pairs = tuple((i, j) for i in range(N) for j in range(i+1, N))
        d = np.asarray([(N/np.pi)*np.sin(np.pi*abs(i-j)/N) for i, j in pairs])
        values = SOURCE_MULTIPLIER*ring_normalization()*rng.standard_normal(len(pairs))/d**2.5
    else:
        pairs = torus_edges()
        values = SOURCE_MULTIPLIER*rng.standard_normal(len(pairs))
    weights = np.rint(values).astype(np.int64)
    edges = tuple((i, j, int(w)) for (i, j), w in zip(pairs, weights))
    return rudy_bytes(edges), {
        "family": family, "index": index, "seed_sequence": entropy,
        "raw_edges": len(edges), "raw_zeros": int(np.count_nonzero(weights == 0)),
        "max_abs_weight": int(np.max(np.abs(weights))),
    }


def prepare_sources():
    """Source-only operation; no solver or quantization outcomes."""
    if RESULT_DIR.exists():
        raise ValueError("result directory already exists")
    manifest = {"numpy": NUMPY_VERSION, "graph_count": 48, "graphs": []}
    for family in (0, 1):
        name = ("ring", "torus")[family]
        for index in range(GRAPHS):
            data, meta = generate_source(family, index)
            path = SOURCE_DIR / name / f"{index:03d}.rudy"
            save_new(path, data)
            manifest["graphs"].append({**meta, "file": str(path.relative_to(ROOT)),
                                       "sha256": digest(path)})
    save_new(SOURCE_DIR/"source_manifest.json", json_bytes(manifest))
    return manifest


def rep_from_edges(graph, edges, label):
    adjacency = [[] for _ in range(graph.n)]
    for (i, j, _), (a, b, q) in zip(graph.edges, edges):
        if (i, j) != (a, b):
            raise ValueError("edge order mismatch")
        adjacency[i].append((j, q))
        adjacency[j].append((i, q))
    return {"edges": edges, "adjacency": adjacency, "label": label}


def lattice_codes(rep):
    """Exact integer energy keys; prove binary64 updates cannot lose bits."""
    ratios = [float(q).as_integer_ratio() for _, _, q in rep["edges"]]
    denominator = max((d for _, d in ratios), default=1)
    codes = [n*(denominator//d) for n, d in ratios]
    if denominator & (denominator-1) or 2*sum(map(abs, codes)) >= 2**53:
        raise ValueError("represented energy is not proven exactly binary64-additive")
    return denominator, np.asarray(codes, dtype=np.int64)


def build_arms(graph):
    ref, fp, integer = (representation(graph, x) for x in CONTROLS)
    masked, restored, kept = [], [], []
    for (i, j, w), (_, _, f), (_, _, z) in zip(graph.edges, fp["edges"], integer["edges"]):
        masked.append((i, j, f if z != 0 else 0.0))
        restored.append((i, j, z if z != 0 else f))
        kept.append((i, j, z if z != 0 else math.copysign(integer["scale"], -float(w))))
    reps = {"ref64": ref, "fp6": fp, "int6": integer,
            "fp6_mask": rep_from_edges(graph, masked, "mechanism_probe"),
            "int6_tail": rep_from_edges(graph, restored, "mechanism_probe"),
            "int6_keep": rep_from_edges(graph, kept, "diagnostic_inflated_tail")}
    for a in ARMS:
        lattice_codes(reps[a])
    for f, z, m, t in zip(fp["edges"], integer["edges"], masked, restored):
        if f[2]-m[2] != t[2]-z[2]:
            raise AssertionError("factorial tail arrays differ")
    return reps


class PassiveBuffer:
    """Lowest represented energy, earliest first visit; original cut is payload."""
    def __init__(self, capacity=K):
        if capacity < 1:
            raise ValueError("positive capacity required")
        self.capacity = capacity
        self.first_seen = {}
        self.active = {}
        self.heap = []

    def observe(self, state, energy, attempt, cut):
        if state in self.first_seen:
            return
        self.first_seen[state] = attempt
        key = (energy, attempt, state)
        if len(self.active) == self.capacity:
            worst = self.heap[0]
            worst_key = (-worst[0], -worst[1], worst[2])
            if key >= worst_key:
                return
            popped = heapq.heappop(self.heap)
            del self.active[popped[2]]
        self.active[state] = {"state_hex": format(state, "x"), "energy": energy,
                              "first_visit": attempt, "original_cut": cut}
        heapq.heappush(self.heap, (-energy, -attempt, state))

    def rows(self):
        return sorted(self.active.values(), key=lambda r: (r["energy"], r["first_visit"], int(r["state_hex"], 16)))


def solve_buffered(graph, rep, beta, updates, seed, *, source_rep=None,
                   checkpoints=CHECKPOINTS, capacity=K):
    """Arithmetic and RNG order match the archived kernel; added logging passive."""
    if not updates >= 1 or not beta > 0 or any(t < 1 or t > updates for t in checkpoints):
        raise ValueError("invalid solver settings")
    if 2*sum(abs(int(w)) for _, _, w in graph.edges) >= 2**53:
        raise ValueError("original-score cache not exactly representable")
    lattice_codes(rep)
    rng = random.Random(seed)
    spins = [1 if rng.randrange(2) else -1 for _ in range(graph.n)]
    state = int(hex_state(spins), 16)
    adj = rep["adjacency"]
    fields = [sum(q*spins[j] for j, q in adj[i]) for i in range(graph.n)]
    energy = represented_energy(rep["edges"], spins)
    best_e, best_state = energy, tuple(spins)
    source_rep = source_rep or representation(graph, "ref64")
    src_adj = source_rep["adjacency"]
    src_field = [sum(q*spins[j] for j, q in src_adj[i]) for i in range(graph.n)]
    current_cut = original_cut(graph, spins)
    V = M = R = R_last = current_cut
    V_state = M_state = last_state = best_state
    flips = improvements = 0
    snaps, checkpoint_set = [], set(checkpoints)
    buffer = PassiveBuffer(capacity)
    buffer.observe(state, energy, 0, current_cut)
    minimum_states = {state}
    for step in range(updates):
        i = rng.randrange(graph.n)
        u = rng.random()
        b = schedule_beta(beta, "linear", step, updates)
        old = spins[i]
        nxt = 1 if u < sigmoid(2*b*fields[i]) else -1
        if nxt != old:
            delta = nxt-old
            current_cut -= old*src_field[i]
            energy += 2*old*fields[i]
            spins[i] = nxt
            state ^= 1 << i
            flips += 1
            for j, q in adj[i]:
                fields[j] += q*delta
            for j, q in src_adj[i]:
                src_field[j] += q*delta
            buffer.observe(state, energy, step+1, current_cut)
        if current_cut > V:
            V, V_state = current_cut, tuple(spins)
        if energy < best_e:
            best_e, best_state = energy, tuple(spins)
            improvements += 1
            R = M = current_cut
            M_state = best_state
            R_last, last_state = current_cut, best_state
            minimum_states = {state}
        elif energy == best_e:
            R_last = current_cut
            minimum_states.add(state)
            if nxt != old:
                last_state = tuple(spins)
            if current_cut > M:
                M, M_state = current_cut, tuple(spins)
        if step+1 in checkpoint_set:
            if current_cut != exact_original_cut(graph, spins):
                raise AssertionError("original-score cache drift")
            snaps.append({"attempt": step+1, "beta": b, "current_state_hex": hex_state(spins),
                          "V": V, "M": M, "R": R, "R_last": R_last,
                          "unreached": None, "selection": V-M, "tie": M-R})
    final_e = represented_energy(rep["edges"], spins)
    saved = represented_energy(rep["edges"], best_state)
    if final_e != energy or saved != best_e:
        raise AssertionError("exact represented-energy cache parity failed")
    for score, st in ((V, V_state), (M, M_state), (R, best_state), (R_last, last_state)):
        if score != exact_original_cut(graph, st):
            raise AssertionError("saved original score mismatch")
    top = buffer.rows()
    for item in top:
        st = state_from_hex(item["state_hex"], graph.n)
        if item["original_cut"] != exact_original_cut(graph, st) or item["energy"] != represented_energy(rep["edges"], st):
            raise AssertionError("buffer payload mismatch")
    if not V >= M >= R or not M >= R_last or not V >= max(x["original_cut"] for x in top) >= R:
        raise AssertionError("passive output ordering failed")
    return {"seed": seed, "attempted_updates": updates, "actual_flips": flips,
            "improvements": improvements, "returned_original_cut": R,
            "final_original_cut": original_cut(graph, spins),
            "returned_represented_energy": saved, "final_represented_energy": final_e,
            "returned_state_hex": hex_state(best_state), "V": V, "M": M, "R": R,
            "R_last": R_last, "V_state_hex": hex_state(V_state),
            "M_state_hex": hex_state(M_state), "checkpoints": snaps,
            "buffer": top, "buffer_best_original_cut": max(x["original_cut"] for x in top),
            "minimum_distinct_states": len(minimum_states), "visited_distinct_states": len(buffer.first_seen)}


def legacy_fields(row):
    return {k: v for k, v in row.items() if k not in
            {"buffer", "buffer_best_original_cut", "minimum_distinct_states", "visited_distinct_states"}}


def common_bank(graph, reps, records):
    """Exactly rank a shared pooled bank; arm-neutral smallest-state tie rule."""
    bank = {}
    for r in records:
        for p in r["buffer"]:
            state = int(p["state_hex"], 16)
            cut = int(p["original_cut"])
            if state in bank and bank[state] != cut:
                raise AssertionError("common-bank source score mismatch")
            bank[state] = cut
    states = sorted(bank)
    spins = np.asarray([state_from_hex(format(s, "x"), graph.n) for s in states], dtype=np.int8)
    ii = np.asarray([i for i, _, _ in graph.edges])
    jj = np.asarray([j for _, j, _ in graph.edges])
    codes = np.column_stack([lattice_codes(reps[a])[1] for a in ARMS])
    energies = np.empty((len(states), len(ARMS)), dtype=np.int64)
    original = np.asarray([int(w) for _, _, w in graph.edges], dtype=np.int64)
    original_check = np.empty(len(states), dtype=np.int64)
    for start in range(0, len(states), 256):
        pair = (spins[start:start+256, ii]*spins[start:start+256, jj]).astype(np.int64)
        energies[start:start+len(pair)] = -(pair @ codes)
        original_check[start:start+len(pair)] = np.sum((spins[start:start+len(pair), ii] != spins[start:start+len(pair), jj])*original, axis=1)
    cuts = np.asarray([bank[s] for s in states], dtype=np.int64)
    if not np.array_equal(cuts, original_check):
        raise AssertionError("common bank exact original rescore failed")
    best = int(cuts.max())
    result = []
    for col, arm in enumerate(ARMS):
        min_e = int(energies[:, col].min())
        tied = np.flatnonzero(energies[:, col] == min_e)
        chosen = int(tied[0])
        m = int(cuts[tied].max())
        r = int(cuts[chosen])
        result.append({"representation": arm, "bank_size": len(states), "V_bank": best,
                       "M_bank": m, "R_bank": r, "selection_loss_cut": best-m,
                       "tie_loss_cut": m-r, "total_loss_cut": best-r,
                       "minimum_distinct_states": len(tied), "selected_state_hex": format(states[chosen], "x"),
                       "energy_integer_key": min_e, "energy_denominator": lattice_codes(reps[arm])[0]})
    if result[0]["total_loss_cut"] != 0:
        raise AssertionError("FP64 bank failed to select best original state")
    return {"tie_rule": "smallest unsigned spin-state integer, independent of original quality",
            "states": [{"state_hex": format(s, "x"), "original_cut": bank[s]} for s in states],
            "results": result}


def verify_freeze(freeze_commit):
    require_numpy_version()
    receipt = json.loads(RECEIPT.read_text())
    if receipt["freeze_commit"] != freeze_commit or receipt["freeze_sha256"] != digest(FREEZE):
        raise ValueError("published freeze receipt mismatch")
    frozen = json.loads(FREEZE.read_text())
    for p, expected in frozen["file_sha256"].items():
        if digest(ROOT/p) != expected:
            raise ValueError("frozen file changed: "+p)
    return frozen


def run_graph(family, index, freeze_commit):
    verify_freeze(freeze_commit)
    name = ("ring", "torus")[family]
    graph_path = SOURCE_DIR/name/f"{index:03d}.rudy"
    folder = RESULT_DIR/name/f"{index:03d}"
    if folder.exists():
        raise FileExistsError("no implicit resume or rerun: "+str(folder))
    folder.mkdir(parents=True)
    (folder/"IN_PROGRESS").write_text("started\n")
    started = time.monotonic()
    graph = load_rudy(graph_path)
    beta = beta_from_original_graph(graph)
    reps = build_arms(graph)
    rows = []
    for arm in ARMS:
        for replicate in range(SEEDS):
            r = solve_buffered(graph, reps[arm], beta, UPDATES, solver_seed(family, index, replicate), source_rep=reps["ref64"])
            rows.append(seal({**r, "family": name, "index": index, "graph": f"{name}_{index:03d}",
                              "graph_sha256": graph.sha256, "representation": arm, "replicate": replicate,
                              "gain": 1.0, "offset_logit": 0.0, "source_beta": beta,
                              "freeze_commit": freeze_commit}))
    controls = [r for r in rows if r["representation"] in CONTROLS]
    witness = max(controls, key=lambda r: r["V"])
    b = max(0, witness["V"])
    if b <= 0:
        raise ValueError("nonpositive reference denominator; stop, no substitution")
    metrics = {}
    for arm, rep in reps.items():
        weights = [q for _, _, q in rep["edges"]]
        metrics[arm] = {"nonzero_count": sum(q != 0 for q in weights),
                        "coefficient_mse": sum((-float(w)-q)**2 for (_, _, w), q in zip(graph.edges, weights))/len(weights),
                        "energy_denominator": lattice_codes(rep)[0],
                        "probe_only": arm not in CONTROLS,
                        "diagnostic": arm == "int6_keep"}
    bank = common_bank(graph, reps, rows)
    save_gzip(folder/"records.json.gz", rows)
    save_gzip(folder/"common_bank.json.gz", bank)
    save_new(folder/"representations.json", json_bytes(metrics))
    manifest = {"family": name, "index": index, "graph_sha256": graph.sha256,
                "freeze_commit": freeze_commit, "records": len(rows), "B_control": b,
                "reference_pool": "best V over exactly FP64/FP6/INT6 x64; not a known optimum",
                "B_witness": {"representation": witness["representation"], "seed": witness["seed"],
                               "state_hex": witness["V_state_hex"]},
                "files": {p.name: digest(p) for p in folder.iterdir() if p.name not in ("IN_PROGRESS", "manifest.json")}}
    save_new(folder/"manifest.json", json_bytes(manifest))
    (folder/"IN_PROGRESS").unlink()
    return {"family": name, "index": index, "records": len(rows), "seconds": time.monotonic()-started}


def run_all(freeze_commit, workers=6):
    verify_freeze(freeze_commit)
    if RESULT_DIR.exists():
        raise FileExistsError("campaign result root already exists; no implicit rerun")
    RESULT_DIR.mkdir()
    started = time.monotonic()
    done = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_graph, f, g, freeze_commit) for f in (0, 1) for g in range(GRAPHS)]
        for future in as_completed(futures):
            item = future.result()
            done.append(item)
            print(json.dumps(item, sort_keys=True), flush=True)
    result = {"status": "COMPLETE_PENDING_ANALYSIS", "freeze_commit": freeze_commit,
              "python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform(),
              "workers": workers, "wall_seconds": time.monotonic()-started,
              "graphs": sorted(done, key=lambda x: (x["family"], x["index"])),
              "trajectories": sum(r["records"] for r in done)}
    save_new(RESULT_DIR/"execution.json", json_bytes(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-sources", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--freeze-commit")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if args.prepare_sources:
        print(json.dumps({"source_graphs": prepare_sources()["graph_count"]}))
    elif args.run:
        if not args.freeze_commit:
            parser.error("--freeze-commit required")
        print(json.dumps(run_all(args.freeze_commit, args.workers), sort_keys=True))
    else:
        parser.error("choose --prepare-sources or --run")
