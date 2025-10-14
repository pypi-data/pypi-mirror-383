import attrs
from fileformats.generic import File
from fileformats.vendor.afni.medimage import OneD
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


@shell.define(
    xor=[["out_format", "out_cint", "out_int", "out_fint", "out_nice", "out_double"]]
)
class Cat(shell.Task["Cat.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.vendor.afni.medimage import OneD
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.cat import Cat

    >>> task = Cat()
    >>> task.inputs.out_file = "catout.1d"
    >>> task.inputs.sel = "'[0,2]'"
    >>> task.cmdline
    'None'


    """

    executable = "1dcat"
    in_files: list[File] = shell.arg(help="", argstr="{in_files}", position=-2)
    out_file: Path | None = shell.arg(
        help="output (concatenated) file name",
        argstr="> {out_file}",
        position=-1,
        default="catout.1d",
    )
    omitconst: bool = shell.arg(
        help="Omit columns that are identically constant from output.",
        argstr="-nonconst",
    )
    keepfree: bool = shell.arg(
        help="Keep only columns that are marked as 'free' in the 3dAllineate header from '-1Dparam_save'. If there is no such header, all columns are kept.",
        argstr="-nonfixed",
    )
    out_format: ty.Any | None = shell.arg(
        help="specify data type for output.", argstr="-form {out_format}"
    )
    stack: bool = shell.arg(
        help="Stack the columns of the resultant matrix in the output.", argstr="-stack"
    )
    sel: str = shell.arg(
        help="Apply the same column/row selection string to all filenames on the command line.",
        argstr="-sel {sel}",
    )
    out_int: bool = shell.arg(help="specify int data type for output", argstr="-i")
    out_nice: bool = shell.arg(help="specify nice data type for output", argstr="-n")
    out_double: bool = shell.arg(
        help="specify double data type for output", argstr="-d"
    )
    out_fint: bool = shell.arg(
        help="specify int, rounded down, data type for output", argstr="-f"
    )
    out_cint: bool = shell.arg(help="specify int, rounded up, data type for output")
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: OneD | None = shell.out(
            help="output file", callable=out_file_callable
        )
