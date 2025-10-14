from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


@shell.define(xor=[["mask", "automask"]])
class TProject(shell.Task["TProject.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.t_project import TProject

    >>> task = TProject()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.out_file = "projected.nii.gz"
    >>> task.inputs.censor = File.mock()
    >>> task.inputs.concat = File.mock()
    >>> task.inputs.ort = File.mock()
    >>> task.inputs.polort = 3
    >>> task.inputs.mask = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dTproject"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dTproject", argstr="-input {in_file}", position=1
    )
    censor: File = shell.arg(
        help="Filename of censor .1D time series.\nThis is a file of 1s and 0s, indicating which\ntime points are to be included (1) and which are\nto be excluded (0).",
        argstr="-censor {censor}",
    )
    censortr: list[str] = shell.arg(
        help="List of strings that specify time indexes\nto be removed from the analysis.  Each string is\nof one of the following forms:\n\n* ``37`` => remove global time index #37\n* ``2:37`` => remove time index #37 in run #2\n* ``37..47`` => remove global time indexes #37-47\n* ``37-47`` => same as above\n* ``2:37..47`` => remove time indexes #37-47 in run #2\n* ``*:0-2`` => remove time indexes #0-2 in all runs\n\n  * Time indexes within each run start at 0.\n  * Run indexes start at 1 (just be to confusing).\n  * N.B.: 2:37,47 means index #37 in run #2 and\n    global time index 47; it does NOT mean\n    index #37 in run #2 AND index #47 in run #2.\n\n",
        argstr="-CENSORTR {censortr}",
    )
    cenmode: ty.Any = shell.arg(
        help="Specifies how censored time points are treated in\nthe output dataset:\n\n* mode = ZERO -- put zero values in their place;\n  output dataset is same length as input\n* mode = KILL -- remove those time points;\n  output dataset is shorter than input\n* mode = NTRP -- censored values are replaced by interpolated\n  neighboring (in time) non-censored values,\n  BEFORE any projections, and then the\n  analysis proceeds without actual removal\n  of any time points -- this feature is to\n  keep the Spanish Inquisition happy.\n* The default mode is KILL !!!\n\n",
        argstr="-cenmode {cenmode}",
    )
    concat: File = shell.arg(
        help="The catenation file, as in 3dDeconvolve, containing the\nTR indexes of the start points for each contiguous run\nwithin the input dataset (the first entry should be 0).\n\n* Also as in 3dDeconvolve, if the input dataset is\n  automatically catenated from a collection of datasets,\n  then the run start indexes are determined directly,\n  and '-concat' is not needed (and will be ignored).\n* Each run must have at least 9 time points AFTER\n  censoring, or the program will not work!\n* The only use made of this input is in setting up\n  the bandpass/stopband regressors.\n* '-ort' and '-dsort' regressors run through all time\n  points, as read in.  If you want separate projections\n  in each run, then you must either break these ort files\n  into appropriate components, OR you must run 3dTproject\n  for each run separately, using the appropriate pieces\n  from the ort files via the ``{...}`` selector for the\n  1D files and the ``[...]`` selector for the datasets.\n\n",
        argstr="-concat {concat}",
    )
    noblock: bool = shell.arg(
        help="Also as in 3dDeconvolve, if you want the program to treat\nan auto-catenated dataset as one long run, use this option.\nHowever, '-noblock' will not affect catenation if you use\nthe '-concat' option.",
        argstr="-noblock",
    )
    ort: File = shell.arg(
        help="Remove each column in file.\nEach column will have its mean removed.",
        argstr="-ort {ort}",
    )
    polort: int = shell.arg(
        help="Remove polynomials up to and including degree pp.\n\n* Default value is 2.\n* It makes no sense to use a value of pp greater than\n  2, if you are bandpassing out the lower frequencies!\n* For catenated datasets, each run gets a separate set\n  set of pp+1 Legendre polynomial regressors.\n* Use of -polort -1 is not advised (if data mean != 0),\n  even if -ort contains constant terms, as all means are\n  removed.\n\n",
        argstr="-polort {polort}",
    )
    dsort: list[File] = shell.arg(
        help="Remove the 3D+time time series in dataset fset.\n\n* That is, 'fset' contains a different nuisance time\n  series for each voxel (e.g., from AnatICOR).\n* Multiple -dsort options are allowed.\n\n",
        argstr="-dsort {dsort}...",
    )
    bandpass: ty.Any = shell.arg(
        help="Remove all frequencies EXCEPT those in the range",
        argstr="-bandpass {bandpass[0]} {bandpass[1]}",
    )
    stopband: ty.Any = shell.arg(
        help="Remove all frequencies in the range",
        argstr="-stopband {stopband[0]} {stopband[1]}",
    )
    TR: float = shell.arg(
        help="Use time step dd for the frequency calculations,\nrather than the value stored in the dataset header.",
        argstr="-TR {TR}",
    )
    mask: File | None = shell.arg(
        help="Only operate on voxels nonzero in the mset dataset.\n\n* Voxels outside the mask will be filled with zeros.\n* If no masking option is given, then all voxels\n  will be processed.\n\n",
        argstr="-mask {mask}",
    )
    automask: bool = shell.arg(help="Generate a mask automatically", argstr="-automask")
    blur: float = shell.arg(
        help="Blur (inside the mask only) with a filter that has\nwidth (FWHM) of fff millimeters.\nSpatial blurring (if done) is after the time\nseries filtering.",
        argstr="-blur {blur}",
    )
    norm: bool = shell.arg(
        help="\nNormalize each output time series to have sum of\nsquares = 1. This is the LAST operation.",
        argstr="-norm",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            position=-1,
            path_template="{in_file}_tproject",
        )
