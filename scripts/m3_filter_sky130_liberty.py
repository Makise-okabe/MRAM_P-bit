#!/usr/bin/env python3
"""Prune Sky130 power-domain / clock-specialty cells for Yosys 0.33.

OpenROAD sky130hd config marks lpflow cells DONT_USE. Yosys 0.33
doesn't accept -dont_use in abc/dfflibmap, so remove these whole
Liberty cell blocks. This does not establish STA or layout evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

CELL_HEADER = re.compile(
    r'(?m)^[ \t]*cell[ \t]*\([ \t]*"?([a-zA-Z0-9_]+)"?[ \t]*\)[ \t]*\{'
)
EXCLUDED_PREFIXES = ("sky130_fd_sc_hd__lpflow_", "sky130_fd_sc_hd__clkinv_")


def _end_brace(s: str, opening: int) -> int:
    depth = 0
    quote = False
    line_comment = False
    block_comment = False
    i = opening
    while i < len(s):
        c = s[i]
        nxt = s[i+1] if i+1 < len(s) else ""
        if line_comment:
            if c == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if c == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if c == "\\":
                i += 2
            elif c == '"':
                quote = False
                i += 1
            else:
                i += 1
            continue
        if c == "/" and nxt == "*":
            block_comment = True
            i += 2
        elif c == "/" and nxt == "/":
            line_comment = True
            i += 2
        elif c == '"':
            quote = True
            i += 1
        elif c == "{":
            depth += 1
            i += 1
        elif c == "}":
            depth -= 1
            i += 1
            if depth == 0:
                return i
            if depth < 0:
                raise ValueError("negative Liberty brace nesting")
        else:
            i += 1
    raise ValueError("unterminated Liberty cell block")


def filter_library(src: str) -> tuple[str, list[str], int]:
    matches = list(CELL_HEADER.finditer(src))
    if not matches:
        raise ValueError("no Liberty cell blocks detected")
    kept = []
    removed = []
    pos = 0
    for m in matches:
        name = m.group(1)
        if not name.startswith(EXCLUDED_PREFIXES):
            continue
        opening = src.find("{", m.start(), m.end())
        end = _end_brace(src,opening)
        if m.start() < pos:
            raise ValueError("overlapping Liberty cell blocks")
        kept.append(src[pos:m.start()])
        pos = end
        removed.append(name)
    kept.append(src[pos:])
    filtered = "".join(kept)
    if not removed:
        raise ValueError("no excluded cells matched; review Liberty format")
    remaining_matches = list(CELL_HEADER.finditer(filtered))
    if len(remaining_matches) != len(matches)-len(removed):
        raise ValueError("unexpected Liberty cell count after pruning")
    if any(m.group(1).startswith(EXCLUDED_PREFIXES) for m in remaining_matches):
        raise ValueError("excluded cell survived")
    return filtered,removed,len(remaining_matches)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    args=p.parse_args()
    original=args.input.read_text(encoding="utf-8")
    filtered,removed,remaining=filter_library(original)
    if args.output.exists() or args.manifest.exists():
        raise ValueError("refuse to replace Liberty or metadata")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.manifest.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(filtered,encoding="utf-8")
    data=dict(
        source_sha256=hashlib.sha256(original.encode()).hexdigest(),
        filtered_sha256=hashlib.sha256(filtered.encode()).hexdigest(),
        original_cell_count=len(list(CELL_HEADER.finditer(original))),
        remaining_cell_count=remaining,excluded_count=len(removed),
        excluded_cell_names=removed, excluded_prefixes=list(EXCLUDED_PREFIXES),
        evidence="OPEN SKY130 DIGITAL ROW ONLY, NOT GF22FDX/MTJ FULL-COST",
    )
    args.manifest.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("M3 LIBERTY FILTER PASS",data["excluded_count"],"removed,",
          data["remaining_cell_count"],"cells remain")


if __name__=="__main__":
    main()
