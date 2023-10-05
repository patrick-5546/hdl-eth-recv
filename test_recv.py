import argparse
import os

from cocotb_test.simulator import Modelsim

SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
VERILOG_SOURCES = [
    "recv_top.sv",
]
SYNTH_DIR = os.path.join(os.path.dirname(__file__), "synth")
SYNTH_VERILOG_SOURCES = [
    "recv_top_map.v",
    "NanGate_15nm_OCL_conditional.v",
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

        # add synth instance variable
        self.synth = kwargs["synth"] if "synth" in kwargs else False

        # gui and cli files conflict with each other, so put in separate directories
        sim_build = kwargs["sim_build"] if "sim_build" in kwargs else "sim_build"
        sim_build = os.path.join(sim_build, "gui" if gui else "cli")

        # put synthesized design runs in separate directories
        if self.synth:
            sim_build += "-synth"

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

    def build_command(self):
        cmd = super().build_command()

        # add sdf file for simulation of synthesized design
        if not self.compile_only and self.synth:
            sim_cmd = cmd[-1]
            top = self.toplevel[0].split(".")[0]
            sdf_args = ["-sdfnoerror", "-sdftyp", f"/{top}=../../synth/{top}_map.sdf"]
            sim_cmd += sdf_args

        return cmd


def test_recv(args):
    if not args.synth:
        verilog_sources = [os.path.join(SRC_DIR, f) for f in VERILOG_SOURCES]
    else:
        verilog_sources = [os.path.join(SYNTH_DIR, f) for f in SYNTH_VERILOG_SOURCES]

    ModelsimCustom(
        verilog_sources=verilog_sources,
        toplevel="recv_top",
        module="recv_cocotb",
        waves=True,
        gui=args.gui,
        debug=args.debug,
        synth=args.synth,
    ).run()


if __name__ == "__main__":
    # argparse configuration
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", "-g", action="store_true", help="run in gui")
    parser.add_argument(
        "--debug", "-d", action="store_true", help="set log level to debug"
    )
    parser.add_argument(
        "--synth", "-s", action="store_true", help="simulate synthesized design"
    )
    args = parser.parse_args()

    test_recv(args)
