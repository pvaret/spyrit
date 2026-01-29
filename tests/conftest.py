import gzip
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

from spyrit.resources.resources import Resource


class MockResource(Resource):
    # We want to expose a type that works like Resource types, but is filled out
    # dynamically by the fixture below. Enums make that prodigiously painful due to
    # their weird typing. So we just cheat by describing the type, and cast the
    # dynamically created resource enum in the fixture to that, and call it a day.
    TEXT_TXT = ""
    TEXT_TXT_GZ = ""


@pytest.fixture
def make_text_resource(tmp_path: Path) -> Callable[[str], type[MockResource]]:
    def _make_text_resource(text: str) -> type[MockResource]:
        text_txt_path = tmp_path / "text.txt"
        text_txt_path.write_text(text)

        text_txt_gz_path = tmp_path / "text.txt.gz"
        text_txt_gz_path.write_bytes(gzip.compress(text.encode()))

        class DummyResource(Resource):
            TEXT_TXT = text_txt_path.as_posix()
            TEXT_TXT_GZ = text_txt_gz_path.as_posix()

        return cast(type[MockResource], DummyResource)

    return _make_text_resource
