import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import fname_presuffix
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "in_files":
        return argstr % (
            " ".join(
                [
                    "'" + v[0] + "(" + v[1] + ")'" if isinstance(v, tuple) else v
                    for v in value
                ]
            )
        )

    return argstr.format(**inputs)


def in_files_formatter(field, inputs):
    return _format_arg("in_files", field, inputs, argstr="{in_files}")


def _gen_filename(name, inputs):
    if name == "out_file":
        return _gen_fname(
            inputs["in_files"][0][0],
            suffix="_NwarpCat",
            outputtype=inputs["outputtype"],
        )


@shell.define
class NwarpCat(shell.Task["NwarpCat.Outputs"]):
    """
    Examples
    -------

    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.nwarp_cat import NwarpCat

    >>> task = NwarpCat()
    >>> task.inputs.in_files = ["Q25_warp+tlrc.HEAD", ("IDENT", "structural.nii")]
    >>> task.cmdline
    'None'


    """

    executable = "3dNwarpCat"
    in_files: list[ty.Any] = shell.arg(
        help="list of tuples of 3D warps and associated functions",
        position=-1,
        formatter=in_files_formatter,
    )
    space: ty.Any = shell.arg(
        help="string to attach to the output dataset as its atlas space marker.",
        argstr="-space {space}",
    )
    inv_warp: bool = shell.arg(
        help="invert the final warp before output", argstr="-iwarp"
    )
    interp: ty.Any = shell.arg(
        help="specify a different interpolation method than might be used for the warp",
        argstr="-interp {interp}",
        default="wsinc5",
    )
    expad: int = shell.arg(
        help="Pad the nonlinear warps by the given number of voxels in all directions. The warp displacements are extended by linear extrapolation from the faces of the input grid..",
        argstr="-expad {expad}",
    )
    verb: bool = shell.arg(help="be verbose", argstr="-verb")
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_files}_NwarpCat",
        )


def _gen_fname(
    basename, cwd=None, suffix=None, change_ext=True, ext=None, outputtype=None
):
    """
    Generate a filename based on the given parameters.

    The filename will take the form: cwd/basename<suffix><ext>.
    If change_ext is True, it will use the extensions specified in
    <instance>inputs.output_type.

    Parameters
    ----------
    basename : str
        Filename to base the new filename on.
    cwd : str
        Path to prefix to the new filename. (default is output_dir)
    suffix : str
        Suffix to add to the `basename`.  (defaults is '' )
    change_ext : bool
        Flag to change the filename extension to the FSL output type.
        (default True)

    Returns
    -------
    fname : str
        New filename based on given parameters.

    """
    if not basename:
        msg = "Unable to generate filename for command %s. " % "3dNwarpCat"
        msg += "basename is not set!"
        raise ValueError(msg)

    if cwd is None:
        cwd = output_dir
    if ext is None:
        ext = Info.output_type_to_ext(outputtype)
    if change_ext:
        suffix = f"{suffix}{ext}" if suffix else ext

    if suffix is None:
        suffix = ""
    fname = fname_presuffix(basename, suffix=suffix, use_ext=False, newpath=cwd)
    return fname
