import pytest

from spyrit.ui.colors import (
    ANSIColor,
    ANSIColorCodes,
    NoColor,
    RGBColor,
    brighten,
    hsl_to_rgb,
    rgb_to_hsl,
)


class TestRGB:
    def test_rgb_to_hsl(self) -> None:
        assert rgb_to_hsl(0.0, 0.0, 0.0) == (0.0, 0.0, 0.0)
        assert rgb_to_hsl(1.0, 0.0, 0.0) == (0 / 3, 1.0, 0.5)
        assert rgb_to_hsl(0.0, 1.0, 0.0) == (1 / 3, 1.0, 0.5)
        assert rgb_to_hsl(0.0, 0.0, 1.0) == (2 / 3, 1.0, 0.5)
        assert rgb_to_hsl(1.0, 1.0, 1.0) == (0.0, 0.0, 1.0)

    def test_rgb_to_hsl_to_rgb_stability(self) -> None:
        values = (0, 10, 100, 255)
        for r in values:
            for g in values:
                for b in values:
                    rr, gg, bb = hsl_to_rgb(
                        *rgb_to_hsl(r / 255, g / 255, b / 255)
                    )
                    assert (
                        round(rr * 255),
                        round(gg * 255),
                        round(bb * 255),
                    ) == (r, g, b)

    def test_brighten(self) -> None:
        assert brighten(1.0, 1.0, 1.0, brightness=0.1) == (1.0, 1.0, 1.0)
        assert brighten(
            0.0, 0.0, 0.0, brightness=0.1
        ) == pytest.approx(  # type: ignore
            (0.1, 0.1, 0.1)
        )


class TestColor:
    def test_repr(self) -> None:
        assert repr(NoColor()) == "NoColor(-)"
        assert repr(ANSIColor(ANSIColorCodes.DarkGray)) == "ANSIColor(DarkGray)"
        assert repr(RGBColor(1, 2, 3)) == "RGBColor(#010203)"
