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
    if inputs["oned_file"]:
        outputs["oned_file"] = os.path.abspath(inputs["oned_file"])

    return outputs


def oned_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("oned_file")


@shell.define
class DegreeCentrality(shell.Task["DegreeCentrality.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.preprocess.degree_centrality import DegreeCentrality

    >>> task = DegreeCentrality()
    >>> task.inputs.in_file = Nifti1.mock("functional.nii")
    >>> task.inputs.sparsity = 1 # keep the top one percent of connections
    >>> task.inputs.mask = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "3dDegreeCentrality"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dDegreeCentrality", argstr="{in_file}", position=-1
    )
    sparsity: float = shell.arg(
        help="only take the top percent of connections", argstr="-sparsity {sparsity}"
    )
    oned_file: str = shell.arg(
        help="output filepath to text dump of correlation matrix",
        argstr="-out1D {oned_file}",
    )
    mask: File = shell.arg(help="mask file to mask input data", argstr="-mask {mask}")
    thresh: float = shell.arg(
        help="threshold to exclude connections where corr <= thresh",
        argstr="-thresh {thresh}",
    )
    polort: int = shell.arg(help="", argstr="-polort {polort}")
    autoclip: bool = shell.arg(
        help="Clip off low-intensity regions in the dataset", argstr="-autoclip"
    )
    automask: bool = shell.arg(
        help="Mask the dataset to target brain-only voxels", argstr="-automask"
    )
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_afni",
        )
        oned_file: File | None = shell.out(
            help="The text output of the similarity matrix computed after thresholding with one-dimensional and ijk voxel indices, correlations, image extents, and affine matrix.",
            callable=oned_file_callable,
        )
