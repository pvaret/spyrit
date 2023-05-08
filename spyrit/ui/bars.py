# Copyright (c) 2007-2023 Pascal Varet <p.varet@gmail.com>
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

"""
Implements vertical and horizontal bars.
"""


import enum

from PySide6.QtWidgets import QFrame, QWidget


class _Direction(enum.Enum):
    VERTICAL = enum.auto()
    HORIZONTAL = enum.auto()


class _Bar(QFrame):
    def __init__(
        self, direction: _Direction, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        if direction == _Direction.VERTICAL:
            self.setFrameShape(QFrame.Shape.VLine)
        elif direction == _Direction.HORIZONTAL:
            self.setFrameShape(QFrame.Shape.HLine)

        self.setFrameShadow(QFrame.Shadow.Plain)


class HBar(_Bar):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(_Direction.HORIZONTAL, parent)


class VBar(_Bar):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(_Direction.VERTICAL, parent)
