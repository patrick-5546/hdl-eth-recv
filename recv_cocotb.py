"""Cocotb testbench for recv_top

Notes
- Write after RisingEdge, read/assert after FallingEdge
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Combine, FallingEdge, RisingEdge

MACDST = "00:0a:95:9d:68:16"
MACSRC = "00:14:22:01:23:45"
PAYLOAD = "Hello World!"


@cocotb.test()
async def test_recv_pass(dut):
    """Test that receiver can successfully receive good data."""
    await init(dut)
    # await driver(dut)
    d = cocotb.start_soon(driver(dut, MACDST, PAYLOAD))
    # await monitor(dut)
    # m = cocotb.start_soon(monitor(dut))
    # await Combine(d, m)
    await ClockCycles(dut.clk, 45)


@cocotb.test()
async def test_recv_fail(dut):
    """Test that receiver can detect bad data."""
    await init(dut)
    # await driver(dut)
    d = cocotb.start_soon(driver(dut, MACDST, PAYLOAD, wrong_fcs=True))
    # await monitor(dut)
    # m = cocotb.start_soon(monitor(dut))
    # await Combine(d, m)
    await ClockCycles(dut.clk, 45)


@cocotb.test()
async def test_recv_wrong(dut):
    """Test that receiver can ignore data that is not intended for it."""
    await init(dut)
    # await driver(dut)
    d = cocotb.start_soon(driver(dut, MACSRC, PAYLOAD))
    # await monitor(dut)
    # m = cocotb.start_soon(monitor(dut))
    # await Combine(d, m)
    await ClockCycles(dut.clk, 15)


async def init(dut):
    clock = Clock(dut.clk, 1, units="us")  # Create a 1us period clock on port clk
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))

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


async def driver(dut, mac_dest, payload, wrong_fcs=False):
    await RisingEdge(dut.clk)

    dut._log.info("Driver: preamble start")
    preamble_byte = "1010_1010"
    dut.data.value = int(preamble_byte, 2)
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    for _ in range(6):
        await RisingEdge(dut.clk)

    dut._log.info("Driver: sfd start")
    sfd_byte = "1010_1011"
    dut.data.value = int(sfd_byte, 2)
    await RisingEdge(dut.clk)

    dut._log.info("Driver: macdst start")
    macdst_bytes = parse_mac_address(mac_dest)
    for b in macdst_bytes:
        dut.data.value = b
        await RisingEdge(dut.clk)

    dut._log.info("Driver: macsrc start")
    macsrc_bytes = parse_mac_address(MACSRC)
    for b in macsrc_bytes:
        dut.data.value = b
        await RisingEdge(dut.clk)

    dut._log.info("Driver: pllen start")
    pllen_bytes = get_pllen_bytes(payload)
    for b in pllen_bytes:
        dut.data.value = b
        await RisingEdge(dut.clk)

    dut._log.info("Driver: pl start")
    payload_bytes = parse_payload(payload)
    # dut._log.info([hex(b)[2:] for b in payload_bytes])
    for b in payload_bytes:
        dut.data.value = b
        await RisingEdge(dut.clk)

    dut._log.info("Driver: fcs start")
    fcs_bytes = compute_fcs_bytes(
        macdst_bytes, macsrc_bytes, pllen_bytes, payload_bytes
    )
    for i in range(4):
        if wrong_fcs and i == 2:
            dut.data.value = 0
        else:
            dut.data.value = fcs_bytes
        await RisingEdge(dut.clk)


async def monitor(dut):
    await FallingEdge(dut.clk)

    while dut.vld.value == 0:
        await FallingEdge(dut.clk)

    dut._log.info("Monitor: output start")
    while dut.vld.value == 1:
        await FallingEdge(dut.clk)
    dut._log.info("Monitor: output end")
    # out_ascii = []
    # while dut.vld.value == 1:
    #     out_ascii.append(chr(dut.out.value))
    #     await FallingEdge(dut.clk)
    # out = "".join(out_ascii[::-1])
    # dut._log.info(f"output: {out}")


def parse_mac_address(mac_str):
    """
    Example
        Input: "00:0a:95:9d:68:16"
        Output: [16, 68, 9d, 95, 0a, 00]
    """
    return [int(b, 16) for b in mac_str.split(":")][::-1]


def get_pllen_bytes(payload_str):
    payload_len = len(payload_str)
    payload_bytes = [
        payload_len & 0xFF,
        payload_len >> 8,
    ]
    return payload_bytes


def parse_payload(payload_str):
    """
    Example
        Input: "Hello World!"
        Output: [33, 100, 108, 114, 111, 87, 32, 111, 108, 108, 101, 72]
    """
    return [ord(c) for c in payload_str][::-1]


def compute_fcs_bytes(macdst_bytes, macsrc_bytes, pllen_bytes, payload_bytes):
    buffer = macdst_bytes + macsrc_bytes + pllen_bytes + payload_bytes
    return compute_lrc(buffer)


def compute_lrc(buffer):
    lrc = 0
    for b in buffer:
        lrc = (lrc + b) & 0xFF
    lrc = ((lrc ^ 0xFF) + 1) & 0xFF
    return lrc
