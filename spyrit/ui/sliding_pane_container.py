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

    _ANIMATION_DURATION: int = constants.ANIMATION_DURATION_MS

    # Which animation should be used for the switch.

    _EASING_CURVE: QtCore.QEasingCurve.Type = QtCore.QEasingCurve.Type.OutCubic

    _panes: list[QtWidgets.QWidget]
    _pending_cleanup: list[QtWidgets.QWidget]
    _active_pane: int
    _x_scroll_enforced_value: int
    _y_scroll_enforced_value: int
    _pane_switch_animation: QtCore.QVariantAnimation

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        # Structures to keep track of currently added panes.

        self._panes = []
        self._pending_cleanup = []
        self._active_pane = 0

        # Set up the view port: no margins, no scrollbars.

        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # Set up the widget that's going to serve as the parent of our panes.

        self.setWidget(QtWidgets.QWidget())
        self._resizeContainer()

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
        safe_signal(self._pane_switch_animation, "valueChanged").connect(
            self._onMotionMaybeComplete
        )

    def append(self, pane: QtWidgets.QWidget, switch: bool = True) -> None:
        """
        Add a new pane at the end of the existing set of panes, and update
        geometry accordingly.
        """

        # Install on all widgets and sub-widgets in the pane the event filter
        # that disables clicks while an animation is in progress.

        self._installEventFilterRecursively(pane)

        # Add the pane to this container.

        self._panes.append(pane)
        pane.setParent(self.widget())

        # Set up the geometry of the pane.

        width, height = (
            self.viewport().size().width(),
            self.viewport().size().height(),
        )

        pane.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Fixed,
                QtWidgets.QSizePolicy.Policy.Fixed,
            )
        )
        pane.resize(width, height)
        pane.move(width * (self._indexOfLastPane()), 0)

        # Resize the container to account for the new pane.

        self._resizeContainer()

        # And make the pane visible.

        pane.show()

        if switch:
            self.switchToPane(self._indexOfLastPane())

    def pop(self) -> None:
        """
        Remove the rightmost pane, scrolling to the left as needed.

        This will not remove the last remaining pane.
        """
        if len(self._panes) <= 1:
            return

        self._pending_cleanup.append(self._panes.pop())

        if self._active_pane > self._indexOfLastPane():
            self.switchToPane(self._indexOfLastPane())
        else:
            self._cleanupRemovedPanes()

    def switchToPane(self, i: int) -> None:
        """
        Make the given pane the active one, with an animated transition.
        """

        if i < 0 or i > self._indexOfLastPane():
            return

        if i == self._active_pane:
            return

        # If the animation is currently running already, then use its current
        # position as the starting position for a new animation.

        initial_value = float(
            self._active_pane
            if not self._isInMotion()
            else self._pane_switch_animation.currentValue()
        )

        self._pane_switch_animation.stop()
        self._pane_switch_animation.setStartValue(initial_value)
        self._pane_switch_animation.setEndValue(float(i))
        self._pane_switch_animation.start()

        # Consider the target pane active right away.

        self._active_pane = i

    def _isInMotion(self) -> bool:
        """
        Returns whether a sliding animation is in progress.
        """

        return (
            not self._pane_switch_animation.state()
            == QtCore.QVariantAnimation.State.Stopped
        )

    def _indexOfLastPane(self) -> int:
        """
        Computes the index of the rightmost pane held on this container.

        If there are no widgets, returns -1.
        """

        return len(self._panes) - 1

    def _onMotionMaybeComplete(self, value: float) -> None:
        """
        Check if the animation just completed. If so, clean up removed panes.
        """

        if (
            self._isInMotion()
            and value == self._pane_switch_animation.endValue()
        ):
            self._cleanupRemovedPanes()

    def _cleanupRemovedPanes(self) -> None:
        """
        Clean up the panes that were popped from this container.
        """

        while self._pending_cleanup:
            pane = self._pending_cleanup.pop()
            pane.hide()
            pane.setParent(None)  # type: ignore  # Actually legal.
            pane.deleteLater()
        self._resizeContainer()

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

        self._resizeContainer()

        # Note that the *viewport* is the element whose size we care about here.

        width, height = (
            self.viewport().size().width(),
            self.viewport().size().height(),
        )

        # Note that we also resize the widgets that are about to be cleaned up.
        # Until they are, in fact, cleaned up, they're still there.

        for i, pane in enumerate(self._panes + self._pending_cleanup[::-1]):
            pane.resize(width, height)
            pane.move(i * width, 0)

        if not self._isInMotion():
            self._x_scroll_enforced_value = self._active_pane * width
            self._enforceXScrollValue()

        super().resizeEvent(arg__1)

    def _resizeContainer(self) -> None:
        """
        Ensures the container widget of the scroll area has the right size to
        show its subwidgets.
        """
        # Note that the *viewport* is the element whose size we care about here.

        width, height = (
            self.viewport().size().width(),
            self.viewport().size().height(),
        )

        if self._panes:
            self.widget().resize(
                width * max(len(self._panes) + len(self._pending_cleanup), 1),
                height,
            )

    def wheelEvent(self, arg__1: QtGui.QWheelEvent) -> None:
        """
        Override QScrollArea's mouse wheel handling. We never want to scroll
        this widget from mouse events. Instead, pass down the mouse event to the
        current pane.
        """

        if self._panes:
            self._panes[self._active_pane].wheelEvent(arg__1)

    def _installEventFilterRecursively(self, widget: QtWidgets.QWidget) -> None:
        """
        Set up our mouse-filtering event filter in all subchildren of the given
        widget.
        """
        widget.installEventFilter(self)
        for child in widget.children():
            if isinstance(child, QtWidgets.QWidget):
                self._installEventFilterRecursively(child)

    def eventFilter(
        self, arg__1: QtCore.QObject, arg__2: QtCore.QEvent
    ) -> bool:
        """
        Only pass down clicks if we are not currently scrolling.
        """
        if arg__2.type() in (
            QtCore.QEvent.Type.MouseButtonPress,
            QtCore.QEvent.Type.MouseButtonRelease,
            QtCore.QEvent.Type.MouseButtonDblClick,
        ):
            if self._isInMotion():
                return True  # Eat the event.
        return super().eventFilter(arg__1, arg__2)
