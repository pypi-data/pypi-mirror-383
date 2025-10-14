import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
import numpy as np
import os
import os.path as op
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    parsed_inputs = _parse_inputs(inputs) if inputs else {}
    if value is None:
        return ""

    if name == "detrend":
        if value is True:
            return argstr
        elif value is False:
            return None
        elif isinstance(value, int):
            return argstr + " %d" % value

    if name == "acf":
        if value is True:
            return argstr
        elif value is False:
            parsed_inputs["_acf"] = False
            return None
        elif isinstance(value, tuple):
            return argstr + " %s %f" % value
        elif isinstance(value, (str, bytes)):
            return argstr + " " + value

    return argstr.format(**inputs)


def detrend_formatter(field, inputs):
    return _format_arg("detrend", field, inputs, argstr="-detrend")


def acf_formatter(field, inputs):
    return _format_arg("acf", field, inputs, argstr="-acf")


def _parse_inputs(inputs, output_dir=None):
    if not output_dir:
        output_dir = os.getcwd()
    parsed_inputs = {}
    skip = []

    if not inputs["detrend"]:
        if skip is None:
            skip = []
        skip += ["out_detrend"]

    return parsed_inputs


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    parsed_inputs = _parse_inputs(inputs, output_dir=output_dir)

    outputs = {}

    if inputs["detrend"]:
        fname, ext = op.splitext(inputs["in_file"])
        if ".gz" in ext:
            _, ext2 = op.splitext(fname)
            ext = ext2 + ext
        outputs["out_detrend"] += ext
    else:
        outputs["out_detrend"] = type(attrs.NOTHING)

    sout = np.loadtxt(outputs["out_file"])

    if sout.size == 8:
        outputs["fwhm"] = tuple(sout[0, :])
    else:
        outputs["fwhm"] = tuple(sout)

    if parsed_inputs["_acf"]:
        assert sout.size == 8, "Wrong number of elements in %s" % str(sout)
        outputs["acf_param"] = tuple(sout[1])

        outputs["out_acf"] = op.abspath("3dFWHMx.1D")
        if isinstance(inputs["acf"], (str, bytes)):
            outputs["out_acf"] = op.abspath(inputs["acf"])

    return outputs


def fwhm_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("fwhm")


def acf_param_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("acf_param")


def out_acf_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_acf")


@shell.define(xor=[["arith", "geom"], ["demed", "detrend"]])
class FWHMx(shell.Task["FWHMx.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.fwh_mx import FWHMx

    >>> task = FWHMx()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.mask = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dFWHMx"
    in_file: Nifti1 = shell.arg(help="input dataset", argstr="-input {in_file}")
    mask: File = shell.arg(
        help="use only voxels that are nonzero in mask", argstr="-mask {mask}"
    )
    automask: bool = shell.arg(
        help="compute a mask from THIS dataset, a la 3dAutomask",
        argstr="-automask",
        default=False,
    )
    detrend: ty.Any | None = shell.arg(
        help="instead of demed (0th order detrending), detrend to the specified order.  If order is not given, the program picks q=NT/30. -detrend disables -demed, and includes -unif.",
        formatter=detrend_formatter,
        default=False,
    )
    demed: bool = shell.arg(
        help="If the input dataset has more than one sub-brick (e.g., has a time axis), then subtract the median of each voxel's time series before processing FWHM. This will tend to remove intrinsic spatial structure and leave behind the noise.",
        argstr="-demed",
    )
    unif: bool = shell.arg(
        help="If the input dataset has more than one sub-brick, then normalize each voxel's time series to have the same MAD before processing FWHM.",
        argstr="-unif",
    )
    geom: bool = shell.arg(
        help="if in_file has more than one sub-brick, compute the final estimate as the geometric mean of the individual sub-brick FWHM estimates",
        argstr="-geom",
    )
    arith: bool = shell.arg(
        help="if in_file has more than one sub-brick, compute the final estimate as the arithmetic mean of the individual sub-brick FWHM estimates",
        argstr="-arith",
    )
    combine_: bool = shell.arg(
        help="combine the final measurements along each axis", argstr="-combine"
    )
    compat: bool = shell.arg(
        help="be compatible with the older 3dFWHM", argstr="-compat"
    )
    acf: ty.Any = shell.arg(
        help="computes the spatial autocorrelation",
        formatter=acf_formatter,
        default=False,
    )

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output file",
            argstr="> {out_file}",
            position=-1,
            path_template="{in_file}_fwhmx.out",
        )
        out_subbricks: Path = shell.outarg(
            help="output file listing the subbricks FWHM",
            argstr="-out {out_subbricks}",
            path_template="{in_file}_subbricks.out",
        )
        out_detrend: Path = shell.outarg(
            help="Save the detrended file into a dataset",
            argstr="-detprefix {out_detrend}",
            path_template="{in_file}_detrend",
        )
        fwhm: ty.Any | None = shell.out(
            help="FWHM along each axis", callable=fwhm_callable
        )
        acf_param: ty.Any | None = shell.out(
            help="fitted ACF model parameters", callable=acf_param_callable
        )
        out_acf: File | None = shell.out(
            help="output acf file", callable=out_acf_callable
        )
