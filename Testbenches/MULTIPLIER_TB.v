// The randomize function available in iverilog seems insufficient.
// We can try using Questasim first, or python.

module MULTIPLIER_TB;

    localparam A_WIDTH = 7;
    localparam B_WIDTH = 4;
    localparam NO_TESTS = 40;
    //localparam seed_val = 23;
    // Declare testbench signals
    reg  [A_WIDTH-1:0] a;       // Input a
    reg  [B_WIDTH-1:0] b;       // Input b
    wire [A_WIDTH+B_WIDTH-1:0] Output;     // Output sum
    reg  [A_WIDTH+B_WIDTH-1:0] expected_output;  // Expected sum for comparison
    integer i;           // Loop variable

    // Instantiate the adder module
    MAC_UNIT dut (
        .A(a),
        .B(b),
        .Result(Output)
    );

    // Testbench process
    initial begin
        $dumpfile("waves.vcd");
        $dumpvars(0, MULTIPLIER_TB);
        //$srand(seed_val);

        // Using $random to generate random values for a and b
        for (i = 0; i < NO_TESTS; i = i + 1) begin
            a = $random;  // Generate random 16-bit input for a
            b = $random;  // Generate random 16-bit input for b
            expected_output = a * b;  // Calculate the expected result
            
            #10; // Wait for 10 time units
            
            // Check if the output is correct
            if (Output === expected_output) begin
                $display("Test %0d PASSED: a = %d, b = %d, result = %d (expected %d)", i, a, b, Output, expected_output);
            end else begin
                $display("Test %0d FAILED: a = %d, b = %d, result = %d (expected %d)", i, a, b, Output, expected_output);
            end
        end

        // End the simulation
        $finish;
    end
endmodule