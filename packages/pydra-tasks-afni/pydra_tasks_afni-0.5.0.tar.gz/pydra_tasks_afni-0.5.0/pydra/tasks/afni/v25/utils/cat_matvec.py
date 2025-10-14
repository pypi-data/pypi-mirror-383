import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "in_file":

        return " ".join(
            f"{mfile} -{opkey}" if opkey else mfile for mfile, opkey in value
        )

    return argstr.format(**inputs)


def in_file_formatter(field, inputs):
    return _format_arg("in_file", field, inputs, argstr="{in_file}")


@shell.define(xor=[["fourxfour", "oneline", "matrix"]])
class CatMatvec(shell.Task["CatMatvec.Outputs"]):
    """
    Examples
    -------

    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.cat_matvec import CatMatvec

    >>> task = CatMatvec()
    >>> task.inputs.in_file = [("structural.BRIK::WARP_DATA","I")]
    >>> task.cmdline
    'None'


    """

    executable = "cat_matvec"
    in_file: list[ty.Any] = shell.arg(
        help="list of tuples of mfiles and associated opkeys",
        position=-2,
        formatter=in_file_formatter,
    )
    matrix: bool = shell.arg(
        help="indicates that the resulting matrix willbe written to outfile in the 'MATRIX(...)' format (FORM 3).This feature could be used, with clever scripting, to inputa matrix directly on the command line to program 3dWarp.",
        argstr="-MATRIX",
    )
    oneline: bool = shell.arg(
        help="indicates that the resulting matrixwill simply be written as 12 numbers on one line.",
        argstr="-ONELINE",
    )
    fourxfour: bool = shell.arg(
        help="Output matrix in augmented form (last row is 0 0 0 1)This option does not work with -MATRIX or -ONELINE",
        argstr="-4x4",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="File to write concattenated matvecs to",
            argstr=" > {out_file}",
            position=-1,
            path_template="{in_file}_cat.aff12.1D",
        )
