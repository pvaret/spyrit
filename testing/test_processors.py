from pytest import MonkeyPatch
from pytest_mock import MockerFixture
from sunset import Key, List, Settings

from spyrit.network.fragments import (
    ANSIFragment,
    ByteFragment,
    FlowControlCode,
    FlowControlFragment,
    Fragment,
    PatternMatchFragment,
    TextFragment,
)
from spyrit.network.processors import (
    ANSIProcessor,
    BaseProcessor,
    ChainProcessor,
    UnicodeProcessor,
    UserPatternProcessor,
)
from spyrit.settings.spyrit_settings import (
    ANSIBoldEffect,
    Encoding,
    PatternScope,
    PatternType,
    SpyritSettings,
)
from spyrit.ui.colors import ANSIColor, ANSIColorCodes, NoColor, RGBColor
from spyrit.ui.format import FormatUpdate


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

    def test_all_encodings_are_valid(self) -> None:
        for encoding in Encoding:
            assert "x".encode(encoding) != b""


class TestANSIProcessor:
    def test_no_ansi(self) -> None:
        processor = ANSIProcessor(Key(default=ANSIBoldEffect.BOLD))
        output = OutputCatcher(processor)

        processor.feed(
            [ByteFragment(b"no ANSI codes here"), TextFragment("Nor here.")]
        )
        assert output.get() == [
            ByteFragment(b"no ANSI codes here"),
            TextFragment("Nor here."),
        ]

    def test_ansi_found_between_bytes(self) -> None:
        processor = ANSIProcessor(Key(default=ANSIBoldEffect.BOLD))
        output = OutputCatcher(processor)

        # Note that 99999 is not a valid SGR code, so the resulting format is
        # empty.

        processor.feed([ByteFragment(b"BEFORE\033[99999mAFTER\033[99999mEND")])
        assert output.get() == [
            ByteFragment(b"BEFORE"),
            ANSIFragment(FormatUpdate()),
            ByteFragment(b"AFTER"),
            ANSIFragment(FormatUpdate()),
            ByteFragment(b"END"),
        ]

    def test_ansi_reconstructed_from_split_packets(self) -> None:
        processor = ANSIProcessor(Key(default=ANSIBoldEffect.BOLD))
        output = OutputCatcher(processor)

        # Note that 99999 is not a valid SGR code, so the resulting format is
        # empty.

        processor.feed(
            [ByteFragment(b"BEFORE\033[99"), ByteFragment(b"999mAFTER")]
        )
        assert output.get() == [
            ByteFragment(b"BEFORE"),
            ANSIFragment(FormatUpdate()),
            ByteFragment(b"AFTER"),
        ]

    def test_ansi_reset(self) -> None:
        processor = ANSIProcessor(Key(default=ANSIBoldEffect.BOLD))
        output = OutputCatcher(processor)

        reset_all = FormatUpdate(
            bold=False,
            bright=False,
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
        bold_effect = Key(default=ANSIBoldEffect.BOLD)
        processor = ANSIProcessor(bold_effect)
        output = OutputCatcher(processor)

        processor.feed([ByteFragment(b"\033[1m")])
        assert output.get() == [ANSIFragment(FormatUpdate(bold=True))]

        bold_effect.set(ANSIBoldEffect.BRIGHT)
        processor.feed([ByteFragment(b"\033[1m")])
        assert output.get() == [ANSIFragment(FormatUpdate(bright=True))]

        bold_effect.set(ANSIBoldEffect.BOTH)
        processor.feed([ByteFragment(b"\033[1m")])
        assert output.get() == [
            ANSIFragment(FormatUpdate(bold=True, bright=True))
        ]

        processor.feed([ByteFragment(b"\033[3m")])
        assert output.get() == [ANSIFragment(FormatUpdate(italic=True))]

        processor.feed([ByteFragment(b"\033[4m")])
        assert output.get() == [ANSIFragment(FormatUpdate(underline=True))]

        processor.feed([ByteFragment(b"\033[7m")])
        assert output.get() == [ANSIFragment(FormatUpdate(reverse=True))]

        processor.feed([ByteFragment(b"\033[9m")])
        assert output.get() == [ANSIFragment(FormatUpdate(strikeout=True))]

        processor.feed([ByteFragment(b"\033[21m")])
        assert output.get() == [
            ANSIFragment(FormatUpdate(bold=False, bright=False))
        ]

        processor.feed([ByteFragment(b"\033[22m")])
        assert output.get() == [
            ANSIFragment(FormatUpdate(bold=False, bright=False))
        ]

        processor.feed([ByteFragment(b"\033[23m")])
        assert output.get() == [ANSIFragment(FormatUpdate(italic=False))]

        processor.feed([ByteFragment(b"\033[24m")])
        assert output.get() == [ANSIFragment(FormatUpdate(underline=False))]

        processor.feed([ByteFragment(b"\033[27m")])
        assert output.get() == [ANSIFragment(FormatUpdate(reverse=False))]

        processor.feed([ByteFragment(b"\033[29m")])
        assert output.get() == [ANSIFragment(FormatUpdate(strikeout=False))]

        processor.feed([ByteFragment(b"\033[30m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(foreground=ANSIColor(ANSIColorCodes.Black))
            )
        ]

        processor.feed([ByteFragment(b"\033[31m")])
        assert output.get() == [
            ANSIFragment(FormatUpdate(foreground=ANSIColor(ANSIColorCodes.Red)))
        ]

        processor.feed([ByteFragment(b"\033[32m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(foreground=ANSIColor(ANSIColorCodes.Green))
            )
        ]

        processor.feed([ByteFragment(b"\033[33m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(foreground=ANSIColor(ANSIColorCodes.Yellow))
            )
        ]

        processor.feed([ByteFragment(b"\033[34m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(foreground=ANSIColor(ANSIColorCodes.Blue))
            )
        ]

        processor.feed([ByteFragment(b"\033[35m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(foreground=ANSIColor(ANSIColorCodes.Magenta))
            )
        ]

        processor.feed([ByteFragment(b"\033[36m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(foreground=ANSIColor(ANSIColorCodes.Cyan))
            )
        ]

        processor.feed([ByteFragment(b"\033[37m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(foreground=ANSIColor(ANSIColorCodes.LightGray))
            )
        ]

        processor.feed([ByteFragment(b"\033[38;5;42m")])
        assert output.get() == [
            ANSIFragment(FormatUpdate(foreground=ANSIColor(42)))
        ]

        processor.feed([ByteFragment(b"\033[38;2;55;66;77m")])
        assert output.get() == [
            ANSIFragment(FormatUpdate(foreground=RGBColor(55, 66, 77)))
        ]

        processor.feed([ByteFragment(b"\033[39m")])
        assert output.get() == [
            ANSIFragment(FormatUpdate(foreground=NoColor()))
        ]

        processor.feed([ByteFragment(b"\033[40m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(background=ANSIColor(ANSIColorCodes.Black))
            )
        ]

        processor.feed([ByteFragment(b"\033[41m")])
        assert output.get() == [
            ANSIFragment(FormatUpdate(background=ANSIColor(ANSIColorCodes.Red)))
        ]

        processor.feed([ByteFragment(b"\033[42m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(background=ANSIColor(ANSIColorCodes.Green))
            )
        ]

        processor.feed([ByteFragment(b"\033[43m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(background=ANSIColor(ANSIColorCodes.Yellow))
            )
        ]

        processor.feed([ByteFragment(b"\033[44m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(background=ANSIColor(ANSIColorCodes.Blue))
            )
        ]

        processor.feed([ByteFragment(b"\033[45m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(background=ANSIColor(ANSIColorCodes.Magenta))
            )
        ]

        processor.feed([ByteFragment(b"\033[46m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(background=ANSIColor(ANSIColorCodes.Cyan))
            )
        ]

        processor.feed([ByteFragment(b"\033[47m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(background=ANSIColor(ANSIColorCodes.LightGray))
            )
        ]

        processor.feed([ByteFragment(b"\033[48;5;42m")])
        assert output.get() == [
            ANSIFragment(FormatUpdate(background=ANSIColor(42)))
        ]

        processor.feed([ByteFragment(b"\033[48;2;55;66;77m")])
        assert output.get() == [
            ANSIFragment(FormatUpdate(background=RGBColor(55, 66, 77)))
        ]

        processor.feed([ByteFragment(b"\033[49m")])
        assert output.get() == [
            ANSIFragment(FormatUpdate(background=NoColor()))
        ]

    def test_compound_ansi_sequence(self) -> None:
        processor = ANSIProcessor(Key(default=ANSIBoldEffect.BOLD))
        output = OutputCatcher(processor)

        processor.feed([ByteFragment(b"\033[1;4;27;31m")])
        assert output.get() == [
            ANSIFragment(
                FormatUpdate(
                    bold=True,
                    underline=True,
                    reverse=False,
                    foreground=ANSIColor(ANSIColorCodes.Red),
                )
            )
        ]

    def test_invalid_extended_color_sequence(self) -> None:
        processor = ANSIProcessor(Key(default=ANSIBoldEffect.BOLD))
        output = OutputCatcher(processor)

        processor.feed([ByteFragment(b"\033[38m")])
        assert output.get() == [ANSIFragment(FormatUpdate())]

        processor.feed([ByteFragment(b"\033[38;99999m")])
        assert output.get() == [ANSIFragment(FormatUpdate())]

        processor.feed([ByteFragment(b"\033[48m")])
        assert output.get() == [ANSIFragment(FormatUpdate())]

        processor.feed([ByteFragment(b"\033[48;99999m")])
        assert output.get() == [ANSIFragment(FormatUpdate())]


class TestUserPatternProcessor:
    def _match_output(
        self, output: OutputCatcher
    ) -> list[PatternMatchFragment]:
        return [f for f in output.get() if isinstance(f, PatternMatchFragment)]

    def test_simple_line_match(self) -> None:
        patterns = List(SpyritSettings.Pattern())
        processor = UserPatternProcessor(patterns)
        output = OutputCatcher(processor)

        p1 = patterns.appendOne()
        p1.scope.set(PatternScope.ENTIRE_LINE)

        f1 = p1.fragments.appendOne()
        f1.format.set(format_ := FormatUpdate(italic=True))
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("abcde")

        processor.feed(
            [TextFragment("abcde"), FlowControlFragment(FlowControlCode.LF)]
        )
        assert self._match_output(output) == [
            PatternMatchFragment(format_, 0, 5),
        ]

    def test_complex_line_match(self) -> None:
        patterns = List(SpyritSettings.Pattern())
        processor = UserPatternProcessor(patterns)
        output = OutputCatcher(processor)

        p1 = patterns.appendOne()
        p1.scope.set(PatternScope.ENTIRE_LINE)
        p1.format.set(format_ := FormatUpdate(italic=True))

        p1.fragments.appendOne().type.set(PatternType.ANYTHING)

        f1 = p1.fragments.appendOne()
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("abcde")

        p1.fragments.appendOne().type.set(PatternType.ANYTHING)

        processor.feed(
            [
                TextFragment("1234abcde12345"),
                FlowControlFragment(FlowControlCode.LF),
            ]
        )
        assert self._match_output(output) == [
            PatternMatchFragment(format_, 0, 4),
            PatternMatchFragment(format_, 4, 9),
            PatternMatchFragment(format_, 9, 14),
        ]

    def test_simple_anywhere_match(self) -> None:
        patterns = List(SpyritSettings.Pattern())
        processor = UserPatternProcessor(patterns)
        output = OutputCatcher(processor)

        p1 = patterns.appendOne()
        p1.scope.set(PatternScope.ANYWHERE_IN_LINE)
        p1.format.set(format_ := FormatUpdate(italic=True))

        f1 = p1.fragments.appendOne()
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("abcde")

        processor.feed(
            [
                TextFragment("1234abcde12345"),
                FlowControlFragment(FlowControlCode.LF),
            ]
        )
        assert self._match_output(output) == [
            PatternMatchFragment(format_, 4, 9),
        ]

    def test_complex_anywhere_match(self) -> None:
        patterns = List(SpyritSettings.Pattern())
        processor = UserPatternProcessor(patterns)
        output = OutputCatcher(processor)

        p1 = patterns.appendOne()
        p1.scope.set(PatternScope.ANYWHERE_IN_LINE)

        f1 = p1.fragments.appendOne()
        f1.type.set(PatternType.ANY_NOT_IN)
        f1.pattern_text.set("x")
        f1.format.set(format1 := FormatUpdate(italic=True))

        f2 = p1.fragments.appendOne()
        f2.type.set(PatternType.REGEX)
        f2.pattern_text.set("a{4,8}")
        f2.format.set(format2 := FormatUpdate(bold=True))

        f3 = p1.fragments.appendOne()
        f3.type.set(PatternType.EXACT_MATCH)
        f3.pattern_text.set("aaaab")
        f3.format.set(format3 := FormatUpdate(underline=True))

        processor.feed(
            [
                TextFragment("xxxxxxxaaaaaaaaaaaaaaaabxxxxx"),
                FlowControlFragment(FlowControlCode.LF),
            ]
        )
        assert self._match_output(output) == [
            PatternMatchFragment(format1, 7, 15),
            PatternMatchFragment(format2, 15, 19),
            PatternMatchFragment(format3, 19, 24),
        ]

    def test_repeated_anywhere_match(self) -> None:
        patterns = List(SpyritSettings.Pattern())
        processor = UserPatternProcessor(patterns)
        output = OutputCatcher(processor)

        p1 = patterns.appendOne()
        p1.scope.set(PatternScope.ANYWHERE_IN_LINE)
        p1.format.set(format_ := FormatUpdate(bold=True))

        f1 = p1.fragments.appendOne()
        f1.type.set(PatternType.REGEX)
        f1.pattern_text.set("a{2,5}")

        processor.feed(
            [
                TextFragment(" a  aa  aaaaa  aaaaaa  aaaaaaa"),
                FlowControlFragment(FlowControlCode.LF),
            ]
        )

        assert self._match_output(output) == [
            PatternMatchFragment(format_, 4, 6),
            PatternMatchFragment(format_, 8, 13),
            PatternMatchFragment(format_, 15, 20),
            PatternMatchFragment(format_, 23, 28),
            PatternMatchFragment(format_, 28, 30),
        ]

    def test_match_across_text_fragments(self) -> None:
        patterns = List(SpyritSettings.Pattern())
        processor = UserPatternProcessor(patterns)
        output = OutputCatcher(processor)

        p1 = patterns.appendOne()
        p1.scope.set(PatternScope.ANYWHERE_IN_LINE)
        p1.format.set(format_ := FormatUpdate(bold=True))

        f1 = p1.fragments.appendOne()
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("ab")

        processor.feed(
            [
                TextFragment("    a"),
                TextFragment("b    "),
                FlowControlFragment(FlowControlCode.LF),
            ]
        )
        assert self._match_output(output) == [
            PatternMatchFragment(format_, 4, 6),
        ]

        processor.feed(
            [
                TextFragment("   a "),
                TextFragment("b    "),
                FlowControlFragment(FlowControlCode.LF),
            ]
        )
        assert self._match_output(output) == []

    def test_fragment_format_overrides_pattern_format(self) -> None:
        patterns = List(SpyritSettings.Pattern())
        processor = UserPatternProcessor(patterns)
        output = OutputCatcher(processor)

        p1 = patterns.appendOne()
        p1.scope.set(PatternScope.ENTIRE_LINE)
        p1.format.set(line_format := FormatUpdate(bright=True, underline=True))

        f1 = p1.fragments.appendOne()
        f1.type.set(PatternType.ANYTHING)

        f2 = p1.fragments.appendOne()
        f2.type.set(PatternType.EXACT_MATCH)
        f2.pattern_text.set("test")
        f2.format.set(
            fragment_format := FormatUpdate(strikeout=True, reverse=True)
        )

        f3 = p1.fragments.appendOne()
        f3.type.set(PatternType.ANYTHING)

        processor.feed(
            [
                TextFragment("....test...."),
                FlowControlFragment(FlowControlCode.LF),
            ]
        )

        assert self._match_output(output) == [
            PatternMatchFragment(line_format, 0, 4),
            PatternMatchFragment(fragment_format, 4, 8),
            PatternMatchFragment(line_format, 8, 12),
        ]

    def test_fragments_passed_verbatim(self) -> None:
        patterns = List(SpyritSettings.Pattern())
        processor = UserPatternProcessor(patterns)
        output = OutputCatcher(processor)

        p1 = patterns.appendOne()
        p1.scope.set(PatternScope.ANYWHERE_IN_LINE)
        p1.format.set(format_ := FormatUpdate(bold=True))

        f1 = p1.fragments.appendOne()
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("test")

        processor.feed(
            [
                TextFragment("  te"),
                ANSIFragment(FormatUpdate(reverse=True)),
                TextFragment("st  "),
                FlowControlFragment(FlowControlCode.LF),
            ]
        )
        assert output.get() == [
            PatternMatchFragment(format_, 2, 6),
            TextFragment("  te"),
            ANSIFragment(FormatUpdate(reverse=True)),
            TextFragment("st  "),
            FlowControlFragment(FlowControlCode.LF),
        ]

    def test_parent_patterns_matched_first(self) -> None:
        class TestSettings(Settings):
            patterns: List[SpyritSettings.Pattern] = List(
                SpyritSettings.Pattern()
            )

        parent_settings = TestSettings()
        derived_settings = parent_settings.newSection("child")

        processor = UserPatternProcessor(derived_settings.patterns)
        output = OutputCatcher(processor)

        p1 = parent_settings.patterns.appendOne()
        p1.scope.set(PatternScope.ANYWHERE_IN_LINE)
        p1.format.set(format1 := FormatUpdate(underline=True))

        f1 = p1.fragments.appendOne()
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("cdef")

        p2 = derived_settings.patterns.appendOne()
        p2.scope.set(PatternScope.ANYWHERE_IN_LINE)
        p2.format.set(format2 := FormatUpdate(bright=True))

        f2 = p2.fragments.appendOne()
        f2.type.set(PatternType.EXACT_MATCH)
        f2.pattern_text.set("abcd")

        processor.feed(
            [
                TextFragment("abcdef"),
                FlowControlFragment(FlowControlCode.LF),
            ]
        )

        assert self._match_output(output) == [
            PatternMatchFragment(format1, 2, 6),
            PatternMatchFragment(format2, 0, 4),
        ]


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
