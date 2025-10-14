from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class TSmooth(shell.Task["TSmooth.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.t_smooth import TSmooth

    >>> task = TSmooth()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.custom = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dTsmooth"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dTSmooth", argstr="{in_file}", position=-1
    )
    datum: str = shell.arg(
        help="Sets the data type of the output dataset", argstr="-datum {datum}"
    )
    lin: bool = shell.arg(
        help="3 point linear filter: :math:`0.15\\,a + 0.70\\,b + 0.15\\,c` [This is the default smoother]",
        argstr="-lin",
    )
    med: bool = shell.arg(help="3 point median filter: median(a,b,c)", argstr="-med")
    osf: bool = shell.arg(
        help="3 point order statistics filter::math:`0.15\\,min(a,b,c) + 0.70\\,median(a,b,c) + 0.15\\,max(a,b,c)`",
        argstr="-osf",
    )
    lin3: int = shell.arg(
        help="3 point linear filter: :math:`0.5\\,(1-m)\\,a + m\\,b + 0.5\\,(1-m)\\,c`. Here, 'm' is a number strictly between 0 and 1.",
        argstr="-3lin {lin3}",
    )
    hamming: int = shell.arg(
        help="Use N point Hamming windows. (N must be odd and bigger than 1.)",
        argstr="-hamming {hamming}",
    )
    blackman: int = shell.arg(
        help="Use N point Blackman windows. (N must be odd and bigger than 1.)",
        argstr="-blackman {blackman}",
    )
    custom: File = shell.arg(
        help="odd # of coefficients must be in a single column in ASCII file",
        argstr="-custom {custom}",
    )
    adaptive: int = shell.arg(
        help="use adaptive mean filtering of width N (where N must be odd and bigger than 3).",
        argstr="-adaptive {adaptive}",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output file from 3dTSmooth",
            argstr="-prefix {out_file}",
            path_template="{in_file}_smooth",
        )
