from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class LFCD(shell.Task["LFCD.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.lfcd import LFCD

    >>> task = LFCD()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.mask = File.mock()
    >>> task.inputs.thresh = 0.8 # keep all connections with corr >= 0.8
    >>> task.cmdline
    'None'


    """

    executable = "3dLFCD"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dLFCD", argstr="{in_file}", position=-1
    )
    mask: File = shell.arg(help="mask file to mask input data", argstr="-mask {mask}")
    thresh: float = shell.arg(
        help="threshold to exclude connections where corr <= thresh",
        argstr="-thresh {thresh}",
    )
    polort: int = shell.arg(help="", argstr="-polort {polort}")
    autoclip: bool = shell.arg(
        help="Clip off low-intensity regions in the dataset", argstr="-autoclip"
    )
    automask: bool = shell.arg(
        help="Mask the dataset to target brain-only voxels", argstr="-automask"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_afni",
        )
