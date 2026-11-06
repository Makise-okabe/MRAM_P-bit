// M2 bit-exact smoke check for 3 modes at N=2 (no external device).
// iverilog -g2012 -s tb_pbit_local_field_row -o /tmp/row.vvp rtl/pbit_local_field_row.sv rtl/tb_pbit_local_field_row.sv
// vvp /tmp/row.vvp
module tb_pbit_local_field_row;
reg clk=0; always #5 clk=~clk;
reg rst_n=0,start=0,coeff_valid=0;
wire done_fp,done_int,done_bfp;
wire ready_fp,ready_int,ready_bfp;
wire signed [63:0] q24_fp,q24_int,q24_bfp;
wire signed [31:0] q16_fp,q16_int,q16_bfp;
pbit_local_field_row #(.N_SPINS(2),.MODE(0)) dut_fp (
 .clk(clk),.rst_n(rst_n),.start(start),.coeff_valid(coeff_valid),
 .j_code(6'b000011),.spin_pos(1'b1),.bias_code(6'b001100),
 .scale_j_q20(32'd1048576),.scale_h_q20(32'd1048576),
 .bfp_exp_j(8'sd0),.bfp_exp_h(8'sd0),
 .coeff_ready(ready_fp),.busy(),.done(done_fp),
 .field_q24(q24_fp),.field_q16(q16_fp));
pbit_local_field_row #(.N_SPINS(2),.MODE(1)) dut_int (
 .clk(clk),.rst_n(rst_n),.start(start),.coeff_valid(coeff_valid),
 .j_code(6'b000011),.spin_pos(1'b1),.bias_code(6'b000010),
 .scale_j_q20(32'd1048576),.scale_h_q20(32'd1048576),
 .bfp_exp_j(8'sd0),.bfp_exp_h(8'sd0),
 .coeff_ready(ready_int),.busy(),.done(done_int),
 .field_q24(q24_int),.field_q16(q16_int));
pbit_local_field_row #(.N_SPINS(2),.MODE(2)) dut_bfp (
 .clk(clk),.rst_n(rst_n),.start(start),.coeff_valid(coeff_valid),
 .j_code(6'b111101),.spin_pos(1'b0),.bias_code(6'b000001),
 .scale_j_q20(32'd0),.scale_h_q20(32'd0),
 .bfp_exp_j(-8'sd1),.bfp_exp_h(8'sd0),
 .coeff_ready(ready_bfp),.busy(),.done(done_bfp),
 .field_q24(q24_bfp),.field_q16(q16_bfp));
initial begin
 repeat(2) @(negedge clk); rst_n=1; start=1;
 @(negedge clk); start=0;
 if(!(ready_fp && ready_int && ready_bfp)) $fatal(1,"not ready");
 coeff_valid=1;
 @(negedge clk); coeff_valid=0;
 @(posedge done_fp); #1;
 if(!done_int || !done_bfp) $fatal(1,"completion skew");
 // FP J=1.5, h=1; INT J=3, h=2; BFP J=-1.5, spin=-1, h=1
 if(q24_fp!==64'sd41943040 || q16_fp!==32'sd163840)
   $fatal(1,"mixed FP wrong: %0d / %0d",q24_fp,q16_fp);
 if(q24_int!==64'sd83886080 || q16_int!==32'sd327680)
   $fatal(1,"mixed INT wrong: %0d / %0d",q24_int,q16_int);
 if(q24_bfp!==64'sd41943040 || q16_bfp!==32'sd163840)
   $fatal(1,"BFP6 wrong: %0d / %0d",q24_bfp,q16_bfp);
 $display("M2 ROW SMOKE PASS: FP, INT, BFP6");
 $finish;
end
initial begin #1000; $fatal(1,"test timeout"); end
endmodule
