from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor

from spyrit.network.connection import Status
from spyrit.network.fragments import (
    ANSIFragment,
    FlowControlCode,
    FlowControlFragment,
    MatchBoundary,
    NetworkFragment,
    PatternMatchFragment,
    TextFragment,
)
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.colors import NoColor, RGBColor
from spyrit.ui.format import FormatUpdate
from spyrit.ui.scribe import CharFormatUpdater, Scribe


def _describe_char_format(char_format: QTextCharFormat) -> str:
    ret: list[str] = []
    if char_format.fontWeight() == QFont.Weight.Bold:
        ret.append("bold")
    if char_format.fontItalic():
        ret.append("italic")
    if char_format.fontUnderline():
        ret.append("underline")
    if char_format.fontStrikeOut():
        ret.append("strikeout")
    fg = char_format.foreground().color()
    bg = char_format.background().color()
    if fg.isValid() and (fg.red() or fg.green() or fg.blue()):
        ret.append(f"fg: {fg.red()},{fg.green()},{fg.blue()}")
    if bg.isValid() and (bg.red() or bg.green() or bg.blue()):
        ret.append(f"bg: {bg.red()},{bg.green()},{bg.blue()}")

    return " ; ".join(ret)


class TestCursor(QTextCursor):
    _text: str = ""

    def insertText(
        self, text: str, format: QTextCharFormat | None = None
    ) -> None:
        if format is not None:
            format_desc = _describe_char_format(format)
            if format_desc:
                self._text += f"[{format_desc}]"

        self._text += text

    def get(self) -> str:
        text = self._text
        self._text = ""

        return text


class TestCharFormatUpdater:
    def test_format_updates_properly_applied(self) -> None:
        updater = CharFormatUpdater()
        updater.pushFormat(format_ := FormatUpdate())
        char_format = QTextCharFormat()

        format_.setBold(True)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "bold"

        format_.setBold(False)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == ""

        format_.setForeground(RGBColor(100, 100, 100))

        format_.setBright(True)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "fg: 115,115,115"

        format_.setBright(False)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "fg: 100,100,100"

        format_.setForeground(NoColor())

        format_.setItalic(True)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "italic"

        format_.setItalic(False)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == ""

        format_.setUnderline(True)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "underline"

        format_.setUnderline(False)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == ""

        format_.setForeground(RGBColor(100, 100, 100))
        format_.setBackground(RGBColor(10, 10, 10))

        format_.setReverse(True)
        updater.applyFormat(char_format)
        assert (
            _describe_char_format(char_format)
            == "fg: 10,10,10 ; bg: 100,100,100"
        )

        format_.setReverse(False)
        updater.applyFormat(char_format)
        assert (
            _describe_char_format(char_format)
            == "fg: 100,100,100 ; bg: 10,10,10"
        )

        format_.setForeground(NoColor())
        format_.setBackground(NoColor())

        format_.setStrikeout(True)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "strikeout"

        format_.setStrikeout(False)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == ""

    def test_format_layers_applied_in_order(self) -> None:
        updater = CharFormatUpdater()
        char_format = QTextCharFormat()

        format1 = FormatUpdate(bold=True, italic=True)
        format2 = FormatUpdate(italic=False, underline=True)
        format3 = FormatUpdate(strikeout=True, underline=False)

        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == ""

        updater.pushFormat(format1)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "bold ; italic"

        updater.pushFormat(format2)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "bold ; underline"

        updater.pushFormat(format3)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "bold ; strikeout"

        updater.popFormat(format2)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "bold ; italic ; strikeout"

    def test_identical_format_popped_correctly(self) -> None:
        format1 = FormatUpdate(bold=True)
        format2 = FormatUpdate(bold=False, italic=True)
        format3 = FormatUpdate(bold=True)

        assert format1 == format3

        char_format = QTextCharFormat()
        updater = CharFormatUpdater()

        updater.pushFormat(format1)
        updater.pushFormat(format2)
        updater.pushFormat(format3)

        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "bold ; italic"

        updater.popFormat(format1)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "bold ; italic"

        char_format = QTextCharFormat()
        updater = CharFormatUpdater()

        updater.pushFormat(format1)
        updater.pushFormat(format2)
        updater.pushFormat(format3)

        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "bold ; italic"

        updater.popFormat(format3)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "italic"

    def test_reverse_plus_bright(self) -> None:
        char_format = QTextCharFormat()
        updater = CharFormatUpdater()
        updater.pushFormat(format_ := FormatUpdate())

        format_.setForeground(RGBColor(100, 100, 100))
        format_.setBackground(RGBColor(10, 10, 10))
        updater.applyFormat(char_format)
        assert (
            _describe_char_format(char_format)
            == "fg: 100,100,100 ; bg: 10,10,10"
        )

        format_.setBright(True)
        updater.applyFormat(char_format)
        assert (
            _describe_char_format(char_format)
            == "fg: 115,115,115 ; bg: 10,10,10"
        )

        format_.setReverse(True)
        updater.applyFormat(char_format)
        assert (
            _describe_char_format(char_format)
            == "fg: 10,10,10 ; bg: 115,115,115"
        )

        format_.setBright(False)
        updater.applyFormat(char_format)
        assert (
            _describe_char_format(char_format)
            == "fg: 10,10,10 ; bg: 100,100,100"
        )


