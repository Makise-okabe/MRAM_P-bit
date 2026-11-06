// M2 best-of-visited represented-energy retention controller (NOT an ML oracle).
// Sequential single-spin updates; field_q24 must be the PRE-update local field
// from the same quantized Hamiltonian and fixed-point representation.
// On a spin flip: E_new - E_old = 2*s_old*field_q24.
// Energy origin E(initial_state)=0 is arbitrary; comparisons remain valid.
// Tie policy: keep the earliest visited best-energy configuration.
// A scheduler must provide the correct full next_state and both spin values.
// Independent module: MRAM, p-bit, DAC, scheduling and field generation excluded.
module pbit_best_energy_tracker #(
    parameter integer N_SPINS=128
)(
    input wire clk,
    input wire rst_n,
    input wire init,
    input wire [N_SPINS-1:0] initial_state,
    input wire update_valid,
    input wire old_spin_pos,
    input wire new_spin_pos,
    input wire signed [63:0] field_q24,
    input wire [N_SPINS-1:0] next_state,
    output reg active,
    output reg fault_overflow,
    output reg [N_SPINS-1:0] best_state,
    output reg signed [63:0] current_energy_q24,
    output reg signed [63:0] best_energy_q24,
    output reg [31:0] accepted_updates
);
    wire flip = old_spin_pos ^ new_spin_pos;
    wire signed [65:0] field_extended = {{2{field_q24[63]}},field_q24};
    wire signed [65:0] twice_field = field_extended <<< 1;
    wire signed [65:0] delta_energy = !flip ? 66'sd0
                                          : old_spin_pos ? twice_field : -twice_field;
    wire signed [65:0] next_energy_extended =
        {{2{current_energy_q24[63]}},current_energy_q24} + delta_energy;
    wire overflows_64 =
        (next_energy_extended[65:64] != {2{next_energy_extended[63]}});
    wire signed [63:0] next_energy = next_energy_extended[63:0];

    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin
            active<=1'b0;
            fault_overflow<=1'b0;
            best_state<={N_SPINS{1'b0}};
            current_energy_q24<=64'sd0;
            best_energy_q24<=64'sd0;
            accepted_updates<=32'd0;
        end else if (init) begin
            active<=1'b1;
            fault_overflow<=1'b0;
            best_state<=initial_state;
            current_energy_q24<=64'sd0;
            best_energy_q24<=64'sd0;
            accepted_updates<=32'd0;
        end else if(active && update_valid && !fault_overflow) begin
            if(overflows_64 || accepted_updates == 32'hffffffff) begin
                fault_overflow<=1'b1;
                active<=1'b0;
            end else begin
                current_energy_q24<=next_energy;
                accepted_updates<=accepted_updates+1'b1;
                if(next_energy<best_energy_q24) begin
                    best_energy_q24<=next_energy;
                    best_state<=next_state;
                end
            end
        end
    end
endmodule
