from fileformats.vendor.afni.medimage import ThreeD
import logging
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _gen_filename(name, inputs):
    return os.path.abspath()


@shell.define(xor=[["oldid", "newid"]])
class AFNItoNIFTI(shell.Task["AFNItoNIFTI.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.vendor.afni.medimage import ThreeD
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.afn_ito_nifti import AFNItoNIFTI

    >>> task = AFNItoNIFTI()
    >>> task.inputs.in_file = ThreeD.mock("afni_output.3D")
    >>> task.cmdline
    'None'


    """

    executable = "3dAFNItoNIFTI"
    in_file: ThreeD = shell.arg(
        help="input file to 3dAFNItoNIFTI", argstr="{in_file}", position=-1
    )
    pure: bool = shell.arg(
        help="Do NOT write an AFNI extension field into the output file. Only use this option if needed. You can also use the 'nifti_tool' program to strip extensions from a file.",
        argstr="-pure",
    )
    denote: bool = shell.arg(
        help="When writing the AFNI extension field, remove text notes that might contain subject identifying information.",
        argstr="-denote",
    )
    oldid: bool = shell.arg(
        help="Give the new dataset the input datasets AFNI ID code.", argstr="-oldid"
    )
    newid: bool = shell.arg(
        help="Give the new dataset a new AFNI ID code, to distinguish it from the input dataset.",
        argstr="-newid",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}.nii",
        )
