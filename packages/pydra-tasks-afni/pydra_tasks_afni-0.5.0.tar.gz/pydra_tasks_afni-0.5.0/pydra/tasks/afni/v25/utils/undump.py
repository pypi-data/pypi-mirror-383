import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import split_filename
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    self_dict = {}

    outputs = {}
    metadata = dict(name_source=lambda t: t is not None)
    out_names = list(self_dict["inputs"].traits(**metadata).keys())
    if out_names:
        for name in out_names:
            if outputs[name]:
                _, _, ext = split_filename(outputs[name])
                if ext == "":
                    outputs[name] = outputs[name] + "+orig.BRIK"
    return outputs


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


@shell.define
class Undump(shell.Task["Undump.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.undump import Undump

    >>> task = Undump()
    >>> task.inputs.in_file = Nifti1.mock("structural.nii")
    >>> task.inputs.mask_file = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dUndump"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dUndump, whose geometry will determinethe geometry of the output",
        argstr="-master {in_file}",
        position=-1,
    )
    out_file: Path = shell.arg(
        help="output image file name", argstr="-prefix {out_file}"
    )
    mask_file: File = shell.arg(
        help="mask image file name. Only voxels that are nonzero in the mask can be set.",
        argstr="-mask {mask_file}",
    )
    datatype: ty.Any = shell.arg(
        help="set output file datatype", argstr="-datum {datatype}"
    )
    default_value: float = shell.arg(
        help="default value stored in each input voxel that does not have a value supplied in the input file",
        argstr="-dval {default_value}",
    )
    fill_value: float = shell.arg(
        help="value, used for each voxel in the output dataset that is NOT listed in the input file",
        argstr="-fval {fill_value}",
    )
    coordinates_specification: ty.Any = shell.arg(
        help="Coordinates in the input file as index triples (i, j, k) or spatial coordinates (x, y, z) in mm",
        argstr="-{coordinates_specification}",
    )
    srad: float = shell.arg(
        help="radius in mm of the sphere that will be filled about each input (x,y,z) or (i,j,k) voxel. If the radius is not given, or is 0, then each input data line sets the value in only one voxel.",
        argstr="-srad {srad}",
    )
    orient: ty.Any = shell.arg(
        help="Specifies the coordinate order used by -xyz. The code must be 3 letters, one each from the pairs {R,L} {A,P} {I,S}.  The first letter gives the orientation of the x-axis, the second the orientation of the y-axis, the third the z-axis: R = right-to-left         L = left-to-right A = anterior-to-posterior P = posterior-to-anterior I = inferior-to-superior  S = superior-to-inferior If -orient isn't used, then the coordinate order of the -master (in_file) dataset is used to interpret (x,y,z) inputs.",
        argstr="-orient {orient}",
    )
    head_only: bool = shell.arg(
        help="create only the .HEAD file which gets exploited by the AFNI matlab library function New_HEAD.m",
        argstr="-head_only",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: File | None = shell.out(
            help="assembled file", callable=out_file_callable
        )
