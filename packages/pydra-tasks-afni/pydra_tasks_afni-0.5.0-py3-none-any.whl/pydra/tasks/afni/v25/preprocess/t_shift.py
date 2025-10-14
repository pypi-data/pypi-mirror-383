import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import split_filename
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "tpattern" and value.startswith("@"):
        iflogger.warning(
            'Passing a file prefixed by "@" will be deprecated'
            "; please use the `slice_timing` input"
        )
    elif name == "slice_timing" and isinstance(value, list):
        value = _write_slice_timing(
            slice_timing=inputs["slice_timing"],
            slice_encoding_direction=inputs["slice_encoding_direction"],
        )

    return argstr.format(**inputs)


def tpattern_formatter(field, inputs):
    return _format_arg("tpattern", field, inputs, argstr="-tpattern {tpattern}")


def slice_timing_formatter(field, inputs):
    return _format_arg(
        "slice_timing", field, inputs, argstr="-tpattern @{slice_timing}"
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
    if inputs["slice_timing"] is not attrs.NOTHING:
        if isinstance(inputs["slice_timing"], list):
            outputs["timing_file"] = os.path.abspath("slice_timing.1D")
        else:
            outputs["timing_file"] = os.path.abspath(inputs["slice_timing"])
    return outputs


def timing_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("timing_file")


@shell.define(xor=[["slice_timing", "tpattern"], ["tzero", "tslice"]])
class TShift(shell.Task["TShift.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.t_shift import TShift

    >>> task = TShift()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.tr = "%.1fs" % TR
    >>> task.cmdline
    '3dTshift -prefix functional_tshift -tpattern @slice_timing.1D -TR 2.5s -tzero 0.0 functional.nii'


    >>> task = TShift()
    >>> task.inputs.in_file = Nifti1.mock()
    >>> task.inputs.slice_encoding_direction = "k-"
    >>> task.cmdline
    '3dTshift -prefix functional_tshift -tpattern @slice_timing.1D -TR 2.5s -tzero 0.0 functional.nii" >>> np.loadtxt(tshift._list_outputs()["timing_file'


    >>> task = TShift()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.tr = "%.1fs" % TR
    >>> task.cmdline
    '3dTshift -prefix functional_tshift -tpattern @slice_timing.1D -TR 2.5s -tzero 0.0 functional.nii'


    >>> task = TShift()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.tr = "%.1fs" % TR
    >>> task.cmdline
    '3dTshift -prefix functional_tshift -tpattern alt+z -TR 2.5s -tzero 0.0 functional.nii'


    >>> task = TShift()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.tr = "%.1fs" % TR
    >>> task.cmdline
    '3dTshift -prefix functional_tshift -tpattern @slice_timing.1D -TR 2.5s -tzero 0.0 functional.nii'


    """

    executable = "3dTshift"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dTshift", argstr="{in_file}", position=-1
    )
    tr: str = shell.arg(
        help='manually set the TR. You can attach suffix "s" for seconds or "ms" for milliseconds.',
        argstr="-TR {tr}",
    )
    tzero: float | None = shell.arg(
        help="align each slice to given time offset", argstr="-tzero {tzero}"
    )
    tslice: int | None = shell.arg(
        help="align each slice to time offset of given slice", argstr="-slice {tslice}"
    )
    ignore: int = shell.arg(
        help="ignore the first set of points specified", argstr="-ignore {ignore}"
    )
    interp: ty.Any = shell.arg(
        help="different interpolation methods (see 3dTshift for details) default = Fourier",
        argstr="-{interp}",
    )
    tpattern: ty.Any | None = shell.arg(
        help="use specified slice time pattern rather than one in header",
        formatter=tpattern_formatter,
    )
    slice_timing: ty.Any | None = shell.arg(
        help="time offsets from the volume acquisition onset for each slice",
        formatter=slice_timing_formatter,
    )
    slice_encoding_direction: ty.Any = shell.arg(
        help="Direction in which slice_timing is specified (default: k). If negative,slice_timing is defined in reverse order, that is, the first entry corresponds to the slice with the largest index, and the final entry corresponds to slice index zero. Only in effect when slice_timing is passed as list, not when it is passed as file.",
        default="k",
    )
    rlt: bool = shell.arg(
        help="Before shifting, remove the mean and linear trend", argstr="-rlt"
    )
    rltplus: bool = shell.arg(
        help="Before shifting, remove the mean and linear trend and later put back the mean",
        argstr="-rlt+",
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_tshift",
        )
        timing_file: File | None = shell.out(
            help="AFNI formatted timing file, if ``slice_timing`` is a list",
            callable=timing_file_callable,
        )


def _write_slice_timing(slice_timing=None, slice_encoding_direction=None):
    slice_timing = list(slice_timing)
    if slice_encoding_direction.endswith("-"):
        slice_timing.reverse()

    fname = "slice_timing.1D"
    with open(fname, "w") as fobj:
        fobj.write("\t".join(map(str, slice_timing)))
    return fname


iflogger = logging.getLogger("nipype.interface")
