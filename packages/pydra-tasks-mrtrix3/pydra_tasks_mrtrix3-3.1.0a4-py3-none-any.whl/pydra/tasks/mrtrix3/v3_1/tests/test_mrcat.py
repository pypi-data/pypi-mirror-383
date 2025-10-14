# Auto-generated test for mrcat

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.vendor.mrtrix3.medimage import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrCat


@pytest.mark.xfail
def test_mrcat(tmp_path, cli_parse_only):

    task = MrCat(
        axis=None,
        datatype=None,
        debug=False,
        force=False,
        inputs=[Nifti1.sample()],
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
