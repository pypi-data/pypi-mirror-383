from fileformats.core import from_mime
from fileformats.vendor.mrtrix3.medimage import ImageFormatGz as MifGz


def test_mif_gz_mime_roundtrip():
    assert MifGz is from_mime(MifGz.mime_type)


def test_mif_gz_mime_like_roundtrip():
    assert MifGz is from_mime(MifGz.mime_like)
