from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class Synthesize(shell.Task["Synthesize.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.model.synthesize import Synthesize

    >>> task = Synthesize()
    >>> task.inputs.cbucket = Nifti1.mock("functional.nii")
    >>> task.inputs.matrix = File.mock()
    >>> task.inputs.select = ["baseline"]
    >>> task.cmdline
    '3dSynthesize -cbucket functional.nii -matrix output.1D -select baseline'


    """

    executable = "3dSynthesize"
    cbucket: Nifti1 = shell.arg(
        help="Read the dataset output from 3dDeconvolve via the '-cbucket' option.",
        argstr="-cbucket {cbucket}",
    )
    matrix: File = shell.arg(
        help="Read the matrix output from 3dDeconvolve via the '-x1D' option.",
        argstr="-matrix {matrix}",
    )
    select: list[str] = shell.arg(
        help="A list of selected columns from the matrix (and the corresponding coefficient sub-bricks from the cbucket). Valid types include 'baseline',  'polort', 'allfunc', 'allstim', 'all', Can also provide 'something' where something matches a stim_label from 3dDeconvolve, and 'digits' where digits are the numbers of the select matrix columns by numbers (starting at 0), or number ranges of the form '3..7' and '3-7'.",
        argstr="-select {select}",
    )
    dry_run: bool = shell.arg(
        help="Don't compute the output, just check the inputs.", argstr="-dry"
    )
    TR: float = shell.arg(
        help="TR to set in the output.  The default value of TR is read from the header of the matrix file.",
        argstr="-TR {TR}",
    )
    cenfill: ty.Any = shell.arg(
        help="Determines how censored time points from the 3dDeconvolve run will be filled. Valid types are 'zero', 'nbhr' and 'none'.",
        argstr="-cenfill {cenfill}",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output dataset prefix name (default 'syn')",
            argstr="-prefix {out_file}",
            path_template="syn",
        )
