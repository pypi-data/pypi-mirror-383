from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class TNorm(shell.Task["TNorm.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.t_norm import TNorm

    >>> task = TNorm()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.out_file = "rm.errts.unit errts+tlrc"
    >>> task.cmdline
    'None'


    """

    executable = "3dTnorm"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dTNorm", argstr="{in_file}", position=-1
    )
    norm2: bool = shell.arg(
        help="L2 normalize (sum of squares = 1) [DEFAULT]", argstr="-norm2"
    )
    normR: bool = shell.arg(
        help="normalize so sum of squares = number of time points \\* e.g., so RMS = 1.",
        argstr="-normR",
    )
    norm1: bool = shell.arg(
        help="L1 normalize (sum of absolute values = 1)", argstr="-norm1"
    )
    normx: bool = shell.arg(
        help="Scale so max absolute value = 1 (L_infinity norm)", argstr="-normx"
    )
    polort: int = shell.arg(
        help="Detrend with polynomials of order p before normalizing [DEFAULT = don't do this].\nUse '-polort 0' to remove the mean, for example",
        argstr="-polort {polort}",
    )
    L1fit: bool = shell.arg(
        help="Detrend with L1 regression (L2 is the default)\nThis option is here just for the hell of it",
        argstr="-L1fit",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_tnorm",
        )
