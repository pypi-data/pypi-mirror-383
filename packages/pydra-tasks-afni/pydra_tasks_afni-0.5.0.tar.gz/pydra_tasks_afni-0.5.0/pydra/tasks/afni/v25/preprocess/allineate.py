import attrs
from fileformats.datascience import TextMatrix
from fileformats.generic import File
from fileformats.medimage import Nifti1
from fileformats.text import TextFile
import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import (
    fname_presuffix,
    split_filename,
)
import os
import os.path as op
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    self_dict = {}

    outputs = {}
    metadata = dict(name_source=lambda t: t is not None)
    out_names = list(self_dict["inputs"].traits(**metadata).keys())
    if out_names:
        for name in out_names:
            if outputs[name]:
                _, _, ext = split_filename(outputs[name])
                if ext == "":
                    outputs[name] = outputs[name] + "+orig.BRIK"

    if inputs["out_weight_file"]:
        outputs["out_weight_file"] = op.abspath(inputs["out_weight_file"])

    if inputs["out_matrix"]:
        ext = split_filename(inputs["out_matrix"])[-1]
        if ext.lower() not in [".1d", ".1D"]:
            outputs["out_matrix"] = _gen_fname(
                inputs["out_matrix"],
                suffix=".aff12.1D",
                outputtype=inputs["outputtype"],
                inputs=inputs["inputs"],
                stdout=inputs["stdout"],
                stderr=inputs["stderr"],
                output_dir=inputs["output_dir"],
            )
        else:
            outputs["out_matrix"] = op.abspath(inputs["out_matrix"])

    if inputs["out_param_file"]:
        ext = split_filename(inputs["out_param_file"])[-1]
        if ext.lower() not in [".1d", ".1D"]:
            outputs["out_param_file"] = _gen_fname(
                inputs["out_param_file"],
                suffix=".param.1D",
                outputtype=inputs["outputtype"],
                inputs=inputs["inputs"],
                stdout=inputs["stdout"],
                stderr=inputs["stderr"],
                output_dir=inputs["output_dir"],
            )
        else:
            outputs["out_param_file"] = op.abspath(inputs["out_param_file"])

    if inputs["allcostx"]:
        outputs["allcostX"] = os.path.abspath(inputs["allcostx"])
    return outputs


def out_matrix_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_matrix")


def out_param_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_param_file")


def out_weight_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_weight_file")


def allcostx_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("allcostx")


