import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import split_filename
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name in inputs["_thresh_opts"]:
        return argstr.format(**{name: inputs["thresholds"] + [value]})
    elif name in inputs["_expr_opts"]:
        return argstr % (inputs["expr"], value)
    elif name == "histogram":
        return argstr % (inputs["histogram_bin_numbers"], value)
    else:
        pass

    return argstr.format(**inputs)


def histogram_formatter(field, inputs):
    return _format_arg(
        "histogram", field, inputs, argstr="-Hist {histogram[0]} {histogram[1]}"
    )


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
    return outputs


def mean_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("mean_file")


def zmean_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("zmean")


def qmean_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("qmean")


def pmean_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("pmean")


def absolute_threshold_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("absolute_threshold")


def var_absolute_threshold_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("var_absolute_threshold")


def var_absolute_threshold_normalize_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("var_absolute_threshold_normalize")


def correlation_maps_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("correlation_maps")


def correlation_maps_masked_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("correlation_maps_masked")


def average_expr_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("average_expr")


def average_expr_nonzero_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("average_expr_nonzero")


def sum_expr_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("sum_expr")


def histogram_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("histogram")


@shell.define(
    xor=[
        [
            "absolute_threshold",
            "var_absolute_threshold",
            "var_absolute_threshold_normalize",
        ],
        ["average_expr", "average_expr_nonzero", "sum_expr"],
        ["seeds_width", "seeds"],
    ]
)
class TCorrMap(shell.Task["TCorrMap.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.t_corr_map import TCorrMap

    >>> task = TCorrMap()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.seeds = File.mock()
    >>> task.inputs.mask = File.mock()
    >>> task.inputs.regress_out_timeseries = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dTcorrMap"
    in_file: Nifti1 = shell.arg(help="", argstr="-input {in_file}")
    seeds: File | None = shell.arg(help="", argstr="-seed {seeds}")
    mask: File = shell.arg(help="", argstr="-mask {mask}")
    automask: bool = shell.arg(help="", argstr="-automask")
    polort: int = shell.arg(help="", argstr="-polort {polort}")
    bandpass: ty.Any = shell.arg(help="", argstr="-bpass {bandpass[0]} {bandpass[1]}")
    regress_out_timeseries: File = shell.arg(
        help="", argstr="-ort {regress_out_timeseries}"
    )
    blur_fwhm: float = shell.arg(help="", argstr="-Gblur {blur_fwhm}")
    seeds_width: float | None = shell.arg(help="", argstr="-Mseed {seeds_width}")
    mean_file: Path = shell.arg(help="", argstr="-Mean {mean_file}")
    zmean: Path = shell.arg(help="", argstr="-Zmean {zmean}")
    qmean: Path = shell.arg(help="", argstr="-Qmean {qmean}")
    pmean: Path = shell.arg(help="", argstr="-Pmean {pmean}")
    thresholds: list[int] = shell.arg(help="")
    absolute_threshold: Path | None = shell.arg(
        help="", argstr="-Thresh {absolute_threshold[0]} {absolute_threshold[1]}"
    )
    var_absolute_threshold: Path | None = shell.arg(
        help="",
        argstr="-VarThresh {var_absolute_threshold[0]} {var_absolute_threshold[1]} {var_absolute_threshold[2]} {var_absolute_threshold[3]}",
    )
    var_absolute_threshold_normalize: Path | None = shell.arg(
        help="",
        argstr="-VarThreshN {var_absolute_threshold_normalize[0]} {var_absolute_threshold_normalize[1]} {var_absolute_threshold_normalize[2]} {var_absolute_threshold_normalize[3]}",
    )
    correlation_maps: Path = shell.arg(help="", argstr="-CorrMap {correlation_maps}")
    correlation_maps_masked: Path = shell.arg(
        help="", argstr="-CorrMask {correlation_maps_masked}"
    )
    expr: str = shell.arg(help="")
    average_expr: Path | None = shell.arg(
        help="", argstr="-Aexpr {average_expr[0]} {average_expr[1]}"
    )
    average_expr_nonzero: Path | None = shell.arg(
        help="", argstr="-Cexpr {average_expr_nonzero[0]} {average_expr_nonzero[1]}"
    )
    sum_expr: Path | None = shell.arg(
        help="", argstr="-Sexpr {sum_expr[0]} {sum_expr[1]}"
    )
    histogram_bin_numbers: int = shell.arg(help="")
    histogram: Path = shell.arg(help="", formatter=histogram_formatter)
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")
    out_file: Path = shell.arg(
        help="output image file name", argstr="-prefix {out_file}"
    )

    class Outputs(shell.Outputs):
        mean_file: File | None = shell.out(callable=mean_file_callable)
        zmean: File | None = shell.out(callable=zmean_callable)
        qmean: File | None = shell.out(callable=qmean_callable)
        pmean: File | None = shell.out(callable=pmean_callable)
        absolute_threshold: File | None = shell.out(
            callable=absolute_threshold_callable
        )
        var_absolute_threshold: File | None = shell.out(
            callable=var_absolute_threshold_callable
        )
        var_absolute_threshold_normalize: File | None = shell.out(
            callable=var_absolute_threshold_normalize_callable
        )
        correlation_maps: File | None = shell.out(callable=correlation_maps_callable)
        correlation_maps_masked: File | None = shell.out(
            callable=correlation_maps_masked_callable
        )
        average_expr: File | None = shell.out(callable=average_expr_callable)
        average_expr_nonzero: File | None = shell.out(
            callable=average_expr_nonzero_callable
        )
        sum_expr: File | None = shell.out(callable=sum_expr_callable)
        histogram: File | None = shell.out(callable=histogram_callable)
