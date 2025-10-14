import attrs
from fileformats.generic import File
from fileformats.vendor.afni.medimage import OneD
import logging
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}

    if inputs["out_file"] is not attrs.NOTHING:
        outputs["out_file"] = os.path.join(os.getcwd(), inputs["out_file"])
    if inputs["show_cormat_warnings"] is not attrs.NOTHING:
        outputs["out_file"] = os.path.join(os.getcwd(), inputs["show_cormat_warnings"])
    if inputs["censor_motion"] is not attrs.NOTHING:
        outputs["out_file"] = os.path.join(
            os.getcwd(), inputs["censor_motion"][1] + "_censor.1D"
        )
    return outputs


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


@shell.define(xor=[["show_cormat_warnings", "out_file"]])
class OneDToolPy(shell.Task["OneDToolPy.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.vendor.afni.medimage import OneD
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.one_d_tool_py import OneDToolPy

    >>> task = OneDToolPy()
    >>> task.inputs.in_file = OneD.mock("f1.1D")
    >>> task.inputs.demean = True
    >>> task.inputs.show_cormat_warnings = File.mock()
    >>> task.cmdline
    'python2 ...1d_tool.py -demean -infile f1.1D -write motion_dmean.1D -set_nruns 3'


    """

    executable = "1d_tool.py"
    in_file: OneD = shell.arg(help="input file to OneDTool", argstr="-infile {in_file}")
    set_nruns: int = shell.arg(
        help="treat the input data as if it has nruns", argstr="-set_nruns {set_nruns}"
    )
    derivative: bool = shell.arg(
        help="take the temporal derivative of each vector (done as first backward difference)",
        argstr="-derivative",
    )
    demean: bool = shell.arg(
        help="demean each run (new mean of each run = 0.0)", argstr="-demean"
    )
    out_file: Path | None = shell.arg(
        help="write the current 1D data to FILE", argstr="-write {out_file}"
    )
    show_censor_count: bool = shell.arg(
        help="display the total number of censored TRs  Note : if input is a valid xmat.1D dataset, then the count will come from the header.  Otherwise the input is assumed to be a binary censorfile, and zeros are simply counted.",
        argstr="-show_censor_count",
    )
    censor_motion: ty.Any = shell.arg(
        help="Tuple of motion limit and outfile prefix. need to also set set_nruns -r set_run_lengths",
        argstr="-censor_motion {censor_motion[0]} {censor_motion[1]}",
    )
    censor_prev_TR: bool = shell.arg(
        help="for each censored TR, also censor previous", argstr="-censor_prev_TR"
    )
    show_trs_uncensored: ty.Any = shell.arg(
        help="display a list of TRs which were not censored in the specified style",
        argstr="-show_trs_uncensored {show_trs_uncensored}",
    )
    show_cormat_warnings: File | None = shell.arg(
        help="Write cormat warnings to a file",
        argstr="-show_cormat_warnings |& tee {show_cormat_warnings}",
        position=-1,
    )
    show_indices_interest: bool = shell.arg(
        help="display column indices for regs of interest",
        argstr="-show_indices_interest",
    )
    show_trs_run: int = shell.arg(
        help="restrict -show_trs_[un]censored to the given 1-based run",
        argstr="-show_trs_run {show_trs_run}",
    )
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")
    py27_path: ty.Any = shell.arg(help="", default="python2")

    class Outputs(shell.Outputs):
        out_file: File | None = shell.out(
            help="output of 1D_tool.py", callable=out_file_callable
        )
