import attrs
from fileformats.generic import File
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

    _neigh_dict = {"faces": 7, "edges": 19, "vertices": 27}
    if name == "neighborhood":
        value = _neigh_dict[value]

    return argstr.format(**inputs)


def neighborhood_formatter(field, inputs):
    return _format_arg("neighborhood", field, inputs, argstr="-nneigh {neighborhood}")


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    if inputs["label_set"]:
        outputs["out_vals"] = outputs["out_file"] + "_ROI_reho.vals"
    return outputs


def out_vals_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_vals")


@shell.define(xor=[["neighborhood", "ellipsoid", "sphere"]])
class ReHo(shell.Task["ReHo.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.re_ho import ReHo

    >>> task = ReHo()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.mask_file = File.mock()
    >>> task.inputs.neighborhood = "vertices"
    >>> task.inputs.label_set = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dReHo"
    in_file: Nifti1 = shell.arg(
        help="input dataset", argstr="-inset {in_file}", position=2
    )
    chi_sq: bool = shell.arg(
        help="Output the Friedman chi-squared value in addition to the Kendall's W. This option is currently compatible only with the AFNI (BRIK/HEAD) output type; the chi-squared value will be the second sub-brick of the output dataset.",
        argstr="-chi_sq",
    )
    mask_file: File = shell.arg(
        help="Mask within which ReHo should be calculated voxelwise",
        argstr="-mask {mask_file}",
    )
    neighborhood: ty.Any | None = shell.arg(
        help="\nvoxels in neighborhood. can be:\n``faces`` (for voxel and 6 facewise neighbors, only),\n``edges`` (for voxel and 18 face- and edge-wise neighbors),\n``vertices`` (for voxel and 26 face-, edge-, and node-wise neighbors).",
        formatter=neighborhood_formatter,
    )
    sphere: float | None = shell.arg(
        help="\\\nFor additional voxelwise neighborhood control, the\nradius R of a desired neighborhood can be put in; R is\na floating point number, and must be >1. Examples of\nthe numbers of voxels in a given radius are as follows\n(you can roughly approximate with the ol' :math:`4\\pi\\,R^3/3`\nthing):\n\n    * R=2.0 -> V=33\n    * R=2.3 -> V=57,\n    * R=2.9 -> V=93,\n    * R=3.1 -> V=123,\n    * R=3.9 -> V=251,\n    * R=4.5 -> V=389,\n    * R=6.1 -> V=949,\n\nbut you can choose most any value.",
        argstr="-neigh_RAD {sphere}",
    )
    ellipsoid: ty.Any | None = shell.arg(
        help="\\\nTuple indicating the x, y, and z radius of an ellipsoid\ndefining the neighbourhood of each voxel.\nThe 'hood is then made according to the following relation:\n:math:`(i/A)^2 + (j/B)^2 + (k/C)^2 \\le 1.`\nwhich will have approx. :math:`V=4 \\pi \\, A B C/3`. The impetus for\nthis freedom was for use with data having anisotropic\nvoxel edge lengths.",
        argstr="-neigh_X {ellipsoid[0]} -neigh_Y {ellipsoid[1]} -neigh_Z {ellipsoid[2]}",
    )
    label_set: File = shell.arg(
        help="a set of ROIs, each labelled with distinct integers. ReHo will then be calculated per ROI.",
        argstr="-in_rois {label_set}",
    )
    overwrite: bool = shell.arg(
        help="overwrite output file if it already exists", argstr="-overwrite"
    )

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="Output dataset.",
            argstr="-prefix {out_file}",
            path_template="{in_file}_reho",
            position=1,
        )
        out_vals: File | None = shell.out(
            help="Table of labelwise regional homogeneity values",
            callable=out_vals_callable,
        )
