#!/usr/bin/env python3
"""Read-only intake of PREEXISTING NUS 4x4 GF 2T1MTJ PEX read results.

Purpose: inspect the actual R1 simultaneous 4-BL IDEAL/PEX results and MC1
P/AP paired provenance before deciding if a physical joint-error pilot exists.
No Spectre, no data modification, no PDK or extracted netlist contents printed.

Compatible with Python 3.6; standard library only.
"""
from __future__ import print_function
import argparse
import csv
import hashlib
import io
import os
import re
import zipfile

ROOT_DEFAULT = os.path.expanduser(
    "~/mram_fyp/cadence/manual_cross5_runs/M047_READ_CIM_PILOT")
E01_DEFAULT = os.path.expanduser(
    "~/MRAM_Path_Finding/experiments/runs/E01_MNIST_20261104T085558Z_038af9/review_packet.zip")
E01_SHA = "400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a"

def sha256(path):
    dig = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b: break
            dig.update(b)
    return dig.hexdigest()

def sample_csv(label, path):
    print("\n========== CSV {} ==========".format(label))
    if not os.path.isfile(path):
        print("E26B_MISSING", path)
        return
    print("BASENAME", os.path.basename(path), "BYTES", os.path.getsize(path),
          "SHA256", sha256(path))
    try:
        with io.open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            first = f.read(8192)
            if not first.strip():
                print("EMPTY")
                return
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(first, delimiters=",;\t")
            except csv.Error:
                dialect = csv.excel
            reader = csv.reader(f, dialect)
            columns = next(reader, [])
            print("CSV_FIELDS_COUNT", len(columns))
            print("CSV_HEADER", repr(columns[:40]))
            count = 0
            for row in reader:
                if not any(str(c).strip() for c in row):
                    continue
                if count < 3:
                    print("CSV_SAMPLE_ROW_{}".format(count + 1), repr(row[:30]))
                count += 1
            print("CSV_DATA_ROWS", count)
    except Exception as exc:
        print("CSV_PARSE_WARNING", type(exc).__name__, str(exc)[:170])

def summary_txt(label, path, limit=80):
    print("\n========== TEXT {} ==========".format(label))
    if not os.path.isfile(path):
        print("E26B_MISSING", path)
        return
    print("BASENAME", os.path.basename(path), "BYTES", os.path.getsize(path),
          "SHA256", sha256(path))
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        for idx, line in enumerate(f, 1):
            if idx > limit:
                print("TEXT_TRUNCATED_AFTER", limit)
                break
            # Never print foundry model includes, extracted netlist or PDK paths.
            lower = line.lower()
            if "pdk" in lower or "cmos22fdx" in lower or "gf22" in lower:
                print("TEXT_LINE_{}".format(idx), "[redacted model/source metadata]")
            else:
                print("TEXT_LINE_{}".format(idx), line.rstrip()[:240])

def r1_deck_audit(path):
    print("\n========== R1 READ DECK STIMULUS / OBSERVABILITY ==========")
    if not os.path.isfile(path):
        print("E26B_MISSING", path)
        return
    print("DECK_BYTES", os.path.getsize(path), "SHA256", sha256(path))
    selected = []
    counters = dict(include=0, sources=0, analyses=0, saves=0)
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        for idx, line in enumerate(f, 1):
            s = line.strip()
            if not s or s.startswith("*") or s.startswith("//"): continue
            if re.search(r'^\s*(include|ahdl_include|simulator\s+lang|library|section)\b', s, re.I):
                counters["include"] += 1
                continue
            if re.search(r'\b(tran|dc|ac|stb|save|options)\b', s, re.I):
                counters["analyses"] += 1
            if re.search(r'\bsave\b', s, re.I):
                counters["saves"] += 1
            if re.match(r'^[VI]\w+\b', s, re.I):
                counters["sources"] += 1
            if re.search(r'\b(wll|wlr|wl|bl|sl|vread|vwl|save|tran|dc)\b', s, re.I) \
               or re.search(r'\b(WLL|WLR|BL|SL)[_<\[]?\d', s, re.I):
                # Only show user-written *stimulus* lines; not instance cards or foundry includes.
                if re.match(r'^[VI]\w+\b', s, re.I) or re.search(r'\b(save|tran|dc)\b', s, re.I):
                    selected.append((idx, s[:210]))
    print("DECK_COUNTS", counters)
    print("DECK_SELECTED_USER_STIMULUS_COUNT", len(selected))
    for idx, line in selected[:50]:
        print("DECK_LINE_{}".format(idx), line)
    if len(selected) > 50:
        print("DECK_STIMULUS_TRUNCATED", len(selected) - 50)
    print("DECK_WARNING no conclusion about simultaneous multirow CIM solely from stimulus regex")

