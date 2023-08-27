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
#


"""
Provides a class that manages the scrollbar for a continuously growing text edit
widget.
"""


from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QAbstractSlider, QScrollBar


class Scroller(QObject):
    """
    Manages a scrollbar to make its behavior feel natural and pleasant to users.
    """

    _scrollbar: QScrollBar
    _pin_to_bottom: bool = True

    def __init__(self, scrollbar: QScrollBar) -> None:
        super().__init__(parent=scrollbar)

        self._scrollbar = scrollbar

        # Report value updates continuously, not just at the end of a user
        # motion.

        scrollbar.setTracking(True)

        # Keep track when the user moves the bar.

        scrollbar.sliderMoved.connect(self.onUserInitiatedMove)
        scrollbar.actionTriggered.connect(self.onUserInitiatedMove)

        # Take action, maybe, when the size of the document grows.

        scrollbar.rangeChanged.connect(self.maybeScrollToBottom)

    @Slot()
    def onUserInitiatedMove(self) -> None:
        self._pin_to_bottom = (
            self._scrollbar.sliderPosition() == self._scrollbar.maximum()
        )

    @Slot()
    def maybeScrollToBottom(self) -> None:
        if self._pin_to_bottom:
            self._scrollbar.setValue(self._scrollbar.maximum())

    @Slot()
    def scrollOnePageUp(self) -> None:
        self._scrollbar.triggerAction(
            QAbstractSlider.SliderAction.SliderPageStepSub
        )

    @Slot()
    def scrollOnePageDown(self) -> None:
        self._scrollbar.triggerAction(
            QAbstractSlider.SliderAction.SliderPageStepAdd
        )

    @Slot()
    def scrollOneLineUp(self) -> None:
        self._scrollbar.triggerAction(
            QAbstractSlider.SliderAction.SliderSingleStepSub
        )

    @Slot()
    def scrollOneLineDown(self) -> None:
        self._scrollbar.triggerAction(
            QAbstractSlider.SliderAction.SliderSingleStepAdd
        )
