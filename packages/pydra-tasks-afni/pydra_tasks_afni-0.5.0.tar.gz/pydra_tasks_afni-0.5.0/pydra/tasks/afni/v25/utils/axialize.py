from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define(xor=[["sagittal", "coronal", "axial"]])
class Axialize(shell.Task["Axialize.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.axialize import Axialize

    >>> task = Axialize()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.cmdline
    'None'


    """

    executable = "3daxialize"
    in_file: Nifti1 = shell.arg(
        help="input file to 3daxialize", argstr="{in_file}", position=-2
    )
    verb: bool = shell.arg(help="Print out a progerss report", argstr="-verb")
    sagittal: bool = shell.arg(
        help="Do sagittal slice order [-orient ASL]", argstr="-sagittal"
    )
    coronal: bool = shell.arg(
        help="Do coronal slice order  [-orient RSA]", argstr="-coronal"
    )
    axial: bool = shell.arg(
        help="Do axial slice order    [-orient RAI]This is the default AFNI axial order, andis the one currently required by thevolume rendering plugin; this is alsothe default orientation output by thisprogram (hence the program's name).",
        argstr="-axial",
    )
    orientation: str = shell.arg(
        help="new orientation code", argstr="-orient {orientation}"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_axialize",
        )
