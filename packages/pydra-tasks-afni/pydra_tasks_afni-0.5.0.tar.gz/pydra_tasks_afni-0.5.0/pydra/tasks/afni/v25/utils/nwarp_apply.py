from fileformats.generic import File
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define(xor=[["verb", "quiet"]])
class NwarpApply(shell.Task["NwarpApply.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.nwarp_apply import NwarpApply

    >>> task = NwarpApply()
    >>> task.inputs.in_file = "Fred+orig"
    >>> task.inputs.warp = "'Fred_WARP+tlrc Fred.Xaff12.1D'"
    >>> task.inputs.master = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dNwarpApply"
    in_file: ty.Any = shell.arg(
        help="the name of the dataset to be warped can be multiple datasets",
        argstr="-source {in_file}",
    )
    warp: ty.Any = shell.arg(
        help="the name of the warp dataset. multiple warps can be concatenated (make sure they exist)",
        argstr="-nwarp {warp}",
    )
    inv_warp: bool = shell.arg(
        help="After the warp specified in '-nwarp' is computed, invert it",
        argstr="-iwarp",
    )
    master: File = shell.arg(
        help="the name of the master dataset, which defines the output grid",
        argstr="-master {master}",
    )
    interp: ty.Any = shell.arg(
        help="defines interpolation method to use during warp",
        argstr="-interp {interp}",
        default="wsinc5",
    )
    ainterp: ty.Any = shell.arg(
        help="specify a different interpolation method than might be used for the warp",
        argstr="-ainterp {ainterp}",
    )
    short: bool = shell.arg(
        help="Write output dataset using 16-bit short integers, rather than the usual 32-bit floats.",
        argstr="-short",
    )
    quiet: bool = shell.arg(help="don't be verbose :(", argstr="-quiet")
    verb: bool = shell.arg(help="be extra verbose :)", argstr="-verb")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_Nwarp",
        )
