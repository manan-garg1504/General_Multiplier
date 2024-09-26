# Python script to generate verilog for an mXn Dadda Multiplier
# Author: Manan Garg (manan.garg1504@gmail.com)

# %%
import math
# Input bits, both assumed to be >= 2. Also, a >= b
a = 16
b = 16
accumulate = True

addend_width = a+b
# Calculate number of stages
s = b
if (accumulate):
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
module_init.append("module MAC_UNIT#(parameter SIZE_A = "+str(a)+", SIZE_B = "+str(b)+")(")
module_init.append("\tinput [SIZE_A-1:0] A,")
module_init.append("\tinput [SIZE_B-1:0] B,")
if (accumulate):
    module_init.append("\tinput [" + str(addend_width-1) + ":0] C,")
module_init.append("\toutput [" + str(width-1) + ":0] Result")

module_init.append(");")

for line in module_init:
    print(line)

# %%

wires = []
for i in range(width):
    wires.append(0)

if accumulate:
    for i in range(addend_width):
        wires[i] += 1

# Find a better way to do this, this is bad
for j in range(b):
    for k in range(a):
        wires[j+k] += 1

    #print(wires)

# %%
flip = [
"wire [SIZE_B:0] flipped_B;",
"genvar j;",
"// Generate block to reverse the bits of the input wire",
"generate",
"\tfor (j = 0; j < SIZE_B; j = j + 1) begin",
"\t\tassign flipped_B[j] = B[SIZE_B-1-j]; // Reverse the bits",
"\tend",
"endgenerate"
]

for line in flip:
    print(line)

# %%
# Create the AND array, and assign to Stage_1

# For the addend, whether there will be wires from the AND-array is conditional. (On i < width - 1)
for i in range(width):

    if (wires[i] < 1):
        continue

    wname = "S1_P" + str(i)
    print("wire ["+ str(wires[i]-1)+":0] " + wname + ";")

    if (accumulate):
        print("assign " + wname + "[0] = C[" + str(i) + "];")

    if i >= a+b-1:
        continue

    if (accumulate):
        wname = wname + '[' + str(wires[i]-1) + ":1]"

    A_range_msb = min(i, a-1)
    A_range_lsb = max(i-(b-1), 0)
    A_str = "A[" + str(A_range_msb) + ":" + str(A_range_lsb) + "]"

    B_range_lsb = max(0, (b-1)-i)
    B_range_msb = min(b-1, (b-1)+(a-1)-i)
    B_str = "flipped_B[" + str(B_range_msb) + ":" + str(B_range_lsb) + "]"
    print("assign " + wname + " = "  + A_str + " & " + B_str + ";")

# %% [markdown]
# The code below would be very much helped by comments

# %%
stage_no = 1

def wire_name(stage, position, begin = None, end = None):
    ret = "S" + str(stage) + "_P" + str(position)
    if (begin != None ):
        ret += '[' + str(begin)
        if (end != None):
            ret += ':' + str(end)
        ret += ']'
    
    return ret

# General rule: The end bits are the most delayed
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
        wire_def = "wire [" + str(wires[i]-1) + ":0] S" + str(stage_no+1) + "_P" + str(i) + ";"
        wire_definitions.append(wire_def)
        next_stage_and_pos_wires_left = 0

        if i + 1 < width:
            next_stage_and_pos_wires_left = min(wires[i+1], next_stage_max_width) - 1

        wire_for_fa_last = fa*2
        wire_no = 0

        # Generate strings for instantiations of full adders
        for k in range(fa):
            adder_string = "FULL_ADDER s" + str(stage_no) + "i" + str(i) + "n" + str(k) + ' ('
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
            adder_string = "HALF_ADDER s" + str(stage_no) + "i" + str(i) + ' ('
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
    print("assign Result[0] = S" + str(stage_no) + "_P0[0];")

print("wire Carry;")

if (wires[-1] == 0):
    flag2 = 1
    print("assign Result[" + str(width-1) + "] = Carry;")

adder_width = width - flag1 -flag2
print("wire [" + str(adder_width-1) + ":0] Add_A, Add_B, Adder_Out;")
print("assign Result["+str(width-1-flag2)+":"+str(flag1)+"] = Adder_Out;")

i = flag1
while(i < len(wires) - flag2):
    print("assign Add_A["+str(i-flag1)+"] = "+ wire_name(stage_no, i, 0) + ";")

    B_assign = "assign Add_B["+str(i-flag1)+"] = "
    if (wires[i] == 1):
        print(B_assign + "1'b0;")
    else:
        print(B_assign + wire_name(stage_no, i, 1) + ";")
    i += 1

print("BRENT_N_ADDER #(.INPUT_SIZE(" + str (adder_width) + ")) final_adder (Add_A, Add_B, 1'b0, Adder_Out, Carry);")

print("endmodule")


