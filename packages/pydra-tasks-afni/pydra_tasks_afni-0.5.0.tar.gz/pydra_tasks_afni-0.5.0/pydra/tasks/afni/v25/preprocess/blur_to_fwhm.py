from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class BlurToFWHM(shell.Task["BlurToFWHM.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.blur_to_fwhm import BlurToFWHM

    >>> task = BlurToFWHM()
    >>> task.inputs.in_file = Nifti1.mock("epi.nii")
    >>> task.inputs.blurmaster = File.mock()
    >>> task.inputs.mask = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dBlurToFWHM"
    in_file: Nifti1 = shell.arg(
        help="The dataset that will be smoothed", argstr="-input {in_file}"
    )
    automask: bool = shell.arg(
        help="Create an automask from the input dataset.", argstr="-automask"
    )
    fwhm: float = shell.arg(
        help="Blur until the 3D FWHM reaches this value (in mm)", argstr="-FWHM {fwhm}"
    )
    fwhmxy: float = shell.arg(
        help="Blur until the 2D (x,y)-plane FWHM reaches this value (in mm)",
        argstr="-FWHMxy {fwhmxy}",
    )
    blurmaster: File = shell.arg(
        help="The dataset whose smoothness controls the process.",
        argstr="-blurmaster {blurmaster}",
    )
    mask: File = shell.arg(
        help="Mask dataset, if desired. Voxels NOT in mask will be set to zero in output.",
        argstr="-mask {mask}",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_afni",
        )