@shell.define(
    xor=[
        ["allcostx", "out_file"],
        ["allcostx", "out_matrix", "in_matrix"],
        ["allcostx", "in_param_file", "out_param_file"],
        ["allcostx", "out_weight_file"],
        ["in_param_file", "out_param_file"],
        ["out_file", "out_matrix", "out_param_file", "allcostx", "out_weight_file"],
        ["out_matrix", "in_matrix"],
    ]
)
class Allineate(shell.Task["Allineate.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.datascience import TextMatrix
    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from fileformats.text import TextFile
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.allineate import Allineate

    >>> task = Allineate()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.reference = File.mock()
    >>> task.inputs.in_param_file = File.mock()
    >>> task.inputs.in_matrix = TextMatrix.mock("cmatrix.mat")
    >>> task.inputs.weight_file = File.mock()
    >>> task.inputs.source_mask = File.mock()
    >>> task.inputs.master = File.mock()
    >>> task.cmdline
    'None'


    >>> task = Allineate()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.reference = File.mock()
    >>> task.inputs.in_param_file = File.mock()
    >>> task.inputs.in_matrix = TextMatrix.mock()
    >>> task.inputs.allcostx = "out.allcostX.txt"
    >>> task.inputs.weight_file = File.mock()
    >>> task.inputs.source_mask = File.mock()
    >>> task.inputs.master = File.mock()
    >>> task.cmdline
    '3dAllineate -source functional.nii -base structural.nii -allcostx |& tee out.allcostX.txt'


    >>> task = Allineate()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.reference = File.mock()
    >>> task.inputs.in_param_file = File.mock()
    >>> task.inputs.in_matrix = TextMatrix.mock()
    >>> task.inputs.weight_file = File.mock()
    >>> task.inputs.source_mask = File.mock()
    >>> task.inputs.master = File.mock()
    >>> task.inputs.nwarp_fixmot = ["X", "Y"]
    >>> task.cmdline
    '3dAllineate -source functional.nii -nwarp_fixmotX -nwarp_fixmotY -prefix functional_allineate -base structural.nii'


    """

    executable = "3dAllineate"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dAllineate", argstr="-source {in_file}"
    )
    reference: File = shell.arg(
        help="file to be used as reference, the first volume will be used if not given the reference will be the first volume of in_file.",
        argstr="-base {reference}",
    )
    out_param_file: Path | None = shell.arg(
        help="Save the warp parameters in ASCII (.1D) format.",
        argstr="-1Dparam_save {out_param_file}",
    )
    in_param_file: File | None = shell.arg(
        help="Read warp parameters from file and apply them to the source dataset, and produce a new dataset",
        argstr="-1Dparam_apply {in_param_file}",
    )
    out_matrix: Path | None = shell.arg(
        help="Save the transformation matrix for each volume.",
        argstr="-1Dmatrix_save {out_matrix}",
    )
    in_matrix: TextMatrix | None = shell.arg(
        help="matrix to align input file",
        argstr="-1Dmatrix_apply {in_matrix}",
        position=-3,
    )
    overwrite: bool = shell.arg(
        help="overwrite output file if it already exists", argstr="-overwrite"
    )
    allcostx: Path | None = shell.arg(
        help="Compute and print ALL available cost functionals for the un-warped inputsAND THEN QUIT. If you use this option none of the other expected outputs will be produced",
        argstr="-allcostx |& tee {allcostx}",
        position=-1,
    )
    cost: ty.Any = shell.arg(
        help="Defines the 'cost' function that defines the matching between the source and the base",
        argstr="-cost {cost}",
    )
    interpolation: ty.Any = shell.arg(
        help="Defines interpolation method to use during matching",
        argstr="-interp {interpolation}",
    )
    final_interpolation: ty.Any = shell.arg(
        help="Defines interpolation method used to create the output dataset",
        argstr="-final {final_interpolation}",
    )
    nmatch: int = shell.arg(
        help="Use at most n scattered points to match the datasets.",
        argstr="-nmatch {nmatch}",
    )
    no_pad: bool = shell.arg(
        help="Do not use zero-padding on the base image.", argstr="-nopad"
    )
    zclip: bool = shell.arg(
        help="Replace negative values in the input datasets (source & base) with zero.",
        argstr="-zclip",
    )
    convergence: float = shell.arg(
        help="Convergence test in millimeters (default 0.05mm).",
        argstr="-conv {convergence}",
    )
    usetemp: bool = shell.arg(help="temporary file use", argstr="-usetemp")
    check: list[ty.Any] = shell.arg(
        help="After cost functional optimization is done, start at the final parameters and RE-optimize using this new cost functions. If the results are too different, a warning message will be printed. However, the final parameters from the original optimization will be used to create the output dataset.",
        argstr="-check {check}",
    )
    one_pass: bool = shell.arg(
        help="Use only the refining pass -- do not try a coarse resolution pass first.  Useful if you know that only small amounts of image alignment are needed.",
        argstr="-onepass",
    )
    two_pass: bool = shell.arg(
        help="Use a two pass alignment strategy for all volumes, searching for a large rotation+shift and then refining the alignment.",
        argstr="-twopass",
    )
    two_blur: float = shell.arg(
        help="Set the blurring radius for the first pass in mm.",
        argstr="-twoblur {two_blur}",
    )
    two_first: bool = shell.arg(
        help="Use -twopass on the first image to be registered, and then on all subsequent images from the source dataset, use results from the first image's coarse pass to start the fine pass.",
        argstr="-twofirst",
    )
    two_best: int = shell.arg(
        help="In the coarse pass, use the best 'bb' set of initialpoints to search for the starting point for the finepass.  If bb==0, then no search is made for the beststarting point, and the identity transformation isused as the starting point.  [Default=5; min=0 max=11]",
        argstr="-twobest {two_best}",
    )
    fine_blur: float = shell.arg(
        help="Set the blurring radius to use in the fine resolution pass to 'x' mm.  A small amount (1-2 mm?) of blurring at the fine step may help with convergence, if there is some problem, especially if the base volume is very noisy. [Default == 0 mm = no blurring at the final alignment pass]",
        argstr="-fineblur {fine_blur}",
    )
    center_of_mass: str = shell.arg(
        help="Use the center-of-mass calculation to bracket the shifts.",
        argstr="-cmass{center_of_mass}",
    )
    autoweight: str = shell.arg(
        help="Compute a weight function using the 3dAutomask algorithm plus some blurring of the base image.",
        argstr="-autoweight{autoweight}",
    )
    automask: int = shell.arg(
        help="Compute a mask function, set a value for dilation or 0.",
        argstr="-automask+{automask}",
    )
    autobox: bool = shell.arg(
        help="Expand the -automask function to enclose a rectangular box that holds the irregular mask.",
        argstr="-autobox",
    )
    nomask: bool = shell.arg(
        help="Don't compute the autoweight/mask; if -weight is not also used, then every voxel will be counted equally.",
        argstr="-nomask",
    )
    weight_file: File = shell.arg(
        help="Set the weighting for each voxel in the base dataset; larger weights mean that voxel count more in the cost function. Must be defined on the same grid as the base dataset",
        argstr="-weight {weight_file}",
    )
    weight: ty.Any = shell.arg(
        help="Set the weighting for each voxel in the base dataset; larger weights mean that voxel count more in the cost function. If an image file is given, the volume must be defined on the same grid as the base dataset",
        argstr="-weight {weight}",
    )
    out_weight_file: Path | None = shell.arg(
        help="Write the weight volume to disk as a dataset",
        argstr="-wtprefix {out_weight_file}",
    )
    source_mask: File = shell.arg(
        help="mask the input dataset", argstr="-source_mask {source_mask}"
    )
    source_automask: int = shell.arg(
        help="Automatically mask the source dataset with dilation or 0.",
        argstr="-source_automask+{source_automask}",
    )
    warp_type: ty.Any = shell.arg(help="Set the warp type.", argstr="-warp {warp_type}")
    warpfreeze: bool = shell.arg(
        help="Freeze the non-rigid body parameters after first volume.",
        argstr="-warpfreeze",
    )
    replacebase: bool = shell.arg(
        help="If the source has more than one volume, then after the first volume is aligned to the base.",
        argstr="-replacebase",
    )
    replacemeth: ty.Any = shell.arg(
        help="After first volume is aligned, switch method for later volumes. For use with '-replacebase'.",
        argstr="-replacemeth {replacemeth}",
    )
    epi: bool = shell.arg(
        help="Treat the source dataset as being composed of warped EPI slices, and the base as comprising anatomically 'true' images.  Only phase-encoding direction image shearing and scaling will be allowed with this option.",
        argstr="-EPI",
    )
    maxrot: float = shell.arg(
        help="Maximum allowed rotation in degrees.", argstr="-maxrot {maxrot}"
    )
    maxshf: float = shell.arg(
        help="Maximum allowed shift in mm.", argstr="-maxshf {maxshf}"
    )
    maxscl: float = shell.arg(
        help="Maximum allowed scaling factor.", argstr="-maxscl {maxscl}"
    )
    maxshr: float = shell.arg(
        help="Maximum allowed shearing factor.", argstr="-maxshr {maxshr}"
    )
    master: File = shell.arg(
        help="Write the output dataset on the same grid as this file.",
        argstr="-master {master}",
    )
    newgrid: float = shell.arg(
        help="Write the output dataset using isotropic grid spacing in mm.",
        argstr="-newgrid {newgrid}",
    )
    nwarp: ty.Any = shell.arg(
        help="Experimental nonlinear warping: bilinear or legendre poly.",
        argstr="-nwarp {nwarp}",
    )
    nwarp_fixmot: list[ty.Any] = shell.arg(
        help="To fix motion along directions.", argstr="-nwarp_fixmot{nwarp_fixmot}..."
    )
    nwarp_fixdep: list[ty.Any] = shell.arg(
        help="To fix non-linear warp dependency along directions.",
        argstr="-nwarp_fixdep{nwarp_fixdep}...",
    )
    verbose: bool = shell.arg(
        help="Print out verbose progress reports.", argstr="-verb"
    )
    quiet: bool = shell.arg(
        help="Don't print out verbose progress reports.", argstr="-quiet"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path | None = shell.outarg(
            help="output file from 3dAllineate",
            argstr="-prefix {out_file}",
            path_template="{in_file}_allineate",
        )
        out_matrix: File | None = shell.out(
            help="matrix to align input file", callable=out_matrix_callable
        )
        out_param_file: File | None = shell.out(
            help="warp parameters", callable=out_param_file_callable
        )
        out_weight_file: File | None = shell.out(
            help="weight volume", callable=out_weight_file_callable
        )
        allcostx: TextFile | None = shell.out(
            help="Compute and print ALL available cost functionals for the un-warped inputs",
            callable=allcostx_callable,
        )


def _gen_fname(
    basename,
    cwd=None,
    suffix=None,
    change_ext=True,
    ext=None,
    outputtype=None,
    inputs=None,
    stdout=None,
    stderr=None,
    output_dir=None,
):
    """
    Generate a filename based on the given parameters.

    The filename will take the form: cwd/basename<suffix><ext>.
    If change_ext is True, it will use the extensions specified in
    <instance>inputs.output_type.

    Parameters
    ----------
    basename : str
        Filename to base the new filename on.
    cwd : str
        Path to prefix to the new filename. (default is output_dir)
    suffix : str
        Suffix to add to the `basename`.  (defaults is '' )
    change_ext : bool
        Flag to change the filename extension to the FSL output type.
        (default True)

    Returns
    -------
    fname : str
        New filename based on given parameters.

    """
    if not basename:
        msg = "Unable to generate filename for command %s. " % "3dAllineate"
        msg += "basename is not set!"
        raise ValueError(msg)

    if cwd is None:
        cwd = output_dir
    if ext is None:
        ext = Info.output_type_to_ext(outputtype)
    if change_ext:
        suffix = f"{suffix}{ext}" if suffix else ext

    if suffix is None:
        suffix = ""
    fname = fname_presuffix(basename, suffix=suffix, use_ext=False, newpath=cwd)
    return fname
