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
Custom serializers used in our settings.
"""


import re

from typing import Sequence

from PySide6.QtCore import QSize
from PySide6.QtGui import QFont

from spyrit.ui.colors import ANSIColor, ANSIColorCodes, Color, NoColor, RGBColor
from spyrit.ui.format import FormatUpdate


class IntList:
    def fromStr(self, string: str) -> list[int] | None:
        ret: list[int] = []

        for element in string.split(","):
            element = element.strip()
            if not element:
                continue

            if not element.isdigit():
                return None

            ret.append(int(element))

        return ret

    def toStr(self, value: list[int]) -> str:
        return ", ".join(str(i) for i in value)


class Font:
    def fromStr(self, string: str) -> QFont | None:
        font = QFont()
        return font if font.fromString(string) else None

    def toStr(self, value: QFont) -> str:
        return value.toString()


class Size:
    def fromStr(self, string: str) -> QSize | None:
        size = string.split(",", 1)
        if len(size) != 2:
            return None
        w, h = size
        w = w.strip()
        h = h.strip()
        if w.isdigit() and h.isdigit():
            return QSize(int(w), int(h))
        return None

    def toStr(self, value: QSize) -> str:
        return f"{value.width()}, {value.height()}"


class ColorSerializer:
    def fromStr(self, string: str) -> Color | None:
        string = string.strip()

        if string == "-":
            return NoColor()

        if string.isdigit():
            ansi_code = int(string)
            if 0 <= ansi_code <= 255:
                return ANSIColor(ansi_code)

        string = string.lower()

        if re.match(r"#[0-9a-f]{6}$", string):
            r = int(string[1:3], 16)
            g = int(string[3:5], 16)
            b = int(string[5:7], 16)

            return RGBColor(r, g, b)

        for code in ANSIColorCodes:
            if code.name.lower() == string:
                return ANSIColor(code)

        return None

    def toStr(self, value: Color) -> str:
        return value.toStr()


class SemiColonJoiner:
    _SEP = ";"

    @classmethod
    def _escape(cls, string: str) -> str:
        return string.replace(cls._SEP, cls._SEP * 2)

    @classmethod
    def _unescape(cls, string: str) -> str:
        return string.replace(cls._SEP * 2, cls._SEP)

    @classmethod
    def join(cls, strings: Sequence[str]) -> str:
        sep = f" {cls._SEP} "
        return sep.join(cls._escape(string) for string in strings)

    @classmethod
    def split(cls, string: str) -> list[str]:
        splitter = re.compile(f"[^{cls._SEP}]{cls._SEP}[^{cls._SEP}]")
        return list(
            filter(
                None, (cls._unescape(s).strip() for s in splitter.split(string))
            )
        )


class FormatSerializer:
    def fromStr(self, string: str) -> FormatUpdate | None:
        format_update = FormatUpdate()

        for item in string.split(";"):
            item = item.strip().lower()

            apply = True
            if item.startswith(("+", "-", "!")):
                apply = not item.startswith(("-", "!"))
                item = item[1:].lstrip()

            match item:
                case "bold":
                    format_update.setBold(apply)

                case "bright":
                    format_update.setBright(apply)

                case "italic":
                    format_update.setItalic(apply)

                case "underline":
                    format_update.setUnderline(apply)

                case "reverse":
                    format_update.setReverse(apply)

                case "strikeout":
                    format_update.setStrikeout(apply)

                case _ if ":" in item:
                    scope, maybe_color = item.split(":", 1)
                    color = ColorSerializer().fromStr(maybe_color)

                    if color is None:
                        return None

                    if scope == "foreground":
                        format_update.setForeground(color)
                    elif scope == "background":
                        format_update.setBackground(color)
                    else:
                        return None

                case _:
                    return None

        return format_update

    def toStr(self, value: FormatUpdate) -> str:
        return value.toStr()
