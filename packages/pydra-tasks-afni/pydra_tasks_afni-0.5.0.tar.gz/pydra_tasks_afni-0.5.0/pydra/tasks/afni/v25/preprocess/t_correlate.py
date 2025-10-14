from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class TCorrelate(shell.Task["TCorrelate.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.t_correlate import TCorrelate

    >>> task = TCorrelate()
    >>> task.inputs.xset = Nifti1.mock("u_rc1s1_Template.nii")
    >>> task.inputs.yset = File.mock()
    >>> task.inputs.out_file = "functional_tcorrelate.nii.gz"
    >>> task.inputs.pearson = True
    >>> task.cmdline
    'None'


    """

    executable = "3dTcorrelate"
    xset: Nifti1 = shell.arg(help="input xset", argstr="{xset}", position=-2)
    yset: File = shell.arg(help="input yset", argstr="{yset}", position=-1)
    pearson: bool = shell.arg(
        help="Correlation is the normal Pearson correlation coefficient",
        argstr="-pearson",
    )
    polort: int = shell.arg(
        help="Remove polynomial trend of order m", argstr="-polort {polort}"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{xset}_tcorr",
        )
