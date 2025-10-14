import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import fname_presuffix
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _gen_filename(name, inputs):
    if name == "out_file":
        return _gen_fname(
            inputs["in_files"][0][0], suffix="_tcat", outputtype=inputs["outputtype"]
        )


def out_file_default(inputs):
    return _gen_filename("out_file", inputs=inputs)


@shell.define
class TCatSubBrick(shell.Task["TCatSubBrick.Outputs"]):
    """
    Examples
    -------

    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.t_cat_sub_brick import TCatSubBrick

    >>> task = TCatSubBrick()
    >>> task.inputs.in_files = [('functional.nii', "'{2..$}'"), ('functional2.nii', "'{2..$}'")]
    >>> task.inputs.rlt = "+"
    >>> task.cmdline
    'None'


    """

    executable = "3dTcat"
    in_files: list[ty.Any] = shell.arg(
        help="List of tuples of file names and subbrick selectors as strings.Don't forget to protect the single quotes in the subbrick selectorso the contents are protected from the command line interpreter.",
        argstr="{in_files[0]}{in_files[1]} ...",
        position=-1,
    )
    rlt: ty.Any = shell.arg(
        help="Remove linear trends in each voxel time series loaded from each input dataset, SEPARATELY. Option -rlt removes the least squares fit of 'a+b*t' to each voxel time series. Option -rlt+ adds dataset mean back in. Option -rlt++ adds overall mean of all dataset timeseries back in.",
        argstr="-rlt{rlt}",
        position=1,
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="out_file",
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
        msg = "Unable to generate filename for command %s. " % "3dTcat"
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
