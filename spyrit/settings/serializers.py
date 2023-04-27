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
Custom serializers used in our settings.
"""


from PySide6.QtCore import QSize
from PySide6.QtGui import QFont


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