class TestScribe:
    def test_carriage_return_behavior(self) -> None:
        settings = SpyritSettings.UI.Output()
        settings.default_text_color.set(RGBColor(100, 100, 100))
        settings.background_color.set(RGBColor(10, 10, 10))

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)

        scribe.inscribe([FlowControlFragment(FlowControlCode.LF)])
        assert cursor.get() == ""

        scribe.inscribe([FlowControlFragment(FlowControlCode.LF)])
        assert cursor.get() == "\n"

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)

        scribe.inscribe([FlowControlFragment(FlowControlCode.CR)])
        assert cursor.get() == ""

        scribe.inscribe([FlowControlFragment(FlowControlCode.CR)])
        assert cursor.get() == ""

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)

        scribe.inscribe([TextFragment("Test.")])
        assert cursor.get() == "[fg: 100,100,100 ; bg: 10,10,10]Test."

        scribe.inscribe([FlowControlFragment(FlowControlCode.LF)])
        assert cursor.get() == ""

        scribe.inscribe([TextFragment("Test.")])
        assert cursor.get() == "\n[fg: 100,100,100 ; bg: 10,10,10]Test."

    def test_basic_text(self) -> None:
        settings = SpyritSettings.UI.Output()
        settings.default_text_color.set(RGBColor(100, 100, 100))
        settings.background_color.set(RGBColor(10, 10, 10))

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)

        scribe.inscribe([TextFragment("Test!")])
        assert cursor.get() == "[fg: 100,100,100 ; bg: 10,10,10]Test!"

        scribe.inscribe([TextFragment("More text.")])  # No LF.
        assert cursor.get() == "[fg: 100,100,100 ; bg: 10,10,10]More text."

        scribe.inscribe([FlowControlFragment(FlowControlCode.LF)])
        assert cursor.get() == ""

        scribe.inscribe([TextFragment("Yet more text.")])
        assert (
            cursor.get() == "\n[fg: 100,100,100 ; bg: 10,10,10]Yet more text."
        )

    def test_default_text_color_update_applied(self) -> None:
        settings = SpyritSettings.UI.Output()
        settings.default_text_color.set(RGBColor(100, 100, 100))
        settings.background_color.set(RGBColor(10, 10, 10))

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)

        scribe.inscribe([TextFragment("Test!")])
        assert cursor.get() == "[fg: 100,100,100 ; bg: 10,10,10]Test!"

        settings.default_text_color.set(RGBColor(50, 50, 50))
        settings.background_color.set(RGBColor(200, 200, 200))

        scribe.inscribe([TextFragment("Test!")])
        assert cursor.get() == "[fg: 50,50,50 ; bg: 200,200,200]Test!"

    def test_ansi_fragments(self) -> None:
        settings = SpyritSettings.UI.Output()
        settings.default_text_color.set(RGBColor(100, 100, 100))
        settings.background_color.set(RGBColor(10, 10, 10))

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)

        scribe.inscribe([ANSIFragment(FormatUpdate(bold=True, italic=True))])
        assert cursor.get() == ""

        scribe.inscribe([TextFragment("")])
        assert (
            cursor.get() == "[bold ; italic ; fg: 100,100,100 ; bg: 10,10,10]"
        )

        scribe.inscribe(
            [ANSIFragment(FormatUpdate(bold=False, underline=True))]
        )
        scribe.inscribe(
            [ANSIFragment(FormatUpdate(underline=False, strikeout=True))]
        )
        scribe.inscribe([TextFragment("")])
        assert (
            cursor.get()
            == "[italic ; strikeout ; fg: 100,100,100 ; bg: 10,10,10]"
        )

    def test_network_fragments(self) -> None:
        settings = SpyritSettings.UI.Output()
        settings.default_text_color.set(RGBColor(100, 100, 100))
        settings.background_color.set(RGBColor(10, 10, 10))
        settings.status_text_format.set(FormatUpdate())

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)

        scribe.inscribe([NetworkFragment(Status.CONNECTING, "")])
        assert cursor.get() == "[fg: 100,100,100 ; bg: 10,10,10]• Connecting..."

        scribe.inscribe([NetworkFragment(Status.CONNECTED, "")])
        assert cursor.get() == "\n[fg: 100,100,100 ; bg: 10,10,10]• Connected!"

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)

        settings.default_text_color.set(RGBColor(55, 55, 55))
        settings.background_color.set(RGBColor(200, 200, 200))
        settings.status_text_format.set(FormatUpdate(italic=True))

        scribe.inscribe([NetworkFragment(Status.RESOLVING, "test.test")])
        assert cursor.get() == (
            "[italic ; fg: 55,55,55 ; bg: 200,200,200]"
            "• Looking up 'test.test'..."
        )

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)

        scribe.inscribe([NetworkFragment(Status.ERROR, "(test)")])
        assert cursor.get() == (
            "[italic ; fg: 55,55,55 ; bg: 200,200,200]‼ Error: (test)!"
        )

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)

        scribe.inscribe([TextFragment("Test.")])  # No LF.
        scribe.inscribe([NetworkFragment(Status.DISCONNECTED, "")])
        assert cursor.get() == (
            "[fg: 55,55,55 ; bg: 200,200,200]Test.\n"
            "[italic ; fg: 55,55,55 ; bg: 200,200,200]• Disconnected."
        )

    def test_pattern_match_fragments(self) -> None:
        settings = SpyritSettings.UI.Output()
        settings.default_text_color.set(RGBColor(100, 100, 100))
        settings.background_color.set(RGBColor(10, 10, 10))

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)
        format_ = FormatUpdate(reverse=True)

        scribe.inscribe([TextFragment("1234")])
        scribe.inscribe([PatternMatchFragment(format_, MatchBoundary.START)])
        scribe.inscribe([TextFragment("5678")])
        scribe.inscribe([PatternMatchFragment(format_, MatchBoundary.END)])
        scribe.inscribe([TextFragment("9012")])

        assert cursor.get() == (
            "[fg: 100,100,100 ; bg: 10,10,10]1234"
            "[fg: 10,10,10 ; bg: 100,100,100]5678"
            "[fg: 100,100,100 ; bg: 10,10,10]9012"
        )

    def test_pattern_match_override_ansi(self) -> None:
        settings = SpyritSettings.UI.Output()
        settings.default_text_color.set(RGBColor(100, 100, 100))
        settings.background_color.set(RGBColor(10, 10, 10))

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)
        pattern_format = FormatUpdate(foreground=RGBColor(50, 50, 50))
        ansi_format = FormatUpdate(foreground=RGBColor(20, 20, 20))

        scribe.inscribe([ANSIFragment(ansi_format)])
        scribe.inscribe(
            [PatternMatchFragment(pattern_format, MatchBoundary.START)]
        )
        scribe.inscribe([TextFragment("1234")])
        scribe.inscribe(
            [PatternMatchFragment(pattern_format, MatchBoundary.END)]
        )
        scribe.inscribe([TextFragment("5678")])

        assert cursor.get() == (
            "[fg: 50,50,50 ; bg: 10,10,10]1234"
            "[fg: 20,20,20 ; bg: 10,10,10]5678"
        )

    def test_later_pattern_match_overrides_earlier(self) -> None:
        settings = SpyritSettings.UI.Output()
        settings.default_text_color.set(RGBColor(100, 100, 100))
        settings.background_color.set(RGBColor(10, 10, 10))

        cursor = TestCursor()
        scribe = Scribe(cursor, settings)
        format1 = FormatUpdate(foreground=RGBColor(20, 20, 20))
        format2 = FormatUpdate(foreground=RGBColor(50, 50, 50))

        scribe.inscribe([PatternMatchFragment(format1, MatchBoundary.START)])
        scribe.inscribe([TextFragment("1234")])
        scribe.inscribe([PatternMatchFragment(format2, MatchBoundary.START)])
        scribe.inscribe([TextFragment("5678")])
        scribe.inscribe([PatternMatchFragment(format2, MatchBoundary.END)])
        scribe.inscribe([TextFragment("9012")])
        scribe.inscribe([PatternMatchFragment(format1, MatchBoundary.END)])

        assert cursor.get() == (
            "[fg: 20,20,20 ; bg: 10,10,10]1234"
            "[fg: 50,50,50 ; bg: 10,10,10]5678"
            "[fg: 20,20,20 ; bg: 10,10,10]9012"
        )
