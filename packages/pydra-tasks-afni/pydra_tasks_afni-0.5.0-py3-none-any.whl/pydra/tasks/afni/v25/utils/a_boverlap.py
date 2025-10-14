import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
from fileformats.text import TextFile
import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import split_filename
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
    return outputs


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


@shell.define
class ABoverlap(shell.Task["ABoverlap.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from fileformats.text import TextFile
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.a_boverlap import ABoverlap

    >>> task = ABoverlap()
    >>> task.inputs.in_file_a = Nifti1.mock("functional.nii")
    >>> task.inputs.in_file_b = File.mock()
    >>> task.inputs.out_file =  "out.mask_ae_overlap.txt"
    >>> task.cmdline
    'None'


    """

    executable = "3dABoverlap"
    in_file_a: Nifti1 = shell.arg(
        help="input file A", argstr="{in_file_a}", position=-3
    )
    in_file_b: File = shell.arg(help="input file B", argstr="{in_file_b}", position=-2)
    out_file: Path = shell.arg(
        help="collect output to a file", argstr=" |& tee {out_file}", position=-1
    )
    no_automask: bool = shell.arg(
        help="consider input datasets as masks", argstr="-no_automask"
    )
    quiet: bool = shell.arg(
        help="be as quiet as possible (without being entirely mute)", argstr="-quiet"
    )
    verb: bool = shell.arg(
        help="print out some progress reports (to stderr)", argstr="-verb"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: TextFile | None = shell.out(
            help="output file", callable=out_file_callable
        )
