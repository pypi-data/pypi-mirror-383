from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _parse_inputs(inputs, output_dir=None):
    if not output_dir:
        output_dir = os.getcwd()
    parsed_inputs = {}
    skip = []

    if not inputs["in_files"]:
        if skip is None:
            skip = []
        skip += ["out_file"]

    return parsed_inputs


@shell.define
class NwarpAdjust(shell.Task["NwarpAdjust.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import NiftiGz
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.nwarp_adjust import NwarpAdjust

    >>> task = NwarpAdjust()
    >>> task.inputs.warps = [NiftiGz.mock("func2anat_InverseWarp.nii.gz"), NiftiGz.mock("func2anat_InverseWarp.nii.gz"), NiftiGz.mock("func2anat_InverseWarp.nii.gz"), NiftiGz.mock("func2anat_InverseWarp.nii.gz"), NiftiGz.mock("func2anat_InverseWarp.nii.gz")]
    >>> task.cmdline
    'None'


    """

    executable = "3dNwarpAdjust"
    warps: list[NiftiGz] = shell.arg(
        help="List of input 3D warp datasets", argstr="-nwarp {warps}"
    )
    in_files: list[File] = shell.arg(
        help="List of input 3D datasets to be warped by the adjusted warp datasets.  There must be exactly as many of these datasets as there are input warps.",
        argstr="-source {in_files}",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: File | None = shell.outarg(
            help="Output mean dataset, only needed if in_files are also given. The output dataset will be on the common grid shared by the source datasets.",
            argstr="-prefix {out_file}",
            requires=["in_files"],
            path_template="{in_files}_NwarpAdjust",
        )
