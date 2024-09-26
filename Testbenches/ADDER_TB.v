// The randomize function available in iverilog seems insufficient.
// We can try using Questasim first, or python.

module ADDER_TB;

    localparam bits = 35;
    localparam no_tests = 40;
    //localparam seed_val = 23;
    // Declare testbench signals
    reg  [bits-1:0] a;       // Input a
    reg  [bits-1:0] b;       // Input b
    reg Carry_in;            // Carry Input
    wire [bits-1:0] sum;     // Output sum
    wire carry;              // Output carry
    reg  [bits-1:0] expected_sum;  // Expected sum for comparison
    reg expected_carry;      // Expected carry
    integer i;           // Loop variable

    // Instantiate the adder module
    BRENT_N_ADDER#(.INPUT_SIZE(bits)) dut (
        .A(a),
        .B(b),
        .Cin(Carry_in),
        .Sum(sum),
        .Cout(carry)
    );

    // Testbench process
    initial begin
        $dumpfile("waves.vcd");
        $dumpvars(0, ADDER_TB);
        //$srand(seed_val);

        // Using $random to generate random values for a and b
        for (i = 0; i < no_tests; i = i + 1) begin
            a = $random;  // Generate random 16-bit input for a
            b = $random;  // Generate random 16-bit input for b
            Carry_in = $random;
            {expected_carry, expected_sum} = a + b + Carry_in;  // Calculate the expected result
            
            #10; // Wait for 10 time units
            
            // Check if the output is correct
            if (sum === expected_sum && expected_carry === carry) begin
                $display("Test %0d PASSED: a = %d, b = %d, Cin = %d, sum = %d (expected %d), Carry = %d (expected %d)", i, a, b, Carry_in, sum, expected_sum, carry, expected_carry);
            end else begin
                $display("Test %0d FAILED: a = %d, b = %d, Cin = %d, sum = %d (expected %d), Carry = %d (expected %d)", i, a, b, Carry_in, sum, expected_sum, carry, expected_carry);
            end
        end

        // End the simulation
        $finish;
    end
endmodule