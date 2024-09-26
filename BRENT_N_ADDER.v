// Verilog Code to add two numbers of any input size using the Brent Kung Architecture
// Author: Manan Garg (manan.garg1504@gmail.com)

module BRENT_N_ADDER#(parameter INPUT_SIZE = 8)(
    input [INPUT_SIZE-1:0] A, 
    input [INPUT_SIZE-1:0] B,
    input Cin,
    output [INPUT_SIZE-1:0] Sum,
    output Cout
);

wire [INPUT_SIZE:0] Carry;
assign Carry[0] = Cin;
localparam N = $clog2(INPUT_SIZE);

// Propogate and generate signals
genvar j, k;
generate
    for (j = 0; (INPUT_SIZE>>j) > 0; j = j + 1) begin: gen_prop
        localparam WIDTH = INPUT_SIZE >> j;
        wire [WIDTH-1:0] P;
        wire [WIDTH-1:0] G;
    end
endgenerate

// Calculate the first-stage generate and propogate signals
assign gen_prop[0].G = A & B;
assign gen_prop[0].P = A ^ B;

// Basic G-P equation
generate
    for (j = 1; j <= N; j = j + 1) begin
        localparam lim = INPUT_SIZE >> j;
        for (k = 0; k < lim; k = k + 1) begin
            assign gen_prop[j].G[k] = gen_prop[j-1].G[2*k+1] | (gen_prop[j-1].P[2*k+1] & gen_prop[j-1].G[2*k]);
            assign gen_prop[j].P[k] = gen_prop[j-1].P[2*k] & gen_prop[j-1].P[2*k+1]; 
        end
    end    
endgenerate

// Carry generation
generate
    for (k = 0; (1<<k) <= INPUT_SIZE; k = k+1) begin
        localparam base = (1<<k);
        for (j = 0; (base*(2*j+1)) <= INPUT_SIZE; j = j+1) begin
            assign Carry[base*(2*j+1)] = gen_prop[k].G[2*j] | (gen_prop[k].P[2*j] & Carry[2*j*base]);
        end
    end
endgenerate

// Calculate Sums
assign Sum = gen_prop[0].P ^ Carry;

assign Cout = Carry[INPUT_SIZE];

endmodule
