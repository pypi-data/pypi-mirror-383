from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class ECM(shell.Task["ECM.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.ecm import ECM

    >>> task = ECM()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.sparsity = 0.1 # keep top 0.1% of connections
    >>> task.inputs.mask = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dECM"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dECM", argstr="{in_file}", position=-1
    )
    sparsity: float = shell.arg(
        help="only take the top percent of connections", argstr="-sparsity {sparsity}"
    )
    full: bool = shell.arg(
        help="Full power method; enables thresholding; automatically selected if -thresh or -sparsity are set",
        argstr="-full",
    )
    fecm: bool = shell.arg(
        help="Fast centrality method; substantial speed increase but cannot accommodate thresholding; automatically selected if -thresh or -sparsity are not set",
        argstr="-fecm",
    )
    shift: float = shell.arg(
        help="shift correlation coefficients in similarity matrix to enforce non-negativity, s >= 0.0; default = 0.0 for -full, 1.0 for -fecm",
        argstr="-shift {shift}",
    )
    scale: float = shell.arg(
        help="scale correlation coefficients in similarity matrix to after shifting, x >= 0.0; default = 1.0 for -full, 0.5 for -fecm",
        argstr="-scale {scale}",
    )
    eps: float = shell.arg(
        help="sets the stopping criterion for the power iteration; :math:`l2\\|v_\\text{old} - v_\\text{new}\\| < eps\\|v_\\text{old}\\|`; default = 0.001",
        argstr="-eps {eps}",
    )
    max_iter: int = shell.arg(
        help="sets the maximum number of iterations to use in the power iteration; default = 1000",
        argstr="-max_iter {max_iter}",
    )
    memory: float = shell.arg(
        help="Limit memory consumption on system by setting the amount of GB to limit the algorithm to; default = 2GB",
        argstr="-memory {memory}",
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
