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
Autoscroller is a helper that keeps a scrollbar at the bottom of its range when it's
already there when the range grows.
"""

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QScrollBar


class Autoscroller(QObject):
    _scrollbar: QScrollBar
    _at_bottom: bool

    def __init__(self, scrollbar: QScrollBar) -> None:
        super().__init__(parent=scrollbar)
        self._scrollbar = scrollbar
        self._scrollbar.valueChanged.connect(self._setAtBottom)
        self._scrollbar.rangeChanged.connect(self._maybeScrollToBottom)
        self._setAtBottom(self._scrollbar.value())

    @Slot(int)
    def _setAtBottom(self, value: int) -> None:
        self._at_bottom = value == self._scrollbar.maximum()

    @Slot(int, int)
    def _maybeScrollToBottom(self, minimum: int, maximum: int) -> None:
        del minimum
        if self._at_bottom:
            self._scrollbar.setValue(maximum)
