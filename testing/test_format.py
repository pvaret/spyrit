from spyrit.ui.colors import ANSIColor, ANSIColorCodes, NoColor, RGBColor
from spyrit.ui.format import FormatUpdate


class TestFormat:
    def test_emptiness(self) -> None:
        assert FormatUpdate().empty()
        assert not FormatUpdate(bold=True).empty()
        assert not FormatUpdate(bright=True).empty()
        assert not FormatUpdate(italic=True).empty()
        assert not FormatUpdate(underline=True).empty()
        assert not FormatUpdate(reverse=True).empty()
        assert not FormatUpdate(strikeout=True).empty()
        assert not FormatUpdate(bold=False).empty()
        assert not FormatUpdate(bright=False).empty()
        assert not FormatUpdate(italic=False).empty()
        assert not FormatUpdate(underline=False).empty()
        assert not FormatUpdate(reverse=False).empty()
        assert not FormatUpdate(strikeout=False).empty()
        assert not FormatUpdate(foreground=RGBColor(10, 20, 30)).empty()
        assert not FormatUpdate(background=RGBColor(10, 20, 30)).empty()
        assert not FormatUpdate(foreground=NoColor()).empty()
        assert not FormatUpdate(background=NoColor()).empty()

    def test_equality(self) -> None:
        assert FormatUpdate(
            bold=True,
            bright=False,
            reverse=True,
        ) == FormatUpdate(
            bold=True,
            bright=False,
            reverse=True,
        )
        assert FormatUpdate(
            italic=False,
            strikeout=True,
            underline=False,
        ) == FormatUpdate(
            italic=False,
            strikeout=True,
            underline=False,
        )
        assert FormatUpdate(
            foreground=RGBColor(10, 50, 100),
            background=ANSIColor(ANSIColorCodes.Black),
        ) == FormatUpdate(
            foreground=RGBColor(10, 50, 100),
            background=ANSIColor(ANSIColorCodes.Black),
        )
        assert FormatUpdate(
            foreground=NoColor(),
            background=NoColor(),
        ) == FormatUpdate(
            foreground=NoColor(),
            background=NoColor(),
        )
