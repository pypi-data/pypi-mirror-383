import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
from fileformats.vendor.afni.medimage import OneD
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "in_file":
        if (inputs["card"] is attrs.NOTHING) and (inputs["resp"] is attrs.NOTHING):
            return None

    return argstr.format(**inputs)


def in_file_formatter(field, inputs):
    return _format_arg("in_file", field, inputs, argstr="{in_file}")


@shell.define
class Retroicor(shell.Task["Retroicor.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from fileformats.vendor.afni.medimage import OneD
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.retroicor import Retroicor

    >>> task = Retroicor()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.card = File.mock()
    >>> task.inputs.resp = OneD.mock("resp.1D")
    >>> task.inputs.cardphase = File.mock()
    >>> task.inputs.respphase = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dretroicor"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dretroicor", position=-1, formatter=in_file_formatter
    )
    card: File = shell.arg(
        help="1D cardiac data file for cardiac correction",
        argstr="-card {card}",
        position=-2,
    )
    resp: OneD = shell.arg(
        help="1D respiratory waveform data for correction",
        argstr="-resp {resp}",
        position=-3,
    )
    threshold: int = shell.arg(
        help="Threshold for detection of R-wave peaks in input (Make sure it is above the background noise level, Try 3/4 or 4/5 times range plus minimum)",
        argstr="-threshold {threshold}",
        position=-4,
    )
    order: int = shell.arg(
        help="The order of the correction (2 is typical)",
        argstr="-order {order}",
        position=-5,
    )
    cardphase: File = shell.arg(
        help="Filename for 1D cardiac phase output",
        argstr="-cardphase {cardphase}",
        position=-6,
    )
    respphase: File = shell.arg(
        help="Filename for 1D resp phase output",
        argstr="-respphase {respphase}",
        position=-7,
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            position=1,
            path_template="{in_file}_retroicor",
        )
