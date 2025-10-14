from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class Fim(shell.Task["Fim.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.fim import Fim

    >>> task = Fim()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.out_file = "functional_corr.nii"
    >>> task.inputs.ideal_file = File.mock()
    >>> task.inputs.fim_thr = 0.0009
    >>> task.cmdline
    'None'


    """

    executable = "3dfim+"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dfim+", argstr="-input {in_file}", position=1
    )
    ideal_file: File = shell.arg(
        help="ideal time series file name",
        argstr="-ideal_file {ideal_file}",
        position=2,
    )
    fim_thr: float = shell.arg(
        help="fim internal mask threshold value",
        argstr="-fim_thr {fim_thr}",
        position=3,
    )
    out: str = shell.arg(
        help="Flag to output the specified parameter", argstr="-out {out}", position=4
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-bucket {out_file}",
            path_template="{in_file}_fim",
        )
