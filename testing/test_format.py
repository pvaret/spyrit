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
        assert not FormatUpdate(href="").empty()
        assert not FormatUpdate(href="test").empty()

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

        assert FormatUpdate(href="test") == FormatUpdate(href="test")

    def test_update(self) -> None:
        format_ = FormatUpdate()

        format_.update(FormatUpdate(bold=True))
        assert format_.bold
        format_.update(FormatUpdate(bold=False))
        assert not format_.bold

        format_.update(FormatUpdate(bright=True))
        assert format_.bright
        format_.update(FormatUpdate(bright=False))
        assert not format_.bright

        format_.update(FormatUpdate(italic=True))
        assert format_.italic
        format_.update(FormatUpdate(italic=False))
        assert not format_.italic

        format_.update(FormatUpdate(underline=True))
        assert format_.underline
        format_.update(FormatUpdate(underline=False))
        assert not format_.underline

        format_.update(FormatUpdate(reverse=True))
        assert format_.reverse
        format_.update(FormatUpdate(reverse=False))
        assert not format_.reverse

        format_.update(FormatUpdate(strikeout=True))
        assert format_.strikeout
        format_.update(FormatUpdate(strikeout=False))
        assert not format_.strikeout

        format_.update(FormatUpdate(foreground=ANSIColor(ANSIColorCodes.Red)))
        assert format_.foreground == ANSIColor(ANSIColorCodes.Red)
        format_.update(FormatUpdate(foreground=NoColor()))
        assert format_.foreground == NoColor()

        format_.update(FormatUpdate(background=ANSIColor(ANSIColorCodes.Red)))
        assert format_.background == ANSIColor(ANSIColorCodes.Red)
        format_.update(FormatUpdate(background=NoColor()))
        assert format_.background == NoColor()

        assert format_.href is None
        format_.update(FormatUpdate(href="test"))
        assert format_.href == "test"
