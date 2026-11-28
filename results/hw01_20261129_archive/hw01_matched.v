
module hw01_row #(
    parameter integer B = 5,
    parameter integer IS_FP = 1,
    parameter integer ACC_WIDTH = 13
)(
    input wire clk,
    input wire rst_n,
    input wire clear,
    input wire valid,
    input wire [B-1:0] coeff_bits,
    input wire spin_positive,
    output reg signed [ACC_WIDTH-1:0] accum_q
);

    wire signed [ACC_WIDTH-1:0] coefficient;

    generate
        if (IS_FP) begin : fp_decode
            wire [1:0] exp = coeff_bits[3:2];
            wire [1:0] frac = coeff_bits[1:0];

            wire [4:0] base = {2'b00, 1'b1, frac};

            wire [4:0] magnitude =
                (exp == 0)
                ? {3'b000, frac}
                : (base << (exp - 2'd1));

            wire signed [ACC_WIDTH-1:0] positive_value =
                $signed({1'b0, magnitude});

            assign coefficient =
                coeff_bits[4]
                ? -positive_value
                : positive_value;

        end else begin : int_decode

            assign coefficient = $signed(coeff_bits);

        end
    endgenerate

    wire signed [ACC_WIDTH-1:0] term =
        spin_positive ? coefficient : -coefficient;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            accum_q <= 0;
        else if (clear)
            accum_q <= 0;
        else if (valid)
            accum_q <= accum_q + term;
    end

endmodule

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
module hw01_logit #(
    parameter integer B = 5,
    parameter integer IS_FP = 1,
    parameter integer ACC_WIDTH = 13
)(
    input  wire clk,
    input  wire rst_n,
    input  wire clear,
    input  wire valid,
    input  wire last,
    input wire [B-1:0] coeff_bits,
    input  wire spin_positive,
    input  wire signed [31:0] gain_q28,
    output wire signed [ACC_WIDTH-1:0] accum_q,
    output reg signed [17:0] logit_q12,
    output reg logit_valid
);
    hw01_row #(
        .B(B),
        .IS_FP(IS_FP),
        .ACC_WIDTH(ACC_WIDTH)
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



module hw01_fp5(
    input wire clk, rst_n, clear, valid, last,
    input wire [4:0] coeff_bits,
    input wire spin_positive,
    input wire signed [31:0] gain_q28,
    output wire signed [12:0] accum_q,
    output wire signed [17:0] logit_q12,
    output wire logit_valid
);

    hw01_logit #(
        .B(5),
        .IS_FP(1),
        .ACC_WIDTH(13)
    ) core (
        .clk(clk),
        .rst_n(rst_n),
        .clear(clear),
        .valid(valid),
        .last(last),
        .coeff_bits(coeff_bits),
        .spin_positive(spin_positive),
        .gain_q28(gain_q28),
        .accum_q(accum_q),
        .logit_q12(logit_q12),
        .logit_valid(logit_valid)
    );

endmodule


module hw01_int5(
    input wire clk, rst_n, clear, valid, last,
    input wire [4:0] coeff_bits,
    input wire spin_positive,
    input wire signed [31:0] gain_q28,
    output wire signed [11:0] accum_q,
    output wire signed [17:0] logit_q12,
    output wire logit_valid
);

    hw01_logit #(
        .B(5),
        .IS_FP(0),
        .ACC_WIDTH(12)
    ) core (
        .clk(clk),
        .rst_n(rst_n),
        .clear(clear),
        .valid(valid),
        .last(last),
        .coeff_bits(coeff_bits),
        .spin_positive(spin_positive),
        .gain_q28(gain_q28),
        .accum_q(accum_q),
        .logit_q12(logit_q12),
        .logit_valid(logit_valid)
    );

endmodule


module hw01_int6(
    input wire clk, rst_n, clear, valid, last,
    input wire [5:0] coeff_bits,
    input wire spin_positive,
    input wire signed [31:0] gain_q28,
    output wire signed [12:0] accum_q,
    output wire signed [17:0] logit_q12,
    output wire logit_valid
);

    hw01_logit #(
        .B(6),
        .IS_FP(0),
        .ACC_WIDTH(13)
    ) core (
        .clk(clk),
        .rst_n(rst_n),
        .clear(clear),
        .valid(valid),
        .last(last),
        .coeff_bits(coeff_bits),
        .spin_positive(spin_positive),
        .gain_q28(gain_q28),
        .accum_q(accum_q),
        .logit_q12(logit_q12),
        .logit_valid(logit_valid)
    );

endmodule
