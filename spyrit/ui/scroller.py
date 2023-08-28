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


from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QVariantAnimation,
    Slot,
)
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QAbstractSlider, QScrollBar

from spyrit import constants


class Scroller(QObject):
    """
    Manages a scrollbar to make its behavior feel natural and pleasant to users.
    """

    # How long should the scroll animation last, in milliseconds.

    _ANIMATION_DURATION: int = constants.SCROLL_ANIMATION_DURATION_MS

    # Which animation curve should be used for the scrolling.

    _EASING_CURVE: QEasingCurve.Type = QEasingCurve.Type.OutCubic

    _scrollbar: QScrollBar
    _pin_to_bottom: bool = True
    _target_scroll_position: int = 0
    _current_scroll_position: int = 0
    _scroll_animation: QVariantAnimation

    def __init__(self, scrollbar: QScrollBar) -> None:
        super().__init__(parent=scrollbar)

        self._scrollbar = scrollbar

        # Intercept events on the scrollbar with this Scroller so we can handle
        # WheelEvents ourselves, and smoothly.

        scrollbar.installEventFilter(self)

        # Set up the scroll animation properties.

        self._scroll_animation = QVariantAnimation(self)
        self._scroll_animation.setDuration(self._ANIMATION_DURATION)
        self._scroll_animation.setEasingCurve(self._EASING_CURVE)
        self._scroll_animation.valueChanged.connect(
            self._updateSmoothScrollPosition
        )

        # Report value updates continuously, not just at the end of a user
        # motion.

        scrollbar.setTracking(True)

        # Keep track when the user moves the bar in any way, so we can turn the
        # action into a smooth scrolling.

        scrollbar.actionTriggered.connect(self.onUserInitiatedMove)

        # Prevent changes to the scrollbar value not initiated by the Scroller
        # itself.

        scrollbar.valueChanged.connect(self._applyCurrentScrollPosition)

        # Take action, maybe, when the size of the document grows.

        scrollbar.rangeChanged.connect(self.maybeScrollToBottom)

    def smoothScrollToPosition(self, position: int) -> None:
        position = max(self._scrollbar.minimum(), position)
        position = min(self._scrollbar.maximum(), position)

        self._pin_to_bottom = position == self._scrollbar.maximum()

        if position == self._target_scroll_position:
            return

        self._target_scroll_position = position
        self._scroll_animation.setStartValue(self._current_scroll_position)
        self._scroll_animation.setEndValue(position)
        self._scroll_animation.stop()
        self._scroll_animation.start()

    @Slot(QAbstractSlider.SliderAction)
    def onUserInitiatedMove(self, action: QAbstractSlider.SliderAction) -> None:
        # Note that we apply the relative position updates to the current
        # *target* position.

        position = self._target_scroll_position

        # Note that we explicitly cast the action, because Qt actually passes an
        # int here, which Python -- correctly -- doesn't match to a
        # QAbstractSlider.SliderAction value.

        match QAbstractSlider.SliderAction(action):
            case QAbstractSlider.SliderAction.SliderNoAction:
                return

            case QAbstractSlider.SliderAction.SliderMove:
                # We also smooth-scroll when the user is moving the slider
                # directly. This induces a lag on the slider itself, but
                # hopefully this is nevertheless the most pleasant behavior for
                # the user.

                position = self._scrollbar.sliderPosition()

            case QAbstractSlider.SliderAction.SliderSingleStepAdd:
                position += self._scrollbar.singleStep()

            case QAbstractSlider.SliderAction.SliderSingleStepSub:
                position -= self._scrollbar.singleStep()

            case QAbstractSlider.SliderAction.SliderPageStepAdd:
                position += self._scrollbar.pageStep()

            case QAbstractSlider.SliderAction.SliderPageStepSub:
                position -= self._scrollbar.pageStep()

            case QAbstractSlider.SliderAction.SliderToMaximum:
                position = self._scrollbar.maximum()

            case QAbstractSlider.SliderAction.SliderToMinimum:
                position = self._scrollbar.minimum()

        self.smoothScrollToPosition(position)

    @Slot()
    def maybeScrollToBottom(self) -> None:
        if self._pin_to_bottom:
            self.smoothScrollToPosition(self._scrollbar.maximum())

    @Slot()
    def _applyCurrentScrollPosition(self) -> None:
        self._scrollbar.setValue(self._current_scroll_position)

    @Slot(int)
    def _updateSmoothScrollPosition(self, position: int) -> None:
        self._current_scroll_position = position
        self._applyCurrentScrollPosition()

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

    @Slot()
    def scrollToTop(self) -> None:
        self._scrollbar.triggerAction(
            QAbstractSlider.SliderAction.SliderToMinimum
        )

    @Slot()
    def scrollToBottom(self) -> None:
        self._scrollbar.triggerAction(
            QAbstractSlider.SliderAction.SliderToMaximum
        )

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._scrollbar and isinstance(event, QWheelEvent):
            # The default wheel event handler applies the scrolling delta from
            # the current slider position. We want to apply it to the current
            # *target* position. Else scrolling further while a scrolling is
            # already in progress undershoots, and feels sluggish.

            self.smoothScrollToPosition(
                self._target_scroll_position - event.pixelDelta().y()
            )
            return True

        return super().eventFilter(watched, event)
