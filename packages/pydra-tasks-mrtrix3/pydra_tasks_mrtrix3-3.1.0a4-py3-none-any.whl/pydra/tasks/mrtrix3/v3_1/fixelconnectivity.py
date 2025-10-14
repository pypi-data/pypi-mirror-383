# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.vendor.mrtrix3.medimage import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class FixelConnectivity(shell.Task["FixelConnectivity.Outputs"]):
    """This command will generate a directory containing three images, which encodes the fixel-fixel connectivity matrix. Documentation regarding this format and how to use it will come in the future.

        Fixel data are stored utilising the fixel directory format described in the main documentation, which can be found at the following link:
    https://mrtrix.readthedocs.io/en/3.0.4/fixel_based_analysis/fixel_directory_format.html


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

    executable = "fixelconnectivity"

    # Arguments
    fixel_directory: Directory = shell.arg(
        argstr="",
        position=1,
        help="""the directory containing the fixels between which connectivity will be quantified""",
    )
    tracks: Tracks = shell.arg(
        argstr="",
        position=2,
        help="""the tracks used to determine fixel-fixel connectivity""",
    )

    # Options

    # Options that influence generation of the connectivity matrix / matrices:
    threshold: float | None = shell.arg(
        default=None,
        argstr="-threshold",
        help="""a threshold to define the required fraction of shared connections to be included in the neighbourhood (default: 0.01)""",
    )
    angle: float | None = shell.arg(
        default=None,
        argstr="-angle",
        help="""the max angle threshold for assigning streamline tangents to fixels (Default: 45 degrees)""",
    )
    mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask",
        help="""provide a fixel data file containing a mask of those fixels to be computed; fixels outside the mask will be empty in the output matrix""",
    )
    tck_weights_in: File | None = shell.arg(
        default=None,
        argstr="-tck_weights_in",
        help="""specify a text scalar file containing the streamline weights""",
    )

    # Options for additional outputs to be generated:

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
        matrix: Directory = shell.outarg(
            argstr="",
            position=3,
            path_template="matrix",
            help="""the output fixel-fixel connectivity matrix directory path""",
        )
        count: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-count",
            path_template="count.mif",
            help="""export a fixel data file encoding the number of connections for each fixel""",
        )
        extent: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-extent",
            path_template="extent.mif",
            help="""export a fixel data file encoding the extent of connectivity (sum of weights) for each fixel""",
        )
