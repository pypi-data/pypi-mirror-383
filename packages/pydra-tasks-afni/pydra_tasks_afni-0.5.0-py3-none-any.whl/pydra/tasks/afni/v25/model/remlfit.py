import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
from fileformats.vendor.afni.medimage import OneD
import logging
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _parse_inputs(inputs, output_dir=None):
    if not output_dir:
        output_dir = os.getcwd()
    parsed_inputs = {}
    skip = []

    if skip is None:
        skip = []

    return parsed_inputs


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    parsed_inputs = _parse_inputs(inputs, output_dir=output_dir)
    self_dict = {}

    outputs = {}

    for key in outputs:
        if self_dict["inputs"].get()[key] is not attrs.NOTHING:
            outputs[key] = os.path.abspath(self_dict["inputs"].get()[key])

    return outputs


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


def var_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("var_file")


def rbeta_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("rbeta_file")


def glt_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("glt_file")


def fitts_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("fitts_file")


def errts_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("errts_file")


def wherr_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("wherr_file")


def ovar_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("ovar")


def obeta_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("obeta")


def obuck_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("obuck")


def oglt_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("oglt")


def ofitts_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("ofitts")


def oerrts_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("oerrts")


@shell.define(xor=[["matrix", "matim"], ["matrix", "polort"]])
class Remlfit(shell.Task["Remlfit.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from fileformats.vendor.afni.medimage import OneD
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.model.remlfit import Remlfit

    >>> task = Remlfit()
    >>> task.inputs.in_files = [Nifti1.mock("functional.nii"), Nifti1.mock("functional2.nii")]
    >>> task.inputs.matrix = OneD.mock("output.1D")
    >>> task.inputs.matim = File.mock()
    >>> task.inputs.mask = File.mock()
    >>> task.inputs.STATmask = File.mock()
    >>> task.inputs.dsort = File.mock()
    >>> task.cmdline
    '3dREMLfit -gltsym "SYM: +Lab1 -Lab2" TestSYM -gltsym "timeseries.txt" TestFile -input "functional.nii functional2.nii" -matrix output.1D -Rbuck output.nii'


    """

    executable = "3dREMLfit"
    in_files: list[Nifti1] = shell.arg(
        help="Read time series dataset", argstr='-input "{in_files}"', sep=" "
    )
    matrix: OneD | None = shell.arg(
        help="the design matrix file, which should have been output from Deconvolve via the 'x1D' option",
        argstr="-matrix {matrix}",
    )
    polort: int | None = shell.arg(
        help="if no 'matrix' option is given, AND no 'matim' option, create a matrix with Legendre polynomial regressorsup to the specified order. The default value is 0, whichproduces a matrix with a single column of all ones",
        argstr="-polort {polort}",
    )
    matim: File | None = shell.arg(
        help="read a standard file as the matrix. You can use only Col as a name in GLTs with these nonstandard matrix input methods, since the other names come from the 'matrix' file. These mutually exclusive options are ignored if 'matrix' is used.",
        argstr="-matim {matim}",
    )
    mask: File = shell.arg(
        help="filename of 3D mask dataset; only data time series from within the mask will be analyzed; results for voxels outside the mask will be set to zero.",
        argstr="-mask {mask}",
    )
    automask: bool = shell.arg(
        help="build a mask automatically from input data (will be slow for long time series datasets)",
        argstr="-automask",
        default=False,
    )
    STATmask: File = shell.arg(
        help="filename of 3D mask dataset to be used for the purpose of reporting truncation-to float issues AND for computing the FDR curves. The actual results ARE not masked with this option (only with 'mask' or 'automask' options).",
        argstr="-STATmask {STATmask}",
    )
    addbase: list[File] = shell.arg(
        help="file(s) to add baseline model columns to the matrix with this option. Each column in the specified file(s) will be appended to the matrix. File(s) must have at least as many rows as the matrix does.",
        argstr="-addbase {addbase}",
        sep=" ",
    )
    slibase: list[File] = shell.arg(
        help="similar to 'addbase' in concept, BUT each specified file must have an integer multiple of the number of slices in the input dataset(s); then, separate regression matrices are generated for each slice, with the first column of the file appended to the matrix for the first slice of the dataset, the second column of the file appended to the matrix for the first slice of the dataset, and so on. Intended to help model physiological noise in FMRI, or other effects you want to regress out that might change significantly in the inter-slice time intervals. This will slow the program down, and make it use a lot more memory (to hold all the matrix stuff).",
        argstr="-slibase {slibase}",
    )
    slibase_sm: list[File] = shell.arg(
        help="similar to 'slibase', BUT each file much be in slice major order (i.e. all slice0 columns come first, then all slice1 columns, etc).",
        argstr="-slibase_sm {slibase_sm}",
    )
    usetemp: bool = shell.arg(
        help="write intermediate stuff to disk, to economize on RAM. Using this option might be necessary to run with 'slibase' and with 'Grid' values above the default, since the program has to store a large number of matrices for such a problem: two for every slice and for every (a,b) pair in the ARMA parameter grid. Temporary files are written to the directory given in environment variable TMPDIR, or in /tmp, or in ./ (preference is in that order)",
        argstr="-usetemp",
    )
    nodmbase: bool = shell.arg(
        help="by default, baseline columns added to the matrix via 'addbase' or 'slibase' or 'dsort' will each have their mean removed (as is done in Deconvolve); this option turns this centering off",
        argstr="-nodmbase",
        requires=["addbase", "dsort"],
    )
    dsort: File = shell.arg(
        help="4D dataset to be used as voxelwise baseline regressor",
        argstr="-dsort {dsort}",
    )
    dsort_nods: bool = shell.arg(
        help="if 'dsort' option is used, this command will output additional results files excluding the 'dsort' file",
        argstr="-dsort_nods",
        requires=["dsort"],
    )
    fout: bool = shell.arg(help="output F-statistic for each stimulus", argstr="-fout")
    rout: bool = shell.arg(
        help="output the R^2 statistic for each stimulus", argstr="-rout"
    )
    tout: bool = shell.arg(
        help="output the T-statistic for each stimulus; if you use 'out_file' and do not give any of 'fout', 'tout',or 'rout', then the program assumes 'fout' is activated.",
        argstr="-tout",
    )
    nofdr: bool = shell.arg(
        help="do NOT add FDR curve data to bucket datasets; FDR curves can take a long time if 'tout' is used",
        argstr="-noFDR",
    )
    nobout: bool = shell.arg(
        help="do NOT add baseline (null hypothesis) regressor betas to the 'rbeta_file' and/or 'obeta_file' output datasets.",
        argstr="-nobout",
    )
    gltsym: list[ty.Any] = shell.arg(
        help="read a symbolic GLT from input file and associate it with a label. As in Deconvolve, you can also use the 'SYM:' method to provide the definition of the GLT directly as a string (e.g., with 'SYM: +Label1 -Label2'). Unlike Deconvolve, you MUST specify 'SYM: ' if providing the GLT directly as a string instead of from a file",
        argstr='-gltsym "{gltsym[0]}" {gltsym[1]}...',
    )
    out_file: Path = shell.arg(
        help="output dataset for beta + statistics from the REML estimation; also contains the results of any GLT analysis requested in the Deconvolve setup, similar to the 'bucket' output from Deconvolve. This dataset does NOT get the betas (or statistics) of those regressors marked as 'baseline' in the matrix file.",
        argstr="-Rbuck {out_file}",
    )
    var_file: Path = shell.arg(
        help="output dataset for REML variance parameters", argstr="-Rvar {var_file}"
    )
    rbeta_file: Path = shell.arg(
        help="output dataset for beta weights from the REML estimation, similar to the 'cbucket' output from Deconvolve. This dataset will contain all the beta weights, for baseline and stimulus regressors alike, unless the '-nobout' option is given -- in that case, this dataset will only get the betas for the stimulus regressors.",
        argstr="-Rbeta {rbeta_file}",
    )
    glt_file: Path = shell.arg(
        help="output dataset for beta + statistics from the REML estimation, but ONLY for the GLTs added on the REMLfit command line itself via 'gltsym'; GLTs from Deconvolve's command line will NOT be included.",
        argstr="-Rglt {glt_file}",
    )
    fitts_file: Path = shell.arg(
        help="output dataset for REML fitted model", argstr="-Rfitts {fitts_file}"
    )
    errts_file: Path = shell.arg(
        help="output dataset for REML residuals = data - fitted model",
        argstr="-Rerrts {errts_file}",
    )
    wherr_file: Path = shell.arg(
        help="dataset for REML residual, whitened using the estimated ARMA(1,1) correlation matrix of the noise",
        argstr="-Rwherr {wherr_file}",
    )
    quiet: bool = shell.arg(help="turn off most progress messages", argstr="-quiet")
    verb: bool = shell.arg(
        help="turns on more progress messages, including memory usage progress reports at various stages",
        argstr="-verb",
    )
    goforit: bool = shell.arg(
        help="With potential issues flagged in the design matrix, an attempt will nevertheless be made to fit the model",
        argstr="-GOFORIT",
    )
    ovar: Path = shell.arg(
        help="dataset for OLSQ st.dev. parameter (kind of boring)",
        argstr="-Ovar {ovar}",
    )
    obeta: Path = shell.arg(
        help="dataset for beta weights from the OLSQ estimation",
        argstr="-Obeta {obeta}",
    )
    obuck: Path = shell.arg(
        help="dataset for beta + statistics from the OLSQ estimation",
        argstr="-Obuck {obuck}",
    )
    oglt: Path = shell.arg(
        help="dataset for beta + statistics from 'gltsym' options",
        argstr="-Oglt {oglt}",
    )
    ofitts: Path = shell.arg(
        help="dataset for OLSQ fitted model", argstr="-Ofitts {ofitts}"
    )
    oerrts: Path = shell.arg(
        help="dataset for OLSQ residuals (data - fitted model)",
        argstr="-Oerrts {oerrts}",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: File | None = shell.out(
            help="dataset for beta + statistics from the REML estimation (if generated)",
            callable=out_file_callable,
        )
        var_file: File | None = shell.out(
            help="dataset for REML variance parameters (if generated)",
            callable=var_file_callable,
        )
        rbeta_file: File | None = shell.out(
            help="output dataset for beta weights from the REML estimation (if generated)",
            callable=rbeta_file_callable,
        )
        glt_file: File | None = shell.out(
            help="output dataset for beta + statistics from the REML estimation, but ONLY for the GLTs added on the REMLfit command line itself via 'gltsym' (if generated)",
            callable=glt_file_callable,
        )
        fitts_file: File | None = shell.out(
            help="output dataset for REML fitted model (if generated)",
            callable=fitts_file_callable,
        )
        errts_file: File | None = shell.out(
            help="output dataset for REML residuals = data - fitted model (if generated)",
            callable=errts_file_callable,
        )
        wherr_file: File | None = shell.out(
            help="dataset for REML residual, whitened using the estimated ARMA(1,1) correlation matrix of the noise (if generated)",
            callable=wherr_file_callable,
        )
        ovar: File | None = shell.out(
            help="dataset for OLSQ st.dev. parameter (if generated)",
            callable=ovar_callable,
        )
        obeta: File | None = shell.out(
            help="dataset for beta weights from the OLSQ estimation (if generated)",
            callable=obeta_callable,
        )
        obuck: File | None = shell.out(
            help="dataset for beta + statistics from the OLSQ estimation (if generated)",
            callable=obuck_callable,
        )
        oglt: File | None = shell.out(
            help="dataset for beta + statistics from 'gltsym' options (if generated)",
            callable=oglt_callable,
        )
        ofitts: File | None = shell.out(
            help="dataset for OLSQ fitted model (if generated)",
            callable=ofitts_callable,
        )
        oerrts: File | None = shell.out(
            help="dataset for OLSQ residuals = data - fitted model (if generated)",
            callable=oerrts_callable,
        )
