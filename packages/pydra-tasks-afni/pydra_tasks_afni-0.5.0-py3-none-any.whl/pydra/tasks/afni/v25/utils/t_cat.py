from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class TCat(shell.Task["TCat.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.t_cat import TCat

    >>> task = TCat()
    >>> task.inputs.in_files = [Nifti1.mock("functional.nii"), Nifti1.mock("functional2.nii")]
    >>> task.inputs.rlt = "+"
    >>> task.cmdline
    'None'


    """

    executable = "3dTcat"
    in_files: list[Nifti1] = shell.arg(
        help="input file to 3dTcat", argstr=" {in_files}", position=-1
    )
    rlt: ty.Any = shell.arg(
        help="Remove linear trends in each voxel time series loaded from each input dataset, SEPARATELY. Option -rlt removes the least squares fit of 'a+b*t' to each voxel time series. Option -rlt+ adds dataset mean back in. Option -rlt++ adds overall mean of all dataset timeseries back in.",
        argstr="-rlt{rlt}",
        position=1,
    )
    verbose: bool = shell.arg(
        help="Print out some verbose output as the program", argstr="-verb"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_files}_tcat",
        )
