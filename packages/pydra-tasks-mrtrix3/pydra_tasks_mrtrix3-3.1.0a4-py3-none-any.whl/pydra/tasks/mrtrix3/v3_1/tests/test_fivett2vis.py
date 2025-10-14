# Auto-generated test for fivett2vis

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.vendor.mrtrix3.medimage import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Fivett2Vis


@pytest.mark.xfail
def test_fivett2vis(tmp_path, cli_parse_only):

    task = Fivett2Vis(
        bg=None,
        cgm=None,
        csf=None,
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        path=None,
        sgm=None,
        wm=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
