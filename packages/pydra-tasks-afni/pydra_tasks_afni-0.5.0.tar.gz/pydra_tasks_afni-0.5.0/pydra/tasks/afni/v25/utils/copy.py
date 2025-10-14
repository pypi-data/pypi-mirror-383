from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class Copy(shell.Task["Copy.Outputs"]):
    """
    Examples
    -------

    >>> from copy import deepcopy
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.copy import Copy

    >>> task = Copy()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.cmdline
    'None'


    >>> task = Copy()
    >>> task.inputs.in_file = Nifti1.mock()
    >>> task.inputs.outputtype = "NIFTI"
    >>> task.cmdline
    '3dcopy functional.nii functional_copy.nii'


    >>> task = Copy()
    >>> task.inputs.in_file = Nifti1.mock()
    >>> task.inputs.outputtype = "NIFTI_GZ"
    >>> task.cmdline
    '3dcopy functional.nii functional_copy.nii.gz'


    >>> task = Copy()
    >>> task.inputs.in_file = Nifti1.mock()
    >>> task.inputs.out_file = "new_func.nii"
    >>> task.cmdline
    '3dcopy functional.nii new_func.nii'


    """

    executable = "3dcopy"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dcopy", argstr="{in_file}", position=-2
    )
    verbose: bool = shell.arg(help="print progress reports", argstr="-verb")
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="{out_file}",
            position=-1,
            path_template="{in_file}_copy",
        )
