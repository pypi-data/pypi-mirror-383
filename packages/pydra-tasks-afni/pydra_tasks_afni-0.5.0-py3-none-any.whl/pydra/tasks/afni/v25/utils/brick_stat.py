import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import load_json, save_json
import os
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def aggregate_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    needed_outputs = ["min_val"]

    outputs = {}

    outfile = os.path.join(os.getcwd(), "stat_result.json")

    if runtime is None:
        try:
            min_val = load_json(outfile)["stat"]
        except OSError:
            return None.outputs
    else:
        min_val = []
        for line in stdout.split("\n"):
            if line:
                values = line.split()
                if len(values) > 1:
                    min_val.append([float(val) for val in values])
                else:
                    min_val.extend([float(val) for val in values])

        if len(min_val) == 1:
            min_val = min_val[0]
        save_json(outfile, dict(stat=min_val))
    outputs["min_val"] = min_val

    return outputs


def min_val_callable(output_dir, inputs, stdout, stderr):
    outputs = aggregate_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("min_val")


@shell.define
class BrickStat(shell.Task["BrickStat.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pydra.tasks.afni.v25.utils.brick_stat import BrickStat

    >>> task = BrickStat()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.mask = File.mock()
    >>> task.inputs.min = True
    >>> task.cmdline
    'None'


    """

    executable = "3dBrickStat"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dmaskave", argstr="{in_file}", position=-1
    )
    mask: File = shell.arg(
        help="-mask dset = use dset as mask to include/exclude voxels",
        argstr="-mask {mask}",
        position=2,
    )
    min: bool = shell.arg(
        help="print the minimum value in dataset", argstr="-min", position=1
    )
    slow: bool = shell.arg(
        help="read the whole dataset to find the min and max values", argstr="-slow"
    )
    max: bool = shell.arg(help="print the maximum value in the dataset", argstr="-max")
    mean: bool = shell.arg(help="print the mean value in the dataset", argstr="-mean")
    sum: bool = shell.arg(help="print the sum of values in the dataset", argstr="-sum")
    var: bool = shell.arg(help="print the variance in the dataset", argstr="-var")
    percentile: ty.Any = shell.arg(
        help="p0 ps p1 write the percentile values starting at p0% and ending at p1% at a step of ps%. only one sub-brick is accepted.",
        argstr="-percentile {percentile[0]:.3} {percentile[1]:.3} {percentile[2]:.3}",
    )

    class Outputs(shell.Outputs):
        min_val: float | None = shell.out(help="output", callable=min_val_callable)
