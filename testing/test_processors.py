from pytest import MonkeyPatch
from pytest_mock import MockerFixture
from sunset import Key

from spyrit.network.fragments import (
    ANSIFragment,
    ByteFragment,
    Fragment,
    TextFragment,
)
from spyrit.network.processors import (
    ANSIProcessor,
    BaseProcessor,
    ChainProcessor,
    UnicodeProcessor,
)
from spyrit.settings.spyrit_settings import Encoding
from spyrit.ui.colors import ANSIColor, AnsiColorCodes, NoColor, RGBColor
from spyrit.ui.format import CharFormat


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


class TestANSIProcessor:
    def test_no_ansi(self) -> None:
        processor = ANSIProcessor()
        output = OutputCatcher(processor)

        processor.feed(
            [ByteFragment(b"no ANSI codes here"), TextFragment("Nor here.")]
        )
        assert output.get() == [
            ByteFragment(b"no ANSI codes here"),
            TextFragment("Nor here."),
        ]

    def test_ansi_found_between_bytes(self) -> None:
        processor = ANSIProcessor()
        output = OutputCatcher(processor)

        # Note that 99999 is not a valid SGR code, so the resulting format is
        # empty.

        processor.feed([ByteFragment(b"BEFORE\033[99999mAFTER\033[99999mEND")])
        assert output.get() == [
            ByteFragment(b"BEFORE"),
            ANSIFragment(CharFormat()),
            ByteFragment(b"AFTER"),
            ANSIFragment(CharFormat()),
            ByteFragment(b"END"),
        ]

    def test_ansi_reconstructed_from_split_packets(self) -> None:
        processor = ANSIProcessor()
        output = OutputCatcher(processor)

        # Note that 99999 is not a valid SGR code, so the resulting format is
        # empty.

        processor.feed(
            [ByteFragment(b"BEFORE\033[99"), ByteFragment(b"999mAFTER")]
        )
        assert output.get() == [
            ByteFragment(b"BEFORE"),
            ANSIFragment(CharFormat()),
            ByteFragment(b"AFTER"),
        ]

    def test_ansi_reset(self) -> None:
        processor = ANSIProcessor()
        output = OutputCatcher(processor)

        reset_all = CharFormat(
            bold=False,
            italic=False,
            underline=False,
            reverse=False,
            strikeout=False,
            foreground=NoColor(),
            background=NoColor(),
        )

        processor.feed([ByteFragment(b"\033[m")])
        assert output.get() == [ANSIFragment(reset_all)]

        processor.feed([ByteFragment(b"\033[0m")])
        assert output.get() == [ANSIFragment(reset_all)]

    def test_ansi_sgr_sequences(self) -> None:
        processor = ANSIProcessor()
        output = OutputCatcher(processor)

        processor.feed([ByteFragment(b"\033[1m")])
        assert output.get() == [ANSIFragment(CharFormat(bold=True))]

        processor.feed([ByteFragment(b"\033[3m")])
        assert output.get() == [ANSIFragment(CharFormat(italic=True))]

        processor.feed([ByteFragment(b"\033[4m")])
        assert output.get() == [ANSIFragment(CharFormat(underline=True))]

        processor.feed([ByteFragment(b"\033[7m")])
        assert output.get() == [ANSIFragment(CharFormat(reverse=True))]

        processor.feed([ByteFragment(b"\033[9m")])
        assert output.get() == [ANSIFragment(CharFormat(strikeout=True))]

        processor.feed([ByteFragment(b"\033[21m")])
        assert output.get() == [ANSIFragment(CharFormat(bold=False))]

        processor.feed([ByteFragment(b"\033[22m")])
        assert output.get() == [ANSIFragment(CharFormat(bold=False))]

        processor.feed([ByteFragment(b"\033[23m")])
        assert output.get() == [ANSIFragment(CharFormat(italic=False))]

        processor.feed([ByteFragment(b"\033[24m")])
        assert output.get() == [ANSIFragment(CharFormat(underline=False))]

        processor.feed([ByteFragment(b"\033[27m")])
        assert output.get() == [ANSIFragment(CharFormat(reverse=False))]

        processor.feed([ByteFragment(b"\033[29m")])
        assert output.get() == [ANSIFragment(CharFormat(strikeout=False))]

        processor.feed([ByteFragment(b"\033[30m")])
        assert output.get() == [
            ANSIFragment(CharFormat(foreground=ANSIColor(AnsiColorCodes.Black)))
        ]

        processor.feed([ByteFragment(b"\033[31m")])
        assert output.get() == [
            ANSIFragment(CharFormat(foreground=ANSIColor(AnsiColorCodes.Red)))
        ]

        processor.feed([ByteFragment(b"\033[32m")])
        assert output.get() == [
            ANSIFragment(CharFormat(foreground=ANSIColor(AnsiColorCodes.Green)))
        ]

        processor.feed([ByteFragment(b"\033[33m")])
        assert output.get() == [
            ANSIFragment(
                CharFormat(foreground=ANSIColor(AnsiColorCodes.Yellow))
            )
        ]

        processor.feed([ByteFragment(b"\033[34m")])
        assert output.get() == [
            ANSIFragment(CharFormat(foreground=ANSIColor(AnsiColorCodes.Blue)))
        ]

        processor.feed([ByteFragment(b"\033[35m")])
        assert output.get() == [
            ANSIFragment(
                CharFormat(foreground=ANSIColor(AnsiColorCodes.Magenta))
            )
        ]

        processor.feed([ByteFragment(b"\033[36m")])
        assert output.get() == [
            ANSIFragment(CharFormat(foreground=ANSIColor(AnsiColorCodes.Cyan)))
        ]

        processor.feed([ByteFragment(b"\033[37m")])
        assert output.get() == [
            ANSIFragment(
                CharFormat(foreground=ANSIColor(AnsiColorCodes.LightGray))
            )
        ]

        processor.feed([ByteFragment(b"\033[38;5;42m")])
        assert output.get() == [
            ANSIFragment(CharFormat(foreground=ANSIColor(42)))
        ]

        processor.feed([ByteFragment(b"\033[38;2;55;66;77m")])
        assert output.get() == [
            ANSIFragment(CharFormat(foreground=RGBColor(55, 66, 77)))
        ]

        processor.feed([ByteFragment(b"\033[39m")])
        assert output.get() == [ANSIFragment(CharFormat(foreground=NoColor()))]

        processor.feed([ByteFragment(b"\033[40m")])
        assert output.get() == [
            ANSIFragment(CharFormat(background=ANSIColor(AnsiColorCodes.Black)))
        ]

        processor.feed([ByteFragment(b"\033[41m")])
        assert output.get() == [
            ANSIFragment(CharFormat(background=ANSIColor(AnsiColorCodes.Red)))
        ]

        processor.feed([ByteFragment(b"\033[42m")])
        assert output.get() == [
            ANSIFragment(CharFormat(background=ANSIColor(AnsiColorCodes.Green)))
        ]

        processor.feed([ByteFragment(b"\033[43m")])
        assert output.get() == [
            ANSIFragment(
                CharFormat(background=ANSIColor(AnsiColorCodes.Yellow))
            )
        ]

        processor.feed([ByteFragment(b"\033[44m")])
        assert output.get() == [
            ANSIFragment(CharFormat(background=ANSIColor(AnsiColorCodes.Blue)))
        ]

        processor.feed([ByteFragment(b"\033[45m")])
        assert output.get() == [
            ANSIFragment(
                CharFormat(background=ANSIColor(AnsiColorCodes.Magenta))
            )
        ]

        processor.feed([ByteFragment(b"\033[46m")])
        assert output.get() == [
            ANSIFragment(CharFormat(background=ANSIColor(AnsiColorCodes.Cyan)))
        ]

        processor.feed([ByteFragment(b"\033[47m")])
        assert output.get() == [
            ANSIFragment(
                CharFormat(background=ANSIColor(AnsiColorCodes.LightGray))
            )
        ]

        processor.feed([ByteFragment(b"\033[48;5;42m")])
        assert output.get() == [
            ANSIFragment(CharFormat(background=ANSIColor(42)))
        ]

        processor.feed([ByteFragment(b"\033[48;2;55;66;77m")])
        assert output.get() == [
            ANSIFragment(CharFormat(background=RGBColor(55, 66, 77)))
        ]

        processor.feed([ByteFragment(b"\033[49m")])
        assert output.get() == [ANSIFragment(CharFormat(background=NoColor()))]

    def test_compound_ansi_sequence(self) -> None:
        processor = ANSIProcessor()
        output = OutputCatcher(processor)

        processor.feed([ByteFragment(b"\033[1;4;27;31m")])
        assert output.get() == [
            ANSIFragment(
                CharFormat(
                    bold=True,
                    underline=True,
                    reverse=False,
                    foreground=ANSIColor(AnsiColorCodes.Red),
                )
            )
        ]

    def test_invalid_extended_color_sequence(self) -> None:
        processor = ANSIProcessor()
        output = OutputCatcher(processor)

        processor.feed([ByteFragment(b"\033[38m")])
        assert output.get() == [ANSIFragment(CharFormat())]

        processor.feed([ByteFragment(b"\033[38;99999m")])
        assert output.get() == [ANSIFragment(CharFormat())]

        processor.feed([ByteFragment(b"\033[48m")])
        assert output.get() == [ANSIFragment(CharFormat())]

        processor.feed([ByteFragment(b"\033[48;99999m")])
        assert output.get() == [ANSIFragment(CharFormat())]


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
