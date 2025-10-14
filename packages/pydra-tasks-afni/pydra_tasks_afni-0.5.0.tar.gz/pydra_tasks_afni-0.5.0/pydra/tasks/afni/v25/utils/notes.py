import attrs
from fileformats.generic import File
from fileformats.vendor.afni.medimage import Head
import logging
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
    return outputs


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


@shell.define(xor=[["add_history", "rep_history"]])
class Notes(shell.Task["Notes.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.vendor.afni.medimage import Head
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.notes import Notes

    >>> task = Notes()
    >>> task.inputs.in_file = Head.mock("functional.HEAD")
    >>> task.inputs.add_history = "This note is added to history."
    >>> task.cmdline
    'None'


    """

    executable = "3dNotes"
    in_file: Head = shell.arg(
        help="input file to 3dNotes", argstr="{in_file}", position=-1
    )
    add: str = shell.arg(help="note to add", argstr='-a "{add}"')
    add_history: str = shell.arg(
        help="note to add to history", argstr='-h "{add_history}"'
    )
    rep_history: str = shell.arg(
        help="note with which to replace history", argstr='-HH "{rep_history}"'
    )
    delete: int = shell.arg(help="delete note number num", argstr="-d {delete}")
    ses: bool = shell.arg(help="print to stdout the expanded notes", argstr="-ses")
    out_file: Path = shell.arg(help="output image file name", argstr="{out_file}")
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: File | None = shell.out(
            help="output file", callable=out_file_callable
        )
