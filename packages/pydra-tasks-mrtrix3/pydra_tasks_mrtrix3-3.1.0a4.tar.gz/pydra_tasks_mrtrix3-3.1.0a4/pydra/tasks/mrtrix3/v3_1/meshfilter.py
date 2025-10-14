# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.vendor.mrtrix3.medimage import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class MeshFilter(shell.Task["MeshFilter.Outputs"]):
    """While this command has only one filter operation currently available, it nevertheless presents with a comparable interface to the MRtrix3 commands maskfilter and mrfilter


        Example usages
        --------------


        Apply a mesh smoothing filter (currently the only filter available):

        `$ meshfilter input.vtk smooth output.vtk`

        The usage of this command may cause confusion due to the generic interface despite only one filtering operation being currently available. This simple example usage is therefore provided for clarity.


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: Robert E. Smith (robert.smith@florey.edu.au)

        Copyright: Copyright (c) 2008-2025 the MRtrix3 contributors.

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Covered Software is provided under this License on an "as is"
    basis, without warranty of any kind, either expressed, implied, or
    statutory, including, without limitation, warranties that the
    Covered Software is free of defects, merchantable, fit for a
    particular purpose or non-infringing.
    See the Mozilla Public License v. 2.0 for more details.

    For more details, see http://www.mrtrix.org/.
    """

    executable = "meshfilter"

    # Arguments
    in_file: File = shell.arg(
        argstr="",
        position=1,
        help="""the input mesh file""",
    )
    filter: str = shell.arg(
        argstr="",
        position=2,
        help="""the filter to apply; options are: smooth""",
        allowed_values=["smooth"],
    )

    # Options

    # Options for mesh smoothing filter:
    smooth_spatial: float | None = shell.arg(
        default=None,
        argstr="-smooth_spatial",
        help="""spatial extent of smoothing (default: 10mm)""",
    )
    smooth_influence: float | None = shell.arg(
        default=None,
        argstr="-smooth_influence",
        help="""influence factor for smoothing (default: 10)""",
    )

    # Standard options
    info: bool = shell.arg(
        default=False,
        argstr="-info",
        help="""display information messages.""",
    )
    quiet: bool = shell.arg(
        default=False,
        argstr="-quiet",
        help="""do not display information messages or progress status; alternatively, this can be achieved by setting the MRTRIX_QUIET environment variable to a non-empty string.""",
    )
    debug: bool = shell.arg(
        default=False,
        argstr="-debug",
        help="""display debugging messages.""",
    )
    force: bool = shell.arg(
        default=False,
        argstr="-force",
        help="""force overwrite of output files (caution: using the same file as input and output might cause unexpected behaviour).""",
    )
    nthreads: int | None = shell.arg(
        default=None,
        argstr="-nthreads",
        help="""use this number of threads in multi-threaded applications (set to 0 to disable multi-threading).""",
    )
    config: MultiInputObj[tuple[str, str]] | None = shell.arg(
        default=None,
        argstr="-config",
        help="""temporarily set the value of an MRtrix config file entry.""",
        sep=" ",
    )

    class Outputs(shell.Outputs):
        out_file: File = shell.outarg(
            argstr="",
            position=3,
            path_template="out_file.txt",
            help="""the output mesh file""",
        )
