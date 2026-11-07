// Reference-vector driven HDL test of a *single* 99-term local-field row.
// No hidden FP arithmetic: FP E3M2 is decoded to signed Q4 integer.
// Compile separately for FORMAT=0 FP6, 1 INT6, 2 BFP6.
module tb_m3_row;
    parameter integer FORMAT = 0;
    parameter integer ACC_WIDTH=(FORMAT==0 ? 17 : 13);
    reg clk=0;
    always #5 clk=~clk;
    reg rst_n=0, clear=0, valid=0, spin_positive=0;
    reg [5:0] coeff_bits=0;
    wire signed [ACC_WIDTH-1:0] accum_q;

    m3_local_field_row #(.FORMAT(FORMAT),.MAX_TERMS(99),
        .ACC_WIDTH(ACC_WIDTH)) dut (
        .clk(clk), .rst_n(rst_n), .clear(clear), .valid(valid),
        .coeff_bits(coeff_bits), .spin_positive(spin_positive),
        .accum_q(accum_q)
    );

    reg [1023:0] filename;
    integer fd, rc, step_idx, spin_temp, expected_integer;
    initial begin
        if (!$value$plusargs("VEC=%s",filename))
            $fatal(1, "Use +VEC=filename");
        fd=$fopen(filename,"r");
        if (fd == 0)
            $fatal(1, "Cannot read vector: %s", filename);
        repeat(2) @(negedge clk);
        rst_n=1;
        clear=1;
        @(negedge clk);
        clear=0;
        if (accum_q !== {ACC_WIDTH{1'b0}})
            $fatal(1, "CLEAR did not initialize accumulator");
        for (step_idx=0;step_idx<99;step_idx=step_idx+1) begin
            rc=$fscanf(fd,"%h %d %d\n",coeff_bits,spin_temp,expected_integer);
            if (rc != 3)
                $fatal(1,"Input vector incomplete at step %0d, rc=%0d",step_idx,rc);
            if (spin_temp != 0 && spin_temp != 1)
                $fatal(1,"Invalid spin at step %0d", step_idx);
            spin_positive=spin_temp[0];
            valid=1;
            @(posedge clk);
            #1;
            if ($signed(accum_q) !== expected_integer)
                $fatal(1,"FORMAT=%0d step=%0d RTL=%0d oracle=%0d code=%h spin=%0d",
                    FORMAT,step_idx,$signed(accum_q),expected_integer,coeff_bits,spin_positive);
            @(negedge clk);
        end
        valid=0;
        $fclose(fd);
        $display("M3 RTL PASS FORMAT=%0d 99 terms final_q=%0d",FORMAT,$signed(accum_q));
        $finish;
    end
endmodule
