from PySide6.QtCore import QSize
from PySide6.QtGui import QFont

import hypothesis
import hypothesis.strategies

from spyrit.settings.serializers import (
    ColorSerializer,
    Font,
    FormatSerializer,
    IntList,
    SemiColonJoiner,
    Size,
)
from spyrit.ui.colors import ANSIColor, ANSIColorCodes, NoColor, RGBColor
from spyrit.ui.format import FormatUpdate


def test_int_list_serializer() -> None:
    serializer = IntList

    assert serializer.fromStr("") == []
    assert serializer.fromStr(" 1 ") == [1]
    assert serializer.fromStr("2  ,3,4") == [2, 3, 4]
    assert serializer.fromStr("1,,3") == [1, 3]
    assert serializer.fromStr("5,six,7") is None
    assert serializer.fromStr("5,6.0,7") is None

    assert serializer.toStr([]) == ""
    assert serializer.toStr([1]) == "1"
    assert serializer.toStr([2, 3, 4]) == "2, 3, 4"


def test_font_serializer() -> None:
    font = Font.fromStr("arial,10")
    assert font is not None
    assert font.family() == "arial"
    assert font.pointSize() == 10

    font = QFont("sans serif", 12)
    assert Font.toStr(font).startswith("sans serif,12,")


def test_size_serializer() -> None:
    size = Size.fromStr("12, 34")
    assert size is not None
    assert size.width() == 12
    assert size.height() == 34

    assert Size.toStr(QSize(56, 78)) == "56, 78"


def test_color_serializer() -> None:
    assert ColorSerializer.toStr(NoColor()) == "-"
    assert ColorSerializer.toStr(ANSIColor(ANSIColorCodes.Black)) == "Black"
    assert (
        ColorSerializer.toStr(ANSIColor(ANSIColorCodes.LightCyan))
        == "LightCyan"
    )
    assert ColorSerializer.toStr(ANSIColor(201)) == "201"
    assert ColorSerializer.toStr(RGBColor(0, 0, 0)) == "#000000"
    assert ColorSerializer.toStr(RGBColor(123, 231, 132)) == "#7be784"

    assert ColorSerializer.fromStr("") is None
    assert ColorSerializer.fromStr("-") == NoColor()
    assert ColorSerializer.fromStr("#7be784") == RGBColor(123, 231, 132)
    assert ColorSerializer.fromStr("128") == ANSIColor(128)
    assert ColorSerializer.fromStr("0") == ANSIColor(ANSIColorCodes.Black)
    assert ColorSerializer.fromStr("black") == ANSIColor(ANSIColorCodes.Black)
    assert ColorSerializer.fromStr("BLACK") == ANSIColor(ANSIColorCodes.Black)
    assert ColorSerializer.fromStr("13") == ANSIColor(
        ANSIColorCodes.LightMagenta
    )
    assert ColorSerializer.fromStr("lightmagenta") == ANSIColor(
        ANSIColorCodes.LightMagenta
    )
    assert ColorSerializer.fromStr("LIGHTMAGENTA") == ANSIColor(
        ANSIColorCodes.LightMagenta
    )
    assert ColorSerializer.fromStr("300") is None
    assert ColorSerializer.fromStr("-1") is None
    assert ColorSerializer.fromStr("#000") is None
    assert ColorSerializer.fromStr("#1234567") is None
    assert ColorSerializer.fromStr("123456") is None


def test_format_serializer() -> None:
    assert FormatSerializer.toStr(FormatUpdate()) == ""
    assert FormatSerializer.toStr(
        FormatUpdate(
            bold=True,
            bright=True,
            italic=True,
            underline=True,
            reverse=True,
            strikeout=True,
            foreground=RGBColor(0, 0, 0),
            background=ANSIColor(ANSIColorCodes.White),
            href="http://python.org/",
        )
    ) == (
        "bold ; bright ; italic ; underline ; reverse ; strikeout ;"
        " foreground: #000000 ; background: White ; href: http://python.org/"
    )
    assert FormatSerializer.toStr(
        FormatUpdate(
            bold=False,
            bright=False,
            italic=False,
            underline=False,
            reverse=False,
            strikeout=False,
            foreground=NoColor(),
            background=NoColor(),
        )
    ) == (
        "-bold ; -bright ; -italic ; -underline ; -reverse ; -strikeout ;"
        " foreground: - ; background: -"
    )

    assert FormatSerializer.fromStr(
        "bold ; Bright ; +italic ; UNDERLINE ; + reverse ; strikeout ;"
        " foreground: #000000 ; background: White ; href: http://python.org/"
    ) == FormatUpdate(
        bold=True,
        bright=True,
        italic=True,
        underline=True,
        reverse=True,
        strikeout=True,
        foreground=RGBColor(0, 0, 0),
        background=ANSIColor(ANSIColorCodes.White),
        href="http://python.org/",
    )
    assert FormatSerializer.fromStr(
        "-bold ; - bright ; -italic ; !underline ; -reverse ; ! strikeout ;"
        " foreground: -"
    ) == FormatUpdate(
        bold=False,
        bright=False,
        italic=False,
        underline=False,
        reverse=False,
        strikeout=False,
        foreground=NoColor(),
    )
    assert FormatSerializer.fromStr("background: #000000") == FormatUpdate(
        background=RGBColor(0, 0, 0)
    )
    assert FormatSerializer.fromStr("href:   test  ") == FormatUpdate(
        href="test"
    )
    assert FormatSerializer.fromStr(
        FormatSerializer.toStr(FormatUpdate(href="a;b;c"))
    ) == FormatUpdate(href="a;b;c")

    assert FormatSerializer.fromStr("href:") is None
    assert FormatSerializer.fromStr("badground: #000000") is None
    assert FormatSerializer.fromStr("badground: #0000") is None
    assert FormatSerializer.fromStr("background: #00000000") is None
    assert FormatSerializer.fromStr("background: #0000zz") is None
    assert FormatSerializer.fromStr("invalid") is None
    assert FormatSerializer.fromStr("bold ; invalid") is None


def _text_hypothesis() -> hypothesis.strategies.SearchStrategy[str]:
    return hypothesis.strategies.text(
        alphabet=hypothesis.strategies.characters(
            categories=(), include_characters=" a;"
        ),
        min_size=1,
    ).filter(lambda s: s == s.strip())


@hypothesis.given(hypothesis.strategies.lists(_text_hypothesis()))
def test_semi_colon_joiner(items: list[str]) -> None:
    assert SemiColonJoiner.split(SemiColonJoiner.join(items)) == items
