from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define
class Bandpass(shell.Task["Bandpass.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.bandpass import Bandpass

    >>> task = Bandpass()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.lowpass = 0.1
    >>> task.inputs.mask = File.mock()
    >>> task.inputs.orthogonalize_dset = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dBandpass"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dBandpass", argstr="{in_file}", position=-1
    )
    lowpass: float = shell.arg(help="lowpass", argstr="{lowpass}", position=-2)
    highpass: float = shell.arg(help="highpass", argstr="{highpass}", position=-3)
    mask: File = shell.arg(help="mask file", argstr="-mask {mask}", position=2)
    despike: bool = shell.arg(
        help="Despike each time series before other processing. Hopefully, you don't actually need to do this, which is why it is optional.",
        argstr="-despike",
    )
    orthogonalize_file: list[File] = shell.arg(
        help="Also orthogonalize input to columns in f.1D. Multiple '-ort' options are allowed.",
        argstr="-ort {orthogonalize_file}",
    )
    orthogonalize_dset: File = shell.arg(
        help="Orthogonalize each voxel to the corresponding voxel time series in dataset 'fset', which must have the same spatial and temporal grid structure as the main input dataset. At present, only one '-dsort' option is allowed.",
        argstr="-dsort {orthogonalize_dset}",
    )
    no_detrend: bool = shell.arg(
        help="Skip the quadratic detrending of the input that occurs before the FFT-based bandpassing. You would only want to do this if the dataset had been detrended already in some other program.",
        argstr="-nodetrend",
    )
    tr: float = shell.arg(
        help="Set time step (TR) in sec [default=from dataset header].",
        argstr="-dt {tr}",
    )
    nfft: int = shell.arg(
        help="Set the FFT length [must be a legal value].", argstr="-nfft {nfft}"
    )
    normalize: bool = shell.arg(
        help="Make all output time series have L2 norm = 1 (i.e., sum of squares = 1).",
        argstr="-norm",
    )
    automask: bool = shell.arg(
        help="Create a mask from the input dataset.", argstr="-automask"
    )
    blur: float = shell.arg(
        help="Blur (inside the mask only) with a filter width (FWHM) of 'fff' millimeters.",
        argstr="-blur {blur}",
    )
    localPV: float = shell.arg(
        help="Replace each vector by the local Principal Vector (AKA first singular vector) from a neighborhood of radius 'rrr' millimeters. Note that the PV time series is L2 normalized. This option is mostly for Bob Cox to have fun with.",
        argstr="-localPV {localPV}",
    )
    notrans: bool = shell.arg(
        help="Don't check for initial positive transients in the data. The test is a little slow, so skipping it is OK, if you KNOW the data time series are transient-free.",
        argstr="-notrans",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output file from 3dBandpass",
            argstr="-prefix {out_file}",
            position=1,
            path_template="{in_file}_bp",
        )
