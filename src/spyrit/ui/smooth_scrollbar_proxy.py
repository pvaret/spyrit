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
SmoothScrollbarProxy is a specialized scrollbar that remotely pilots another scrollbar
using a smooth scrolling animation.
"""

from PySide6.QtCore import QEasingCurve, QSignalBlocker, QVariantAnimation, Slot
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QScrollBar

from spyrit import constants


class SmoothScrollbarProxy(QScrollBar):
    # How long should the scroll animation last, in milliseconds.

    _ANIMATION_DURATION: int = constants.SCROLL_ANIMATION_DURATION_MS

    # Which animation curve should be used for the scrolling.

    _EASING_CURVE: QEasingCurve.Type = QEasingCurve.Type.OutCubic

    _document: QTextDocument
    _proxied_scrollbar: QScrollBar
    _proxied_value: int
    _target_proxied_value: int
    _previous_document_length: float

    def __init__(self, proxied_scrollbar: QScrollBar, document: QTextDocument) -> None:
        super().__init__(proxied_scrollbar.orientation(), parent=proxied_scrollbar)

        self._document = document
        self._proxied_scrollbar = proxied_scrollbar
        self._proxied_scrollbar.setVisible(False)
        self._target_proxied_value = self._proxied_value = (
            self._proxied_scrollbar.value()
        )
        self._previous_document_length = 0

        # Set up the scroll animation properties.

        self._scroll_animation = QVariantAnimation(self)
        self._scroll_animation.setDuration(self._ANIMATION_DURATION)
        self._scroll_animation.setEasingCurve(self._EASING_CURVE)
        self._scroll_animation.valueChanged.connect(self._enforceProxiedValue)

        # Plug the proxied scrollbar's properties into this one.

        self.setRange(
            self._proxied_scrollbar.minimum(), self._proxied_scrollbar.maximum()
        )
        self.setValue(self._proxied_value)
        self.valueChanged.connect(self._startSmoothProxyScrollToValue)

        self._proxied_scrollbar.rangeChanged.connect(self._updateRangeFromProxied)
        self._proxied_scrollbar.valueChanged.connect(self._onProxiedValueChanged)

    @Slot(int)
    def setValue(self, value: int) -> None:
        if value == self.value():
            return

        value = max(value, self.minimum())
        value = min(value, self.maximum())

        self._startSmoothProxyScrollToValue(value)

        super().setValue(value)

    @Slot(int, int)
    def _updateRangeFromProxied(self, minimum: int, maximum: int) -> None:
        # Reflect any step value change onto this scrollbar.

        self.setPageStep(self._proxied_scrollbar.pageStep())
        self.setSingleStep(self._proxied_scrollbar.singleStep())

        # The range of a text edit scrollbar may change for two reasons: the document
        # length has changed, or the viewport size has changed. We need to handle these
        # scenarios individually.

        document_length = self._document.size().height()

        if document_length == self._previous_document_length:
            # This is a viewport resize. We update the scrollbar values so that they
            # remain fixed relative to the bottom of the document.

            delta = maximum - self.maximum()

            self._enforceProxiedValue(self._proxied_value + delta)
            self._target_proxied_value += delta

            # Also update the smooth scroll animation parameters so that the scrolling
            # ends at the same relative position in the document it would have before
            # the resizing.

            if self._scroll_animation.state() == QVariantAnimation.State.Running:
                with QSignalBlocker(self._scroll_animation):
                    # Update the animation in one go, not allowing it to send signals
                    # until it's fully up to date.
                    self._scroll_animation.setStartValue(
                        self._scroll_animation.startValue() + delta
                    )
                    self._scroll_animation.setEndValue(
                        self._scroll_animation.endValue() + delta
                    )

        else:
            # This is a document length change. No special handling required.
            self._previous_document_length = document_length

        self.setRange(minimum, maximum)
        if self.value() != self._target_proxied_value:
            super().setValue(self._target_proxied_value)

    @Slot(int)
    def _onProxiedValueChanged(self, value: int) -> None:
        if value == self._proxied_value:
            return

        # Pin the proxied scrollbar to the value we want it to have, but reflect its
        # attempted value change onto this scrollbar.

        self._proxied_scrollbar.setValue(self._proxied_value)

        delta = value - self._proxied_value
        new_value = self._target_proxied_value + delta

        self.setValue(new_value)

    @Slot(int)
    def _enforceProxiedValue(self, value: int | None) -> None:
        if value is not None and value != self._proxied_value:
            self._proxied_value = value
            self._proxied_scrollbar.setValue(value)

    @Slot(int)
    def _startSmoothProxyScrollToValue(self, value: int) -> None:
        if value != self._target_proxied_value:
            self._target_proxied_value = value

            self._scroll_animation.stop()
            self._scroll_animation.setStartValue(self._proxied_value)
            self._scroll_animation.setEndValue(self._target_proxied_value)
            self._scroll_animation.start()
