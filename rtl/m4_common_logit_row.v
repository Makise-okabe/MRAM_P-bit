// M4B common digital logit interface for one M3 99-term serial row.
// Frozen candidate contract: gain signed positive Q4.28, logit signed Q6.12,
// RNE (ties to EVEN) after integer multiplication, then clip at +/-12.
// Gain is supplied by EXTERNAL schedule/controller and latched on CLEAR.
// One extra output cycle AFTER the 99th accepted term; no sigmoid/DAC/p-bit.
//
// THIS MODULE IS NOT a full Ising machine, SRAM controller or gain generator.
// FP6 remains frozen finite E3M2 -> decoded q4 integer -> 17-bit accumulator;
// INT6 and global BFP6 use symmetric 13-bit integer accumulator.
// M4B hardware applies gain, and gain delivery cost is NOT claimed to be zero.
module m4_common_logit_row #(
    parameter integer FORMAT = 0,
    parameter integer MAX_TERMS = 99,
    parameter integer ACC_WIDTH =
        (FORMAT == 0 ? $clog2(MAX_TERMS*448+1)+1 :
                       $clog2(MAX_TERMS*31+1)+1)
)(
    input  wire clk,
    input  wire rst_n,
    input  wire clear,
    input  wire valid,
    input  wire last,
    input  wire [5:0] coeff_bits,
    input  wire spin_positive,
    input  wire signed [31:0] gain_q28,
    output wire signed [ACC_WIDTH-1:0] accum_q,
    output reg signed [17:0] logit_q12,
    output reg logit_valid
);
    m3_local_field_row #(
        .FORMAT(FORMAT), .MAX_TERMS(MAX_TERMS), .ACC_WIDTH(ACC_WIDTH)
    ) row (
        .clk(clk), .rst_n(rst_n), .clear(clear), .valid(valid),
        .coeff_bits(coeff_bits), .spin_positive(spin_positive),
        .accum_q(accum_q)
    );

    reg signed [31:0] gain_reg;
    reg pending;

    localparam integer PRODUCT_WIDTH = ACC_WIDTH + 32;
    wire signed [PRODUCT_WIDTH-1:0] product =
        $signed(accum_q) * $signed(gain_reg);
    wire signed [63:0] product_ext =
        {{(64-PRODUCT_WIDTH){product[PRODUCT_WIDTH-1]}}, product};

    // Product is signed integer times signed Q4.28: output Q6.12 requires
    // divide by 2^(28-12) = 2^16, with ties to EVEN by integer magnitude.
    wire [63:0] absolute_product =
        product_ext[63] ? -product_ext : product_ext;
    wire [63:0] quotient = absolute_product >> 16;
    wire [15:0] remainder = absolute_product[15:0];
    wire increment =
        (remainder > 16'h8000) ||
        ((remainder == 16'h8000) && quotient[0]);
    wire [63:0] nearest_even_magnitude = quotient + increment;
    wire [17:0] limited_magnitude =
        (nearest_even_magnitude > 64'd49152) ? 18'd49152 :
        nearest_even_magnitude[17:0];
    wire signed [17:0] next_logit =
        product_ext[63] ? -$signed(limited_magnitude) :
                          $signed(limited_magnitude);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            gain_reg <= 32'sd0;
            pending <= 1'b0;
            logit_valid <= 1'b0;
            logit_q12 <= 18'sd0;
        end else begin
            logit_valid <= pending;
            if (pending)
                logit_q12 <= next_logit;
            // CLEAR dominates the M3 row valid input. Gain is updated when
            // CLEAR loads the new row, not on the completion cycle.
            pending <= valid && last && !clear;
            if (clear)
                gain_reg <= gain_q28;
        end
    end
endmodule

// Fixed compile-time format wrappers (no runtime format MUX).
module m4_fp6_logit(
    input wire clk, rst_n, clear, valid, last,
    input wire [5:0] coeff_bits,
    input wire spin_positive,
    input wire signed [31:0] gain_q28,
    output wire signed [16:0] accum_q,
    output wire signed [17:0] logit_q12,
    output wire logit_valid
);
    m4_common_logit_row #(.FORMAT(0), .ACC_WIDTH(17)) core
      ( .clk(clk), .rst_n(rst_n), .clear(clear), .valid(valid), .last(last),
        .coeff_bits(coeff_bits), .spin_positive(spin_positive),
        .gain_q28(gain_q28), .accum_q(accum_q),
        .logit_q12(logit_q12), .logit_valid(logit_valid));
endmodule

module m4_int6_logit(
    input wire clk, rst_n, clear, valid, last,
    input wire [5:0] coeff_bits,
    input wire spin_positive,
    input wire signed [31:0] gain_q28,
    output wire signed [12:0] accum_q,
    output wire signed [17:0] logit_q12,
    output wire logit_valid
);
    m4_common_logit_row #(.FORMAT(1), .ACC_WIDTH(13)) core
      ( .clk(clk), .rst_n(rst_n), .clear(clear), .valid(valid), .last(last),
        .coeff_bits(coeff_bits), .spin_positive(spin_positive),
        .gain_q28(gain_q28), .accum_q(accum_q),
        .logit_q12(logit_q12), .logit_valid(logit_valid));
endmodule

module m4_bfp6_logit(
    input wire clk, rst_n, clear, valid, last,
    input wire [5:0] coeff_bits,
    input wire spin_positive,
    input wire signed [31:0] gain_q28,
    output wire signed [12:0] accum_q,
    output wire signed [17:0] logit_q12,
    output wire logit_valid
);
    m4_common_logit_row #(.FORMAT(2), .ACC_WIDTH(13)) core
      ( .clk(clk), .rst_n(rst_n), .clear(clear), .valid(valid), .last(last),
        .coeff_bits(coeff_bits), .spin_positive(spin_positive),
        .gain_q28(gain_q28), .accum_q(accum_q),
        .logit_q12(logit_q12), .logit_valid(logit_valid));
endmodule
