"""Cocotb testbench for recv_top

Notes
- Write after RisingEdge, read/assert after FallingEdge
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge

MACDST = "00:0a:95:9d:68:16"
MACSRC = "00:14:22:01:23:45"
PAYLOAD = "Hello World!"


@cocotb.test()
async def test_recv_simple(dut):
    """Test that data propagates to out"""

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
    await RisingEdge(dut.clk)

    dut._log.info("preamble start")
    preamble_byte = "1010_1010"
    dut._log.info(f"assigning {hex(int(preamble_byte, 2))[2:]} to data")
    dut.data.value = int(preamble_byte, 2)
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    for _ in range(6):
        await RisingEdge(dut.clk)

    dut._log.info("sfd start")
    sfd_byte = "1010_1011"
    dut._log.info(f"assigning {hex(int(sfd_byte, 2))[2:]} to data")
    dut.data.value = int(sfd_byte, 2)
    await RisingEdge(dut.clk)

    dut._log.info("macdst start")
    macdst_bytes = parse_mac_address(MACDST)
    for b in macdst_bytes:
        dut.data.value = b
        await RisingEdge(dut.clk)

    dut._log.info("macsrc start")
    macsrc_bytes = parse_mac_address(MACSRC)
    for b in macsrc_bytes:
        dut.data.value = b
        await RisingEdge(dut.clk)

    dut._log.info("pllen start")
    pllen_bytes = get_pllen_bytes(PAYLOAD)
    for b in pllen_bytes:
        dut.data.value = b
        await RisingEdge(dut.clk)

    dut._log.info("pl start")
    payload_bytes = parse_payload(PAYLOAD)
    for b in payload_bytes:
        dut.data.value = b
        await RisingEdge(dut.clk)

    dut._log.info("fcs start")
    fcs_bytes = compute_fcs_bytes(
        macdst_bytes, macsrc_bytes, pllen_bytes, payload_bytes
    )
    for _ in range(4):
        dut.data.value = fcs_bytes
        await RisingEdge(dut.clk)

    # await FallingEdge(dut.clk)
    # assert dut.vld.value == 1, "vld shoul be 1"
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
