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


def scale_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("scale_file")


@shell.define(xor=[["gm", "epi"]])
class Unifize(shell.Task["Unifize.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.afni.v25.utils.unifize import Unifize

    >>> task = Unifize()
    >>> task.inputs.in_file = Nifti1.mock("structural.nii")
    >>> task.cmdline
    'None'


    """

    executable = "3dUnifize"
    in_file: Nifti1 = shell.arg(
        help="input file to 3dUnifize", argstr="-input {in_file}", position=-1
    )
    t2: bool = shell.arg(
        help="Treat the input as if it were T2-weighted, rather than T1-weighted. This processing is done simply by inverting the image contrast, processing it as if that result were T1-weighted, and then re-inverting the results counts of voxel overlap, i.e., each voxel will contain the number of masks that it is set in.",
        argstr="-T2",
    )
    gm: bool = shell.arg(
        help="Also scale to unifize 'gray matter' = lower intensity voxels (to aid in registering images from different scanners).",
        argstr="-GM",
    )
    urad: float = shell.arg(
        help="Sets the radius (in voxels) of the ball used for the sneaky trick. Default value is 18.3, and should be changed proportionally if the dataset voxel size differs significantly from 1 mm.",
        argstr="-Urad {urad}",
    )
    scale_file: Path = shell.arg(
        help="output file name to save the scale factor used at each voxel ",
        argstr="-ssave {scale_file}",
    )
    no_duplo: bool = shell.arg(
        help="Do NOT use the 'duplo down' step; this can be useful for lower resolution datasets.",
        argstr="-noduplo",
    )
    epi: bool = shell.arg(
        help="Assume the input dataset is a T2 (or T2\\*) weighted EPI time series. After computing the scaling, apply it to ALL volumes (TRs) in the input dataset. That is, a given voxel will be scaled by the same factor at each TR. This option also implies '-noduplo' and '-T2'.This option turns off '-GM' if you turned it on.",
        argstr="-EPI",
        requires=["no_duplo", "t2"],
    )
    rbt: ty.Any = shell.arg(
        help="Option for AFNI experts only.Specify the 3 parameters for the algorithm:\nR = radius; same as given by option '-Urad', [default=18.3]\nb = bottom percentile of normalizing data range, [default=70.0]\nr = top percentile of normalizing data range, [default=80.0]\n",
        argstr="-rbt {rbt[0]} {rbt[1]} {rbt[2]}",
    )
    t2_up: float = shell.arg(
        help="Option for AFNI experts only.Set the upper percentile point used for T2-T1 inversion. Allowed to be anything between 90 and 100 (inclusive), with default to 98.5  (for no good reason).",
        argstr="-T2up {t2_up}",
    )
    cl_frac: float = shell.arg(
        help="Option for AFNI experts only.Set the automask 'clip level fraction'. Must be between 0.1 and 0.9. A small fraction means to make the initial threshold for clipping (a la 3dClipLevel) smaller, which will tend to make the mask larger.  [default=0.1]",
        argstr="-clfrac {cl_frac}",
    )
    quiet: bool = shell.arg(help="Don't print the progress messages.", argstr="-quiet")
    num_threads: int = shell.arg(help="set number of threads", default=1)
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="output image file name",
            argstr="-prefix {out_file}",
            path_template="{in_file}_unifized",
        )
        scale_file: File | None = shell.out(
            help="scale factor file", callable=scale_file_callable
        )
