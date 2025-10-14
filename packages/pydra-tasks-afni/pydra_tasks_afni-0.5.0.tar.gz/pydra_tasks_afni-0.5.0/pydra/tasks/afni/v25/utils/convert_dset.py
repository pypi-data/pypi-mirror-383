import attrs
from fileformats.medimage import Gifti
from fileformats.vendor.afni.medimage import Dset
import logging
import os.path as op
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["out_file"] = op.abspath(inputs["out_file"])
    return outputs


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


@shell.define
class ConvertDset(shell.Task["ConvertDset.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Gifti
    >>> from fileformats.vendor.afni.medimage import Dset
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.convert_dset import ConvertDset

    >>> task = ConvertDset()
    >>> task.inputs.in_file = Gifti.mock("lh.pial_converted.gii")
    >>> task.inputs.out_file = "lh.pial_converted.niml.dset"
    >>> task.cmdline
    'None'


    """

    executable = "ConvertDset"
    in_file: Gifti = shell.arg(
        help="input file to ConvertDset", argstr="-input {in_file}", position=-2
    )
    out_file: Path = shell.arg(
        help="output file for ConvertDset", argstr="-prefix {out_file}", position=-1
    )
    out_type: ty.Any = shell.arg(help="output type", argstr="-o_{out_type}", position=1)
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Dset | None = shell.out(
            help="output file", callable=out_file_callable
        )
