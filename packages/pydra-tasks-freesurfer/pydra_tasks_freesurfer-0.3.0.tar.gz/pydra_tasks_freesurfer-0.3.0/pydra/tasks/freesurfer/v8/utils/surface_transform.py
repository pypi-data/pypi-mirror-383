import attrs
from fileformats.generic import Directory, File
import logging
from pydra.tasks.freesurfer.v8.nipype_ports.utils.filemanip import (
    fname_presuffix,
    split_filename,
)
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "target_type":
        if inputs["out_file"] is not attrs.NOTHING:
            _, base, ext = split_filename(
                _list_outputs(
                    out_file=inputs["out_file"],
                    source_annot_file=inputs["source_annot_file"],
                    source_file=inputs["source_file"],
                    target_subject=inputs["target_subject"],
                    target_type=inputs["target_type"],
                )["out_file"]
            )
            if ext != filemap[value]:
                if ext in filemap.values():
                    raise ValueError(
                        "Cannot create {} file with extension " "{}".format(value, ext)
                    )
                else:
                    logger.warning(
                        "Creating %s file with extension %s: %s%s",
                        value,
                        ext,
                        base,
                        ext,
                    )
        if value in implicit_filetypes:
            return ""

    return argstr.format(**inputs)


def target_type_formatter(field, inputs):
    return _format_arg("target_type", field, inputs, argstr="--tfmt {target_type}")


def _gen_filename(name, inputs):
    if name == "out_file":
        return _list_outputs(
            out_file=inputs["out_file"],
            source_annot_file=inputs["source_annot_file"],
            source_file=inputs["source_file"],
            target_subject=inputs["target_subject"],
            target_type=inputs["target_type"],
        )[name]
    return None


def out_file_default(inputs):
    return _gen_filename("out_file", inputs=inputs)


@shell.define(xor=[["source_annot_file", "source_file"]])
class SurfaceTransform(shell.Task["SurfaceTransform.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import Directory, File
    >>> from pathlib import Path
    >>> from pydra.tasks.freesurfer.v8.utils.surface_transform import SurfaceTransform

    """

    executable = "mri_surf2surf"

    source_file: ty.Any | None = shell.arg(
        help="surface file with source values",
        argstr="--sval {source_file}",
        default=False,
    )
    source_annot_file: ty.Any | None = shell.arg(
        help="surface annotation file",
        argstr="--sval-annot {source_annot_file}",
        default=False,
    )
    source_subject: ty.Any = shell.arg(
        help="subject id for source surface",
        argstr="--srcsubject {source_subject}",
        default=False,
    )
    hemi: ty.Any = shell.arg(
        help="hemisphere to transform",
        argstr="--hemi {hemi}",
    )
    target_subject: ty.Any = shell.arg(
        help="subject id of target surface",
        argstr="--trgsubject {target_subject}",
    )
    target_ico_order: ty.Any | None = shell.arg(
        help="order of the icosahedron if target_subject is 'ico'",
        argstr="--trgicoorder {target_ico_order}",
        default=False,
    )
    source_type: ty.Any | None = shell.arg(
        help="source file format",
        argstr="--sfmt {source_type}",
        requires=["source_file"],
        default=False,
    )
    target_type: ty.Any | None = shell.arg(
        help="output format",
        formatter=target_type_formatter,
        default=False,
    )
    reshape: bool | None = shell.arg(
        help="reshape output surface to conform with Nifti",
        argstr="--reshape",
        default=False,
    )
    reshape_factor: int | None = shell.arg(
        help="number of slices in reshaped image",
        argstr="--reshape-factor",
        default=False,
    )
    subjects_dir: ty.Any | None = shell.arg(
        help="subjects directory",
        default=False,
    )

    class Outputs(shell.Outputs):
        out_file: File = shell.outarg(
            help="surface file to write",
            argstr="--tval {out_file}",
            path_template="out_file",
        )


def _list_outputs(
    out_file=None,
    source_annot_file=None,
    source_file=None,
    target_subject=None,
    target_type=None,
):
    outputs = {}
    outputs["out_file"] = out_file
    if outputs["out_file"] is attrs.NOTHING:
        if source_file is not attrs.NOTHING:
            source = source_file
        else:
            source = source_annot_file

        bad_extensions = [
            ".%s" % e
            for e in [
                "area",
                "mid",
                "pial",
                "avg_curv",
                "curv",
                "inflated",
                "jacobian_white",
                "orig",
                "nofix",
                "smoothwm",
                "crv",
                "sphere",
                "sulc",
                "thickness",
                "volume",
                "white",
            ]
        ]
        use_ext = True
        if split_filename(source)[2] in bad_extensions:
            source = source + ".stripme"
            use_ext = False
        ext = ""
        if target_type is not attrs.NOTHING:
            ext = "." + filemap[target_type]
            use_ext = False
        outputs["out_file"] = fname_presuffix(
            source,
            suffix=f".{target_subject}{ext}",
            newpath=output_dir,
            use_ext=use_ext,
        )
    else:
        outputs["out_file"] = os.path.abspath(out_file)
    return outputs


filemap = dict(
    cor="cor",
    mgh="mgh",
    mgz="mgz",
    minc="mnc",
    afni="brik",
    brik="brik",
    bshort="bshort",
    spm="img",
    analyze="img",
    analyze4d="img",
    bfloat="bfloat",
    nifti1="img",
    nii="nii",
    niigz="nii.gz",
    gii="gii",
)

implicit_filetypes = ["gii"]

logger = logging.getLogger("nipype.interface")
