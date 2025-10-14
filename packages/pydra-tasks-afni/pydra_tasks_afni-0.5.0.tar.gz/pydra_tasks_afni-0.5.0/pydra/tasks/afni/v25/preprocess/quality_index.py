from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell


logger = logging.getLogger(__name__)


@shell.define(
    xor=[["mask", "automask"], ["mask", "automask", "autoclip"], ["mask", "autoclip"]]
)
class QualityIndex(shell.Task["QualityIndex.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.quality_index import QualityIndex

    >>> task = QualityIndex()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.mask = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dTqual"
    in_file: Nifti1 = shell.arg(help="input dataset", argstr="{in_file}", position=-2)
    mask: File | None = shell.arg(
        help="compute correlation only across masked voxels", argstr="-mask {mask}"
    )
    spearman: bool = shell.arg(
        help="Quality index is 1 minus the Spearman (rank) correlation coefficient of each sub-brick with the median sub-brick. (default).",
        argstr="-spearman",
        default=False,
    )
    quadrant: bool = shell.arg(
        help="Similar to -spearman, but using 1 minus the quadrant correlation coefficient as the quality index.",
        argstr="-quadrant",
        default=False,
    )
    autoclip: bool = shell.arg(
        help="clip off small voxels", argstr="-autoclip", default=False
    )
    automask: bool = shell.arg(
        help="clip off small voxels", argstr="-automask", default=False
    )
    clip: float = shell.arg(help="clip off values below", argstr="-clip {clip}")
    interval: bool = shell.arg(
        help="write out the median + 3.5 MAD of outlier count with each timepoint",
        argstr="-range",
        default=False,
    )

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="capture standard output",
            argstr="> {out_file}",
            position=-1,
            path_template="{in_file}_tqual",
        )
