import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ReadWrite, RisingEdge


@cocotb.test()
async def test_recv_simple(dut):
    """Test that d propagates to q"""

    cocotb.start_soon(Clock(dut.clk, 1, units="us").start())

    await RisingEdge(dut.clk)  # Synchronize with the clock
    await ReadWrite()
    for i in range(10):
        val = random.randint(0, 1)
        dut.d.value = val  # Assign the random value val to the input port d
        await RisingEdge(dut.clk)  # Synchronize with the clock
        await ReadWrite()
        assert dut.q.value == val, "output q was incorrect on the {}th cycle".format(i)
