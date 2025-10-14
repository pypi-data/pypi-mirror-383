from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    _stat_dict = {
        "mean": "-nzmean",
        "median": "-nzmedian",
        "mode": "-nzmode",
        "minmax": "-nzminmax",
        "sigma": "-nzsigma",
        "voxels": "-nzvoxels",
        "sum": "-nzsum",
        "summary": "-summary",
        "zerominmax": "-minmax",
        "zeromedian": "-median",
        "zerosigma": "-sigma",
        "zeromode": "-mode",
    }
    if name == "stat":
        value = [_stat_dict[v] for v in value]

    return argstr.format(**inputs)


def stat_formatter(field, inputs):
    return _format_arg("stat", field, inputs, argstr="{stat}...")


@shell.define(xor=[["format1D", "format1DR"]])
class ROIStats(shell.Task["ROIStats.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.roi_stats import ROIStats
    >>> from pydra.utils.typing import MultiInputObj

    >>> task = ROIStats()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.mask = File.mock()
    >>> task.inputs.mask_file = File.mock()
    >>> task.inputs.roisel = File.mock()
    >>> task.inputs.stat = ["mean", "median", "voxels"]
    >>> task.cmdline
    'None'


    """

    executable = "3dROIstats"
    in_file: Nifti1 = shell.arg(help="input dataset", argstr="{in_file}", position=-2)
    mask: File = shell.arg(help="input mask", argstr="-mask {mask}", position=3)
    mask_file: File = shell.arg(help="input mask", argstr="-mask {mask_file}")
    mask_f2short: bool = shell.arg(
        help="Tells the program to convert a float mask to short integers, by simple rounding.",
        argstr="-mask_f2short",
    )
    num_roi: int = shell.arg(
        help="Forces the assumption that the mask dataset's ROIs are denoted by 1 to n inclusive.  Normally, the program figures out the ROIs on its own.  This option is useful if a) you are certain that the mask dataset has no values outside the range [0 n], b) there may be some ROIs missing between [1 n] in the mask data-set and c) you want those columns in the output any-way so the output lines up with the output from other invocations of 3dROIstats.",
        argstr="-numroi {num_roi}",
    )
    zerofill: str = shell.arg(
        help="For ROI labels not found, use the provided string instead of a '0' in the output file. Only active if `num_roi` is enabled.",
        argstr="-zerofill {zerofill}",
        requires=["num_roi"],
    )
    roisel: File = shell.arg(
        help="Only considers ROIs denoted by values found in the specified file. Note that the order of the ROIs as specified in the file is not preserved. So an SEL.1D of '2 8 20' produces the same output as '8 20 2'",
        argstr="-roisel {roisel}",
    )
    debug: bool = shell.arg(help="print debug information", argstr="-debug")
    quiet: bool = shell.arg(help="execute quietly", argstr="-quiet")
    nomeanout: bool = shell.arg(
        help="Do not include the (zero-inclusive) mean among computed stats",
        argstr="-nomeanout",
    )
    nobriklab: bool = shell.arg(
        help="Do not print the sub-brick label next to its index", argstr="-nobriklab"
    )
    format1D: bool = shell.arg(
        help="Output results in a 1D format that includes commented labels",
        argstr="-1Dformat",
    )
    format1DR: bool = shell.arg(
        help="Output results in a 1D format that includes uncommented labels. May not work optimally with typical 1D functions, but is useful for R functions.",
        argstr="-1DRformat",
    )
    stat: MultiInputObj = shell.arg(
        help="Statistics to compute. Options include:\n\n * mean       =   Compute the mean using only non_zero voxels.\n                  Implies the opposite for the mean computed\n                  by default.\n * median     =   Compute the median of nonzero voxels\n * mode       =   Compute the mode of nonzero voxels.\n                  (integral valued sets only)\n * minmax     =   Compute the min/max of nonzero voxels\n * sum        =   Compute the sum using only nonzero voxels.\n * voxels     =   Compute the number of nonzero voxels\n * sigma      =   Compute the standard deviation of nonzero\n                  voxels\n\nStatistics that include zero-valued voxels:\n\n * zerominmax =   Compute the min/max of all voxels.\n * zerosigma  =   Compute the standard deviation of all\n                  voxels.\n * zeromedian =   Compute the median of all voxels.\n * zeromode   =   Compute the mode of all voxels.\n * summary    =   Only output a summary line with the grand\n                  mean across all briks in the input dataset.\n                  This option cannot be used with nomeanout.\n\nMore that one option can be specified.",
        formatter=stat_formatter,
    )

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output file",
            argstr="> {out_file}",
            position=-1,
            path_template="{in_file}_roistat.1D",
        )
