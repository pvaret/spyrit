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

from PySide6.QtCore import QEasingCurve, QVariantAnimation, Slot
from PySide6.QtWidgets import QScrollBar

from spyrit import constants


class SmoothScrollbarProxy(QScrollBar):
    # How long should the scroll animation last, in milliseconds.

    _ANIMATION_DURATION: int = constants.SCROLL_ANIMATION_DURATION_MS

    # Which animation curve should be used for the scrolling.

    _EASING_CURVE: QEasingCurve.Type = QEasingCurve.Type.OutCubic

    _proxied_scrollbar: QScrollBar
    _current_proxied_value: int
    _target_proxied_value: int

    def __init__(self, proxied_scrollbar: QScrollBar) -> None:
        super().__init__(proxied_scrollbar.orientation(), parent=proxied_scrollbar)

        self._proxied_scrollbar = proxied_scrollbar
        self._proxied_scrollbar.setVisible(False)
        self._current_proxied_value = self._proxied_scrollbar.value()
        self._target_proxied_value = self._current_proxied_value

        # Set up the scroll animation properties.

        self._scroll_animation = QVariantAnimation(self)
        self._scroll_animation.setDuration(self._ANIMATION_DURATION)
        self._scroll_animation.setEasingCurve(self._EASING_CURVE)
        self._scroll_animation.valueChanged.connect(self._setCurrentProxiedValue)

        # Plug the proxied scrollbar's properties into this one.

        self.setRange(
            self._proxied_scrollbar.minimum(), self._proxied_scrollbar.maximum()
        )
        self.setValue(self._current_proxied_value)
        self.valueChanged.connect(self._setTargetProxiedValue)

        self._proxied_scrollbar.rangeChanged.connect(self.setRange)
        self._proxied_scrollbar.valueChanged.connect(self._onProxiedValueChanged)

    @Slot(int)
    def setValue(self, value: int) -> None:
        value = max(value, self.minimum())
        value = min(value, self.maximum())

        self._setTargetProxiedValue(value)

        super().setValue(value)

    @Slot(int, int)
    def setRange(self, minimum: int, maximum: int) -> None:
        # Update the steps when the range changes, since the range could be changing
        # because the viewport was resized.

        self.setPageStep(self._proxied_scrollbar.pageStep())
        self.setSingleStep(self._proxied_scrollbar.singleStep())

        super().setRange(minimum, maximum)

    @Slot(int)
    def _onProxiedValueChanged(self, value: int) -> None:
        if value == self._current_proxied_value:
            return

        # Pin the proxied scrollbar to the value we want it to have, but reflect its
        # attempted value change onto this scrollbar.

        delta = value - self._current_proxied_value
        self._proxied_scrollbar.setValue(self._current_proxied_value)

        new_value = self._target_proxied_value + delta

        self.setValue(new_value)

    @Slot(int)
    def _setCurrentProxiedValue(self, value: int | None) -> None:
        if value is not None and value != self._current_proxied_value:
            self._current_proxied_value = value
            self._proxied_scrollbar.setValue(value)

    @Slot(int)
    def _setTargetProxiedValue(self, value: int) -> None:
        if value != self._target_proxied_value:
            self._target_proxied_value = value

            self._scroll_animation.stop()
            self._scroll_animation.setStartValue(self._current_proxied_value)
            self._scroll_animation.setEndValue(self._target_proxied_value)
            self._scroll_animation.start()
