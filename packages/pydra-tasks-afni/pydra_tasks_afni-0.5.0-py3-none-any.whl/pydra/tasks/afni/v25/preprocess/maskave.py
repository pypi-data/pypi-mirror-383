from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class Maskave(shell.Task["Maskave.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.maskave import Maskave

    >>> task = Maskave()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.mask = File.mock()
    >>> task.inputs.quiet = True
    >>> task.cmdline
    'None'


    """

    executable = "3dmaskave"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dmaskave", argstr="{in_file}", position=-2
    )
    mask: File = shell.arg(
        help="matrix to align input file", argstr="-mask {mask}", position=1
    )
    quiet: bool = shell.arg(
        help="matrix to align input file", argstr="-quiet", position=2
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="> {out_file}",
            position=-1,
            path_template="{in_file}_maskave.1D",
        )
