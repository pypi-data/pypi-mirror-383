import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
import os
import os.path as op
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

    if skip is None:
        skip = []

    if parsed_inputs["terminal_output"] == "none":
        parsed_inputs["terminal_output"] = "file_split"

    if not inputs["save_outliers"]:
        skip += ["outliers_file"]

    return parsed_inputs


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    parsed_inputs = _parse_inputs(inputs, output_dir=output_dir)

    outputs = {}
    outputs["out_file"] = op.abspath(inputs["out_file"])
    if inputs["save_outliers"]:
        outputs["out_outliers"] = op.abspath(inputs["outliers_file"])
    return outputs


def out_outliers_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_outliers")


@shell.define(
    xor=[["mask", "automask"], ["mask", "automask", "autoclip"], ["mask", "autoclip"]]
)
class OutlierCount(shell.Task["OutlierCount.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.outlier_count import OutlierCount

    >>> task = OutlierCount()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.mask = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dToutcount"
    in_file: Nifti1 = shell.arg(help="input dataset", argstr="{in_file}", position=-2)
    mask: File | None = shell.arg(
        help="only count voxels within the given mask", argstr="-mask {mask}"
    )
    qthr: ty.Any = shell.arg(
        help="indicate a value for q to compute alpha",
        argstr="-qthr {qthr:.5}",
        default=0.001,
    )
    autoclip: bool = shell.arg(
        help="clip off small voxels", argstr="-autoclip", default=False
    )
    automask: bool = shell.arg(
        help="clip off small voxels", argstr="-automask", default=False
    )
    fraction: bool = shell.arg(
        help="write out the fraction of masked voxels which are outliers at each timepoint",
        argstr="-fraction",
        default=False,
    )
    interval: bool = shell.arg(
        help="write out the median + 3.5 MAD of outlier count with each timepoint",
        argstr="-range",
        default=False,
    )
    save_outliers: bool = shell.arg(help="enables out_file option", default=False)
    outliers_file: Path = shell.arg(
        help="output image file name", argstr="-save {outliers_file}"
    )
    polort: int = shell.arg(
        help="detrend each voxel timeseries with polynomials", argstr="-polort {polort}"
    )
    legendre: bool = shell.arg(
        help="use Legendre polynomials", argstr="-legendre", default=False
    )

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="capture standard output", path_template="{in_file}_outliers"
        )
        out_outliers: File | None = shell.out(
            help="output image file name", callable=out_outliers_callable
        )
