from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define(
    xor=[
        ["AP", "master"],
        ["master", "P"],
        ["master", "S"],
        ["master", "I"],
        ["master", "mm"],
        ["master", "IS"],
        ["master", "A"],
        ["master", "RL"],
        ["master", "L"],
        ["master", "R"],
        ["S", "IS", "P", "I", "mm", "L", "A", "AP", "R", "master", "z", "RL"],
        ["master", "z"],
    ]
)
class Zeropad(shell.Task["Zeropad.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.zeropad import Zeropad

    >>> task = Zeropad()
    >>> task.inputs.in_files = Nifti1.mock("functional.nii")
    >>> task.inputs.I = 10
    >>> task.inputs.A = 10
    >>> task.inputs.R = 10
    >>> task.inputs.master = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dZeropad"
    in_files: Nifti1 = shell.arg(help="input dataset", argstr="{in_files}", position=-1)
    I: int | None = shell.arg(
        help="adds 'n' planes of zero at the Inferior edge", argstr="-I {I}"
    )
    S: int | None = shell.arg(
        help="adds 'n' planes of zero at the Superior edge", argstr="-S {S}"
    )
    A: int | None = shell.arg(
        help="adds 'n' planes of zero at the Anterior edge", argstr="-A {A}"
    )
    P: int | None = shell.arg(
        help="adds 'n' planes of zero at the Posterior edge", argstr="-P {P}"
    )
    L: int | None = shell.arg(
        help="adds 'n' planes of zero at the Left edge", argstr="-L {L}"
    )
    R: int | None = shell.arg(
        help="adds 'n' planes of zero at the Right edge", argstr="-R {R}"
    )
    z: int | None = shell.arg(
        help="adds 'n' planes of zero on EACH of the dataset z-axis (slice-direction) faces",
        argstr="-z {z}",
    )
    RL: int | None = shell.arg(
        help="specify that planes should be added or cut symmetrically to make the resulting volume haveN slices in the right-left direction",
        argstr="-RL {RL}",
    )
    AP: int | None = shell.arg(
        help="specify that planes should be added or cut symmetrically to make the resulting volume haveN slices in the anterior-posterior direction",
        argstr="-AP {AP}",
    )
    IS: int | None = shell.arg(
        help="specify that planes should be added or cut symmetrically to make the resulting volume haveN slices in the inferior-superior direction",
        argstr="-IS {IS}",
    )
    mm: bool = shell.arg(
        help="pad counts 'n' are in mm instead of slices, where each 'n' is an integer and at least 'n' mm of slices will be added/removed; e.g., n =  3 and slice thickness = 2.5 mm ==> 2 slices added",
        argstr="-mm",
    )
    master: File | None = shell.arg(
        help="match the volume described in dataset 'mset', where mset must have the same orientation and grid spacing as dataset to be padded. the goal of -master is to make the output dataset from 3dZeropad match the spatial 'extents' of mset by adding or subtracting slices as needed. You can't use -I,-S,..., or -mm with -master",
        argstr="-master {master}",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output dataset prefix name (default 'zeropad')",
            argstr="-prefix {out_file}",
            path_template="zeropad",
        )
