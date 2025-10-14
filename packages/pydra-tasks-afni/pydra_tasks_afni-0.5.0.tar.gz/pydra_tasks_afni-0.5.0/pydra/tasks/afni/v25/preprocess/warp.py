import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import (
    fname_presuffix,
    split_filename,
)
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
    if inputs["save_warp"]:
        outputs["warp_file"] = fname_presuffix(
            outputs["out_file"], suffix="_transform.mat", use_ext=False
        )

    return outputs


def warp_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("warp_file")


@shell.define
class Warp(shell.Task["Warp.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.warp import Warp

    >>> task = Warp()
    >>> task.inputs.in_file = Nifti1.mock("structural.nii")
    >>> task.inputs.out_file = "trans.nii.gz"
    >>> task.inputs.matparent = File.mock()
    >>> task.inputs.oblique_parent = File.mock()
    >>> task.inputs.gridset = File.mock()
    >>> task.cmdline
    'None'


    >>> task = Warp()
    >>> task.inputs.in_file = Nifti1.mock("structural.nii")
    >>> task.inputs.out_file = "trans.nii.gz"
    >>> task.inputs.matparent = File.mock()
    >>> task.inputs.oblique_parent = File.mock()
    >>> task.inputs.gridset = File.mock()
    >>> task.cmdline
    '3dWarp -newgrid 1.000000 -prefix trans.nii.gz structural.nii'


    """

    executable = "3dWarp"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dWarp", argstr="{in_file}", position=-1
    )
    tta2mni: bool = shell.arg(
        help="transform dataset from Talairach to MNI152", argstr="-tta2mni"
    )
    mni2tta: bool = shell.arg(
        help="transform dataset from MNI152 to Talaraich", argstr="-mni2tta"
    )
    matparent: File = shell.arg(
        help="apply transformation from 3dWarpDrive", argstr="-matparent {matparent}"
    )
    oblique_parent: File = shell.arg(
        help="Read in the oblique transformation matrix from an oblique dataset and make cardinal dataset oblique to match",
        argstr="-oblique_parent {oblique_parent}",
    )
    deoblique: bool = shell.arg(
        help="transform dataset from oblique to cardinal", argstr="-deoblique"
    )
    interp: ty.Any = shell.arg(
        help="spatial interpolation methods [default = linear]", argstr="-{interp}"
    )
    gridset: File = shell.arg(
        help="copy grid of specified dataset", argstr="-gridset {gridset}"
    )
    newgrid: float = shell.arg(
        help="specify grid of this size (mm)", argstr="-newgrid {newgrid}"
    )
    zpad: int = shell.arg(
        help="pad input dataset with N planes of zero on all sides.",
        argstr="-zpad {zpad}",
    )
    verbose: bool = shell.arg(
        help="Print out some information along the way.", argstr="-verb"
    )
    save_warp: bool = shell.arg(help="save warp as .mat file", requires=["verbose"])
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_warp",
        )
        warp_file: File | None = shell.out(
            help="warp transform .mat file", callable=warp_file_callable
        )
