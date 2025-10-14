import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
import os
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["out_file"] = os.path.abspath(inputs["in_file"])
    return outputs


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


@shell.define
class Refit(shell.Task["Refit.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pydra.tasks.afni.v25.utils.refit import Refit

    >>> task = Refit()
    >>> task.inputs.in_file = Nifti1.mock("structural.nii")
    >>> task.inputs.duporigin_file = File.mock()
    >>> task.cmdline
    'None'


    >>> task = Refit()
    >>> task.inputs.in_file = Nifti1.mock("structural.nii")
    >>> task.inputs.duporigin_file = File.mock()
    >>> task.cmdline
    '3drefit -atrfloat IJK_TO_DICOM_REAL "1 0.2 0 0 -0.2 1 0 0 0 0 1 0" structural.nii'


    """

    executable = "3drefit"
    in_file: Nifti1 = shell.arg(
        help="input file to 3drefit",
        argstr="{in_file}",
        position=-1,
        copy_mode="File.CopyMode.copy",
    )
    deoblique: bool = shell.arg(
        help="replace current transformation matrix with cardinal matrix",
        argstr="-deoblique",
    )
    xorigin: str = shell.arg(
        help="x distance for edge voxel offset", argstr="-xorigin {xorigin}"
    )
    yorigin: str = shell.arg(
        help="y distance for edge voxel offset", argstr="-yorigin {yorigin}"
    )
    zorigin: str = shell.arg(
        help="z distance for edge voxel offset", argstr="-zorigin {zorigin}"
    )
    duporigin_file: File = shell.arg(
        help="Copies the xorigin, yorigin, and zorigin values from the header of the given dataset",
        argstr="-duporigin {duporigin_file}",
    )
    xdel: float = shell.arg(help="new x voxel dimension in mm", argstr="-xdel {xdel}")
    ydel: float = shell.arg(help="new y voxel dimension in mm", argstr="-ydel {ydel}")
    zdel: float = shell.arg(help="new z voxel dimension in mm", argstr="-zdel {zdel}")
    xyzscale: float = shell.arg(
        help="Scale the size of the dataset voxels by the given factor",
        argstr="-xyzscale {xyzscale}",
    )
    space: ty.Any = shell.arg(
        help="Associates the dataset with a specific template type, e.g. TLRC, MNI, ORIG",
        argstr="-space {space}",
    )
    atrcopy: ty.Any = shell.arg(
        help="Copy AFNI header attribute from the given file into the header of the dataset(s) being modified. For more information on AFNI header attributes, see documentation file README.attributes. More than one '-atrcopy' option can be used. For AFNI advanced users only. Do NOT use -atrcopy or -atrstring with other modification options. See also -copyaux.",
        argstr="-atrcopy {atrcopy[0]} {atrcopy[1]}",
    )
    atrstring: ty.Any = shell.arg(
        help="Copy the last given string into the dataset(s) being modified, giving it the attribute name given by the last string.To be safe, the last string should be in quotes.",
        argstr="-atrstring {atrstring[0]} {atrstring[1]}",
    )
    atrfloat: ty.Any = shell.arg(
        help="Create or modify floating point attributes. The input values may be specified as a single string in quotes or as a 1D filename or string, example '1 0.2 0 0 -0.2 1 0 0 0 0 1 0' or flipZ.1D or '1D:1,0.2,2@0,-0.2,1,2@0,2@0,1,0'",
        argstr="-atrfloat {atrfloat[0]} {atrfloat[1]}",
    )
    atrint: ty.Any = shell.arg(
        help="Create or modify integer attributes. The input values may be specified as a single string in quotes or as a 1D filename or string, example '1 0 0 0 0 1 0 0 0 0 1 0' or flipZ.1D or '1D:1,0,2@0,-0,1,2@0,2@0,1,0'",
        argstr="-atrint {atrint[0]} {atrint[1]}",
    )
    saveatr: bool = shell.arg(
        help="(default) Copy the attributes that are known to AFNI into the dset->dblk structure thereby forcing changes to known attributes to be present in the output. This option only makes sense with -atrcopy.",
        argstr="-saveatr",
    )
    nosaveatr: bool = shell.arg(help="Opposite of -saveatr", argstr="-nosaveatr")

    class Outputs(shell.Outputs):
        out_file: File | None = shell.out(
            help="output file", callable=out_file_callable
        )
