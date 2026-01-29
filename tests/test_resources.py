import re
from collections.abc import Callable

import pytest

from spyrit.resources.file import ResourceFile
from spyrit.resources.loader import load

from .conftest import MockResource


class TestResources:
    def test_resources_load(self) -> None:
        assert load()

    def test_resource_file(
        self, make_text_resource: Callable[[str], type[MockResource]]
    ) -> None:
        dummy_resource = make_text_resource("Po-TAH-to\nPo-TAY-to")

        f = ResourceFile(dummy_resource.TEXT_TXT)
        assert f.readable()
        assert f.readall() == b"Po-TAH-to\nPo-TAY-to"

        f = ResourceFile(dummy_resource.TEXT_TXT)
        assert f.readlines() == [b"Po-TAH-to\n", b"Po-TAY-to"]

        f = ResourceFile(dummy_resource.TEXT_TXT)
        assert f.read(10) == b"Po-TAH-to\n"
        assert f.readall() == b"Po-TAY-to"

        assert f.read(1) == b""

        f.close()
        assert f.closed

        with pytest.raises(
            ValueError,
            match=re.escape("File object is closed and cannot be read from."),
        ):
            f.read(1)

    def test_resource_file_readonly_nonseekable(
        self, make_text_resource: Callable[[str], type[MockResource]]
    ) -> None:
        dummy_resource = make_text_resource("Po-TAH-to\nPo-TAY-to")

        f = ResourceFile(dummy_resource.TEXT_TXT)
        f.read(1)

        assert not f.seekable()
        with pytest.raises(ValueError, match="seek"):
            f.tell()

        with pytest.raises(ValueError, match="seek"):
            f.seek(0)

        assert not f.writable()
        with pytest.raises(NotImplementedError):
            f.write(b"xxx")

        with pytest.raises(OSError, match="fileno"):
            f.fileno()

        assert not f.isatty()
