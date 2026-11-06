# Genus LEGACY UI, mapped area/timing comparison for the existing 3-mode
# pbit_local_field_row (no stochastic MTJ or MRAM macro).
# Invoke from repo root with env M2_LIBERTY=/path/to/authorized/standard_cells.lib,
# M2_MODE=0|1|2, M2_N=128, M2_OUTPUT=/path/to/fresh/outdir.
# Genus invocation: genus -legacy_ui -f scripts/m2_genus_row.tcl
# IMPORTANT: one mode PER Genus process, same Liberty and clock for all 3.
foreach key {M2_LIBERTY M2_MODE M2_N M2_OUTPUT} {
    if {![info exists ::env($key)] || $::env($key) eq ""} {
        puts stderr "M2 FATAL: missing required environment variable $key"
        exit 2
    }
}
set liberty $::env(M2_LIBERTY)
set mode $::env(M2_MODE)
set n $::env(M2_N)
set out $::env(M2_OUTPUT)
if {![file isfile $liberty]} {
    puts stderr "M2 FATAL: Liberty file does not exist: $liberty"
    exit 2
}
if {$mode ni {0 1 2} || $n < 2 || $n > 128} {
    puts stderr "M2 FATAL: mode in 0..2 and N in 2..128 required"
    exit 2
}
file mkdir $out
puts "M2 GENUS LIB=$liberty MODE=$mode N=$n OUT=$out"
set_attribute library $liberty /
read_hdl -sv rtl/pbit_local_field_row.sv
elaborate pbit_local_field_row -parameters [list [list N_SPINS $n] [list MODE $mode]]
check_design -unresolved
# Identical illustrative 10ns clock for cross-mode hardware comparison;
# IO delay, load, and real physical constraints remain unspecified.
create_clock -name clk -period 10 [get_ports clk]
set_attribute syn_generic_effort medium /
set_attribute syn_map_effort medium /
syn_generic
syn_map
report_area > "$out/area.rpt"
report_gates > "$out/gates.rpt"
report_timing > "$out/timing.rpt"
write_hdl > "$out/mapped.v"
puts "M2 MAPPED SYNTHESIS COMPLETE: MODE=$mode N=$n"
exit
