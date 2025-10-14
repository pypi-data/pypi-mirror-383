import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.afni.v25.nipype_ports.utils.filemanip import fname_presuffix
import os
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    ext = ".HEAD"
    outputs["out_file"] = os.path.abspath(
        _gen_fname(
            inputs["in_file"],
            suffix="+tlrc",
            outputtype=inputs["outputtype"],
            inputs=inputs["inputs"],
            stdout=inputs["stdout"],
            stderr=inputs["stderr"],
            output_dir=inputs["output_dir"],
        )
        + ext
    )
    return outputs


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


@shell.define
class AutoTLRC(shell.Task["AutoTLRC.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pydra.tasks.afni.v25.preprocess.auto_tlrc import AutoTLRC

    >>> task = AutoTLRC()
    >>> task.inputs.in_file = Nifti1.mock("structural.nii")
    >>> task.inputs.base = "TT_N27+tlrc"
    >>> task.cmdline
    'None'


    """

    executable = "@auto_tlrc"
    outputtype: ty.Any = shell.arg(help="AFNI output filetype")
    in_file: Nifti1 = shell.arg(
        help="Original anatomical volume (+orig).The skull is removed by this scriptunless instructed otherwise (-no_ss).",
        argstr="-input {in_file}",
    )
    base: str = shell.arg(
        help="Reference anatomical volume.\nUsually this volume is in some standard space like\nTLRC or MNI space and with afni dataset view of\n(+tlrc).\nPreferably, this reference volume should have had\nthe skull removed but that is not mandatory.\nAFNI's distribution contains several templates.\nFor a longer list, use \"whereami -show_templates\"\nTT_N27+tlrc --> Single subject, skull stripped volume.\nThis volume is also known as\nN27_SurfVol_NoSkull+tlrc elsewhere in\nAFNI and SUMA land.\n(www.loni.ucla.edu, www.bic.mni.mcgill.ca)\nThis template has a full set of FreeSurfer\n(surfer.nmr.mgh.harvard.edu)\nsurface models that can be used in SUMA.\nFor details, see Talairach-related link:\nhttps://afni.nimh.nih.gov/afni/suma\nTT_icbm452+tlrc --> Average volume of 452 normal brains.\nSkull Stripped. (www.loni.ucla.edu)\nTT_avg152T1+tlrc --> Average volume of 152 normal brains.\nSkull Stripped.(www.bic.mni.mcgill.ca)\nTT_EPI+tlrc --> EPI template from spm2, masked as TT_avg152T1\nTT_avg152 and TT_EPI volume sources are from\nSPM's distribution. (www.fil.ion.ucl.ac.uk/spm/)\nIf you do not specify a path for the template, the script\nwill attempt to locate the template AFNI's binaries directory.\nNOTE: These datasets have been slightly modified from\ntheir original size to match the standard TLRC\ndimensions (Jean Talairach and Pierre Tournoux\nCo-Planar Stereotaxic Atlas of the Human Brain\nThieme Medical Publishers, New York, 1988).\nThat was done for internal consistency in AFNI.\nYou may use the original form of these\nvolumes if you choose but your TLRC coordinates\nwill not be consistent with AFNI's TLRC database\n(San Antonio Talairach Daemon database), for example.",
        argstr="-base {base}",
    )
    no_ss: bool = shell.arg(
        help="Do not strip skull of input data set\n(because skull has already been removed\nor because template still has the skull)\nNOTE: The ``-no_ss`` option is not all that optional.\nHere is a table of when you should and should not use ``-no_ss``\n\n  +------------------+------------+---------------+\n  | Dataset          | Template                   |\n  +==================+============+===============+\n  |                  | w/ skull   | wo/ skull     |\n  +------------------+------------+---------------+\n  | WITH skull       | ``-no_ss`` | xxx           |\n  +------------------+------------+---------------+\n  | WITHOUT skull    | No Cigar   | ``-no_ss``    |\n  +------------------+------------+---------------+\n\nTemplate means: Your template of choice\nDset. means: Your anatomical dataset\n``-no_ss`` means: Skull stripping should not be attempted on Dset\nxxx means: Don't put anything, the script will strip Dset\nNo Cigar means: Don't try that combination, it makes no sense.",
        argstr="-no_ss",
    )

    class Outputs(shell.Outputs):
        out_file: File | None = shell.out(
            help="output file", callable=out_file_callable
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
        msg = "Unable to generate filename for command %s. " % "@auto_tlrc"
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
