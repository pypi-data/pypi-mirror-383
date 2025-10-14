import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.afni.v25.base import Info
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import fname_presuffix
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    anat_prefix = _gen_fname(
        inputs["anat"],
        outputtype=inputs["outputtype"],
        inputs=inputs["inputs"],
        stdout=inputs["stdout"],
        stderr=inputs["stderr"],
        output_dir=inputs["output_dir"],
    )
    epi_prefix = _gen_fname(
        inputs["in_file"],
        outputtype=inputs["outputtype"],
        inputs=inputs["inputs"],
        stdout=inputs["stdout"],
        stderr=inputs["stderr"],
        output_dir=inputs["output_dir"],
    )
    if "+" in anat_prefix:
        anat_prefix = "".join(anat_prefix.split("+")[:-1])
    if "+" in epi_prefix:
        epi_prefix = "".join(epi_prefix.split("+")[:-1])
    outputtype = inputs["outputtype"]
    if outputtype == "AFNI":
        ext = ".HEAD"
    else:
        ext = Info.output_type_to_ext(outputtype)
    matext = ".1D"
    suffix = inputs["suffix"]
    if inputs["anat2epi"]:
        outputs["anat_al_orig"] = _gen_fname(
            anat_prefix,
            suffix=suffix + "+orig",
            ext=ext,
            outputtype=inputs["outputtype"],
            inputs=inputs["inputs"],
            stdout=inputs["stdout"],
            stderr=inputs["stderr"],
            output_dir=inputs["output_dir"],
        )
        outputs["anat_al_mat"] = _gen_fname(
            anat_prefix,
            suffix=suffix + "_mat.aff12",
            ext=matext,
            outputtype=inputs["outputtype"],
            inputs=inputs["inputs"],
            stdout=inputs["stdout"],
            stderr=inputs["stderr"],
            output_dir=inputs["output_dir"],
        )
    if inputs["epi2anat"]:
        outputs["epi_al_orig"] = _gen_fname(
            epi_prefix,
            suffix=suffix + "+orig",
            ext=ext,
            outputtype=inputs["outputtype"],
            inputs=inputs["inputs"],
            stdout=inputs["stdout"],
            stderr=inputs["stderr"],
            output_dir=inputs["output_dir"],
        )
        outputs["epi_al_mat"] = _gen_fname(
            epi_prefix,
            suffix=suffix + "_mat.aff12",
            ext=matext,
            outputtype=inputs["outputtype"],
            inputs=inputs["inputs"],
            stdout=inputs["stdout"],
            stderr=inputs["stderr"],
            output_dir=inputs["output_dir"],
        )
    if inputs["volreg"] == "on":
        outputs["epi_vr_al_mat"] = _gen_fname(
            epi_prefix,
            suffix="_vr" + suffix + "_mat.aff12",
            ext=matext,
            outputtype=inputs["outputtype"],
            inputs=inputs["inputs"],
            stdout=inputs["stdout"],
            stderr=inputs["stderr"],
            output_dir=inputs["output_dir"],
        )
        if inputs["tshift"] == "on":
            outputs["epi_vr_motion"] = _gen_fname(
                epi_prefix,
                suffix="tsh_vr_motion",
                ext=matext,
                outputtype=inputs["outputtype"],
                inputs=inputs["inputs"],
                stdout=inputs["stdout"],
                stderr=inputs["stderr"],
                output_dir=inputs["output_dir"],
            )
        elif inputs["tshift"] == "off":
            outputs["epi_vr_motion"] = _gen_fname(
                epi_prefix,
                suffix="vr_motion",
                ext=matext,
                outputtype=inputs["outputtype"],
                inputs=inputs["inputs"],
                stdout=inputs["stdout"],
                stderr=inputs["stderr"],
                output_dir=inputs["output_dir"],
            )
    if inputs["volreg"] == "on" and inputs["epi2anat"]:
        outputs["epi_reg_al_mat"] = _gen_fname(
            epi_prefix,
            suffix="_reg" + suffix + "_mat.aff12",
            ext=matext,
            outputtype=inputs["outputtype"],
            inputs=inputs["inputs"],
            stdout=inputs["stdout"],
            stderr=inputs["stderr"],
            output_dir=inputs["output_dir"],
        )
    if inputs["save_skullstrip"]:
        outputs["skullstrip"] = _gen_fname(
            anat_prefix,
            suffix="_ns" + "+orig",
            ext=ext,
            outputtype=inputs["outputtype"],
            inputs=inputs["inputs"],
            stdout=inputs["stdout"],
            stderr=inputs["stderr"],
            output_dir=inputs["output_dir"],
        )
    return outputs


