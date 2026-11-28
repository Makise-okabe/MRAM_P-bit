// M4B bit-true bench: 99 M3 coefficient/spin pairs and one quantized
// Q4.28 gain loaded on CLEAR. Checks every M3 accumulator prefix and
// one Q6.12 result one extra cycle after the 99th term.
module tb_m4_common_logit;
    parameter integer FORMAT = 0;
    localparam integer ACC_WIDTH = (FORMAT == 0 ? 17 : 13);
    reg clk=0;
    always #5 clk=~clk;
    reg rst_n=0, clear=0, valid=0, last=0, spin_positive=0;
    reg [5:0] coeff_bits=0;
    reg signed [31:0] gain_q28=0;
    wire signed [ACC_WIDTH-1:0] accum_q;
    wire signed [17:0] logit_q12;
    wire logit_valid;

    m4_common_logit_row #(.FORMAT(FORMAT), .MAX_TERMS(99),
                           .ACC_WIDTH(ACC_WIDTH)) dut (
        .clk(clk), .rst_n(rst_n), .clear(clear), .valid(valid), .last(last),
        .coeff_bits(coeff_bits), .spin_positive(spin_positive),
        .gain_q28(gain_q28), .accum_q(accum_q),
        .logit_q12(logit_q12), .logit_valid(logit_valid)
    );

    reg [1023:0] filename;
    integer fd, rc, step_idx, spin_temp, expected_integer;
    integer expected_final, expected_logit;
    initial begin
        if (!$value$plusargs("VEC=%s",filename))
            $fatal(1, "Use +VEC=filename");
        fd=$fopen(filename,"r");
        if (fd == 0)
            $fatal(1, "Cannot read M4B vector: %s",filename);
        rc=$fscanf(fd,"%h %d %d\n",gain_q28,expected_logit,expected_final);
        if (rc != 3)
            $fatal(1, "Bad M4B vector header");
        if (gain_q28 <= 0)
            $fatal(1, "Frozen gain must be positive signed Q4.28");

        repeat(2) @(negedge clk);
        rst_n=1;
        clear=1;
        @(negedge clk);
        clear=0;
        if (accum_q !== {ACC_WIDTH{1'b0}})
            $fatal(1, "Row CLEAR did not reset accumulator");

        for (step_idx=0;step_idx<99;step_idx=step_idx+1) begin
            rc=$fscanf(fd,"%h %d %d\n",coeff_bits,spin_temp,expected_integer);
            if (rc != 3)
                $fatal(1,"Input vector incomplete at %0d",step_idx);
            if (spin_temp != 0 && spin_temp != 1)
                $fatal(1,"Invalid spin");
            spin_positive=spin_temp[0];
            valid=1;
            last=(step_idx==98);
            @(posedge clk);
            #1;
            if ($signed(accum_q) !== expected_integer)
                $fatal(1,"FORMAT=%0d step=%0d accum RTL=%0d oracle=%0d",
                       FORMAT,step_idx,$signed(accum_q),expected_integer);
            if (logit_valid !== 1'b0)
                $fatal(1,"Premature logit valid");
            @(negedge clk);
        end
        valid=0;
        last=0;
        if ($signed(accum_q) !== expected_final)
            $fatal(1,"Final accumulator mismatch");

        @(posedge clk);
        #1;
        if (logit_valid !== 1'b1)
            $fatal(1,"Missing output valid exactly 1 extra cycle after last");
        if ($signed(logit_q12) !== expected_logit)
            $fatal(1,"FORMAT=%0d Q6.12 RTL=%0d oracle=%0d gain=%h acc=%0d",
                     FORMAT,$signed(logit_q12),expected_logit,gain_q28,
                     $signed(accum_q));
        $display("M4B RTL PASS FORMAT=%0d 99 terms gain=%h logit_q12=%0d",
                 FORMAT,gain_q28,$signed(logit_q12));
        $fclose(fd);
        $finish;
    end
endmodule
