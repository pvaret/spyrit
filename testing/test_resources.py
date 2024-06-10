import base64

from io import BytesIO

import pytest

from PySide6.QtCore import QFile

from spyrit.resources.file import ResourceFile, ZlibIOWrapper
from spyrit.resources.loader import load
from spyrit.resources.resources import Misc, RESOURCES


def example_compressed_buffer() -> BytesIO:
    # This is the contents of Misc.TEST_TXT, compressed with gzip.
    data = b"H4sICJI0ZGYAA3Rlc3QudHh0AAvI1w1x9NAtyecKALEigSwAnojChBMAAAA="
    return BytesIO(base64.decodebytes(data))


class TestResources:
    def test_resources_load(self) -> None:
        assert load()

    def test_all_resources_present(self) -> None:
        for resource_type in RESOURCES:
            for filename in resource_type:
                assert QFile(filename).exists()

    def test_resource_file(self) -> None:
        f = ResourceFile(Misc.TEST_TXT)
        assert f.readable()
        assert f.readall() == b"Po-TAH-to\nPo-TAY-to"

        f = ResourceFile(Misc.TEST_TXT)
        assert f.readlines() == [b"Po-TAH-to\n", b"Po-TAY-to"]

        f = ResourceFile(Misc.TEST_TXT)
        assert f.read(10) == b"Po-TAH-to\n"
        assert f.readall() == b"Po-TAY-to"

        assert f.read(1) == b""

        f.close()
        assert f.closed

        with pytest.raises(ValueError):
            f.read(1)

    def test_resource_file_readonly_nonseekable(self) -> None:
        f = ResourceFile(Misc.TEST_TXT)
        f.read(1)

        assert not f.seekable()
        with pytest.raises(ValueError):
            f.tell()

        with pytest.raises(ValueError):
            f.seek(0)

        assert not f.writable()
        with pytest.raises(NotImplementedError):
            f.write(b"xxx")

        with pytest.raises(OSError):
            f.fileno()

        assert not f.isatty()

    def test_zlib_io_wrapper(self) -> None:
        f = ZlibIOWrapper(example_compressed_buffer())
        assert f.read() == b"Po-TAH-to\nPo-TAY-to"
        assert f.read() == b""

        f = ZlibIOWrapper(example_compressed_buffer())
        assert f.read(1) == b"P"
        assert f.read(1) == b"o"
        assert f.read(1) == b"-"
        assert f.read(3) == b"TAH"

        f = ZlibIOWrapper(example_compressed_buffer())
        assert f.readlines() == [b"Po-TAH-to\n", b"Po-TAY-to"]

        f = ZlibIOWrapper(example_compressed_buffer())
        f.close()
        with pytest.raises(ValueError):
            f.read()