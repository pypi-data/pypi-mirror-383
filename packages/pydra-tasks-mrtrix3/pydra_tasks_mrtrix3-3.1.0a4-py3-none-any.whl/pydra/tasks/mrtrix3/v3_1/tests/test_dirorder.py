# Auto-generated test for dirorder

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.vendor.mrtrix3.medimage import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DirOrder


@pytest.mark.xfail
def test_dirorder(tmp_path, cli_parse_only):

    task = DirOrder(
        cartesian=False,
        debug=False,
        force=False,
        in_file=File.sample(),
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
