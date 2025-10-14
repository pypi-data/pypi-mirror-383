from fileformats.generic import Directory, File
from fileformats.vendor.freesurfer.medimage import Pial
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell


logger = logging.getLogger(__name__)


@shell.define
class Jacobian(shell.Task["Jacobian.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import Directory, File
    >>> from fileformats.vendor.freesurfer.medimage import Pial
    >>> from pathlib import Path
    >>> from pydra.tasks.freesurfer.v8.utils.jacobian import Jacobian

    >>> task = Jacobian()
    >>> task.in_origsurf = Pial.mock("lh.pial")
    >>> task.in_mappedsurf = File.mock()
    >>> task.subjects_dir = Directory.mock()
    >>> task.cmdline
    'None'


    """

    executable = "mris_jacobian"
    in_origsurf: Pial = shell.arg(
        help="Original surface", argstr="{in_origsurf}", position=-3
    )
    in_mappedsurf: File = shell.arg(
        help="Mapped surface", argstr="{in_mappedsurf}", position=-2
    )
    subjects_dir: Directory = shell.arg(help="subjects directory")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="Output Jacobian of the surface mapping",
            argstr="{out_file}",
            position=-1,
            path_template="{in_origsurf}.jacobian",
        )
