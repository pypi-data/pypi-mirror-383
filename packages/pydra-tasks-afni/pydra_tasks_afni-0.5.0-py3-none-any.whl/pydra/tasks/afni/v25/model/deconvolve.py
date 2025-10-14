import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
from fileformats.vendor.afni.medimage import OneD
import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import fname_presuffix
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    parsed_inputs = _parse_inputs(inputs) if inputs else {}
    if value is None:
        return ""

    if name == "gltsym":
        for n, val in enumerate(value):
            if val.startswith("SYM: "):
                value[n] = val.lstrip("SYM: ")

    return argstr.format(**inputs)


def gltsym_formatter(field, inputs):
    return _format_arg("gltsym", field, inputs, argstr="-gltsym 'SYM: {gltsym}'...")


def _parse_inputs(inputs, output_dir=None):
    if not output_dir:
        output_dir = os.getcwd()
    parsed_inputs = {}
    skip = []

    if skip is None:
        skip = []
    if len(inputs["stim_times"]) and (inputs["num_stimts"] is attrs.NOTHING):
        inputs["num_stimts"] = len(inputs["stim_times"])
    if len(inputs["gltsym"]) and (inputs["num_glt"] is attrs.NOTHING):
        inputs["num_glt"] = len(inputs["gltsym"])
    if inputs["out_file"] is attrs.NOTHING:
        inputs["out_file"] = "Decon.nii"

    return parsed_inputs


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    parsed_inputs = _parse_inputs(inputs, output_dir=output_dir)

    outputs = {}

    _gen_fname_opts = {}
    _gen_fname_opts["basename"] = inputs["out_file"]
    _gen_fname_opts["cwd"] = os.getcwd()

    if inputs["x1D"] is not attrs.NOTHING:
        if not inputs["x1D"].endswith(".xmat.1D"):
            outputs["x1D"] = os.path.abspath(inputs["x1D"] + ".xmat.1D")
        else:
            outputs["x1D"] = os.path.abspath(inputs["x1D"])
    else:
        outputs["x1D"] = _gen_fname(
            suffix=".xmat.1D",
            outputtype=inputs["outputtype"],
            inputs=inputs["inputs"],
            stdout=inputs["stdout"],
            stderr=inputs["stderr"],
            output_dir=inputs["output_dir"],
            **_gen_fname_opts,
        )

    if inputs["cbucket"] is not attrs.NOTHING:
        outputs["cbucket"] = os.path.abspath(inputs["cbucket"])

    outputs["reml_script"] = _gen_fname(
        suffix=".REML_cmd",
        outputtype=inputs["outputtype"],
        inputs=inputs["inputs"],
        stdout=inputs["stdout"],
        stderr=inputs["stderr"],
        output_dir=inputs["output_dir"],
        **_gen_fname_opts,
    )

    if inputs["x1D_stop"]:
        del outputs["out_file"], outputs["cbucket"]
    else:
        outputs["out_file"] = os.path.abspath(inputs["out_file"])

    return outputs


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


def reml_script_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("reml_script")


def x1D_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("x1D")


def cbucket_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("cbucket")


