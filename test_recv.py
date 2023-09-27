import argparse
import os

from cocotb_test.simulator import Modelsim

TESTS_DIR = os.path.join(os.path.dirname(__file__), "src")
VERILOG_SOURCES = [
    "recv_top.sv",
]


class ModelsimCustom(Modelsim):
    def __init__(self, *argv, **kwargs):
        # color cli output
        gui = kwargs["gui"] if "gui" in kwargs else False
        if not gui:
            # https://docs.cocotb.org/en/stable/building.html#envvar-COCOTB_ANSI_OUTPUT
            os.environ["COCOTB_ANSI_OUTPUT"] = "1"

        # set log level to debug
        debug = kwargs["debug"] if "debug" in kwargs else False
        if debug:
            os.environ["COCOTB_LOG_LEVEL"] = "DEBUG"

        # gui and cli files conflict with each other, so put in separate directories
        sim_build = kwargs["sim_build"] if "sim_build" in kwargs else "sim_build"
        sim_build = os.path.join(sim_build, "gui" if gui else "cli")

        super().__init__(sim_build=sim_build, *argv, **kwargs)

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
    ModelsimCustom(
        verilog_sources=[os.path.join(TESTS_DIR, f) for f in VERILOG_SOURCES],
        toplevel="recv_top",
        module="recv_cocotb",
        waves=True,
        gui=args.gui,
        debug=args.debug,
    ).run()


if __name__ == "__main__":
    # argparse configuration
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", "-g", action="store_true", help="run in gui")
    parser.add_argument(
        "--debug", "-d", action="store_true", help="set log level to debug"
    )
    args = parser.parse_args()

    test_recv(args)
