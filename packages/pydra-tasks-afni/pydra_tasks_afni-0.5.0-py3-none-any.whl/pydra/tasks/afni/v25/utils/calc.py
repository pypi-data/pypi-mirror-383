import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
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
class Calc(shell.Task["Calc.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.calc import Calc

    >>> task = Calc()
    >>> task.inputs.in_file_a = Nifti1.mock("functional.nii")
    >>> task.inputs.in_file_b = File.mock()
    >>> task.inputs.in_file_c = File.mock()
    >>> task.inputs.expr = "a*b"
    >>> task.inputs.other = File.mock()
    >>> task.inputs.outputtype = "NIFTI"
    >>> task.cmdline
    'None'


    >>> task = Calc()
    >>> task.inputs.in_file_a = Nifti1.mock("functional.nii")
    >>> task.inputs.in_file_b = File.mock()
    >>> task.inputs.in_file_c = File.mock()
    >>> task.inputs.out_file = "rm.epi.all1"
    >>> task.inputs.other = File.mock()
    >>> task.cmdline
    '3dcalc -a functional.nii -expr "1" -prefix rm.epi.all1 -overwrite'


    """

    executable = "3dcalc"
    in_file_a: Nifti1 = shell.arg(
        help="input file to 3dcalc", formatter=in_file_a_formatter, position=1
    )
    in_file_b: File = shell.arg(
        help="operand file to 3dcalc", argstr="-b {in_file_b}", position=2
    )
    in_file_c: File = shell.arg(
        help="operand file to 3dcalc", argstr="-c {in_file_c}", position=3
    )
    expr: str = shell.arg(help="expr", argstr='-expr "{expr}"', position=4)
    start_idx: int = shell.arg(help="start index for in_file_a", requires=["stop_idx"])
    stop_idx: int = shell.arg(help="stop index for in_file_a", requires=["start_idx"])
    single_idx: int = shell.arg(help="volume index for in_file_a")
    overwrite: bool = shell.arg(help="overwrite output", argstr="-overwrite")
    other: File = shell.arg(help="other options", argstr="")
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file_a}_calc",
        )
