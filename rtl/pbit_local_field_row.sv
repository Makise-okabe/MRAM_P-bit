// M2 proof-of-concept: single cycle-serial Ising local-field row.
// MODE=0: finite FP4 E2M1 J, finite FP6 E3M2 h (global scales Q12.20).
// MODE=1: symmetric signed INT4 J, signed INT6 h (global scales Q12.20).
// MODE=2: signed BFP6 J+h (independent signed 8-bit PoT exponents).
// Exact coefficient values for each mode; scales for MODE 0/1 are
// hardware-rounded fixed Q12.20, unlike earlier real-valued H2 scales.
// Output field_q24 is exact in the row's fixed-point semantics, unless
// BFP shifting saturates or integer output ranges overflow.
// field_q16 is Q16.16 saturated for a downstream *unspecified* p-bit DAC.
// No memory macro, ADC/DAC, stochastic MTJ, scheduler, or best-state memory.
// Coefficients are externally streamed 1 per cycle in row order, excluding i.
// N_SPINS <= 128; independent spin_j presented with each coupling.
module pbit_local_field_row #(
    parameter integer N_SPINS = 128,
    parameter integer MODE = 0
)(
    input  wire                   clk,
    input  wire                   rst_n,
    input  wire                   start,
    input  wire                   coeff_valid,
    input  wire [5:0]             j_code,
    input  wire                   spin_pos,
    input  wire [5:0]             bias_code,
    input  wire [31:0]            scale_j_q20,
    input  wire [31:0]            scale_h_q20,
    input  wire signed [7:0]      bfp_exp_j,
    input  wire signed [7:0]      bfp_exp_h,
    output wire                   coeff_ready,
    output wire                   busy,
    output reg                    done,
    output reg signed [63:0]      field_q24,
    output reg signed [31:0]      field_q16
);
    localparam [1:0] ST_IDLE=2'd0, ST_ACC=2'd1, ST_FIN=2'd2;
    localparam integer CNT_W = (N_SPINS > 2) ? $clog2(N_SPINS) : 1;
    reg [1:0] state;
    reg [CNT_W-1:0] count;
    reg signed [15:0] sum_raw;
    reg [5:0] h_saved;
    reg [31:0] sj_saved, sh_saved;
    reg signed [7:0] ej_saved, eh_saved;

    function automatic signed [15:0] decode_j(input [5:0] c);
        integer e,m,mag;
        reg signed [15:0] raw;
        begin
            e=0; m=0; mag=0; raw=0;
            if (MODE == 0) begin
                e=c[2:1]; m=c[0];
                if (e==0) mag=m;
                else mag=(2+m) << (e-1);
                if (c[3]) mag=-mag;
                raw=mag;                // finite E2M1 times 2
            end else if (MODE == 1) begin
                raw=$signed(c[3:0]);
                if (raw==-8) raw=-7;  // reserved min signed code
            end else begin
                raw=$signed(c[5:0]);
                if (raw==-32) raw=-31;
            end
            decode_j=raw;
        end
    endfunction

    function automatic signed [15:0] decode_h(input [5:0] c);
        integer e,m,mag;
        reg signed [15:0] raw;
        begin
            e=0; m=0; mag=0; raw=0;
            if (MODE == 0) begin
                e=c[4:2]; m=c[1:0];
                if (e==0) mag=m;
                else mag=(4+m) << (e-1);
                if (c[5]) mag=-mag;
                raw=mag;                // finite E3M2 times 16
            end else begin
                raw=$signed(c[5:0]);
                if (raw==-32) raw=-31;
            end
            decode_h=raw;
        end
    endfunction

    function automatic signed [63:0] pot_scaled_q24(
        input signed [15:0] raw,
        input signed [7:0] exp
    );
        integer sh;
        reg signed [63:0] x;
        begin
            x=raw;
            sh=$signed(exp)+24;
            if (raw==0) pot_scaled_q24=64'sd0;
            else if (sh>=48)
                pot_scaled_q24=raw<0 ? -64'sh1000000000000000
                                       : 64'sh1000000000000000;
            else if (sh>=0)
                pot_scaled_q24=x <<< sh;
            else if (sh<=-63)
                pot_scaled_q24=raw<0 ? -64'sd1 : 64'sd0;
            else
                pot_scaled_q24=x >>> (-sh);
        end
    endfunction

    function automatic signed [31:0] clip_q16(input signed [63:0] x);
        begin
            if (x>64'sh000000007fffffff) clip_q16=32'sh7fffffff;
            else if (x<64'shffffffff80000000) clip_q16=32'sh80000000;
            else clip_q16=x[31:0];
        end
    endfunction

    wire signed [15:0] j_decoded=decode_j(j_code);
    wire signed [15:0] term=spin_pos ? j_decoded : -j_decoded;
    wire signed [15:0] h_decoded=decode_h(h_saved);

    reg signed [63:0] product_j,product_h;
    reg signed [63:0] full_field;
    always @* begin
        product_j=64'sd0;
        product_h=64'sd0;
        full_field=64'sd0;
        if (MODE==2) begin
            full_field=pot_scaled_q24(sum_raw,ej_saved)
                       +pot_scaled_q24(h_decoded,eh_saved);
        end else begin
            product_j=$signed(sum_raw) * $signed({1'b0,sj_saved});
            product_h=$signed(h_decoded) * $signed({1'b0,sh_saved});
            if (MODE==0)
                full_field=(product_j <<< 3) + product_h;
            else
                full_field=(product_j <<< 4) + (product_h <<< 4);
        end
    end

    assign coeff_ready=(state==ST_ACC);
    assign busy=(state!=ST_IDLE);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state<=ST_IDLE;
            count<=0;
            sum_raw<=0;
            h_saved<=0;
            sj_saved<=0;
            sh_saved<=0;
            ej_saved<=0;
            eh_saved<=0;
            field_q24<=0;
            field_q16<=0;
            done<=0;
        end else begin
            done<=0;
            case (state)
                ST_IDLE: if (start) begin
                    count<=0;
                    sum_raw<=0;
                    h_saved<=bias_code;
                    sj_saved<=scale_j_q20;
                    sh_saved<=scale_h_q20;
                    ej_saved<=bfp_exp_j;
                    eh_saved<=bfp_exp_h;
                    state<=ST_ACC;
                end
                ST_ACC: if (coeff_valid) begin
                    sum_raw<=sum_raw+term;
                    if (count==N_SPINS-2) state<=ST_FIN;
                    else count<=count+1'b1;
                end
                ST_FIN: begin
                    field_q24<=full_field;
                    field_q16<=clip_q16(full_field >>> 8);
                    done<=1;
                    state<=ST_IDLE;
                end
                default: state<=ST_IDLE;
            endcase
        end
    end
endmodule
