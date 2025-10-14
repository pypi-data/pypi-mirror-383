# Auto-generated test for mrcheckerboardmask

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.vendor.mrtrix3.medimage import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrCheckerboardmask


@pytest.mark.xfail
def test_mrcheckerboardmask(tmp_path, cli_parse_only):

    task = MrCheckerboardmask(
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        invert=False,
        nan=False,
        tiles=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
