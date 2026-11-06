// M2 integration gate: one cycle-serial local-field row + best-state retention.
// This is NOT a full p-bit machine: coefficient streamer, row selection,
// spin state/scheduler, probabilistic device and MRAM macro are external.
// The external scheduler MUST hold old_spin_pos, new_spin_pos, next_state,
// and apply_update stable from row start through row_done's following clock.
// The row's field is the PRE-update field; tracker fires on row_done.
// Same symmetric represented J/h Hamiltonian is assumed across all updates.
// Reject an update by holding apply_update=0; then the tracker must not count it.
module pbit_row_best_state_system #(
    parameter integer N_SPINS=128,
    parameter integer MODE=0
)(
    input wire clk,
    input wire rst_n,
    input wire init_tracker,
    input wire [N_SPINS-1:0] initial_state,
    input wire row_start,
    input wire coeff_valid,
    input wire [5:0] j_code,
    input wire spin_pos,
    input wire [5:0] bias_code,
    input wire [31:0] scale_j_q20,
    input wire [31:0] scale_h_q20,
    input wire signed [7:0] bfp_exp_j,
    input wire signed [7:0] bfp_exp_h,
    input wire apply_update,
    input wire old_spin_pos,
    input wire new_spin_pos,
    input wire [N_SPINS-1:0] next_state,
    output wire coeff_ready,
    output wire row_busy,
    output wire row_done,
    output wire signed [63:0] field_q24,
    output wire signed [31:0] field_q16,
    output wire tracker_active,
    output wire tracker_fault_overflow,
    output wire [N_SPINS-1:0] best_state,
    output wire signed [63:0] current_energy_q24,
    output wire signed [63:0] best_energy_q24,
    output wire [31:0] accepted_updates
);
    pbit_local_field_row #(.N_SPINS(N_SPINS),.MODE(MODE)) row (
        .clk(clk),.rst_n(rst_n),.start(row_start),
        .coeff_valid(coeff_valid),.j_code(j_code),.spin_pos(spin_pos),
        .bias_code(bias_code),.scale_j_q20(scale_j_q20),
        .scale_h_q20(scale_h_q20),.bfp_exp_j(bfp_exp_j),
        .bfp_exp_h(bfp_exp_h),.coeff_ready(coeff_ready),
        .busy(row_busy),.done(row_done),.field_q24(field_q24),
        .field_q16(field_q16)
    );
    // row_done is a single-cycle registered pulse. On its next rising
    // clock edge, the tracker sees the stable registered field_q24.
    pbit_best_energy_tracker #(.N_SPINS(N_SPINS)) tracker (
        .clk(clk),.rst_n(rst_n),.init(init_tracker),
        .initial_state(initial_state),
        .update_valid(row_done && apply_update),
        .old_spin_pos(old_spin_pos),.new_spin_pos(new_spin_pos),
        .field_q24(field_q24),.next_state(next_state),
        .active(tracker_active),.fault_overflow(tracker_fault_overflow),
        .best_state(best_state),
        .current_energy_q24(current_energy_q24),
        .best_energy_q24(best_energy_q24),
        .accepted_updates(accepted_updates)
    );
endmodule
