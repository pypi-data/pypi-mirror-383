from fileformats.generic import Directory
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class To3D(shell.Task["To3D.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import Directory
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.to_3d import To3D

    >>> task = To3D()
    >>> task.inputs.out_file = "dicomdir.nii"
    >>> task.inputs.in_folder = Directory.mock()
    >>> task.inputs.datatype = "float"
    >>> task.cmdline
    'None'


    """

    executable = "to3d"
    in_folder: Directory = shell.arg(
        help="folder with DICOM images to convert",
        argstr="{in_folder}/*.dcm",
        position=-1,
    )
    filetype: ty.Any = shell.arg(
        help="type of datafile being converted", argstr="-{filetype}"
    )
    skipoutliers: bool = shell.arg(
        help="skip the outliers check", argstr="-skip_outliers"
    )
    assumemosaic: bool = shell.arg(
        help="assume that Siemens image is mosaic", argstr="-assume_dicom_mosaic"
    )
    datatype: ty.Any = shell.arg(
        help="set output file datatype", argstr="-datum {datatype}"
    )
    funcparams: str = shell.arg(
        help="parameters for functional data", argstr="-time:zt {funcparams} alt+z2"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_folder}",
        )
