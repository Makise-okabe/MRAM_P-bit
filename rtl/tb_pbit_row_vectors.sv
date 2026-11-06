// Verifies actual output from pbit_local_field_row against an independent
// Python-generated bit-true oracle. TOP_TB_N and TOP_TB_MODE are compile-time
// iverilog parameters. Vector file supplied via +VECTORS=... .
module tb_pbit_row_vectors;
parameter integer TOP_TB_N=128;
parameter integer TOP_TB_MODE=0;
reg clk=0;
always #5 clk=~clk;
reg rst_n=0;
reg start=0,coeff_valid=0;
reg [5:0] j_code=0,bias_code=0;
reg spin_pos=0;
reg [31:0] scale_j_q20=0,scale_h_q20=0;
reg signed [7:0] bfp_exp_j=0,bfp_exp_h=0;
wire coeff_ready,busy,done;
wire signed [63:0] field_q24;
wire signed [31:0] field_q16;
integer fd,rc,trials,t,i;
reg [1023:0] path;
reg [5:0] next_code;
reg next_sign;
reg signed [63:0] expected_q24;
reg signed [31:0] expected_q16;

pbit_local_field_row #(.N_SPINS(TOP_TB_N),.MODE(TOP_TB_MODE)) dut (
  .clk(clk),.rst_n(rst_n),.start(start),.coeff_valid(coeff_valid),
  .j_code(j_code),.spin_pos(spin_pos),.bias_code(bias_code),
  .scale_j_q20(scale_j_q20),.scale_h_q20(scale_h_q20),
  .bfp_exp_j(bfp_exp_j),.bfp_exp_h(bfp_exp_h),
  .coeff_ready(coeff_ready),.busy(busy),.done(done),
  .field_q24(field_q24),.field_q16(field_q16)
);

initial begin
  if (!$value$plusargs("VECTORS=%s",path))
    $fatal(1,"missing +VECTORS=<file>");
  fd=$fopen(path,"r");
  if (fd==0) $fatal(1,"cannot open vector file %0s",path);
  rc=$fscanf(fd,"%d",trials);
  if(rc!=1 || trials<1) $fatal(1,"bad vector count");
  repeat(3) @(negedge clk);
  rst_n=1;
  for (t=0; t<trials; t=t+1) begin
    rc=$fscanf(fd,"%h %h %h %h %h %h %h",
      scale_j_q20,scale_h_q20,bfp_exp_j,bfp_exp_h,
      bias_code,expected_q24,expected_q16);
    if(rc!=7) $fatal(1,"header parse failure at t=%0d (%0d)",t,rc);
    @(negedge clk);
    if(busy || coeff_ready) $fatal(1,"row not idle at test %0d",t);
    start=1;
    @(negedge clk);
    start=0;
    if(!coeff_ready || !busy) $fatal(1,"row did not start at test %0d",t);
    for(i=0;i<TOP_TB_N-1;i=i+1) begin
      rc=$fscanf(fd,"%h %h",next_code,next_sign);
      if(rc!=2) $fatal(1,"operand parse failure t=%0d i=%0d",t,i);
      j_code=next_code;
      spin_pos=next_sign;
      coeff_valid=1;
      if(!coeff_ready) $fatal(1,"row not ready t=%0d i=%0d",t,i);
      @(negedge clk);
      coeff_valid=0;
      if(i%17==0) repeat(2) @(negedge clk); // explicit read stalls
    end
    @(posedge done);
    #1;
    if(field_q24 !== expected_q24 || field_q16 !== expected_q16)
      $fatal(1,"mode=%0d N=%0d case=%0d got %h/%h expected %h/%h",
        TOP_TB_MODE,TOP_TB_N,t,
        field_q24,field_q16,expected_q24,expected_q16);
  end
  $fclose(fd);
  $display("M2 VECTORS PASS: mode=%0d N=%0d cases=%0d",
    TOP_TB_MODE,TOP_TB_N,trials);
  $finish;
end
initial begin
  #3000000;
  $fatal(1,"vector test timeout");
end
endmodule
