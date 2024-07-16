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


import logging
import re

from typing import Sequence

from PySide6.QtCore import QSize
from PySide6.QtGui import QFont

from spyrit.ui.colors import ANSIColor, ANSIColorCodes, Color, NoColor, RGBColor
from spyrit.ui.format import FormatUpdate


class IntList:
    @staticmethod
    def fromStr(string: str) -> list[int] | None:
        ret: list[int] = []

        for element in string.split(","):
            element = element.strip()
            if not element:
                continue

            if not element.isdigit():
                return None

            ret.append(int(element))

        return ret

    @staticmethod
    def toStr(value: list[int]) -> str:
        return ", ".join(str(i) for i in value)


class Font:
    @staticmethod
    def fromStr(string: str) -> QFont | None:
        font = QFont()
        return font if font.fromString(string) else None

    @staticmethod
    def toStr(value: QFont) -> str:
        return value.toString()


class Size:
    @staticmethod
    def fromStr(string: str) -> QSize | None:
        size = string.split(",", 1)
        if len(size) != 2:
            return None
        w, h = size
        w = w.strip()
        h = h.strip()
        if w.isdigit() and h.isdigit():
            return QSize(int(w), int(h))
        return None

    @staticmethod
    def toStr(value: QSize) -> str:
        return f"{value.width()}, {value.height()}"


class ColorSerializer:
    @staticmethod
    def fromStr(string: str) -> Color | None:
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

    @staticmethod
    def toStr(value: Color) -> str:
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
        splitter = re.compile(f"(?<!{cls._SEP}){cls._SEP}(?!{cls._SEP})")
        return list(
            filter(
                None, (cls._unescape(s).strip() for s in splitter.split(string))
            )
        )


class FormatSerializer:
    @staticmethod
    def fromStr(string: str) -> FormatUpdate | None:
        format_update = FormatUpdate()

        for item in SemiColonJoiner.split(string):

            value = ""
            if ":" in item:
                item, value = item.split(":", 1)

            item = item.strip()
            value = value.strip()

            apply = True
            if item.startswith(("+", "-", "!")):
                apply = not item.startswith(("-", "!"))
                item = item[1:].lstrip()

            match item.lower():
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

                case "foreground":
                    color = ColorSerializer.fromStr(value)
                    if color is None:
                        logging.warning(
                            f"Invalid format string value for attribute '{item}': '{value}'"
                        )
                        continue
                    format_update.setForeground(color)

                case "background":
                    color = ColorSerializer.fromStr(value)
                    if color is None:
                        logging.warning(
                            f"Invalid format string value for attribute '{item}': '{value}'"
                        )
                        continue
                    format_update.setBackground(color)

                case "underline_color":
                    color = ColorSerializer.fromStr(value)
                    if color is None:
                        logging.warning(
                            f"Invalid format string value for attribute '{item}': '{value}'"
                        )
                        continue
                    format_update.setUnderlineColor(color)

                case "href":
                    if not value:
                        logging.warning(
                            f"Invalid format string value for attribute '{item}': '{value}'"
                        )
                        continue
                    format_update.setHref(value)

                case _:
                    logging.warning(
                        f"Unknown attribute in format string: '{item}'"
                    )
                    continue

        return format_update

    @staticmethod
    def toStr(value: FormatUpdate) -> str:
        items: list[str] = []

        if value.bold is not None:
            items.append(("-" if not value.bold else "") + "bold")

        if value.bright is not None:
            items.append(("-" if not value.bright else "") + "bright")

        if value.italic is not None:
            items.append(("-" if not value.italic else "") + "italic")

        if value.underline is not None:
            items.append(("-" if not value.underline else "") + "underline")

        if value.reverse is not None:
            items.append(("-" if not value.reverse else "") + "reverse")

        if value.strikeout is not None:
            items.append(("-" if not value.strikeout else "") + "strikeout")

        if value.foreground is not None:
            items.append(f"foreground: {value.foreground.toStr()}")

        if value.background is not None:
            items.append(f"background: {value.background.toStr()}")

        if value.underline_color is not None:
            items.append(f"underline_color: {value.underline_color.toStr()}")

        if value.href:
            items.append(f"href: {value.href}")

        return SemiColonJoiner.join(items)
