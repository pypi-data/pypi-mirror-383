from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class Merge(shell.Task["Merge.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.merge import Merge

    >>> task = Merge()
    >>> task.inputs.in_files = [Nifti1.mock("functional.nii"), Nifti1.mock("functional2.nii")]
    >>> task.inputs.doall = True
    >>> task.cmdline
    'None'


    """

    executable = "3dmerge"
    in_files: list[Nifti1] = shell.arg(help="", argstr="{in_files}", position=-1)
    doall: bool = shell.arg(
        help="apply options to all sub-bricks in dataset", argstr="-doall"
    )
    blurfwhm: int = shell.arg(
        help="FWHM blur value (mm)", argstr="-1blur_fwhm {blurfwhm}"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_files}_merge",
        )
