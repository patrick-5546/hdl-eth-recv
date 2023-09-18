onerror {resume}
quietly WaveActivateNextPane {} 0
add wave -noupdate /recv_top/clk
add wave -noupdate /recv_top/d
add wave -noupdate /recv_top/q
TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {9002 ns} 0}
quietly wave cursor active 1
configure wave -namecolwidth 150
configure wave -valuecolwidth 100
configure wave -justifyvalue left
configure wave -signalnamewidth 0
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits ns
update
WaveRestoreZoom {0 ns} {15824 ns}