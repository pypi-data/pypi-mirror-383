import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import fname_presuffix
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    import glob

    outputs = {}

    if inputs["out_file"] is attrs.NOTHING:
        prefix = _gen_fname(
            inputs["in_file"],
            suffix="_netcorr",
            outputtype=inputs["outputtype"],
            inputs=inputs["inputs"],
            stdout=inputs["stdout"],
            stderr=inputs["stderr"],
            output_dir=inputs["output_dir"],
        )
    else:
        prefix = inputs["out_file"]

    odir = os.path.dirname(os.path.abspath(prefix))
    outputs["out_corr_matrix"] = glob.glob(os.path.join(odir, "*.netcc"))[0]

    if inputs["ts_wb_corr"] or inputs["ts_wb_Z"]:
        corrdir = os.path.join(odir, prefix + "_000_INDIV")
        outputs["out_corr_maps"] = glob.glob(os.path.join(corrdir, "*.nii.gz"))

    return outputs


def out_corr_matrix_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_corr_matrix")


def out_corr_maps_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_corr_maps")


@shell.define
class NetCorr(shell.Task["NetCorr.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.net_corr import NetCorr

    >>> task = NetCorr()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.in_rois = Nifti1.mock("maps.nii")
    >>> task.inputs.mask = File.mock()
    >>> task.inputs.weight_ts = File.mock()
    >>> task.inputs.ts_wb_Z = True
    >>> task.inputs.out_file = "sub0.tp1.ncorr"
    >>> task.cmdline
    'None'


    """

    executable = "3dNetCorr"
    in_file: Nifti1 = shell.arg(
        help="input time series file (4D data set)", argstr="-inset {in_file}"
    )
    in_rois: Nifti1 = shell.arg(
        help="input set of ROIs, each labelled with distinct integers",
        argstr="-in_rois {in_rois}",
    )
    mask: File = shell.arg(
        help="can include a whole brain mask within which to calculate correlation. Otherwise, data should be masked already",
        argstr="-mask {mask}",
    )
    weight_ts: File = shell.arg(
        help="input a 1D file WTS of weights that will be applied multiplicatively to each ROI's average time series. WTS can be a column- or row-file of values, but it must have the same length as the input time series volume. If the initial average time series was A[n] for n=0,..,(N-1) time points, then applying a set of weights W[n] of the same length from WTS would produce a new time series:  B[n] = A[n] * W[n]",
        argstr="-weight_ts {weight_ts}",
    )
    fish_z: bool = shell.arg(
        help="switch to also output a matrix of Fisher Z-transform values for the corr coefs (r): Z = atanh(r) , (with Z=4 being output along matrix diagonals where r=1, as the r-to-Z conversion is ceilinged at Z = atanh(r=0.999329) = 4, which is still *quite* a high Pearson-r value",
        argstr="-fish_z",
    )
    part_corr: bool = shell.arg(
        help="output the partial correlation matrix", argstr="-part_corr"
    )
    ts_out: bool = shell.arg(
        help="switch to output the mean time series of the ROIs that have been used to generate the correlation matrices. Output filenames mirror those of the correlation matrix files, with a '.netts' postfix",
        argstr="-ts_out",
    )
    ts_label: bool = shell.arg(
        help="additional switch when using '-ts_out'. Using this option will insert the integer ROI label at the start of each line of the *.netts file created. Thus, for a time series of length N, each line will have N+1 numbers, where the first is the integer ROI label and the subsequent N are scientific notation values",
        argstr="-ts_label",
    )
    ts_indiv: bool = shell.arg(
        help="switch to create a directory for each network that contains the average time series for each ROI in individual files (each file has one line). The directories are labelled PREFIX_000_INDIV/, PREFIX_001_INDIV/, etc. (one per network). Within each directory, the files are labelled ROI_001.netts, ROI_002.netts, etc., with the numbers given by the actual ROI integer labels",
        argstr="-ts_indiv",
    )
    ts_wb_corr: bool = shell.arg(
        help="switch to create a set of whole brain correlation maps. Performs whole brain correlation for each ROI's average time series; this will automatically create a directory for each network that contains the set of whole brain correlation maps (Pearson 'r's). The directories are labelled as above for '-ts_indiv' Within each directory, the files are labelled WB_CORR_ROI_001+orig, WB_CORR_ROI_002+orig, etc., with the numbers given by the actual ROI integer labels",
        argstr="-ts_wb_corr",
    )
    ts_wb_Z: bool = shell.arg(
        help="same as above in '-ts_wb_corr', except that the maps have been Fisher transformed to Z-scores the relation: Z=atanh(r). To avoid infinities in the transform, Pearson values are effectively capped at |r| = 0.999329 (where |Z| = 4.0). Files are labelled WB_Z_ROI_001+orig, etc",
        argstr="-ts_wb_Z",
    )
    ts_wb_strlabel: bool = shell.arg(
        help="by default, '-ts_wb_{corr,Z}' output files are named using the int number of a given ROI, such as: WB_Z_ROI_001+orig. With this option, one can replace the int (such as '001') with the string label (such as 'L-thalamus') *if* one has a labeltable attached to the file",
        argstr="-ts_wb_strlabel",
    )
    nifti: bool = shell.arg(
        help="output any correlation map files as NIFTI files (default is BRIK/HEAD). Only useful if using '-ts_wb_corr' and/or '-ts_wb_Z'",
        argstr="-nifti",
    )
    output_mask_nonnull: bool = shell.arg(
        help="internally, this program checks for where there are nonnull time series, because we don't like those, in general.  With this flag, the user can output the determined mask of non-null time series.",
        argstr="-output_mask_nonnull",
    )
    push_thru_many_zeros: bool = shell.arg(
        help="by default, this program will grind to a halt and refuse to calculate if any ROI contains >10 percent of voxels with null times series (i.e., each point is 0), as of April, 2017.  This is because it seems most likely that hidden badness is responsible. However, if the user still wants to carry on the calculation anyways, then this option will allow one to push on through.  However, if any ROI *only* has null time series, then the program will not calculate and the user will really, really, really need to address their masking",
        argstr="-push_thru_many_zeros",
    )
    ignore_LT: bool = shell.arg(
        help="switch to ignore any label table labels in the '-in_rois' file, if there are any labels attached",
        argstr="-ignore_LT",
    )
    out_file: Path = shell.arg(
        help="output file name part", argstr="-prefix {out_file}", position=1
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_corr_matrix: File | None = shell.out(
            help="output correlation matrix between ROIs written to a text file with .netcc suffix",
            callable=out_corr_matrix_callable,
        )
        out_corr_maps: list[File] | None = shell.out(
            help="output correlation maps in Pearson and/or Z-scores",
            callable=out_corr_maps_callable,
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
        msg = "Unable to generate filename for command %s. " % "3dNetCorr"
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
