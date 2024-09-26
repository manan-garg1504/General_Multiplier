# General Multiplier

This repository contains a python script to create any mXn multiplier, using the Dadda architecture. You can also create a MAC unit instead of a simple multiplier (the addend width will be the sum of the multiplicand widths). Also included is a parametrized n-bit Brent Kung Adder which can be used separately.

Simply edit the relavant variables at the top of ```Gen_Mult.py```, and pipe the output to a verilog file. 

To use the testbenches included, you will have to modify the relevant parameters at the top of the testbench too.

Future updates will include a better testing mechanism, and an easier-to-read script. Please feel free to use this anywhere you need, and site this repository as your source!
