import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
import numpy as np
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["out_file"] = os.path.abspath(inputs["in_file"])
    outputs["cm_file"] = os.path.abspath(inputs["cm_file"])
    sout = np.loadtxt(outputs["cm_file"], ndmin=2)
    outputs["cm"] = [tuple(s) for s in sout]
    return outputs


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


def cm_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("cm")


@shell.define
class CenterMass(shell.Task["CenterMass.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.center_mass import CenterMass

    >>> task = CenterMass()
    >>> task.inputs.in_file = Nifti1.mock("structural.nii")
    >>> task.inputs.mask_file = File.mock()
    >>> task.inputs.roi_vals = [2, 10]
    >>> task.cmdline
    'None'


    """

    executable = "3dCM"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dCM",
        argstr="{in_file}",
        position=-2,
        copy_mode="File.CopyMode.copy",
    )
    mask_file: File = shell.arg(
        help="Only voxels with nonzero values in the provided mask will be averaged.",
        argstr="-mask {mask_file}",
    )
    automask: bool = shell.arg(
        help="Generate the mask automatically", argstr="-automask"
    )
    set_cm: ty.Any = shell.arg(
        help="After computing the center of mass, set the origin fields in the header so that the center of mass will be at (x,y,z) in DICOM coords.",
        argstr="-set {set_cm[0]} {set_cm[1]} {set_cm[2]}",
    )
    local_ijk: bool = shell.arg(
        help="Output values as (i,j,k) in local orientation", argstr="-local_ijk"
    )
    roi_vals: list[int] = shell.arg(
        help="Compute center of mass for each blob with voxel value of v0, v1, v2, etc. This option is handy for getting ROI centers of mass.",
        argstr="-roi_vals {roi_vals}",
    )
    all_rois: bool = shell.arg(
        help="Don't bother listing the values of ROIs you want: The program will find all of them and produce a full list",
        argstr="-all_rois",
    )

    class Outputs(shell.Outputs):
        cm_file: Path = shell.outarg(
            help="File to write center of mass to",
            argstr="> {cm_file}",
            position=-1,
            path_template="{in_file}_cm.out",
        )
        out_file: File | None = shell.out(
            help="output file", callable=out_file_callable
        )
        cm: list[ty.Any] | None = shell.out(help="center of mass", callable=cm_callable)
