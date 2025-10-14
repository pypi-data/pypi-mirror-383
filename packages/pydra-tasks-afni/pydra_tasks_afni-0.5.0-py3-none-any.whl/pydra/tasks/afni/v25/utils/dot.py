import attrs
from fileformats.generic import File
from fileformats.text import TextFile
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
class Dot(shell.Task["Dot.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.text import TextFile
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.dot import Dot

    >>> task = Dot()
    >>> task.inputs.in_files = [File.mock("functional.nii[0]"), File.mock("structural.nii")]
    >>> task.inputs.out_file = "out.mask_ae_dice.txt"
    >>> task.inputs.mask = File.mock()
    >>> task.cmdline
    '3dDot -dodice functional.nii[0] structural.nii |& tee out.mask_ae_dice.txt'


    """

    executable = "3dDot"
    in_files: list[File] = shell.arg(
        help="list of input files, possibly with subbrick selectors",
        argstr="{in_files} ...",
        position=-2,
    )
    out_file: Path = shell.arg(
        help="collect output to a file", argstr=" |& tee {out_file}", position=-1
    )
    mask: File = shell.arg(help="Use this dataset as a mask", argstr="-mask {mask}")
    mrange: ty.Any = shell.arg(
        help="Means to further restrict the voxels from 'mset' so thatonly those mask values within this range (inclusive) willbe used.",
        argstr="-mrange {mrange[0]} {mrange[1]}",
    )
    demean: bool = shell.arg(
        help="Remove the mean from each volume prior to computing the correlation",
        argstr="-demean",
    )
    docor: bool = shell.arg(
        help="Return the correlation coefficient (default).", argstr="-docor"
    )
    dodot: bool = shell.arg(help="Return the dot product (unscaled).", argstr="-dodot")
    docoef: bool = shell.arg(
        help="Return the least square fit coefficients {{a,b}} so that dset2 is approximately a + b\\*dset1",
        argstr="-docoef",
    )
    dosums: bool = shell.arg(
        help="Return the 6 numbers xbar=<x> ybar=<y> <(x-xbar)^2> <(y-ybar)^2> <(x-xbar)(y-ybar)> and the correlation coefficient.",
        argstr="-dosums",
    )
    dodice: bool = shell.arg(
        help="Return the Dice coefficient (the Sorensen-Dice index).", argstr="-dodice"
    )
    doeta2: bool = shell.arg(
        help="Return eta-squared (Cohen, NeuroImage 2008).", argstr="-doeta2"
    )
    full: bool = shell.arg(
        help="Compute the whole matrix. A waste of time, but handy for parsing.",
        argstr="-full",
    )
    show_labels: bool = shell.arg(
        help="Print sub-brick labels to help identify what is being correlated. This option is useful whenyou have more than 2 sub-bricks at input.",
        argstr="-show_labels",
    )
    upper: bool = shell.arg(help="Compute upper triangular matrix", argstr="-upper")
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: TextFile | None = shell.out(
            help="output file", callable=out_file_callable
        )
