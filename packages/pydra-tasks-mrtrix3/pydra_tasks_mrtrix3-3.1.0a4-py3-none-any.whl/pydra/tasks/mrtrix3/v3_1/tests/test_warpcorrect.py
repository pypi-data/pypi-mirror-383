# Auto-generated test for warpcorrect

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.vendor.mrtrix3.medimage import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import WarpCorrect


@pytest.mark.xfail
def test_warpcorrect(tmp_path, cli_parse_only):

    task = WarpCorrect(
        debug=False,
        force=False,
        in_=Nifti1.sample(),
        marker=None,
        tolerance=None,
        out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
