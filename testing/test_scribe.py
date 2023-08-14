from PySide6.QtGui import QFont, QTextCharFormat

from spyrit.ui.colors import NoColor, RGBColor
from spyrit.ui.format import FormatUpdate
from spyrit.ui.scribe import CharFormatUpdater


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
        ret.append(f"fg: {fg.red()}, {fg.green()}, {fg.blue()}")
    if bg.isValid() and (bg.red() or bg.green() or bg.blue()):
        ret.append(f"bg: {bg.red()}, {bg.green()}, {bg.blue()}")

    return " ; ".join(ret)


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
        assert _describe_char_format(char_format) == "fg: 115, 115, 115"

        format_.setBright(False)
        updater.applyFormat(char_format)
        assert _describe_char_format(char_format) == "fg: 100, 100, 100"

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
            == "fg: 10, 10, 10 ; bg: 100, 100, 100"
        )

        format_.setReverse(False)
        updater.applyFormat(char_format)
        assert (
            _describe_char_format(char_format)
            == "fg: 100, 100, 100 ; bg: 10, 10, 10"
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
            == "fg: 100, 100, 100 ; bg: 10, 10, 10"
        )

        format_.setBright(True)
        updater.applyFormat(char_format)
        assert (
            _describe_char_format(char_format)
            == "fg: 115, 115, 115 ; bg: 10, 10, 10"
        )

        format_.setReverse(True)
        updater.applyFormat(char_format)
        assert (
            _describe_char_format(char_format)
            == "fg: 10, 10, 10 ; bg: 115, 115, 115"
        )

        format_.setBright(False)
        updater.applyFormat(char_format)
        assert (
            _describe_char_format(char_format)
            == "fg: 10, 10, 10 ; bg: 100, 100, 100"
        )
