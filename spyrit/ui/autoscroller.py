# Copyright (c) 2007-2025 Pascal Varet <p.varet@gmail.com>
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

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QScrollBar


class BottomTracker(QObject):
    # Threshold under which the scrollbar is considered to be all the way down even if
    # in reality there's a gap of at most this many pixels.

    _THRESHOLD = 4  # pixels

    # This signal fires with True when the target scrollbar is all the way to the
    # bottom, give or take a few pixels, and with False when it is not.

    atBottom: Signal = Signal(bool)  # noqa: N815

    _scrollbar: QScrollBar
    _at_bottom: bool

    def __init__(self, scrollbar: QScrollBar) -> None:
        super().__init__(scrollbar)

        self._scrollbar = scrollbar
        self._scrollbar.rangeChanged.connect(self._updateAtBottom)
        self._scrollbar.valueChanged.connect(self._updateAtBottom)
        self._at_bottom = True

    @Slot()
    def _updateAtBottom(self) -> None:
        at_bottom = (
            self._scrollbar.value() >= self._scrollbar.maximum() - self._THRESHOLD
        )
        if at_bottom != self._at_bottom:
            self._at_bottom = at_bottom
            self.atBottom.emit(at_bottom)


class Autoscroller(QObject):
    _scrollbar: QScrollBar
    _at_bottom: bool = True

    def __init__(self, scrollbar: QScrollBar) -> None:
        super().__init__(parent=scrollbar)
        self._scrollbar = scrollbar
        self._scrollbar.rangeChanged.connect(self.maybeScrollToBottom)
        BottomTracker(self._scrollbar).atBottom.connect(self._setAtBottom)

    @Slot(bool)
    def _setAtBottom(self, at_bottom: bool) -> None:
        self._at_bottom = at_bottom

    @Slot()
    def maybeScrollToBottom(self) -> None:
        if self._at_bottom:
            self._scrollbar.triggerAction(QScrollBar.SliderAction.SliderToMaximum)
