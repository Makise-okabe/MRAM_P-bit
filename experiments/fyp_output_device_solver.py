#!/usr/bin/env python3
"""Pinned offset-enabled counterpart of the frozen 2026-11-21 passive buffer.

Copied verbatim from fyp_tail_probe.PassiveBuffer/solve_buffered, except:
- solver entry point renamed solve_offset_buffered,
- an explicit per-device persistent logit-offset parameter is validated,
- offset added at the existing sigmoid decision, leaving RNG order unchanged.
The source-tail script and its registered result hashes are NOT modified.
Zero offset must pass full-output parity against the unmodified source.
"""
from __future__ import annotations

import heapq
import math
import random

from experiments.fyp_tail_probe import K, CHECKPOINTS, lattice_codes
from experiments.fyp_first_block_20261120 import hex_state, state_from_hex
from experiments.fyp_ideal_solver import exact_original_cut, representation
from experiments.m0_ising_math import sigmoid
from experiments.m1_biqmac_ideal_pilot import original_cut, represented_energy
from experiments.m1_biqmac_reference_quality_gate import schedule_beta

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


def solve_offset_buffered(graph, rep, beta, updates, seed, *, source_rep=None,
                   checkpoints=CHECKPOINTS, capacity=K, offsets=None):
    """Arithmetic and RNG order match the archived kernel; added logging passive."""
    if not updates >= 1 or not beta > 0 or any(t < 1 or t > updates for t in checkpoints):
        raise ValueError("invalid solver settings")
    if 2*sum(abs(int(w)) for _, _, w in graph.edges) >= 2**53:
        raise ValueError("original-score cache not exactly representable")
    lattice_codes(rep)
    offsets = (0.0,) * graph.n if offsets is None else tuple(float(x) for x in offsets)
    if len(offsets) != graph.n or any(not math.isfinite(x) for x in offsets):
        raise ValueError("offset bank must contain one finite logit per spin")
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
        nxt = 1 if u < sigmoid(2*b*fields[i] + offsets[i]) else -1
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