def e01_packet_audit(path):
    print("\n========== FROZEN E01 FULL-NETWORK PROVENANCE HINTS ==========")
    if not os.path.isfile(path):
        print("E01_PACKET_MISSING", path)
        return
    digest = sha256(path)
    print("E01_SHA256", digest, "KNOWN_PACKET_MATCH", digest == E01_SHA)
    if digest != E01_SHA:
        print("E01_FINGERPRINT_MISMATCH_ABORT_FIND")
        return
    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            print("E01_ARCHIVE_MEMBERS", len(names))
            print("E01_MANIFEST_BASENAMES", [os.path.basename(k) for k in names[:35]])
            hits = []
            for name in names:
                if not name.lower().endswith((".json", ".txt", ".md")):
                    continue
                info = zf.getinfo(name)
                if info.file_size > 200000:
                    continue
                data = zf.read(name).decode("utf-8", errors="replace")
                for line in data.splitlines():
                    if re.search(r"checkpoint|fc2|fc3|quantiz|logit|weight.*sha|model.*sha", line, re.I):
                        snippet = line.strip()[:150]
                        # Print only provenance metadata, not embedded tensor/secret content.
                        if re.search(r"token|password|secret|private|key", snippet, re.I):
                            continue
                        hits.append((os.path.basename(name), snippet))
            for name, snippet in hits[:25]:
                print("E01_PROVENANCE_HINT", name, snippet)
    except Exception as exc:
        print("E01_AUDIT_WARNING", type(exc).__name__, str(exc)[:160])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--e01-packet", default=E01_DEFAULT)
    args = ap.parse_args()
    base = os.path.expanduser(args.root)
    r1 = os.path.join(base, "R1_4BL_SIMULTANEOUS_READ")
    mc = os.path.join(base, "MC1_CONTROLLED_READ_MARGIN_MC")
    print("E26B_EXISTING_RESULT_AUDIT_READ_ONLY")
    r1_deck_audit(os.path.join(r1, "pex_R1_4BL_read.scs"))
    summary_txt("R1_FINAL", os.path.join(r1, "R1_final_summary.txt"), 110)
    for name in ("R1_current_comparison.csv", "R1_PEX_currents.csv",
                 "R1_IDEAL_currents.csv", "R1_PEX_mz_all16.csv",
                 "R1_IDEAL_mz_all16.csv"):
        sample_csv(name, os.path.join(r1, name))
    summary_txt("MC1_FORMAL100_ANALYSIS", os.path.join(mc, "MC1_FORMAL100_analysis.txt"), 95)
    summary_txt("MC1_NOMINAL_SUMMARY", os.path.join(mc, "MC1_nominal_summary.txt"), 65)
    for name in ("MC1_FORMAL100_paired_1600.csv",
                 "MC1_FORMAL100_by_location.csv", "MC1_MC5_paired_80.csv"):
        sample_csv(name, os.path.join(mc, name))
    e01_packet_audit(args.e01_packet)
    print("\nE26B_INVENTORY_DONE_NO_NEW_SPECTRE_NO_CORRELATION_CLAIM")

if __name__ == "__main__":
    main()
