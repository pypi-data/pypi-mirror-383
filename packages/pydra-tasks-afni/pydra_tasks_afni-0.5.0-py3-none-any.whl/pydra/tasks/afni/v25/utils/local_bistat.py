from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "neighborhood" and value[0] == "RECT":
        value = ("RECT", "%s,%s,%s" % value[1])

    return argstr.format(**inputs)


def neighborhood_formatter(field, inputs):
    return _format_arg(
        "neighborhood",
        field,
        inputs,
        argstr="-nbhd '{neighborhood[0]}({neighborhood[1]})'",
    )


@shell.define(xor=[["automask", "weight_file"]])
class LocalBistat(shell.Task["LocalBistat.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.local_bistat import LocalBistat
    >>> from pydra.utils.typing import MultiInputObj

    >>> task = LocalBistat()
    >>> task.inputs.in_file1 = Nifti1.mock("functional.nii")
    >>> task.inputs.in_file2 = File.mock()
    >>> task.inputs.neighborhood = ("SPHERE", 1.2)
    >>> task.inputs.mask_file = File.mock()
    >>> task.inputs.weight_file = File.mock()
    >>> task.inputs.outputtype = "NIFTI"
    >>> task.cmdline
    'None'


    """

    executable = "3dLocalBistat"
    in_file1: Nifti1 = shell.arg(
        help="Filename of the first image", argstr="{in_file1}", position=-2
    )
    in_file2: File = shell.arg(
        help="Filename of the second image", argstr="{in_file2}", position=-1
    )
    neighborhood: ty.Any = shell.arg(
        help="The region around each voxel that will be extracted for the statistics calculation. Possible regions are: 'SPHERE', 'RHDD' (rhombic dodecahedron), 'TOHD' (truncated octahedron) with a given radius in mm or 'RECT' (rectangular block) with dimensions to specify in mm.",
        formatter=neighborhood_formatter,
    )
    stat: MultiInputObj = shell.arg(
        help="Statistics to compute. Possible names are:\n\n  * pearson  = Pearson correlation coefficient\n  * spearman = Spearman correlation coefficient\n  * quadrant = Quadrant correlation coefficient\n  * mutinfo  = Mutual Information\n  * normuti  = Normalized Mutual Information\n  * jointent = Joint entropy\n  * hellinger= Hellinger metric\n  * crU      = Correlation ratio (Unsymmetric)\n  * crM      = Correlation ratio (symmetrized by Multiplication)\n  * crA      = Correlation ratio (symmetrized by Addition)\n  * L2slope  = slope of least-squares (L2) linear regression of\n               the data from dataset1 vs. the dataset2\n               (i.e., d2 = a + b*d1 ==> this is 'b')\n  * L1slope  = slope of least-absolute-sum (L1) linear\n               regression of the data from dataset1 vs.\n               the dataset2\n  * num      = number of the values in the region:\n               with the use of -mask or -automask,\n               the size of the region around any given\n               voxel will vary; this option lets you\n               map that size.\n  * ALL      = all of the above, in that order\n\nMore than one option can be used.",
        argstr="-stat {stat}...",
    )
    mask_file: File = shell.arg(
        help="mask image file name. Voxels NOT in the mask will not be used in the neighborhood of any voxel. Also, a voxel NOT in the mask will have its statistic(s) computed as zero (0).",
        argstr="-mask {mask_file}",
    )
    automask: bool = shell.arg(
        help="Compute the mask as in program 3dAutomask.", argstr="-automask"
    )
    weight_file: File | None = shell.arg(
        help="File name of an image to use as a weight.  Only applies to 'pearson' statistics.",
        argstr="-weight {weight_file}",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="Output dataset.",
            argstr="-prefix {out_file}",
            path_template="{in_file1}_bistat",
            position=1,
        )
