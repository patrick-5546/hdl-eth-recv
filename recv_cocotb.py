import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge
from cocotb.types import LogicArray


@cocotb.test()
async def test_recv_simple(dut):
    """Test that data propagates to out"""

    # Assert initial output is unknown
    assert LogicArray(dut.out.value) == LogicArray("XXXXXXXX")
    # Reset to stop output from floating
    dut.rst.value = 1

    clock = Clock(dut.clk, 1, units="us")  # Create a 1us period clock on port clk
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))

    # Synchronize with the clock
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    expected_val = 0  # output is 0 when reset
    for i in range(9):
        val = random.randint(0, 255)
        dut.data.value = val
        dut._log.info(f"Assigning data to {hex(val)[2:]}")
        await FallingEdge(dut.clk)
        assert dut.out.value == expected_val, f"out was incorrect on the {i}th cycle"
        dut._log.info(f"Checking that out is {hex(expected_val)[2:]}")
        expected_val = val
        await RisingEdge(dut.clk)

    # Check the final input
    await FallingEdge(dut.clk)
    assert dut.out.value == expected_val, "out was incorrect on the last cycle"
