import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

MACDST = "00:0a:95:9d:68:16"
MACSRC = "00:14:22:01:23:45"
PAYLOAD = "Hello World!"


@cocotb.test()
async def test_recv_pass(dut):
    """Test that receiver can successfully receive good data."""
    await init(dut)
    cocotb.start_soon(driver(dut, MACDST, PAYLOAD))
    m = cocotb.start_soon(monitor(dut))
    await ClockCycles(dut.clk, 45)
    assert m.result() == 0, "there was an error"


@cocotb.test()
async def test_recv_wrong_preamble(dut):
    """Test that receiver can detect that the Preamble section is wrong."""
    await init(dut)
    cocotb.start_soon(driver(dut, MACDST, PAYLOAD, wrong_preamble=True))
    m = cocotb.start_soon(monitor(dut))
    await ClockCycles(dut.clk, 15)
    assert m.result() == 1, "did not error out in state 1"


@cocotb.test()
async def test_recv_wrong_sfd(dut):
    """Test that receiver can detect that the SFD section is wrong."""
    await init(dut)
    cocotb.start_soon(driver(dut, MACDST, PAYLOAD, wrong_sfd=True))
    m = cocotb.start_soon(monitor(dut))
    await ClockCycles(dut.clk, 15)
    assert m.result() == 2, "did not error out in state 2"


@cocotb.test()
async def test_recv_wrong_fcs(dut):
    """Test that receiver can detect that the FCS section is wrong."""
    await init(dut)
    cocotb.start_soon(driver(dut, MACDST, PAYLOAD, wrong_fcs=True))
    m = cocotb.start_soon(monitor(dut))
    await ClockCycles(dut.clk, 45)
    assert m.result() == 7, "did not error out in state 7"


@cocotb.test()
async def test_recv_wrong_macdst(dut):
    """Test that receiver can ignore data that is not intended for it."""
    await init(dut)
    cocotb.start_soon(driver(dut, MACSRC, PAYLOAD))
    m = cocotb.start_soon(monitor(dut))
    await ClockCycles(dut.clk, 15)
    assert not m.done(), "monitor completed"


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
    await RisingEdge(dut.clk)


async def driver(
    dut, mac_dest, payload, wrong_preamble=False, wrong_sfd=False, wrong_fcs=False
):
    assert dut.rdy.value == 1, "rdy should be 1 after reset"

    dut._log.info("Driver: preamble start")
    preamble_byte = "1010_1010"
    dut.data.value = int(preamble_byte, 2)
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    for _ in range(6):
        if wrong_preamble:
            dut.data.value = 0
        await RisingEdge(dut.clk)

    dut._log.info("Driver: sfd start")
    sfd_byte = "1010_1011"
    if wrong_sfd:
        dut.data.value = 0
    else:
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
    for b in fcs_bytes:
        if wrong_fcs:
            dut.data.value = 0
        else:
            dut.data.value = b
        await RisingEdge(dut.clk)


async def monitor(dut):
    assert dut.out.value == 0, "out should be 0 after reset"
    assert dut.vld.value == 0, "vld should be 0 after reset"

    while dut.vld.value == 0:
        await RisingEdge(dut.clk)

    dut._log.info("Monitor: output start")
    out_int = []
    while dut.vld.value == 1:
        # dut._log.info(f"{hex(int(str(dut.out.value), 2))[2:]}")
        out_int.append(int(dut.out.value))
        await RisingEdge(dut.clk)

    mac_src, payload, ret = out_int[:6], out_int[6:-1], out_int[-1]
    mac_src = ":".join([hex(b)[2:].zfill(2) for b in mac_src])
    payload = "".join([chr(b) for b in payload])
    if ret != 0:
        err_state = ret & 0xF
        dut._log.error(f"Monitor: there was an error in state {err_state}")
    else:
        dut._log.info(f"Monitor: payload received from {mac_src}: {payload}")
        assert mac_src == MACSRC, "source MAC address incorrect"
        assert payload == PAYLOAD, "payload incorrect"
    dut._log.info("Monitor: output end")
    return err_state if ret != 0 else 0


def parse_mac_address(mac_str):
    """
    Example
        Input: "00:0a:95:9d:68:16"
        Output: [0, 10, 149, 157, 104, 22]
    """
    return [int(b, 16) for b in mac_str.split(":")]


def get_pllen_bytes(payload_str):
    payload_len = len(payload_str)
    payload_bytes = [
        payload_len >> 8,
        payload_len & 0xFF,
    ]
    return payload_bytes


def parse_payload(payload_str):
    """
    Example
        Input: "Hello World!"
        Output: [72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100, 33]
    """
    return [ord(c) for c in payload_str]


def compute_fcs_bytes(macdst_bytes, macsrc_bytes, pllen_bytes, payload_bytes):
    buffer = macdst_bytes + macsrc_bytes + pllen_bytes + payload_bytes
    lrc = compute_lrc(buffer)
    return [lrc] * 4


def compute_lrc(buffer):
    lrc = 0
    for b in buffer:
        lrc = (lrc + b) & 0xFF
    lrc = ((lrc ^ 0xFF) + 1) & 0xFF
    return lrc