def anat_al_orig_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("anat_al_orig")


def epi_al_orig_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("epi_al_orig")


def epi_tlrc_al_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("epi_tlrc_al")


def anat_al_mat_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("anat_al_mat")


def epi_al_mat_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("epi_al_mat")


def epi_vr_al_mat_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("epi_vr_al_mat")


def epi_reg_al_mat_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("epi_reg_al_mat")


def epi_al_tlrc_mat_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("epi_al_tlrc_mat")


def epi_vr_motion_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("epi_vr_motion")


def skullstrip_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("skullstrip")


@shell.define
class AlignEpiAnatPy(shell.Task["AlignEpiAnatPy.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pydra.tasks.afni.v25.preprocess.align_epi_anat_py import AlignEpiAnatPy

    >>> task = AlignEpiAnatPy()
    >>> task.inputs.in_file = File.mock()
    >>> task.inputs.anat = Nifti1.mock("structural.nii")
    >>> task.inputs.epi_base = 0
    >>> task.inputs.save_skullstrip = True
    >>> task.inputs.volreg = "off"
    >>> task.cmdline
    'None'


    """

    executable = "align_epi_anat.py"
    in_file: File = shell.arg(help="EPI dataset to align", argstr="-epi {in_file}")
    anat: Nifti1 = shell.arg(help="name of structural dataset", argstr="-anat {anat}")
    epi_base: ty.Any = shell.arg(
        help="the epi base used in alignmentshould be one of (0/mean/median/max/subbrick#)",
        argstr="-epi_base {epi_base}",
    )
    anat2epi: bool = shell.arg(
        help="align anatomical to EPI dataset (default)", argstr="-anat2epi"
    )
    epi2anat: bool = shell.arg(
        help="align EPI to anatomical dataset", argstr="-epi2anat"
    )
    save_skullstrip: bool = shell.arg(
        help="save skull-stripped (not aligned)", argstr="-save_skullstrip"
    )
    suffix: str = shell.arg(
        help='append suffix to the original anat/epi dataset to usein the resulting dataset names (default is "_al")',
        argstr="-suffix {suffix}",
        default="_al",
    )
    epi_strip: ty.Any = shell.arg(
        help="method to mask brain in EPI datashould be one of[3dSkullStrip]/3dAutomask/None)",
        argstr="-epi_strip {epi_strip}",
    )
    volreg: ty.Any = shell.arg(
        help="do volume registration on EPI dataset before alignmentshould be 'on' or 'off', defaults to 'on'",
        argstr="-volreg {volreg}",
        default="on",
    )
    tshift: ty.Any = shell.arg(
        help="do time shifting of EPI dataset before alignmentshould be 'on' or 'off', defaults to 'on'",
        argstr="-tshift {tshift}",
        default="on",
    )
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")
    py27_path: ty.Any = shell.arg(help="", default="python2")

    class Outputs(shell.Outputs):
        anat_al_orig: File | None = shell.out(
            help="A version of the anatomy that is aligned to the EPI",
            callable=anat_al_orig_callable,
        )
        epi_al_orig: File | None = shell.out(
            help="A version of the EPI dataset aligned to the anatomy",
            callable=epi_al_orig_callable,
        )
        epi_tlrc_al: File | None = shell.out(
            help="A version of the EPI dataset aligned to a standard template",
            callable=epi_tlrc_al_callable,
        )
        anat_al_mat: File | None = shell.out(
            help="matrix to align anatomy to the EPI", callable=anat_al_mat_callable
        )
        epi_al_mat: File | None = shell.out(
            help="matrix to align EPI to anatomy", callable=epi_al_mat_callable
        )
        epi_vr_al_mat: File | None = shell.out(
            help="matrix to volume register EPI", callable=epi_vr_al_mat_callable
        )
        epi_reg_al_mat: File | None = shell.out(
            help="matrix to volume register and align epi to anatomy",
            callable=epi_reg_al_mat_callable,
        )
        epi_al_tlrc_mat: File | None = shell.out(
            help="matrix to volume register and align epito anatomy and put into standard space",
            callable=epi_al_tlrc_mat_callable,
        )
        epi_vr_motion: File | None = shell.out(
            help="motion parameters from EPI time-seriesregistration (tsh included in name if slicetiming correction is also included).",
            callable=epi_vr_motion_callable,
        )
        skullstrip: File | None = shell.out(
            help="skull-stripped (not aligned) volume", callable=skullstrip_callable
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
        msg = "Unable to generate filename for command %s. " % "align_epi_anat.py"
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
