
set top $::env(HW_TOP)
set lib $::env(LIB)
set rtl $::env(OUT)/hw01_matched.v
set dst $::env(HW_DST)

if {[catch {

    read_libs $lib

    read_hdl -sv $rtl

    elaborate $top

    check_design -unresolved

    create_clock -name clk -period 10 [get_ports clk]

    # Support both common and legacy Genus interfaces.

    if {[llength [info commands set_db]] > 0} {

        puts "HW01_INTERFACE=COMMON"

        set_db syn_generic_effort medium
        set_db syn_map_effort medium

    } else {

        puts "HW01_INTERFACE=LEGACY"

        set_attribute syn_generic_effort medium /
        set_attribute syn_map_effort medium /

    }

    if {[llength [info commands syn_generic]] > 0} {

        syn_generic
        syn_map

    } else {

        synthesize -to_generic
        synthesize -to_mapped

    }

    report_area > $dst/area.rpt
    report_gates > $dst/gates.rpt

    write_hdl > $dst/mapped.v

} err]} {

    puts stderr "HW01_SYNTH_FAIL: $err"
    exit 1

}

if {[catch {
    report_timing > $dst/timing.rpt
} timing_error]} {

    puts "HW01_TIMING_WARNING: $timing_error"

}

puts "HW01_SYNTH_PASS=$top"
exit 0

