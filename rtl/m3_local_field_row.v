// M3 six-bit coefficient-stream local-field row: ONE incoming coupling per cycle.
// Design scope: digital coefficient decode + spin sign + integer accumulator ONLY.
// A graph with N spins has N-1 non-diagonal terms in each local field row.
//
// FORMAT = 0: frozen finite-only FP6 E3M2 with exp=111 FINITE,
//             signed zero decodes to zero. q/S = k/16, k integer;
//             output accum_q is the integer k sum.
// FORMAT = 1: symmetric signed INT6, two's complement [-31,+31],
//             -32 reserved/invalid. output accum_q is sum of integer codes.
// FORMAT = 2: BFP6, same signed mantissa as INT6;
//             one signed 8-bit shared exponent is applied OUTSIDE the row.
//
// Actual local field: FORMAT=0 -> H = accum_q * global_scale_f32 / 16;
//                     FORMAT=1 -> H = accum_q * global_scale_f32;
//                     FORMAT=2 -> H = accum_q * 2**global_bfp_exponent.
// Physical scale application, beta schedule, DAC, storage, control,
// best-represented-energy retention and p-bit time/energy are NOT implemented.
// This is NOT a full Max-Cut accelerator and NOT GF22FDX silicon evidence.
// clear dominates valid. For all rows, supply each off-diagonal J_ij once.
// To compare formats fairly, synthesise fixed FORMAT=0,1,2 individually.
module m3_local_field_row #(
    parameter integer FORMAT = 0,
    parameter integer MAX_TERMS = 99,
    parameter integer ACC_WIDTH =
       (FORMAT == 0 ? $clog2(MAX_TERMS*448+1)+1 :
                      $clog2(MAX_TERMS*31+1)+1)
)(
    input  wire                   clk,
    input  wire                   rst_n,
    input  wire                   clear,
    input  wire                   valid,
    input  wire [5:0]             coeff_bits,
    input  wire                   spin_positive,
    output reg  signed [ACC_WIDTH-1:0] accum_q
);
    wire [2:0] fp_exp  = coeff_bits[4:2];
    wire [1:0] fp_frac = coeff_bits[1:0];

    // FP E3M2: code 0..3 -> k=frac, code (exp,frac), exp>0 ->
    // k=(4+frac)<< (exp-1); signed k multiplied by S/16.
    // Max |k|=448 (exp=7, frac=3); no NaN/Inf.
    wire [9:0] fp_base = {7'b0000000, 1'b1, fp_frac};
    wire [9:0] fp_magnitude_q4 =
       (fp_exp == 3'b000) ? {8'b00000000, fp_frac} :
          (fp_base << (fp_exp - 3'b001));

    // Two's-complement 6-bit signed integer for INT6/BFP6.
    // Input -32 is forbidden by the frozen symmetric codebook; it is
    // representable in gates but must be rejected by vector generation.
    wire signed [10:0] fp_signed_q4 =
       coeff_bits[5] ? -$signed({1'b0, fp_magnitude_q4}) :
                         $signed({1'b0, fp_magnitude_q4});
    wire signed [10:0] int_signed =
        {{5{coeff_bits[5]}}, coeff_bits};
    wire signed [10:0] coeff_integer =
        (FORMAT == 0) ? fp_signed_q4 : int_signed;
    wire signed [10:0] term =
        spin_positive ? coeff_integer : -coeff_integer;

    wire signed [ACC_WIDTH-1:0] term_extended =
        {{(ACC_WIDTH-11){term[10]}}, term};

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            accum_q <= {ACC_WIDTH{1'b0}};
        else if (clear)
            accum_q <= {ACC_WIDTH{1'b0}};
        else if (valid)
            accum_q <= accum_q + term_extended;
    end
endmodule

// Fixed-form elaboration wrappers: no runtime format selector/mux.
// Each exposes only the bit-true unscaled local-field integer.
module m3_fp6_row #(
    parameter integer MAX_TERMS=99,
    parameter integer ACC_WIDTH=$clog2(MAX_TERMS*448+1)+1
)(
    input wire clk, rst_n, clear, valid,
    input wire [5:0] coeff_bits,
    input wire spin_positive,
    output wire signed [ACC_WIDTH-1:0] accum_q
);
m3_local_field_row #(.FORMAT(0),.MAX_TERMS(MAX_TERMS),.ACC_WIDTH(ACC_WIDTH)) core
 ( .clk(clk), .rst_n(rst_n), .clear(clear), .valid(valid),
   .coeff_bits(coeff_bits), .spin_positive(spin_positive), .accum_q(accum_q));
endmodule

module m3_int6_row #(
    parameter integer MAX_TERMS=99,
    parameter integer ACC_WIDTH=$clog2(MAX_TERMS*31+1)+1
)(
    input wire clk, rst_n, clear, valid,
    input wire [5:0] coeff_bits,
    input wire spin_positive,
    output wire signed [ACC_WIDTH-1:0] accum_q
);
m3_local_field_row #(.FORMAT(1),.MAX_TERMS(MAX_TERMS),.ACC_WIDTH(ACC_WIDTH)) core
 ( .clk(clk), .rst_n(rst_n), .clear(clear), .valid(valid),
   .coeff_bits(coeff_bits), .spin_positive(spin_positive), .accum_q(accum_q));
endmodule

module m3_bfp6_row #(
    parameter integer MAX_TERMS=99,
    parameter integer ACC_WIDTH=$clog2(MAX_TERMS*31+1)+1
)(
    input wire clk, rst_n, clear, valid,
    input wire [5:0] coeff_bits,
    input wire spin_positive,
    output wire signed [ACC_WIDTH-1:0] accum_q
);
m3_local_field_row #(.FORMAT(2),.MAX_TERMS(MAX_TERMS),.ACC_WIDTH(ACC_WIDTH)) core
 ( .clk(clk), .rst_n(rst_n), .clear(clear), .valid(valid),
   .coeff_bits(coeff_bits), .spin_positive(spin_positive), .accum_q(accum_q));
endmodule
