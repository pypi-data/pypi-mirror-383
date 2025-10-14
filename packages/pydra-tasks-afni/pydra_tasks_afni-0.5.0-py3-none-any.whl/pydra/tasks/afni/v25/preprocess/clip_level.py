import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import load_json, save_json
import os
from pydra.compose import shell


logger = logging.getLogger(__name__)


def aggregate_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    needed_outputs = ["clip_val"]

    outputs = {}

    outfile = os.path.join(os.getcwd(), "stat_result.json")

    if runtime is None:
        try:
            clip_val = load_json(outfile)["stat"]
        except OSError:
            return None.outputs
    else:
        clip_val = []
        for line in stdout.split("\n"):
            if line:
                values = line.split()
                if len(values) > 1:
                    clip_val.append([float(val) for val in values])
                else:
                    clip_val.extend([float(val) for val in values])

        if len(clip_val) == 1:
            clip_val = clip_val[0]
        save_json(outfile, dict(stat=clip_val))
    outputs["clip_val"] = clip_val

    return outputs


def clip_val_callable(output_dir, inputs, stdout, stderr):
    outputs = aggregate_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("clip_val")


@shell.define(xor=[["grad", "doall"]])
class ClipLevel(shell.Task["ClipLevel.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pydra.tasks.afni.v25.preprocess.clip_level import ClipLevel

    >>> task = ClipLevel()
    >>> task.inputs.in_file = Nifti1.mock("anatomical.nii")
    >>> task.inputs.grad = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dClipLevel"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dClipLevel", argstr="{in_file}", position=-1
    )
    mfrac: float = shell.arg(
        help="Use the number ff instead of 0.50 in the algorithm",
        argstr="-mfrac {mfrac}",
        position=2,
    )
    doall: bool = shell.arg(
        help="Apply the algorithm to each sub-brick separately.",
        argstr="-doall",
        position=3,
    )
    grad: File | None = shell.arg(
        help="Also compute a 'gradual' clip level as a function of voxel position, and output that to a dataset.",
        argstr="-grad {grad}",
        position=3,
    )

    class Outputs(shell.Outputs):
        clip_val: float | None = shell.out(help="output", callable=clip_val_callable)
