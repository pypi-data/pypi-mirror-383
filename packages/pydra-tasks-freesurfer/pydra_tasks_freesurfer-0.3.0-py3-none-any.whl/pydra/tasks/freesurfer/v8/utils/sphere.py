from fileformats.generic import Directory, File
from fileformats.vendor.freesurfer.medimage import Pial
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell


logger = logging.getLogger(__name__)


@shell.define
class Sphere(shell.Task["Sphere.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import Directory, File
    >>> from fileformats.vendor.freesurfer.medimage import Pial
    >>> from pathlib import Path
    >>> from pydra.tasks.freesurfer.v8.utils.sphere import Sphere

    >>> task = Sphere()
    >>> task.in_file = Pial.mock("lh.pial")
    >>> task.in_smoothwm = File.mock()
    >>> task.subjects_dir = Directory.mock()
    >>> task.cmdline
    'None'


    """

    executable = "mris_sphere"
    in_file: Pial = shell.arg(
        help="Input file for Sphere",
        argstr="{in_file}",
        position=-2,
        copy_mode="File.CopyMode.copy",
    )
    seed: int = shell.arg(
        help="Seed for setting random number generator", argstr="-seed {seed}"
    )
    magic: bool = shell.arg(
        help="No documentation. Direct questions to analysis-bugs@nmr.mgh.harvard.edu",
        argstr="-q",
    )
    in_smoothwm: File = shell.arg(
        help="Input surface required when -q flag is not selected",
        copy_mode="File.CopyMode.copy",
    )
    num_threads: int = shell.arg(help="allows for specifying more threads")
    subjects_dir: Directory = shell.arg(help="subjects directory")

    class Outputs(shell.Outputs):
        out_file: Path = shell.outarg(
            help="Output file for Sphere",
            argstr="{out_file}",
            position=-1,
            path_template="{in_file}.sphere",
        )
