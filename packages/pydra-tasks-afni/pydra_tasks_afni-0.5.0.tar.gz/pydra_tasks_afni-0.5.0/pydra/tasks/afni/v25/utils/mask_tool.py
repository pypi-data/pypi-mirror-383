from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class MaskTool(shell.Task["MaskTool.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.mask_tool import MaskTool

    >>> task = MaskTool()
    >>> task.inputs.in_file = [Nifti1.mock("f"), Nifti1.mock("u"), Nifti1.mock("n"), Nifti1.mock("c"), Nifti1.mock("t"), Nifti1.mock("i"), Nifti1.mock("o"), Nifti1.mock("n"), Nifti1.mock("a"), Nifti1.mock("l"), Nifti1.mock("."), Nifti1.mock("n"), Nifti1.mock("i"), Nifti1.mock("i")]
    >>> task.cmdline
    'None'


    """

    executable = "3dmask_tool"
    in_file: list[Nifti1] = shell.arg(
        help="input file or files to 3dmask_tool",
        argstr="-input {in_file}",
        position=-1,
    )
    count: bool = shell.arg(
        help="Instead of created a binary 0/1 mask dataset, create one with counts of voxel overlap, i.e., each voxel will contain the number of masks that it is set in.",
        argstr="-count",
        position=2,
    )
    datum: ty.Any = shell.arg(
        help="specify data type for output.", argstr="-datum {datum}"
    )
    dilate_inputs: str = shell.arg(
        help="Use this option to dilate and/or erode datasets as they are read. ex. '5 -5' to dilate and erode 5 times",
        argstr="-dilate_inputs {dilate_inputs}",
    )
    dilate_results: str = shell.arg(
        help="dilate and/or erode combined mask at the given levels.",
        argstr="-dilate_results {dilate_results}",
    )
    frac: float = shell.arg(
        help="When combining masks (across datasets and sub-bricks), use this option to restrict the result to a certain fraction of the set of volumes",
        argstr="-frac {frac}",
    )
    inter: bool = shell.arg(help="intersection, this means -frac 1.0", argstr="-inter")
    union: bool = shell.arg(help="union, this means -frac 0", argstr="-union")
    fill_holes: bool = shell.arg(
        help="This option can be used to fill holes in the resulting mask, i.e. after all other processing has been done.",
        argstr="-fill_holes",
    )
    fill_dirs: str = shell.arg(
        help="fill holes only in the given directions. This option is for use with -fill holes. should be a single string that specifies 1-3 of the axes using {x,y,z} labels (i.e. dataset axis order), or using the labels in {R,L,A,P,I,S}.",
        argstr="-fill_dirs {fill_dirs}",
        requires=["fill_holes"],
    )
    verbose: int = shell.arg(
        help="specify verbosity level, for 0 to 3", argstr="-verb {verbose}"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_mask",
        )
