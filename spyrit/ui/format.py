# Copyright (c) 2007-2023 Pascal Varet <p.varet@gmail.com>
#
# This file is part of Spyrit.
#
# Spyrit is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 2 as published by the Free
# Software Foundation.
#
# You should have received a copy of the GNU General Public License along with
# Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
# Fifth Floor, Boston, MA  02110-1301  USA
#

"""
Implements a class that can encode formatting instructions.
"""


from typing import Any

from spyrit.ui.colors import Color, NoColor


class CharFormat:
    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    reverse: bool | None = None
    strikeout: bool | None = None
    background: Color | None = None
    foreground: Color | None = None

    def __init__(  # pylint: disable=too-many-arguments
        self,
        bold: bool | None = None,
        italic: bool | None = None,
        underline: bool | None = None,
        reverse: bool | None = None,
        strikeout: bool | None = None,
        foreground: Color | None = None,
        background: Color | None = None,
    ) -> None:
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.reverse = reverse
        self.strikeout = strikeout
        self.foreground = foreground
        self.background = background

    def resetAll(self) -> None:
        self.setBold(False)
        self.setItalic(False)
        self.setUnderline(False)
        self.setReverse(False)
        self.setStrikeout(False)
        self.setForeground(NoColor())
        self.setBackground(NoColor())

    def setBold(self, bold: bool = True) -> None:
        self.bold = bold

    def setItalic(self, italic: bool = True) -> None:
        self.italic = italic

    def setUnderline(self, underline: bool = True) -> None:
        self.underline = underline

    def setReverse(self, reverse: bool = True) -> None:
        self.reverse = reverse

    def setStrikeout(self, strikeout: bool = True) -> None:
        self.strikeout = strikeout

    def setForeground(self, color: Color) -> None:
        self.foreground = color

    def setBackground(self, color: Color) -> None:
        self.background = color

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CharFormat):
            return False

        return all(
            (
                self.bold == other.bold,
                self.italic == other.italic,
                self.underline == other.underline,
                self.reverse == other.reverse,
                self.strikeout == other.strikeout,
                self.foreground == other.foreground,
                self.background == other.background,
            )
        )
