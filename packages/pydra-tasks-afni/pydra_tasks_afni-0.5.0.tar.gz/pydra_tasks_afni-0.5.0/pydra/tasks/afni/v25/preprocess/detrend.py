from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class Detrend(shell.Task["Detrend.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.detrend import Detrend

    >>> task = Detrend()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.outputtype = "AFNI"
    >>> task.cmdline
    'None'


    """

    executable = "3dDetrend"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dDetrend", argstr="{in_file}", position=-1
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_detrend",
        )
