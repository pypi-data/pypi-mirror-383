import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
import os
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def aggregate_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    needed_outputs = ["out_file"]

    import glob

    outputs = {}

    if inputs["prefix"] is not attrs.NOTHING:
        outfile = os.path.join(os.getcwd(), inputs["prefix"], "Classes+*.BRIK")
    else:
        outfile = os.path.join(os.getcwd(), "Segsy", "Classes+*.BRIK")

    outputs["out_file"] = glob.glob(outfile)[0]

    return outputs


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = aggregate_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


@shell.define
class Seg(shell.Task["Seg.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pydra.tasks.afni.v25.preprocess.seg import Seg

    >>> task = Seg()
    >>> task.inputs.in_file = Nifti1.mock("structural.nii")
    >>> task.cmdline
    'None'


    """

    executable = "3dSeg"
    in_file: Nifti1 = shell.arg(
        help="ANAT is the volume to segment",
        argstr="-anat {in_file}",
        position=-1,
        copy_mode="File.CopyMode.copy",
    )
    mask: ty.Any = shell.arg(
        help='only non-zero voxels in mask are analyzed. mask can either be a dataset or the string "AUTO" which would use AFNI\'s automask function to create the mask.',
        argstr="-mask {mask}",
        position=-2,
    )
    blur_meth: ty.Any = shell.arg(
        help="set the blurring method for bias field estimation",
        argstr="-blur_meth {blur_meth}",
    )
    bias_fwhm: float = shell.arg(
        help="The amount of blurring used when estimating the field bias with the Wells method",
        argstr="-bias_fwhm {bias_fwhm}",
    )
    classes: str = shell.arg(
        help="CLASS_STRING is a semicolon delimited string of class labels",
        argstr="-classes {classes}",
    )
    bmrf: float = shell.arg(
        help="Weighting factor controlling spatial homogeneity of the classifications",
        argstr="-bmrf {bmrf}",
    )
    bias_classes: str = shell.arg(
        help="A semicolon delimited string of classes that contribute to the estimation of the bias field",
        argstr="-bias_classes {bias_classes}",
    )
    prefix: str = shell.arg(
        help="the prefix for the output folder containing all output volumes",
        argstr="-prefix {prefix}",
    )
    mixfrac: str = shell.arg(
        help="MIXFRAC sets up the volume-wide (within mask) tissue fractions while initializing the segmentation (see IGNORE for exception)",
        argstr="-mixfrac {mixfrac}",
    )
    mixfloor: float = shell.arg(
        help="Set the minimum value for any class's mixing fraction",
        argstr="-mixfloor {mixfloor}",
    )
    main_N: int = shell.arg(
        help="Number of iterations to perform.", argstr="-main_N {main_N}"
    )

    class Outputs(shell.Outputs):
        out_file: File | None = shell.out(
            help="output file", callable=out_file_callable
        )
