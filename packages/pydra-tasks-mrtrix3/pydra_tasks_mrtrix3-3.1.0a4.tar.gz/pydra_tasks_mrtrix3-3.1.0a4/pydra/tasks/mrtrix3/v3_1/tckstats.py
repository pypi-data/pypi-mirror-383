# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.vendor.mrtrix3.medimage import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class TckStats(shell.Task["TckStats.Outputs"]):
    """
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

    executable = "tckstats"

    # Arguments
    tracks_in: Tracks = shell.arg(
        argstr="",
        position=1,
        help="""the input track file""",
    )

    # Options
    output: MultiInputObj[str] | None = shell.arg(
        default=None,
        argstr="-output",
        help="""output only the field specified. Multiple such options can be supplied if required. Choices are: mean, median, std, min, max, count. Useful for use in scripts.""",
        allowed_values=["mean", "median", "std", "min", "max", "count"],
    )
    ignorezero: bool = shell.arg(
        default=False,
        argstr="-ignorezero",
        help="""do not generate a warning if the track file contains streamlines with zero length""",
    )
    tck_weights_in: File | None = shell.arg(
        default=None,
        argstr="-tck_weights_in",
        help="""specify a text scalar file containing the streamline weights""",
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
        histogram: File | bool | None = shell.outarg(
            default=None,
            argstr="-histogram",
            path_template="histogram.txt",
            help="""output a histogram of streamline lengths""",
        )
        dump: File | bool | None = shell.outarg(
            default=None,
            argstr="-dump",
            path_template="dump.txt",
            help="""dump the streamlines lengths to a text file""",
        )
