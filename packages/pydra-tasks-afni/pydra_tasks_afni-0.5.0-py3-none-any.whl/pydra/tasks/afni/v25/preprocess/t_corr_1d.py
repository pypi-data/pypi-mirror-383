from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define(xor=[["ktaub", "pearson", "spearman", "quadrant"]])
class TCorr1D(shell.Task["TCorr1D.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.t_corr_1d import TCorr1D

    >>> task = TCorr1D()
    >>> task.inputs.xset = Nifti1.mock("u_rc1s1_Template.nii")
    >>> task.inputs.y_1d = File.mock()
    >>> task.cmdline
    '3dTcorr1D -prefix u_rc1s1_Template_correlation.nii.gz u_rc1s1_Template.nii seed.1D'


    """

    executable = "3dTcorr1D"
    xset: Nifti1 = shell.arg(
        help="3d+time dataset input", argstr=" {xset}", position=-2
    )
    y_1d: File = shell.arg(
        help="1D time series file input", argstr=" {y_1d}", position=-1
    )
    pearson: bool = shell.arg(
        help="Correlation is the normal Pearson correlation coefficient",
        argstr=" -pearson",
        position=1,
    )
    spearman: bool = shell.arg(
        help="Correlation is the Spearman (rank) correlation coefficient",
        argstr=" -spearman",
        position=1,
    )
    quadrant: bool = shell.arg(
        help="Correlation is the quadrant correlation coefficient",
        argstr=" -quadrant",
        position=1,
    )
    ktaub: bool = shell.arg(
        help="Correlation is the Kendall's tau_b correlation coefficient",
        argstr=" -ktaub",
        position=1,
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output filename prefix",
            argstr="-prefix {out_file}",
            path_template="{xset}_correlation.nii.gz",
        )
