from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell


logger = logging.getLogger(__name__)


def _parse_inputs(inputs, output_dir=None):
    if not output_dir:
        output_dir = os.getcwd()
    parsed_inputs = {}
    skip = []

    if not inputs["showhist"]:
        if skip is None:
            skip = []
        skip += ["out_show"]

    return parsed_inputs


@shell.define
class Hist(shell.Task["Hist.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.hist import Hist

    >>> task = Hist()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.mask = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dHist"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dHist", argstr="-input {in_file}", position=1
    )
    showhist: bool = shell.arg(
        help="write a text visual histogram", argstr="-showhist", default=False
    )
    mask: File = shell.arg(help="matrix to align input file", argstr="-mask {mask}")
    nbin: int = shell.arg(help="number of bins", argstr="-nbin {nbin}")
    max_value: float = shell.arg(
        help="maximum intensity value", argstr="-max {max_value}"
    )
    min_value: float = shell.arg(
        help="minimum intensity value", argstr="-min {min_value}"
    )
    bin_width: float = shell.arg(help="bin width", argstr="-binwidth {bin_width}")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="Write histogram to niml file with this prefix",
            argstr="-prefix {out_file}",
            path_template="{in_file}_hist",
        )
        out_show: Path = shell.outarg(
            help="output image file name",
            argstr="> {out_show}",
            position=-1,
            path_template="{in_file}_hist.out",
        )
