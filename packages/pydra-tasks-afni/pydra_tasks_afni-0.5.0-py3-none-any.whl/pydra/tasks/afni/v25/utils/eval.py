import attrs
from fileformats.generic import File
from fileformats.vendor.afni.medimage import OneD
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "in_file_a":
        arg = argstr.format(**{name: value})
        if inputs["start_idx"] is not attrs.NOTHING:
            arg += "[%d..%d]" % (inputs["start_idx"], inputs["stop_idx"])
        if inputs["single_idx"] is not attrs.NOTHING:
            arg += "[%d]" % (inputs["single_idx"])
        return arg

    return argstr.format(**inputs)


def in_file_a_formatter(field, inputs):
    return _format_arg("in_file_a", field, inputs, argstr="-a {in_file_a}")


@shell.define
class Eval(shell.Task["Eval.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.vendor.afni.medimage import OneD
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.eval import Eval

    >>> task = Eval()
    >>> task.inputs.in_file_a = OneD.mock("seed.1D")
    >>> task.inputs.in_file_b = File.mock()
    >>> task.inputs.in_file_c = File.mock()
    >>> task.inputs.out_file =  "data_calc.1D"
    >>> task.inputs.expr = "a*b"
    >>> task.inputs.other = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "1deval"
    in_file_a: OneD = shell.arg(
        help="input file to 1deval", formatter=in_file_a_formatter, position=1
    )
    in_file_b: File = shell.arg(
        help="operand file to 1deval", argstr="-b {in_file_b}", position=2
    )
    in_file_c: File = shell.arg(
        help="operand file to 1deval", argstr="-c {in_file_c}", position=3
    )
    out1D: bool = shell.arg(help="output in 1D", argstr="-1D")
    expr: str = shell.arg(help="expr", argstr='-expr "{expr}"', position=4)
    start_idx: int = shell.arg(help="start index for in_file_a", requires=["stop_idx"])
    stop_idx: int = shell.arg(help="stop index for in_file_a", requires=["start_idx"])
    single_idx: int = shell.arg(help="volume index for in_file_a")
    other: File = shell.arg(help="other options", argstr="")
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file_a}_calc",
        )