@shell.define(xor=[["trans", "sat"], ["local_times", "global_times"]])
class Deconvolve(shell.Task["Deconvolve.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from fileformats.vendor.afni.medimage import OneD
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.model.deconvolve import Deconvolve

    >>> task = Deconvolve()
    >>> task.inputs.in_files = [Nifti1.mock("functional.nii"), Nifti1.mock("functional2.nii")]
    >>> task.inputs.input1D = File.mock()
    >>> task.inputs.mask = File.mock()
    >>> task.inputs.STATmask = File.mock()
    >>> task.inputs.censor = File.mock()
    >>> task.inputs.x1D = "output.1D"
    >>> task.inputs.stim_times = stim_times
    >>> task.inputs.gltsym = ["SYM: +Houses"]
    >>> task.cmdline
    '3dDeconvolve -input functional.nii functional2.nii -bucket output.nii -x1D output.1D -num_stimts 1 -stim_times 1 timeseries.txt "SPMG1(4)" -stim_label 1 Houses -num_glt 1 -gltsym "SYM: +Houses" -glt_label 1 Houses'


    """

    executable = "3dDeconvolve"
    in_files: list[Nifti1] = shell.arg(
        help="filenames of 3D+time input datasets. More than one filename can be given and the datasets will be auto-catenated in time. You can input a 1D time series file here, but the time axis should run along the ROW direction, not the COLUMN direction as in the 'input1D' option.",
        argstr="-input {in_files}",
        sep=" ",
        position=2,
    )
    sat: bool = shell.arg(
        help="check the dataset time series for initial saturation transients, which should normally have been excised before data analysis.",
        argstr="-sat",
    )
    trans: bool = shell.arg(
        help="check the dataset time series for initial saturation transients, which should normally have been excised before data analysis.",
        argstr="-trans",
    )
    noblock: bool = shell.arg(
        help="normally, if you input multiple datasets with 'input', then the separate datasets are taken to be separate image runs that get separate baseline models. Use this options if you want to have the program consider these to be all one big run.* If any of the input dataset has only 1 sub-brick, then this option is automatically invoked!* If the auto-catenation feature isn't used, then this option has no effect, no how, no way.",
        argstr="-noblock",
    )
    force_TR: float = shell.arg(
        help="use this value instead of the TR in the 'input' dataset. (It's better to fix the input using Refit.)",
        argstr="-force_TR {force_TR}",
        position=1,
    )
    input1D: File = shell.arg(
        help="filename of single (fMRI) .1D time series where time runs down the column.",
        argstr="-input1D {input1D}",
    )
    TR_1D: float = shell.arg(
        help="TR to use with 'input1D'. This option has no effect if you do not also use 'input1D'.",
        argstr="-TR_1D {TR_1D}",
    )
    legendre: bool = shell.arg(
        help="use Legendre polynomials for null hypothesis (baseline model)",
        argstr="-legendre",
    )
    nolegendre: bool = shell.arg(
        help="use power polynomials for null hypotheses. Don't do this unless you are crazy!",
        argstr="-nolegendre",
    )
    nodmbase: bool = shell.arg(
        help="don't de-mean baseline time series", argstr="-nodmbase"
    )
    dmbase: bool = shell.arg(
        help="de-mean baseline time series (default if 'polort' >= 0)", argstr="-dmbase"
    )
    svd: bool = shell.arg(
        help="use SVD instead of Gaussian elimination (default)", argstr="-svd"
    )
    nosvd: bool = shell.arg(
        help="use Gaussian elimination instead of SVD", argstr="-nosvd"
    )
    rmsmin: float = shell.arg(
        help="minimum rms error to reject reduced model (default = 0; don't use this option normally!)",
        argstr="-rmsmin {rmsmin}",
    )
    nocond: bool = shell.arg(
        help="DON'T calculate matrix condition number", argstr="-nocond"
    )
    singvals: bool = shell.arg(
        help="print out the matrix singular values", argstr="-singvals"
    )
    goforit: int = shell.arg(
        help="use this to proceed even if the matrix has bad problems (e.g., duplicate columns, large condition number, etc.).",
        argstr="-GOFORIT {goforit}",
    )
    allzero_OK: bool = shell.arg(
        help="don't consider all zero matrix columns to be the type of error that 'gotforit' is needed to ignore.",
        argstr="-allzero_OK",
    )
    dname: ty.Any = shell.arg(
        help="set environmental variable to provided value",
        argstr="-D{dname[0]}={dname[1]}",
    )
    mask: File = shell.arg(
        help="filename of 3D mask dataset; only data time series from within the mask will be analyzed; results for voxels outside the mask will be set to zero.",
        argstr="-mask {mask}",
    )
    automask: bool = shell.arg(
        help="build a mask automatically from input data (will be slow for long time series datasets)",
        argstr="-automask",
    )
    STATmask: File = shell.arg(
        help="build a mask from provided file, and use this mask for the purpose of reporting truncation-to float issues AND for computing the FDR curves. The actual results ARE not masked with this option (only with 'mask' or 'automask' options).",
        argstr="-STATmask {STATmask}",
    )
    censor: File = shell.arg(
        help="filename of censor .1D time series. This is a file of 1s and 0s, indicating which time points are to be included (1) and which are to be excluded (0).",
        argstr="-censor {censor}",
    )
    polort: int = shell.arg(
        help="degree of polynomial corresponding to the null hypothesis [default: 1]",
        argstr="-polort {polort}",
    )
    ortvec: ty.Any = shell.arg(
        help="this option lets you input a rectangular array of 1 or more baseline vectors from a file. This method is a fast way to include a lot of baseline regressors in one step. ",
        argstr="-ortvec {ortvec[0]} {ortvec[1]}",
    )
    x1D: Path = shell.arg(help="specify name for saved X matrix", argstr="-x1D {x1D}")
    x1D_stop: bool = shell.arg(
        help="stop running after writing .xmat.1D file", argstr="-x1D_stop"
    )
    cbucket: str = shell.arg(
        help="Name for dataset in which to save the regression coefficients (no statistics). This dataset will be used in a -xrestore run [not yet implemented] instead of the bucket dataset, if possible.",
        argstr="-cbucket {cbucket}",
    )
    out_file: Path = shell.arg(
        help="output statistics file", argstr="-bucket {out_file}"
    )
    num_threads: int = shell.arg(
        help="run the program with provided number of sub-processes",
        argstr="-jobs {num_threads}",
    )
    fout: bool = shell.arg(help="output F-statistic for each stimulus", argstr="-fout")
    rout: bool = shell.arg(
        help="output the R^2 statistic for each stimulus", argstr="-rout"
    )
    tout: bool = shell.arg(
        help="output the T-statistic for each stimulus", argstr="-tout"
    )
    vout: bool = shell.arg(
        help="output the sample variance (MSE) for each stimulus", argstr="-vout"
    )
    nofdr: bool = shell.arg(
        help="Don't compute the statistic-vs-FDR curves for the bucket dataset.",
        argstr="-noFDR",
    )
    global_times: bool = shell.arg(
        help="use global timing for stimulus timing files", argstr="-global_times"
    )
    local_times: bool = shell.arg(
        help="use local timing for stimulus timing files", argstr="-local_times"
    )
    num_stimts: int = shell.arg(
        help="number of stimulus timing files",
        argstr="-num_stimts {num_stimts}",
        position=-6,
    )
    stim_times: list[ty.Any] = shell.arg(
        help="generate a response model from a set of stimulus times given in file.",
        argstr="-stim_times {stim_times[0]} {stim_times[1]} '{stim_times[2]}'...",
        position=-5,
    )
    stim_label: list[ty.Any] = shell.arg(
        help="label for kth input stimulus (e.g., Label1)",
        argstr="-stim_label {stim_label[0]} {stim_label[1]}...",
        position=-4,
        requires=["stim_times"],
    )
    stim_times_subtract: float = shell.arg(
        help="this option means to subtract specified seconds from each time encountered in any 'stim_times' option. The purpose of this option is to make it simple to adjust timing files for the removal of images from the start of each imaging run.",
        argstr="-stim_times_subtract {stim_times_subtract}",
    )
    num_glt: int = shell.arg(
        help="number of general linear tests (i.e., contrasts)",
        argstr="-num_glt {num_glt}",
        position=-3,
    )
    gltsym: list[str] = shell.arg(
        help="general linear tests (i.e., contrasts) using symbolic conventions (e.g., '+Label1 -Label2')",
        position=-2,
        formatter=gltsym_formatter,
    )
    glt_label: list[ty.Any] = shell.arg(
        help="general linear test (i.e., contrast) labels",
        argstr="-glt_label {glt_label[0]} {glt_label[1]}...",
        position=-1,
        requires=["gltsym"],
    )
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: File | None = shell.out(
            help="output statistics file", callable=out_file_callable
        )
        reml_script: File | None = shell.out(
            help="automatically generated script to run 3dREMLfit",
            callable=reml_script_callable,
        )
        x1D: OneD | None = shell.out(help="save out X matrix", callable=x1D_callable)
        cbucket: File | None = shell.out(
            help="output regression coefficients file (if generated)",
            callable=cbucket_callable,
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
        msg = "Unable to generate filename for command %s. " % "3dDeconvolve"
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
