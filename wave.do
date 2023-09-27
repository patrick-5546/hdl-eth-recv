onerror {resume}
quietly WaveActivateNextPane {} 0
add wave -noupdate /recv_top/clk
add wave -noupdate /recv_top/rst
add wave -noupdate /recv_top/ready
add wave -noupdate -expand -group in /recv_top/start
add wave -noupdate -expand -group in /recv_top/data
add wave -noupdate -expand -group {state logic} /recv_top/data_q
add wave -noupdate -expand -group {state logic} -radix decimal /recv_top/payload_length
add wave -noupdate -expand -group {state logic} /recv_top/lrc
add wave -noupdate -expand -group {state logic} /recv_top/next_state
add wave -noupdate -expand -group state /recv_top/state
add wave -noupdate -expand -group state -radix decimal /recv_top/state_counter
add wave -noupdate -expand -group {out logic} /recv_top/data_q4
add wave -noupdate -expand -group {out logic} /recv_top/data_q6
add wave -noupdate -expand -group out /recv_top/vld
add wave -noupdate -expand -group out /recv_top/out
TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {41281 ns} 0}
quietly wave cursor active 1
configure wave -namecolwidth 150
configure wave -valuecolwidth 100
configure wave -justifyvalue left
configure wave -signalnamewidth 1
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
WaveRestoreZoom {0 ns} {47776 ns}
