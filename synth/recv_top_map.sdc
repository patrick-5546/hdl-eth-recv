# ####################################################################

#  Created by Encounter(R) RTL Compiler RC14.13 - v14.10-s027_1 on Wed Oct 04 13:48:35 -0700 2023

# ####################################################################

set sdc_version 1.7

set_units -capacitance 1.0fF
set_units -time 1.0ps

# Set the current design
current_design recv_top

create_clock -name "clk" -add -period 1000.0 -waveform {0.0 50.0} [get_ports clk]
set_clock_gating_check -setup 0.0 
set_wire_load_mode "enclosed"
set_dont_use [get_lib_cells NanGate_15nm_OCL/ANTENNA]
set_dont_use [get_lib_cells NanGate_15nm_OCL/FILLTIE]
set_dont_use [get_lib_cells NanGate_15nm_OCL/FILL_X1]
set_dont_use [get_lib_cells NanGate_15nm_OCL/FILL_X2]
set_dont_use [get_lib_cells NanGate_15nm_OCL/FILL_X4]
set_dont_use [get_lib_cells NanGate_15nm_OCL/FILL_X8]
set_dont_use [get_lib_cells NanGate_15nm_OCL/FILL_X16]
set_dont_use [get_lib_cells NanGate_15nm_OCL/TIEH]
set_dont_use [get_lib_cells NanGate_15nm_OCL/TIEL]
