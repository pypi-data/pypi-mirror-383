from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class Automask(shell.Task["Automask.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.automask import Automask

    >>> task = Automask()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.outputtype = "NIFTI"
    >>> task.cmdline
    'None'


    """

    executable = "3dAutomask"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dAutomask", argstr="{in_file}", position=-1
    )
    clfrac: float = shell.arg(
        help="sets the clip level fraction (must be 0.1-0.9). A small value will tend to make the mask larger [default = 0.5].",
        argstr="-clfrac {clfrac}",
    )
    dilate: int = shell.arg(help="dilate the mask outwards", argstr="-dilate {dilate}")
    erode: int = shell.arg(help="erode the mask inwards", argstr="-erode {erode}")
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_mask",
        )
        brain_file: Path = shell.outarg(
            help="output file from 3dAutomask",
            argstr="-apply_prefix {brain_file}",
            path_template="{in_file}_masked",
        )
