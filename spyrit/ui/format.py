# Copyright (c) 2007-2024 Pascal Varet <p.varet@gmail.com>
#
# This file is part of Spyrit.
#
# Spyrit is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3 as published by the Free
# Software Foundation.
#
# You should have received a copy of the GNU General Public License along with
# Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
# Fifth Floor, Boston, MA  02110-1301  USA
#

"""
Implements a class that can encode formatting instructions.
"""


import dataclasses

from spyrit.ui.colors import Color


@dataclasses.dataclass
class FormatUpdate:
    _: dataclasses.KW_ONLY

    bold: bool | None = None
    bright: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    reverse: bool | None = None
    strikeout: bool | None = None
    background: Color | None = None
    foreground: Color | None = None
    href: str | None = None

    def setBold(self, bold: bool = True) -> None:
        self.bold = bold

    def setBright(self, bright: bool = True) -> None:
        self.bright = bright

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

    def setHref(self, href: str) -> None:
        self.href = href

    def update(self, other: "FormatUpdate") -> None:
        for attribute, value in dataclasses.asdict(other).items():
            if value is not None:
                setattr(self, attribute, value)

    def empty(self) -> bool:
        return all(attr is None for attr in dataclasses.astuple(self))

    def __repr__(self) -> str:
        attributes = dataclasses.asdict(self)
        reprs = [
            f"{name}={value}"
            for name, value in attributes.items()
            if value is not None
        ]
        contents = "; ".join(reprs)
        return f"{self.__class__.__qualname__}({contents})"
