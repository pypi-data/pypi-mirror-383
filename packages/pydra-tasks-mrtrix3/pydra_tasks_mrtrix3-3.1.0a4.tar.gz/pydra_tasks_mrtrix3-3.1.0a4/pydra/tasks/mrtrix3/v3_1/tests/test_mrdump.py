# Auto-generated test for mrdump

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.vendor.mrtrix3.medimage import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrDump


@pytest.mark.xfail
def test_mrdump(tmp_path, cli_parse_only):

    task = MrDump(
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        mask=None,
        out_file=None,
    )
    result = task(worker="debug")
    assert not result.errored
