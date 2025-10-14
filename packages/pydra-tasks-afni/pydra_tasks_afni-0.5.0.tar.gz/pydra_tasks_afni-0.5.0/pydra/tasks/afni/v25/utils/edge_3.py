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


@shell.define(xor=[["gscale", "fscale", "scale_floats", "nscale"]])
class Edge3(shell.Task["Edge3.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.edge_3 import Edge3

    >>> task = Edge3()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.datum = "byte"
    >>> task.cmdline
    'None'


    """

    executable = "3dedge3"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dedge3", argstr="-input {in_file}", position=1
    )
    out_file: Path = shell.arg(
        help="output image file name", argstr="-prefix {out_file}", position=-1
    )
    datum: ty.Any = shell.arg(
        help="specify data type for output. Valid types are 'byte', 'short' and 'float'.",
        argstr="-datum {datum}",
    )
    fscale: bool = shell.arg(
        help="Force scaling of the output to the maximum integer range.",
        argstr="-fscale",
    )
    gscale: bool = shell.arg(
        help="Same as '-fscale', but also forces each output sub-brick to to get the same scaling factor.",
        argstr="-gscale",
    )
    nscale: bool = shell.arg(
        help="Don't do any scaling on output to byte or short datasets.",
        argstr="-nscale",
    )
    scale_floats: float | None = shell.arg(
        help="Multiply input by VAL, but only if the input datum is float. This is needed when the input dataset has a small range, like 0 to 2.0 for instance. With such a range, very few edges are detected due to what I suspect to be truncation problems. Multiplying such a dataset by 10000 fixes the problem and the scaling is undone at the output.",
        argstr="-scale_floats {scale_floats}",
    )
    verbose: bool = shell.arg(
        help="Print out some information along the way.", argstr="-verbose"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: File | None = shell.out(
            help="output file", callable=out_file_callable
        )
