from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class Fourier(shell.Task["Fourier.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.fourier import Fourier

    >>> task = Fourier()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.highpass = 0.005
    >>> task.cmdline
    'None'


    """

    executable = "3dFourier"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dFourier", argstr="{in_file}", position=-1
    )
    lowpass: float = shell.arg(help="lowpass", argstr="-lowpass {lowpass}")
    highpass: float = shell.arg(help="highpass", argstr="-highpass {highpass}")
    retrend: bool = shell.arg(
        help="Any mean and linear trend are removed before filtering. This will restore the trend after filtering.",
        argstr="-retrend",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_fourier",
        )
