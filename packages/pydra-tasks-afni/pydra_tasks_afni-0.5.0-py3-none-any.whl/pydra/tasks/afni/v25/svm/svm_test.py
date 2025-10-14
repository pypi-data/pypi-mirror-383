from fileformats.generic import File
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class SVMTest(shell.Task["SVMTest.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.svm.svm_test import SVMTest

    """

    executable = "3dsvm"
    model: str = shell.arg(
        help="modname is the basename for the brik containing the SVM model",
        argstr="-model {model}",
    )
    in_file: File = shell.arg(
        help="A 3D or 3D+t AFNI brik dataset to be used for testing.",
        argstr="-testvol {in_file}",
    )
    testlabels: File = shell.arg(
        help="*true* class category .1D labels for the test dataset. It is used to calculate the prediction accuracy performance",
        argstr="-testlabels {testlabels}",
    )
    classout: bool = shell.arg(
        help="Flag to specify that pname files should be integer-valued, corresponding to class category decisions.",
        argstr="-classout",
    )
    nopredcensord: bool = shell.arg(
        help="Flag to prevent writing predicted values for censored time-points",
        argstr="-nopredcensord",
    )
    nodetrend: bool = shell.arg(
        help="Flag to specify that pname files should not be linearly detrended",
        argstr="-nodetrend",
    )
    multiclass: bool = shell.arg(
        help="Specifies multiclass algorithm for classification",
        argstr="-multiclass {multiclass:d}",
    )
    options: str = shell.arg(
        help="additional options for SVM-light", argstr="{options}"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="filename for .1D prediction file(s).",
            argstr="-predictions {out_file}",
            path_template="%s_predictions",
        )
