from typing import Iterable

from pytest import MonkeyPatch
from pytest_mock import MockerFixture
from sunset import Key

from spyrit.network.fragments import ByteFragment, Fragment, TextFragment
from spyrit.network.processors import (
    BaseProcessor,
    ChainProcessor,
    UnicodeProcessor,
)
from spyrit.settings.spyrit_settings import Encoding


def _to_str_list(it: Iterable[Fragment]) -> list[str]:
    ret: list[str] = []

    for fragment in it:
        assert isinstance(
            fragment, TextFragment
        ), f"{fragment} is of unexpected type {type(fragment)}"
        ret.append(fragment.text)

    return ret


class TestUnicodeProcessor:
    def test_process_ascii(self) -> None:
        output: list[Fragment] = []
        processor = UnicodeProcessor(Key(Encoding.ASCII))
        processor.fragmentsReady.connect(output.extend)

        processor.feed([ByteFragment(b"abcde")])
        assert _to_str_list(output) == ["abcde"]
        output.clear()

        processor.feed([ByteFragment(b"non-ascii bytes\xf0 are skipped")])
        assert _to_str_list(output) == ["non-ascii bytes are skipped"]
        output.clear()

        # If all bytes would be stripped from a byte fragment, the output
        # should be empty.

        processor.feed([ByteFragment(b"\xa9")])
        assert _to_str_list(output) == []

    def test_incomplete_utf8(self) -> None:
        processor = UnicodeProcessor(Key(Encoding.UTF8))
        output: list[Fragment] = []
        processor.fragmentsReady.connect(output.extend)

        # 'é' in UTF-8 is encoded as \xc3\xa9. Check that we decode it
        # correctly if it arrives in split fragments.

        processor.feed([ByteFragment(b"abcde\xc3")])
        assert _to_str_list(output) == ["abcde"]
        output.clear()

        processor.feed([ByteFragment(b"\xa9")])
        assert _to_str_list(output) == ["é"]

    def test_encoding_change(self) -> None:
        key = Key(Encoding.ASCII)
        processor = UnicodeProcessor(key)

        output: list[Fragment] = []
        processor.fragmentsReady.connect(output.extend)

        processor.feed([ByteFragment(b"test\xc3\xa9")])
        assert _to_str_list(output) == ["test"]
        output.clear()

        key.set(Encoding.UTF8)
        processor.feed([ByteFragment(b"test\xc3\xa9")])
        assert _to_str_list(output) == ["testé"]


class TestChainProcessor:
    def test_chain_processor(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch
    ) -> None:
        p1 = BaseProcessor()
        p2 = BaseProcessor()
        p3 = BaseProcessor()

        monkeypatch.setattr(p1, "feed", mocker.Mock(wraps=p1.feed))
        monkeypatch.setattr(p2, "feed", mocker.Mock(wraps=p2.feed))
        monkeypatch.setattr(p3, "feed", mocker.Mock(wraps=p3.feed))

        p1_output: list[Fragment] = []
        p1.fragmentsReady.connect(p1_output.extend)

        p1.feed([TextFragment("dummy")])

        assert _to_str_list(p1_output) == ["dummy"]
        p1.feed.assert_called_once()  # type: ignore
        p1.feed.reset_mock()  # type: ignore

        processor = ChainProcessor(p1, p2, p3)
        output: list[Fragment] = []
        processor.fragmentsReady.connect(output.extend)

        processor.feed([TextFragment("dummy")])

        p1.feed.assert_called_once()  # type: ignore
        p2.feed.assert_called_once()  # type: ignore
        p3.feed.assert_called_once()  # type: ignore
        assert _to_str_list(output) == ["dummy"]
