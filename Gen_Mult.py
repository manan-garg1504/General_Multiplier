# %%
import math
# Input bits, both assumed to be >= 2. Also, a >= b
a = 10
b = 10
accumulate = True
signed = True


addend_width = a+b
# Calculate number of stages
s = b
if (accumulate):
    s += 1

if (signed and (a != b)):
    s += 1

stages = [2]
while True:
    if (stages[-1] >= s):
        break

    stages.append (math.floor(stages[-1]*1.5))

stages.pop()

# Create the array for bunches
width = max(addend_width, a+b)

# %%
# Print module begin string

module_init = []
module_init.append("module MAC_UNIT(")
module_init.append(f"\tinput [{a-1}:0] A,")
module_init.append(f"\tinput [{b-1}:0] B,")
if (accumulate):
    module_init.append(f"\tinput [{addend_width-1}:0] C,")
module_init.append(f"\toutput [{width-1}:0] Result")

module_init.append(");")
module_init.append(f"localparam SIZE_A = {a};")
module_init.append(f"localparam SIZE_B = {b};")

for line in module_init:
    print(line)

# %%
wires = []
for i in range(width):
    wires.append(0)

if accumulate:
    for i in range(addend_width):
        wires[i] += 1

for j in range(b):
    for k in range(a):
        wires[j+k] += 1

if (signed):
    if (a == b):
        wires[a] += 1
    else:
        wires[a-1]+=1
        wires[b-1]+=1

    if (not accumulate):
        wires[width-1] += 1

# %%
subtraction_string = ""
if (signed):
    subtraction_string = "-1"
flip = [
f"wire [SIZE_B-{1+signed}:0] flipped_B;",
"genvar j;",
"// Generate block to reverse the bits of the input wire",
"generate",
f"\tfor (j = 0; j < SIZE_B{subtraction_string}; j = j + 1) begin // Only till SIZE_B-1 if signed",
f"\t\tassign flipped_B[j] = B[SIZE_B-1{subtraction_string}-j]; // Reverse the bits",
"\tend",
"endgenerate"
]

for line in flip:
    print(line)

# %%
# Create the AND array, and assign to Stage_1
AND_Array = []
for i in range(width):
    if wires[i] < 1:
        continue

    AND_Array.append(f"wire [{wires[i]-1}:0] S1_P{i};")

if (signed):
    a -= 1
    b -= 1
for i in range(width):
    num = 0
    if (signed):
        if ((a == b)):
            if (i == a+1):
                AND_Array.append(f"assign S1_P{i}[{num}] = 1'b1;")
                num += 1
        elif (i == a or i == b):
            AND_Array.append(f"assign S1_P{i}[{num}] = 1'b1;")
            num += 1

        if (i == width-1 and not accumulate):
            AND_Array.append(f"assign S1_P{i}[{num}] = 1'b1;")
            num += 1

    if (accumulate):
        if (signed and (i == width-1)):
            AND_Array.append(f"assign S1_P{i}[{num}] = ~C[{i}];")
            num += 1
        else:
            AND_Array.append(f"assign S1_P{i}[{num}] = C[{i}];")
            num += 1

    A_range_msb = min(i, a-1)
    A_range_lsb = max(i-(b-1), 0)
    A_str = f"A[{A_range_msb}:{A_range_lsb}]"

    B_range_lsb = max(0, (b-1)-i)
    B_range_msb = min(b-1, (b-1)+(a-1)-i)
    B_str = f"flipped_B[{B_range_msb}:{B_range_lsb}]"

    if (signed and (i < width-1)):
        if(i == a + b):
            AND_Array.append(f"assign S1_P{i}[{num}] = A[SIZE_A-1] & B[SIZE_B-1];")
            num += 1
        
        else:
            if (i >= a):
                AND_Array.append(f"assign S1_P{i}[{num}] = ~(A[SIZE_A-1] & flipped_B[{B_range_msb+1}]);")
                num += 1
            if (i >= b):
                AND_Array.append(f"assign S1_P{i}[{num}] = ~(A[{A_range_lsb-1}] & B[SIZE_B-1]);")
                num += 1

    if (num >= wires[i]):
        continue

    if num >= 0:
        AND_Array.append(f"assign S1_P{i}[{wires[i]-1}:{num}] = {A_str} & {B_str};")
    num = max(num+1, 0)

if (signed):
    a += 1
    b += 1

for line in AND_Array:
    print(line)

# %%
stage_no = 1

