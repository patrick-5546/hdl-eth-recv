"""Cocotb testbench for recv_top

Notes
- Write after RisingEdge, read/assert after FallingEdge
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge


@cocotb.test()
async def test_recv_simple(dut):
    """Test that data propagates to out"""

    clock = Clock(dut.clk, 1, units="us")  # Create a 1us period clock on port clk
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))

    val = 255
    cocotb.start_soon(driver(dut, val))
    cocotb.start_soon(monitor(dut, val))

    # Wait long enough for tasks to finish
    await ClockCycles(dut.clk, 10)
    dut._log.info("Max cycles exceeded")


async def driver(dut, val):
    dut._log.info("Driver: start")
    dut._log.info("Toggling rst and initializing inputs")
    dut.rst.value = 1
    dut.data.value = 0
    dut.start.value = 0
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    # Wait until dut is ready to accept input
    await FallingEdge(dut.clk)
    cycles = 0
    while dut.ready.value != 1:
        dut._log.info("Driver: waiting for ready")
        await FallingEdge(dut.clk)
        cycles += 1
    await RisingEdge(dut.clk)

    dut._log.info(f"Driver: assigning data to {hex(val)[2:]}")
    dut.data.value = val
    dut.start.value = 1
    await RisingEdge(dut.clk)

    dut.start.value = 0


async def monitor(dut, val):
    dut._log.info("Monitor: start")
    # await FallingEdge(dut.clk)
    # assert dut.out.value == 0, "out should be 0 after reset"
    # assert dut.ready.value == 1, "ready should be 1 after reset"
    # assert dut.vld.value == 0, "vld should be 0 after reset"

    # Wait until dut output is valid
    await FallingEdge(dut.clk)
    cycles = 0
    while dut.vld.value != 1:
        dut._log.info("Monitor: waiting for vld")
        await FallingEdge(dut.clk)
        cycles += 1

    dut._log.info(f"Monitor: checking that out is {hex(val)[2:]}")
    assert dut.out.value == val, "out value is unexpected"
