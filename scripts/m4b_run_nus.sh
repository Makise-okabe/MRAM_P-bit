#!/usr/bin/env bash
# M4B NUS: 3 official graphs x 3 formats x 3 anneal points, 27 clocked checks
# bash scripts/m4b_run_nus.sh
# RUN_SKY130=1 bash scripts/m4b_run_nus.sh
set -euo pipefail
cd "$(dirname "$0")/.."
for program in python3 iverilog vvp git; do
  command -v "$program" >/dev/null || { echo "MISSING: $program" >&2; exit 2; }
done
for file in data/biqmac/raw/rudy/w01_100.0 \
  data/biqmac/raw/ising/t2g10_5555 \
  data/biqmac/raw/ising/ising2.5-100_5555; do
  test -f "$file" || { echo "Missing official original Mac graph: $file" >&2; exit 2; }
done
mkdir -p results
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
SHA=$(git rev-parse --short HEAD)
OUT="results/m4b_local_$STAMP"_"$SHA"
test ! -e "$OUT" || { echo "Refusing overwrite: $OUT" >&2; exit 2; }
mkdir -p "$OUT"
git rev-parse HEAD > "$OUT/git_commit.txt"
python3 -m unittest discover -s tests -p 'test_m3_sixbit_encoding.py' -v
python3 -m unittest discover -s tests -p 'test_m4_gain_folding_audit.py' -v
python3 -m unittest discover -s tests -p 'test_m4_common_logit.py' -v

for graph in w01 t2g10 ising2p5; do
  case "$graph" in
    w01) src=data/biqmac/raw/rudy/w01_100.0 ;;
    t2g10) src=data/biqmac/raw/ising/t2g10_5555 ;;
    ising2p5) src=data/biqmac/raw/ising/ising2.5-100_5555 ;;
  esac
  python3 -m experiments.m3_actual_graph_row_vectors \
    --graph "$src" --out "$OUT/m3_$graph"
  python3 -m experiments.m4_common_logit \
    --graph "$src" --m3-vectors "$OUT/m3_$graph" \
    --out "$OUT/m4_$graph" | tee -a "$OUT/numerical_pass.log"
done

for fam in fp int bfp; do
  case "$fam" in fp) idx=0;; int) idx=1;; bfp) idx=2;; esac
  iverilog -g2012 -s tb_m4_common_logit -Ptb_m4_common_logit.FORMAT="$idx" \
    -o "$OUT/tb_$fam" rtl/m3_local_field_row.v \
    rtl/m4_common_logit_row.v rtl/tb_m4_common_logit.v
  for graph in w01 t2g10 ising2p5; do
    for point in begin middle end; do
      vec=$(printf 'm4_%s6_%s.txt' "$fam" "$point")
      vvp "$OUT/tb_$fam" +VEC="$OUT/m4_$graph/$vec" | tee -a "$OUT/rtl_pass.log"
    done
  done
done
test "$(grep -c 'M4B RTL PASS' "$OUT/rtl_pass.log")" = 27 ||
  { echo "ERROR: not 27 RTL passes" >&2; exit 1; }

RUN_SKY130=$(printenv RUN_SKY130 || printf 0)
if [[ "$RUN_SKY130" == 1 ]]; then
  command -v yosys >/dev/null || { echo 'MISSING: yosys' >&2; exit 2; }
  command -v curl >/dev/null || { echo 'MISSING: curl' >&2; exit 2; }
  mkdir -p "$OUT/sky130"
  curl -fL --retry 3 --connect-timeout 15 --max-time 120 \
    https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/aef47dd6ed123b0ed7cedac372b00456722be327/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib \
    -o "$OUT/sky130/original.lib"
  printf '%s  %s\n' ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9 \
    "$OUT/sky130/original.lib" | sha256sum -c
  python3 scripts/m3_filter_sky130_liberty.py \
    --input "$OUT/sky130/original.lib" \
    --output "$OUT/sky130/filtered.lib" \
    --manifest "$OUT/sky130/filter_manifest.json"
  printf '%s  %s\n' cd8abb502b47e96b31b0f179b8f16c34fd2f027c3cc4c7e0dbdbadc71030367b \
    "$OUT/sky130/filtered.lib" | sha256sum -c
  yosys -V > "$OUT/sky130/yosys_version.txt"
  LIB="$OUT/sky130/filtered.lib"
  for fmt in fp6 int6 bfp6; do
    logfile="$OUT/sky130/$fmt""_mapped.log"
    yosys -Q -p "read_liberty -lib $LIB; read_verilog rtl/m3_local_field_row.v rtl/m4_common_logit_row.v; synth -top m4_$fmt""_logit -flatten -noabc; dfflibmap -liberty $LIB; abc -liberty $LIB; clean; stat -liberty $LIB" \
      > "$logfile"
    if sed -n '/^=== m4_/,$p' "$logfile" | grep -Eq 'sky130_fd_sc_hd__(lpflow_|clkinv_)'; then
      echo "DISALLOWED MAPPED CELL: $fmt" >&2; exit 1
    fi
    grep 'Chip area for module' "$logfile"
  done
  REPORT_DIR="$OUT/sky130" python3 - <<'PY'
import csv,os,pathlib,re
root=pathlib.Path(os.environ["REPORT_DIR"])
rows=[]
for fmt in ("fp6","int6","bfp6"):
    src=(root/f"{fmt}_mapped.log").read_text()
    area=re.findall(r"Chip area for module [^\n]*?:\s*([0-9.]+)",src)
    count=re.findall(r"Number of cells:\s+(\d+)",src)
    if not area or not count: raise ValueError(f"Missing area/cell count for {fmt}")
    rows.append((fmt,area[-1],count[-1]))
with (root/"m4b_common_logit_cost.csv").open("w",newline="") as f:
    out=csv.writer(f);out.writerow(("format","area_um2","mapped_cells"));out.writerows(rows)
print((root/"m4b_common_logit_cost.csv").read_text())
PY
fi
echo "PASS: 27/27 RTL and all graph numerical gates"
echo "RESULT DIRECTORY: $OUT"
echo "UNMEASURED: full gain generator, SRAM, timing, p-bit, energy, Max-Cut quality"
