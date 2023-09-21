"""Cocotb testbench for recv_top

Notes
- Write after RisingEdge, read/assert after FallingEdge
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge


@cocotb.test()
async def test_recv_simple(dut):
    """Test that data propagates to out"""

    clock = Clock(dut.clk, 1, units="us")  # Create a 1us period clock on port clk
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))

    val = 255

    dut._log.info("toggling rst and initializing inputs")
    dut.rst.value = 1
    dut.data.value = 0
    dut.start.value = 0
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    await FallingEdge(dut.clk)
    assert dut.out.value == 0, "out should be 0 after reset"
    assert dut.ready.value == 1, "ready should be 1 after reset"
    assert dut.vld.value == 0, "vld should be 0 after reset"
    await RisingEdge(dut.clk)

    dut._log.info(f"assigning data to {hex(val)[2:]}")
    dut.data.value = val
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    # Wait until dut output is valid
    await FallingEdge(dut.clk)
    assert dut.vld.value == 1, "vld shoul be 1"
    dut._log.info(f"checking that out is {hex(val)[2:]}")
    assert dut.out.value == val, "out value is unexpected"
