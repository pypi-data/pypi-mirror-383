from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define(xor=[["fscale", "nscale"]])
class Zcat(shell.Task["Zcat.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.zcat import Zcat

    >>> task = Zcat()
    >>> task.inputs.in_files = [Nifti1.mock("functional2.nii"), Nifti1.mock("functional3.nii")]
    >>> task.cmdline
    'None'


    """

    executable = "3dZcat"
    in_files: list[Nifti1] = shell.arg(help="", argstr="{in_files}", position=-1)
    datum: ty.Any = shell.arg(
        help="specify data type for output. Valid types are 'byte', 'short' and 'float'.",
        argstr="-datum {datum}",
    )
    verb: bool = shell.arg(
        help="print out some verbositiness as the program proceeds.", argstr="-verb"
    )
    fscale: bool = shell.arg(
        help="Force scaling of the output to the maximum integer range.  This only has effect if the output datum is byte or short (either forced or defaulted). This option is sometimes necessary to eliminate unpleasant truncation artifacts.",
        argstr="-fscale",
    )
    nscale: bool = shell.arg(
        help="Don't do any scaling on output to byte or short datasets. This may be especially useful when operating on mask datasets whose output values are only 0's and 1's.",
        argstr="-nscale",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output dataset prefix name (default 'zcat')",
            argstr="-prefix {out_file}",
            path_template="{in_files}_zcat",
        )
