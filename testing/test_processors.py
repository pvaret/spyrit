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


class OutputCatcher:
    processor: BaseProcessor
    buffer: list[Fragment]

    def __init__(self, processor: BaseProcessor) -> None:
        self.processor = processor
        self.buffer = []
        self.processor.fragmentsReady.connect(self.buffer.extend)

    def get(self) -> list[Fragment]:
        ret = self.buffer[:]
        self.buffer.clear()
        return ret


class TestUnicodeProcessor:
    def test_process_ascii(self) -> None:
        processor = UnicodeProcessor(Key(Encoding.ASCII))
        output = OutputCatcher(processor)

        processor.feed([ByteFragment(b"abcde")])
        assert output.get() == [TextFragment("abcde")]

        processor.feed([ByteFragment(b"non-ascii bytes\xf0 are skipped")])
        assert output.get() == [TextFragment("non-ascii bytes are skipped")]

        # If all bytes would be stripped from a byte fragment, the output
        # should be empty.

        processor.feed([ByteFragment(b"\xa9")])
        assert output.get() == []

    def test_incomplete_utf8(self) -> None:
        processor = UnicodeProcessor(Key(Encoding.UTF8))
        output = OutputCatcher(processor)

        # 'é' in UTF-8 is encoded as \xc3\xa9. Check that we decode it
        # correctly if it arrives in split fragments.

        processor.feed([ByteFragment(b"abcde\xc3")])
        assert output.get() == [TextFragment("abcde")]

        processor.feed([ByteFragment(b"\xa9")])
        assert output.get() == [TextFragment("é")]

    def test_encoding_change(self) -> None:
        key = Key(Encoding.ASCII)
        processor = UnicodeProcessor(key)
        output = OutputCatcher(processor)

        processor.feed([ByteFragment(b"test\xc3\xa9")])
        assert output.get() == [TextFragment("test")]

        key.set(Encoding.UTF8)
        processor.feed([ByteFragment(b"test\xc3\xa9")])
        assert output.get() == [TextFragment("testé")]


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

        output_p1 = OutputCatcher(p1)

        p1.feed([TextFragment("dummy")])

        assert output_p1.get() == [TextFragment("dummy")]
        p1.feed.assert_called_once()  # type: ignore
        p1.feed.reset_mock()  # type: ignore

        processor = ChainProcessor(p1, p2, p3)
        output = OutputCatcher(processor)

        processor.feed([TextFragment("dummy")])

        p1.feed.assert_called_once()  # type: ignore
        p2.feed.assert_called_once()  # type: ignore
        p3.feed.assert_called_once()  # type: ignore
        assert output.get() == [TextFragment("dummy")]
