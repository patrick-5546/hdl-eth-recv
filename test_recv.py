import argparse
import os

from cocotb_test.simulator import Modelsim

TESTS_DIR = os.path.join(os.path.dirname(__file__), "src")
VERILOG_SOURCES = [
    "recv_top.sv",
]


class ModelsimCustom(Modelsim):
    def do_script(self):
        """Overridden to run and load waveform in gui."""
        do_script = ""
        if self.waves:
            do_script += "log -recursive /*;"
        do_script += "run -all;"
        if self.gui:
            do_script += "do ../../wave.do"
        else:
            do_script += "quit"
        return do_script


def test_recv(args):
    # color cli output
    if not args.gui:
        # https://docs.cocotb.org/en/stable/building.html#envvar-COCOTB_ANSI_OUTPUT
        os.environ["COCOTB_ANSI_OUTPUT"] = "1"

    ModelsimCustom(
        verilog_sources=[os.path.join(TESTS_DIR, f) for f in VERILOG_SOURCES],
        toplevel="recv_top",
        module="recv_cocotb",
        waves=True,
        # gui and cli files conflict with each other, so put in separate directories
        sim_build=os.path.join("sim_build", "gui" if args.gui else "cli"),
        gui=args.gui,
    ).run()


if __name__ == "__main__":
    # argparse configuration
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", "-g", action="store_true", help="run in gui")
    args = parser.parse_args()

    test_recv(args)
