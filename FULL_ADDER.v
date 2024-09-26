module HALF_ADDER(
    input In1,
    input In2,
    output Sum,
    output Carry    
);

// Half Adder
assign Sum = In1^In2;
assign Carry = In1 & In2;
endmodule

module FULL_ADDER(
    input In1,
    input In2,
    input In3,
    output Sum,
    output Carry    
);

// Internal signals
wire Sum_int, Carry_int1, Carry_int2;

// Half Adders
HALF_ADDER ha1 (In1, In2, Sum_int, Carry_int1);
HALF_ADDER ha2 (Sum_int, In3, Sum, Carry_int2);

assign Carry = Carry_int1 | Carry_int2;

endmodule