// Integrated local-field/retention test driven by independently generated
// *symmetric* Ising Hamiltonian traces (not a p-bit device or MIMO runtime).
// Testbench itself is the external coefficient streamer and spin scheduler.
module tb_pbit_row_best_state_system;
parameter integer TOP_TB_N=128;
parameter integer TOP_TB_MODE=0;
reg clk=0; always #5 clk=~clk;
reg rst_n=0,init_tracker=0,row_start=0,coeff_valid=0;
reg [5:0] j_code=0,bias_code=0;
reg spin_pos=0;
reg [31:0] scale_j_q20=0,scale_h_q20=0;
reg signed [7:0] bfp_exp_j=0,bfp_exp_h=0;
reg apply_update=0,old_spin_pos=0,new_spin_pos=0;
reg [TOP_TB_N-1:0] initial_state=0,next_state=0;
wire coeff_ready,row_busy,row_done,tracker_active,tracker_fault_overflow;
wire signed [63:0] field_q24,current_energy_q24,best_energy_q24;
wire signed [31:0] field_q16;
wire [TOP_TB_N-1:0] best_state;
wire [31:0] accepted_updates;
pbit_row_best_state_system #(.N_SPINS(TOP_TB_N),.MODE(TOP_TB_MODE)) dut(
 .clk(clk),.rst_n(rst_n),.init_tracker(init_tracker),
 .initial_state(initial_state),.row_start(row_start),
 .coeff_valid(coeff_valid),.j_code(j_code),.spin_pos(spin_pos),
 .bias_code(bias_code),.scale_j_q20(scale_j_q20),
 .scale_h_q20(scale_h_q20),.bfp_exp_j(bfp_exp_j),
 .bfp_exp_h(bfp_exp_h),.apply_update(apply_update),
 .old_spin_pos(old_spin_pos),.new_spin_pos(new_spin_pos),
 .next_state(next_state),.coeff_ready(coeff_ready),
 .row_busy(row_busy),.row_done(row_done),.field_q24(field_q24),
 .field_q16(field_q16),.tracker_active(tracker_active),
 .tracker_fault_overflow(tracker_fault_overflow),.best_state(best_state),
 .current_energy_q24(current_energy_q24),
 .best_energy_q24(best_energy_q24),.accepted_updates(accepted_updates)
);
integer fd,rc,nsteps,t,j,idx;
reg [1023:0] path;
reg [TOP_TB_N-1:0] current_state,candidate,expected_best,one_hot;
reg [5:0] next_code;
reg next_sign,do_apply;
reg signed [63:0] expected_field,expected_running,expected_best_energy;
reg [31:0] expected_accepted;
initial begin
 if(!$value$plusargs("VECTORS=%s",path))
   $fatal(1,"missing +VECTORS=...");
 fd=$fopen(path,"r");
 if(fd==0) $fatal(1,"cannot read %0s",path);
 rc=$fscanf(fd,"%d %h %h %h %h %h",
   nsteps,initial_state,scale_j_q20,scale_h_q20,bfp_exp_j,bfp_exp_h);
 if(rc!=6 || nsteps<1) $fatal(1,"invalid trace header");
 repeat(3) @(negedge clk);
 rst_n=1;
 init_tracker=1;
 current_state=initial_state;
 @(negedge clk);
 init_tracker=0;
 if(!tracker_active || accepted_updates!==0 || best_state!==initial_state)
   $fatal(1,"initial state not loaded");
 for(t=0;t<nsteps;t=t+1) begin
   rc=$fscanf(fd,"%d %h %h %h %h %h %h %h %h %h %h",
     idx,bias_code,old_spin_pos,new_spin_pos,do_apply,
     candidate,expected_field,expected_running,
     expected_best_energy,expected_best,expected_accepted);
   if(rc!=11 || idx<0 || idx>=TOP_TB_N)
     $fatal(1,"bad step header: t=%0d rc=%0d idx=%0d",t,rc,idx);
   one_hot=({{(TOP_TB_N-1){1'b0}},1'b1} << idx);
   if(current_state[idx]!==old_spin_pos)
     $fatal(1,"old-spin mismatch t=%0d index=%0d",t,idx);
   if(candidate !== ((current_state & ~one_hot) |
                      (new_spin_pos ? one_hot : {TOP_TB_N{1'b0}})))
     $fatal(1,"candidate mismatch t=%0d",t);
   next_state=candidate;
   apply_update=do_apply;
   @(negedge clk);
   if(row_busy || row_done) $fatal(1,"row not idle t=%0d",t);
   row_start=1;
   @(negedge clk);
   row_start=0;
   if(!coeff_ready) $fatal(1,"row not ready t=%0d",t);
   for(j=0;j<TOP_TB_N-1;j=j+1) begin
     rc=$fscanf(fd,"%h %h",next_code,next_sign);
     if(rc!=2) $fatal(1,"bad operand t=%0d j=%0d",t,j);
     j_code=next_code;
     spin_pos=next_sign;
     coeff_valid=1;
     if(!coeff_ready) $fatal(1,"unexpected row stall t=%0d j=%0d",t,j);
     @(negedge clk);
     coeff_valid=0;
     if(j%19==0) repeat(2) @(negedge clk);
   end
   @(posedge row_done);
   #1; // wait for NBA field register to settle
   if(field_q24!==expected_field)
     $fatal(1,"field mismatch: mode=%0d N=%0d t=%0d got=%h expected=%h",
       TOP_TB_MODE,TOP_TB_N,t,field_q24,expected_field);
   @(posedge clk);
   #1; // tracker samples row_done + registered field at this edge
   if(tracker_fault_overflow || !tracker_active ||
      current_energy_q24!==expected_running ||
      best_energy_q24!==expected_best_energy ||
      best_state!==expected_best ||
      accepted_updates!==expected_accepted)
      $fatal(1,"tracker mismatch mode=%0d N=%0d t=%0d energy=%h/%h bestE=%h/%h best=%h/%h accepted=%0d/%0d",
       TOP_TB_MODE,TOP_TB_N,t,current_energy_q24,expected_running,
       best_energy_q24,expected_best_energy,best_state,expected_best,
       accepted_updates,expected_accepted);
   if(do_apply) current_state=candidate;
   @(negedge clk);
   apply_update=0;
 end
 $fclose(fd);
 $display("M2 INTEGRATED PASS: mode=%0d N=%0d steps=%0d accepted=%0d",
   TOP_TB_MODE,TOP_TB_N,nsteps,accepted_updates);
 $finish;
end
initial begin #3000000; $fatal(1,"integrated test timeout"); end
endmodule
