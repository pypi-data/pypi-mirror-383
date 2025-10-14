from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "neighborhood" and value[0] == "RECT":
        value = ("RECT", "%s,%s,%s" % value[1])
    if name == "stat":
        value = ["perc:%s:%s:%s" % v[1] if len(v) == 2 else v for v in value]
    if name == "reduce_grid" or name == "reduce_restore_grid":
        if len(value) == 3:
            value = "%s %s %s" % value

    return argstr.format(**inputs)


def neighborhood_formatter(field, inputs):
    return _format_arg(
        "neighborhood",
        field,
        inputs,
        argstr="-nbhd '{neighborhood[0]}({neighborhood[1]})'",
    )


def stat_formatter(field, inputs):
    return _format_arg("stat", field, inputs, argstr="-stat {stat}...")


def reduce_grid_formatter(field, inputs):
    return _format_arg(
        "reduce_grid", field, inputs, argstr="-reduce_grid {reduce_grid}"
    )


def reduce_restore_grid_formatter(field, inputs):
    return _format_arg(
        "reduce_restore_grid",
        field,
        inputs,
        argstr="-reduce_restore_grid {reduce_restore_grid}",
    )


@shell.define(xor=[["reduce_restore_grid", "reduce_grid", "reduce_max_vox"]])
class Localstat(shell.Task["Localstat.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.localstat import Localstat
    >>> from pydra.utils.typing import MultiInputObj

    >>> task = Localstat()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.neighborhood = ("SPHERE", 45)
    >>> task.inputs.mask_file = File.mock()
    >>> task.inputs.nonmask = True
    >>> task.cmdline
    'None'


    """

    executable = "3dLocalstat"
    in_file: Nifti1 = shell.arg(help="input dataset", argstr="{in_file}", position=-1)
    neighborhood: ty.Any = shell.arg(
        help="The region around each voxel that will be extracted for the statistics calculation. Possible regions are: 'SPHERE', 'RHDD' (rhombic dodecahedron), 'TOHD' (truncated octahedron) with a given radius in mm or 'RECT' (rectangular block) with dimensions to specify in mm.",
        formatter=neighborhood_formatter,
    )
    stat: MultiInputObj = shell.arg(
        help="statistics to compute. Possible names are:\n\n * mean   = average of the values\n * stdev  = standard deviation\n * var    = variance (stdev\\*stdev)\n * cvar   = coefficient of variation = stdev/fabs(mean)\n * median = median of the values\n * MAD    = median absolute deviation\n * min    = minimum\n * max    = maximum\n * absmax = maximum of the absolute values\n * num    = number of the values in the region:\n            with the use of -mask or -automask,\n            the size of the region around any given\n            voxel will vary; this option lets you\n            map that size.  It may be useful if you\n            plan to compute a t-statistic (say) from\n            the mean and stdev outputs.\n * sum    = sum of the values in the region\n * FWHM   = compute (like 3dFWHM) image smoothness\n            inside each voxel's neighborhood.  Results\n            are in 3 sub-bricks: FWHMx, FHWMy, and FWHMz.\n            Places where an output is -1 are locations\n            where the FWHM value could not be computed\n            (e.g., outside the mask).\n * FWHMbar= Compute just the average of the 3 FWHM values\n            (normally would NOT do this with FWHM also).\n * perc:P0:P1:Pstep =\n            Compute percentiles between P0 and P1 with a\n            step of Pstep.\n            Default P1 is equal to P0 and default P2 = 1\n * rank   = rank of the voxel's intensity\n * frank  = rank / number of voxels in neighborhood\n * P2skew = Pearson's second skewness coefficient\n             3 \\* (mean - median) / stdev\n * ALL    = all of the above, in that order\n            (except for FWHMbar and perc).\n * mMP2s  = Exactly the same output as:\n            median, MAD, P2skew,\n            but a little faster\n * mmMP2s = Exactly the same output as:\n            mean, median, MAD, P2skew\n\nMore than one option can be used.",
        formatter=stat_formatter,
    )
    mask_file: File = shell.arg(
        help="Mask image file name. Voxels NOT in the mask will not be used in the neighborhood of any voxel. Also, a voxel NOT in the mask will have its statistic(s) computed as zero (0) unless the parameter 'nonmask' is set to true.",
        argstr="-mask {mask_file}",
    )
    automask: bool = shell.arg(
        help="Compute the mask as in program 3dAutomask.", argstr="-automask"
    )
    nonmask: bool = shell.arg(
        help="Voxels not in the mask WILL have their local statistics\ncomputed from all voxels in their neighborhood that ARE in\nthe mask. For instance, this option can be used to compute the\naverage local white matter time series, even at non-WM\nvoxels.",
        argstr="-use_nonmask",
    )
    reduce_grid: ty.Any | None = shell.arg(
        help="Compute output on a grid that is reduced by the specified factors. If a single value is passed, output is resampled to the specified isotropic grid. Otherwise, the 3 inputs describe the reduction in the X, Y, and Z directions. This option speeds up computations at the expense of resolution. It should only be used when the nbhd is quite large with respect to the input's resolution, and the resultant stats are expected to be smooth.",
        formatter=reduce_grid_formatter,
    )
    reduce_restore_grid: ty.Any | None = shell.arg(
        help="Like reduce_grid, but also resample output back to input grid.",
        formatter=reduce_restore_grid_formatter,
    )
    reduce_max_vox: float | None = shell.arg(
        help="Like reduce_restore_grid, but automatically set Rx Ry Rz sothat the computation grid is at a resolution of nbhd/MAX_VOXvoxels.",
        argstr="-reduce_max_vox {reduce_max_vox}",
    )
    grid_rmode: ty.Any = shell.arg(
        help="Interpolant to use when resampling the output with thereduce_restore_grid option. The resampling method string RESAM should come from the set {'NN', 'Li', 'Cu', 'Bk'}. These stand for 'Nearest Neighbor', 'Linear', 'Cubic', and 'Blocky' interpolation, respectively.",
        argstr="-grid_rmode {grid_rmode}",
        requires=["reduce_restore_grid"],
    )
    quiet: bool = shell.arg(
        help="Stop the highly informative progress reports.", argstr="-quiet"
    )
    overwrite: bool = shell.arg(
        help="overwrite output file if it already exists", argstr="-overwrite"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="Output dataset.",
            argstr="-prefix {out_file}",
            path_template="{in_file}_localstat",
            position=1,
        )
