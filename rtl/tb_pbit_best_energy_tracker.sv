// Standalone functional test of the ENERGY-RETENTION POLICY, not device.
module tb_pbit_best_energy_tracker;
reg clk=0; always #5 clk=~clk;
reg rst_n=0,init=0,update_valid=0,old_spin_pos=0,new_spin_pos=0;
reg signed [63:0] field_q24=0;
reg [127:0] initial_state=0,next_state=0;
wire active,fault_overflow;
wire [127:0] best_state;
wire signed [63:0] current_energy_q24,best_energy_q24;
wire [31:0] accepted_updates;
pbit_best_energy_tracker #(.N_SPINS(128)) dut (
 .clk(clk),.rst_n(rst_n),.init(init),.initial_state(initial_state),
 .update_valid(update_valid),.old_spin_pos(old_spin_pos),
 .new_spin_pos(new_spin_pos),.field_q24(field_q24),
 .next_state(next_state),.active(active),.fault_overflow(fault_overflow),
 .best_state(best_state),.current_energy_q24(current_energy_q24),
 .best_energy_q24(best_energy_q24),.accepted_updates(accepted_updates)
);
task automatic update(input oldpos,input newpos,input signed [63:0] localfield,
                      input [127:0] resulting_state);
begin
 @(negedge clk);
 old_spin_pos=oldpos;
 new_spin_pos=newpos;
 field_q24=localfield;
 next_state=resulting_state;
 update_valid=1;
 @(negedge clk);
 update_valid=0;
end
endtask
initial begin
 repeat(2) @(negedge clk);
 rst_n=1;
 init=1;
 initial_state=128'd0;
 @(negedge clk);
 init=0;
 if(!active || best_state!==0) $fatal(1,"init failure");
 // Flip old=-1 -> new=+1 at field +2: delta=-4
 update(0,1,64'sd33554432,128'd1);
 if(current_energy_q24!==-64'sd67108864
    || best_energy_q24!==-64'sd67108864
    || best_state!==128'd1) $fatal(1,"first improvement wrong");
 // Flip old=-1 -> new=+1 at field -1: delta=+2, not a new best
 update(0,1,-64'sd16777216,128'd3);
 if(current_energy_q24!==-64'sd33554432
    || best_energy_q24!==-64'sd67108864
    || best_state!==128'd1) $fatal(1,"worse-state retention wrong");
 // Flip old=+1 -> new=-1 at field -3: delta=-6, new best
 update(1,0,-64'sd50331648,128'd2);
 if(current_energy_q24!==-64'sd134217728
    || best_energy_q24!==-64'sd134217728
    || best_state!==128'd2) $fatal(1,"second improvement wrong");
 // No flip: best should not change regardless of field
 update(1,1,64'sd167772160,128'd2);
 if(best_state!==128'd2 || current_energy_q24!==-64'sd134217728
    || accepted_updates!==32'd4) $fatal(1,"no-flip wrong");
 // Reset and force a 64-bit arithmetic overflow.
 @(negedge clk); init=1;
 @(negedge clk); init=0;
 update(0,1,64'sh7fffffffffffffff,128'd1);
 if(!fault_overflow || active || accepted_updates!==32'd0)
    $fatal(1,"overflow guard failed");
 $display("M2 RETENTION PASS: best-quantized-energy, worse-state, no-flip, overflow");
 $finish;
end
initial begin #1000; $fatal(1,"retention test timeout"); end
endmodule
