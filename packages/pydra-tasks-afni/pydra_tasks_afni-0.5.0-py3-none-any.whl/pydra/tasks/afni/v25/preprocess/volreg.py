from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "in_weight_volume" and not isinstance(value, tuple):
        value = (value, 0)

    return argstr.format(**inputs)


def in_weight_volume_formatter(field, inputs):
    return _format_arg(
        "in_weight_volume",
        field,
        inputs,
        argstr="-weight '{in_weight_volume[0]}[{in_weight_volume[1]}]'",
    )


@shell.define
class Volreg(shell.Task["Volreg.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.volreg import Volreg

    >>> task = Volreg()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.basefile = Nifti1.mock()
    >>> task.inputs.zpad = 4
    >>> task.cmdline
    'None'


    >>> task = Volreg()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.basefile = Nifti1.mock("functional.nii")
    >>> task.inputs.oned_file = "dfile.r1.1D"
    >>> task.inputs.verbose = True
    >>> task.cmdline
    '3dvolreg -cubic -1Dfile dfile.r1.1D -1Dmatrix_save mat.r1.tshift+orig.1D -prefix rm.epi.volreg.r1 -verbose -base functional.nii -zpad 1 -maxdisp1D functional_md.1D functional.nii'


    """

    executable = "3dvolreg"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dvolreg", argstr="{in_file}", position=-1
    )
    in_weight_volume: ty.Any = shell.arg(
        help="weights for each voxel specified by a file with an optional volume number (defaults to 0)",
        formatter=in_weight_volume_formatter,
    )
    basefile: Nifti1 = shell.arg(
        help="base file for registration", argstr="-base {basefile}", position=-6
    )
    zpad: int = shell.arg(
        help="Zeropad around the edges by 'n' voxels during rotations",
        argstr="-zpad {zpad}",
        position=-5,
    )
    verbose: bool = shell.arg(
        help="more detailed description of the process", argstr="-verbose"
    )
    timeshift: bool = shell.arg(
        help="time shift to mean slice time offset", argstr="-tshift 0"
    )
    copyorigin: bool = shell.arg(
        help="copy base file origin coords to output", argstr="-twodup"
    )
    interp: ty.Any = shell.arg(
        help="spatial interpolation methods [default = heptic]", argstr="-{interp}"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_volreg",
        )
        md1d_file: Path = shell.outarg(
            help="max displacement output file",
            argstr="-maxdisp1D {md1d_file}",
            position=-4,
            path_template="{in_file}_md.1D",
        )
        oned_file: Path = shell.outarg(
            help="1D movement parameters output file",
            argstr="-1Dfile {oned_file}",
            path_template="{in_file}.1D",
        )
        oned_matrix_save: Path = shell.outarg(
            help="Save the matrix transformation",
            argstr="-1Dmatrix_save {oned_matrix_save}",
            path_template="{in_file}.aff12.1D",
        )
