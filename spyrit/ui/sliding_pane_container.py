# Copyright (c) 2007-2022 Pascal Varet <p.varet@gmail.com>
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
Class that provides a container for sliding panes.
"""

from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets

from spyrit import constants
from spyrit.safe_signal import safe_signal


class SlidingPaneContainer(QtWidgets.QScrollArea):
    """
    A horizontal container for widgets that will take up the full view port and
    can be switched between with a smooth animation.
    """

    # How long should the switch animation last, in milliseconds.

    _ANIMATION_DURATION = constants.ANIMATION_DURATION_MS

    # Which animation should be used for the switch.

    _EASING_CURVE = QtCore.QEasingCurve.OutCubic

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:

        super().__init__(parent)

        # Structures to keep track of currently added panes.

        self._panes: list[QtWidgets.QWidget] = []
        self._active_pane = 0

        # Set up the view port: no margins, no scrollbars.

        self.setViewportMargins(0, 0, 0, 0)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # Set up the widget that's going to serve as the parent of our panes.

        container = QtWidgets.QWidget()
        container.resize(self.viewport().size())

        self.setWidget(container)

        # Set up scrollbar position enforcement. The only reason this widget
        # should ever scroll is if we're switching between panes. This takes a
        # little bit of fiddling.

        self._x_scroll_enforced_value = 0
        self._y_scroll_enforced_value = 0

        safe_signal(self.horizontalScrollBar(), "valueChanged").connect(
            self._enforceXScrollValue
        )

        safe_signal(self.verticalScrollBar(), "valueChanged").connect(
            self._enforceYScrollValue
        )

        # Pane animation setup goes here.

        self._pane_switch_animation = QtCore.QVariantAnimation()
        self._pane_switch_animation.setEasingCurve(self._EASING_CURVE)
        self._pane_switch_animation.setDuration(self._ANIMATION_DURATION)

        safe_signal(self._pane_switch_animation, "valueChanged").connect(
            self._updateXScrollValueFromAnimation
        )

    def tick(self):

        if self._panes:
            self.switchToPane((self._active_pane + 1) % len(self._panes))

    def append(self, pane: QtWidgets.QWidget) -> None:
        """
        Add a new pane at the end of the existing set of panes, and update
        geometry accordingly.
        """

        width, height = (
            self.viewport().size().width(),
            self.viewport().size().height(),
        )

        pane.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
            )
        )

        pane.setParent(self.widget())
        pane.resize(width, height)
        pane.move(width * len(self._panes), 0)

        self._panes.append(pane)

    def switchToPane(self, i: int) -> None:
        """
        Make the given pane the active one, with an animated transition.
        """

        if i < 0 or i >= len(self._panes):
            return

        # If the animation is currently running already, then use its current
        # position as the starting position for a new animation.

        initial_value = (
            float(self._active_pane)
            if (
                self._pane_switch_animation.state()
                == QtCore.QVariantAnimation.State.Stopped
            )
            else self._pane_switch_animation.currentValue()
        )

        self._pane_switch_animation.stop()
        self._pane_switch_animation.setStartValue(initial_value)
        self._pane_switch_animation.setEndValue(float(i))
        self._pane_switch_animation.start()

        # Consider the target pane active right away.

        self._active_pane = i

    def _enforceXScrollValue(self) -> None:
        """
        Force the horizontal scroll position to be whatever this widget thinks
        it should be. Prevents spurious scrolling.
        """

        if self.horizontalScrollBar().value() != self._x_scroll_enforced_value:
            self.horizontalScrollBar().setValue(self._x_scroll_enforced_value)

    def _enforceYScrollValue(self) -> None:
        """
        Force the vertical scroll position to be whatever this widget thinks
        it should be. Prevents spurious scrolling.
        """

        if self.verticalScrollBar().value() != self._y_scroll_enforced_value:
            self.verticalScrollBar().setValue(self._y_scroll_enforced_value)

    def _updateXScrollValueFromAnimation(self, value: float) -> None:
        """
        Compute and update the horizontal scroll position based on the value
        emitted by an ongoing animation.
        """

        width = self.viewport().size().width()
        self._x_scroll_enforced_value = int(value * width)
        self._enforceXScrollValue()

    def resizeEvent(self, arg__1: QtGui.QResizeEvent) -> None:
        """
        Propagate resize events to the child panes and update the scrollbar
        position to stay fixed relative to the panes.
        """

        # Note that the *viewport* is the element whose size we care about here.

        width, height = (
            self.viewport().size().width(),
            self.viewport().size().height(),
        )

        if self._panes:
            self.widget().resize(width * len(self._panes), height)

        for i, pane in enumerate(self._panes):
            pane.resize(width, height)
            pane.move(i * width, 0)

        if (
            self._pane_switch_animation.state()
            == QtCore.QVariantAnimation.State.Stopped
        ):
            self._x_scroll_enforced_value = self._active_pane * width
            self._enforceXScrollValue()

        super().resizeEvent(arg__1)

    def wheelEvent(self, arg__1: QtGui.QWheelEvent) -> None:
        """
        Override QScrollArea's mouse wheel handling. We never want to scroll
        this widget from mouse events. Instead, pass down the mouse event to the
        current pane.
        """

        if self._panes:
            self._panes[self._active_pane].wheelEvent(arg__1)
