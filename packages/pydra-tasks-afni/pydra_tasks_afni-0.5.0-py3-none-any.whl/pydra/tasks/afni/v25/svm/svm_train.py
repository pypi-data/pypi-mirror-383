from fileformats.generic import File
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class SVMTrain(shell.Task["SVMTrain.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.svm.svm_train import SVMTrain

    """

    executable = "3dsvm"
    ttype: str = shell.arg(
        help="tname: classification or regression", argstr="-type {ttype}"
    )
    in_file: File = shell.arg(
        help="A 3D+t AFNI brik dataset to be used for training.",
        argstr="-trainvol {in_file}",
    )
    mask: File = shell.arg(
        help="byte-format brik file used to mask voxels in the analysis",
        argstr="-mask {mask}",
        position=-1,
    )
    nomodelmask: bool = shell.arg(
        help="Flag to enable the omission of a mask file", argstr="-nomodelmask"
    )
    trainlabels: File = shell.arg(
        help=".1D labels corresponding to the stimulus paradigm for the training data.",
        argstr="-trainlabels {trainlabels}",
    )
    censor: File = shell.arg(
        help=".1D censor file that allows the user to ignore certain samples in the training data.",
        argstr="-censor {censor}",
    )
    kernel: str = shell.arg(
        help="string specifying type of kernel function:linear, polynomial, rbf, sigmoid",
        argstr="-kernel {kernel}",
    )
    max_iterations: int = shell.arg(
        help="Specify the maximum number of iterations for the optimization.",
        argstr="-max_iterations {max_iterations}",
    )
    w_out: bool = shell.arg(
        help="output sum of weighted linear support vectors", argstr="-wout"
    )
    options: str = shell.arg(
        help="additional options for SVM-light", argstr="{options}"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output sum of weighted linear support vectors file name",
            argstr="-bucket {out_file}",
            path_template="{in_file}_vectors",
        )
        model: Path = shell.outarg(
            help="basename for the brik containing the SVM model",
            argstr="-model {model}",
            path_template="{in_file}_model",
        )
        alphas: Path = shell.outarg(
            help="output alphas file name",
            argstr="-alpha {alphas}",
            path_template="{in_file}_alphas",
        )
