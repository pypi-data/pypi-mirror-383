from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class BlurInMask(shell.Task["BlurInMask.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.blur_in_mask import BlurInMask

    >>> task = BlurInMask()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.mask = File.mock()
    >>> task.inputs.multimask = File.mock()
    >>> task.inputs.fwhm = 5.0
    >>> task.cmdline
    'None'


    """

    executable = "3dBlurInMask"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dSkullStrip", argstr="-input {in_file}", position=1
    )
    mask: File = shell.arg(
        help="Mask dataset, if desired.  Blurring will occur only within the mask. Voxels NOT in the mask will be set to zero in the output.",
        argstr="-mask {mask}",
    )
    multimask: File = shell.arg(
        help="Multi-mask dataset -- each distinct nonzero value in dataset will be treated as a separate mask for blurring purposes.",
        argstr="-Mmask {multimask}",
    )
    automask: bool = shell.arg(
        help="Create an automask from the input dataset.", argstr="-automask"
    )
    fwhm: float = shell.arg(help="fwhm kernel size", argstr="-FWHM {fwhm}")
    preserve: bool = shell.arg(
        help="Normally, voxels not in the mask will be set to zero in the output. If you want the original values in the dataset to be preserved in the output, use this option.",
        argstr="-preserve",
    )
    float_out: bool = shell.arg(
        help="Save dataset as floats, no matter what the input data type is.",
        argstr="-float",
    )
    options: str = shell.arg(help="options", argstr="{options}", position=2)
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output to the file",
            argstr="-prefix {out_file}",
            position=-1,
            path_template="{in_file}_blur",
        )
