import attrs
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import re
import typing as ty


logger = logging.getLogger(__name__)


def aggregate_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    needed_outputs = ["x_min", "x_max", "y_min", "y_max", "z_min", "z_max"]

    outputs = {}
    pattern = (
        r"x=(?P<x_min>-?\d+)\.\.(?P<x_max>-?\d+)  "
        r"y=(?P<y_min>-?\d+)\.\.(?P<y_max>-?\d+)  "
        r"z=(?P<z_min>-?\d+)\.\.(?P<z_max>-?\d+)"
    )
    for line in stderr.split("\n"):
        m = re.search(pattern, line)
        if m:
            d = m.groupdict()
            outputs["trait_set"](**{k: int(v) for k, v in d.items()})
    return outputs


def x_min_callable(output_dir, inputs, stdout, stderr):
    outputs = aggregate_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("x_min")


def x_max_callable(output_dir, inputs, stdout, stderr):
    outputs = aggregate_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("x_max")


def y_min_callable(output_dir, inputs, stdout, stderr):
    outputs = aggregate_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("y_min")


def y_max_callable(output_dir, inputs, stdout, stderr):
    outputs = aggregate_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("y_max")


def z_min_callable(output_dir, inputs, stdout, stderr):
    outputs = aggregate_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("z_min")


def z_max_callable(output_dir, inputs, stdout, stderr):
    outputs = aggregate_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("z_max")


@shell.define
class Autobox(shell.Task["Autobox.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.autobox import Autobox

    >>> task = Autobox()
    >>> task.inputs.in_file = Nifti1.mock("structural.nii")
    >>> task.cmdline
    'None'


    """

    executable = "3dAutobox"
    in_file: Nifti1 = shell.arg(help="input file", argstr="-input {in_file}")
    padding: int = shell.arg(
        help="Number of extra voxels to pad on each side of box",
        argstr="-npad {padding}",
    )
    no_clustering: bool = shell.arg(
        help="Don't do any clustering to find box. Any non-zero voxel will be preserved in the cropped volume. The default method uses some clustering to find the cropping box, and will clip off small isolated blobs.",
        argstr="-noclust",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="", argstr="-prefix {out_file}", path_template="{in_file}_autobox"
        )
        x_min: int | None = shell.out(callable=x_min_callable)
        x_max: int | None = shell.out(callable=x_max_callable)
        y_min: int | None = shell.out(callable=y_min_callable)
        y_max: int | None = shell.out(callable=y_max_callable)
        z_min: int | None = shell.out(callable=z_min_callable)
        z_max: int | None = shell.out(callable=z_max_callable)