def wire_name(stage, position, begin = None, end = None):
    ret = f"S{stage}_P{position}"
    if (begin != None):
        ret += f"[{begin}"
        if (end != None):
            ret += f":{end}"
        ret += ']'
    
    return ret

# General rule: The msb's are the most delayed
while (len(stages)):
    
    print ("//-------- Stage " + str(stage_no) + " ----------")
    print("")
    next_stage_max_width = stages[-1]

    next_stage_wires_left = min(wires[0], next_stage_max_width) - 1

    wire_definitions = []
    Adders = []
    Assignments = []
    for i in range(width):

        if wires[i] <= 0:
            continue
        
        fa = 0
        ha = 0

        # Calculate number of full and half adders required
        if wires[i] > next_stage_max_width:
            t = wires[i] - next_stage_max_width
            fa = int(t/2)
            ha = t%2

            wires[i] -= (2*fa + ha)
            wires[i+1] += fa + ha

        # Create wire
        wire_def = f"wire [{wires[i]-1}:0] S{stage_no+1}_P{i};"
        wire_definitions.append(wire_def)
        next_stage_and_pos_wires_left = 0

        if i + 1 < width:
            next_stage_and_pos_wires_left = min(wires[i+1], next_stage_max_width) - 1

        wire_for_fa_last = fa*2
        wire_no = 0

        # Generate strings for instantiations of full adders
        for k in range(fa):
            adder_string = f"FULL_ADDER s{stage_no}i{i}n{k} ("
            adder_string += wire_name(stage_no, i, wire_no) + ', '
            adder_string += wire_name(stage_no, i, wire_no+1) + ', '
            adder_string += wire_name(stage_no, i, wire_for_fa_last) + ', '

            adder_string += wire_name(stage_no+1, i, next_stage_wires_left) + ', '
            adder_string += wire_name(stage_no+1, i+1, next_stage_and_pos_wires_left) + ');'

            Adders.append(adder_string)

            next_stage_wires_left -= 1
            wire_no += 2
            wire_for_fa_last += 1
            next_stage_and_pos_wires_left -= 1

        # Generate string for half adder instantiation
        if (ha):
            adder_string = f"HALF_ADDER s{stage_no}i{i} ("
            adder_string += wire_name(stage_no, i, wire_for_fa_last) + ', '
            adder_string += wire_name(stage_no, i, wire_for_fa_last+1) + ', '

            adder_string += wire_name(stage_no+1, i, next_stage_wires_left) + ', '
            adder_string += wire_name(stage_no+1, i+1, next_stage_and_pos_wires_left) + ');'

            Adders.append(adder_string)

            next_stage_and_pos_wires_left -= 1
            next_stage_wires_left -= 1
            wire_for_fa_last += 2

        # Assign the rest of the wires
        if (next_stage_wires_left >=0):
            assign = "assign " + wire_name(stage_no+1, i, next_stage_wires_left, 0) + ' = ' +  wire_name(stage_no, i, wire_for_fa_last + next_stage_wires_left, wire_for_fa_last) + ';'
            Assignments.append(assign)

        next_stage_wires_left = next_stage_and_pos_wires_left

    for wire_def in wire_definitions:
        print(wire_def)
    print("")
    for add in Adders:
        print(add)
    print("")
    for assign in Assignments:
        print(assign)
    print("")

    print("")

    stage_no += 1
    stages.pop()

# %%
wires

# %%
adder_width = width
flag1 = flag2 = 0

if (wires[0] == 1):
    flag1 = 1    
    print(f"assign Result[0] = S{stage_no}_P0[0];")

print("wire Carry;")

if (wires[-1] == 0):
    flag2 = 1
    print(f"assign Result[{width-1}] = Carry;")

adder_width = width - flag1 -flag2
print(f"wire [{adder_width-1}:0] Add_A, Add_B, Adder_Out;")
print(f"assign Result[{width-1-flag2}:{flag1}] = Adder_Out;")

i = flag1
while(i < len(wires) - flag2):
    print(f"assign Add_A[{i-flag1}] = {wire_name(stage_no, i, 0)};")

    B_assign = f"assign Add_B[{i-flag1}] = "
    if (wires[i] == 1):
        print(B_assign + "1'b0;")
    else:
        print(B_assign + wire_name(stage_no, i, 1) + ";")
    i += 1

print(f"BRENT_N_ADDER #(.INPUT_SIZE({adder_width})) final_adder (Add_A, Add_B, 1'b0, Adder_Out, Carry);")

print("endmodule")


