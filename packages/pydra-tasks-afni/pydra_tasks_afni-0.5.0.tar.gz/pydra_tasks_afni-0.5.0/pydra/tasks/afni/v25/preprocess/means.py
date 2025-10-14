from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class Means(shell.Task["Means.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.means import Means

    >>> task = Means()
    >>> task.inputs.in_file_a = Nifti1.mock("im1.nii")
    >>> task.inputs.in_file_b = File.mock()
    >>> task.inputs.out_file =  "output.nii"
    >>> task.cmdline
    'None'


    >>> task = Means()
    >>> task.inputs.in_file_a = Nifti1.mock("im1.nii")
    >>> task.inputs.in_file_b = File.mock()
    >>> task.inputs.datum = "short"
    >>> task.cmdline
    '3dMean -datum short -prefix output.nii im1.nii'


    """

    executable = "3dMean"
    in_file_a: Nifti1 = shell.arg(
        help="input file to 3dMean", argstr="{in_file_a}", position=-2
    )
    in_file_b: File = shell.arg(
        help="another input file to 3dMean", argstr="{in_file_b}", position=-1
    )
    datum: str = shell.arg(
        help="Sets the data type of the output dataset", argstr="-datum {datum}"
    )
    scale: str = shell.arg(help="scaling of output", argstr="-{scale}scale")
    non_zero: bool = shell.arg(help="use only non-zero values", argstr="-non_zero")
    std_dev: bool = shell.arg(help="calculate std dev", argstr="-stdev")
    sqr: bool = shell.arg(help="mean square instead of value", argstr="-sqr")
    summ: bool = shell.arg(help="take sum, (not average)", argstr="-sum")
    count: bool = shell.arg(help="compute count of non-zero voxels", argstr="-count")
    mask_inter: bool = shell.arg(help="create intersection mask", argstr="-mask_inter")
    mask_union: bool = shell.arg(help="create union mask", argstr="-mask_union")
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file_a}_mean",
        )
