from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define(xor=[["mask_only_targets", "mask_source"]])
class AutoTcorrelate(shell.Task["AutoTcorrelate.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.auto_tcorrelate import AutoTcorrelate

    >>> task = AutoTcorrelate()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.eta2 = True
    >>> task.inputs.mask = File.mock()
    >>> task.inputs.mask_only_targets = True
    >>> task.inputs.mask_source = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dAutoTcorrelate"
    in_file: Nifti1 = shell.arg(
        help="timeseries x space (volume or surface) file",
        argstr="{in_file}",
        position=-1,
    )
    polort: int = shell.arg(
        help="Remove polynomial trend of order m or -1 for no detrending",
        argstr="-polort {polort}",
    )
    eta2: bool = shell.arg(help="eta^2 similarity", argstr="-eta2")
    mask: File = shell.arg(help="mask of voxels", argstr="-mask {mask}")
    mask_only_targets: bool = shell.arg(
        help="use mask only on targets voxels", argstr="-mask_only_targets"
    )
    mask_source: File | None = shell.arg(
        help="mask for source voxels", argstr="-mask_source {mask_source}"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_similarity_matrix.1D",
        )
