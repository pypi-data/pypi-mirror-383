from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class Resample(shell.Task["Resample.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.resample import Resample

    >>> task = Resample()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.master = File.mock()
    >>> task.inputs.outputtype = "NIFTI"
    >>> task.cmdline
    'None'


    """

    executable = "3dresample"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dresample", argstr="-inset {in_file}", position=-1
    )
    orientation: str = shell.arg(
        help="new orientation code", argstr="-orient {orientation}"
    )
    resample_mode: ty.Any = shell.arg(
        help='resampling method from set {"NN", "Li", "Cu", "Bk"}. These are for "Nearest Neighbor", "Linear", "Cubic" and "Blocky"interpolation, respectively. Default is NN.',
        argstr="-rmode {resample_mode}",
    )
    voxel_size: ty.Any = shell.arg(
        help="resample to new dx, dy and dz",
        argstr="-dxyz {voxel_size[0]} {voxel_size[1]} {voxel_size[2]}",
    )
    master: File = shell.arg(
        help="align dataset grid to a reference file", argstr="-master {master}"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_resample",
        )
