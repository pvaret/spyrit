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
Class that provides a container for panes that can be switched between with a
sliding animation.
"""


import logging

from PySide6.QtCore import QEasingCurve, Qt, QTimer, QVariantAnimation, Slot
from PySide6.QtGui import QResizeEvent, QWheelEvent
from PySide6.QtWidgets import QFrame, QScrollArea, QSizePolicy, QWidget

from spyrit import constants
from spyrit.ui.base_pane import Pane


class SlidingPaneContainer(QScrollArea):
    """
    A horizontal container for widgets that will take up the full view port and
    can be switched between with a smooth sliding animation.
    """

    # How long should the slide animation last, in milliseconds.

    _ANIMATION_DURATION: int = constants.PANE_ANIMATION_DURATION_MS

    # Which animation curve should be used for the sliding motion.

    _EASING_CURVE: QEasingCurve.Type = QEasingCurve.Type.OutQuad

    _panes: list[Pane]
    _active_pane_index: int
    _x_scroll_enforced_value: int
    _y_scroll_enforced_value: int
    _slide_animation: QVariantAnimation

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Structures to keep track of currently added panes.

        self._panes = []
        self._active_pane_index = -1

        # Set up the view port: no margins, no scrollbars, no focus. (Only child
        # widgets get to have the focus.)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Set up the widget that's going to serve as the parent of our panes.

        self.setWidget(QWidget())
        self._resizeContainer()

        # Set up scrollbar position enforcement. The only reason this widget
        # should ever scroll is if we're switching between panes. This takes a
        # little bit of fiddling.

        self._x_scroll_enforced_value = 0
        self._y_scroll_enforced_value = 0

        self.horizontalScrollBar().valueChanged.connect(
            self._enforceXScrollPosition
        )

        self.verticalScrollBar().valueChanged.connect(
            self._enforceYScrollPosition
        )

        # Pane switching animation setup goes here.

        self._slide_animation = QVariantAnimation()
        self._slide_animation.setEasingCurve(self._EASING_CURVE)
        self._slide_animation.setDuration(self._ANIMATION_DURATION)

        self._slide_animation.valueChanged.connect(
            self._enforceXScrollPositionForValue
        )
        self._slide_animation.stateChanged.connect(
            self._onAnimationMaybeComplete
        )

    def addPaneLeft(self, pane: Pane) -> None:
        """
        Adds the given pane to the left of the current pane, if any.
        """

        index = self._active_pane_index
        self.insertPane(index, pane)
        self.switchToPane(index)

    def addPaneRight(self, pane: Pane) -> None:
        """
        Adds the given pane to the right of the current pane, if any.
        """

        index = self._active_pane_index + 1
        self.insertPane(index, pane)
        self.switchToPane(index)

    def slideLeft(self) -> None:
        """
        Slide the viewport one pane left.
        """
        self.switchToPane(self._active_pane_index - 1)

    def slideRight(self) -> None:
        """
        Slide the viewport one pane right.
        """
        self.switchToPane(self._active_pane_index + 1)

    def insertPane(self, index: int, pane: Pane) -> None:
        """
        Insert the given pane into the viewport at the given index.
        """

        index = max(index, 0)
        index = min(index, len(self))

        # Propagate the pane's minimum size to the container.

        pane_min_size = pane.minimumSizeHint()
        container_min_size = self.minimumSize().expandedTo(pane_min_size)
        self.setMinimumSize(container_min_size)

        # Add the pane to this container.

        pane.setParent(self.widget())
        pane.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Update the current active pane's index if we just inserted a pane to
        # the left of it.

        if not self._panes or index <= self._active_pane_index:
            self._active_pane_index += 1

        self._panes.insert(index, pane)

        # Update the container layout to account for the new pane.

        self._resizeContainer()
        self._layoutPanesInViewport()

        # Plug the pane's controls into the container's controls.

        pane.slideLeftRequested.connect(self.slideLeft)
        pane.slideRightRequested.connect(self.slideRight)
        pane.addPaneLeftRequested.connect(self.addPaneLeft)
        pane.addPaneRightRequested.connect(self.addPaneRight)

        # If there was no pane before, make the newly added pane active.

        if len(self._panes) == 1:
            self._makePaneActive(pane)

        else:
            self._makePaneInactive(pane)

        # And finally, make the pane visible.

        pane.show()

    def switchToPane(self, index: int) -> None:
        """
        Make the pane at the given index the active one, with a sliding animated
        transition.
        """

        index = max(index, 0)
        index = min(index, len(self) - 1)

        if index == self._active_pane_index:
            return

        # Make the current pane inactive. The destination pane will be made
        # active when the animation completes.

        if (pane_from := self._currentActivePane()) is not None:
            self._makePaneInactive(pane_from)

        # If the animation is currently running already, then use its current
        # position as the starting position for a new animation.

        initial_value = float(
            self._active_pane_index
            if not self._isInMotion()
            else self._slide_animation.currentValue()
        )

        self._slide_animation.stop()
        self._slide_animation.setStartValue(initial_value)
        self._slide_animation.setEndValue(float(index))
        self._slide_animation.start()

        # Consider the target pane active right away.

        self._active_pane_index = index

    def _currentActivePane(self) -> Pane | None:
        """
        Returns the widget of the current active pane, if any.
        """
        try:
            return self._panes[self._active_pane_index]
        except IndexError:
            return None

    def _makePaneActive(self, pane: Pane) -> None:
        """
        Set the necessary properties on a pane that is becoming active.
        """

        pane.setEnabled(True)
        pane.setFocus()
        self.setFocusProxy(pane)

        pane.onActive()

    def _makePaneInactive(self, pane: Pane) -> None:
        """
        Set the necessary properties on a pane that is becoming inactive.
        """

        pane.setEnabled(False)

    def _deletePane(self, pane: Pane) -> None:
        """
        Detach a Pane object from this container and set it up to be deleted.
        """

        pane.hide()
        pane.setParent(None)  # type: ignore  # Actually legal.
        pane.deleteLater()

        logging.debug(
            "Pane %s (%s) garbage collected.",
            pane.__class__.__name__,
            hex(id(pane)),
        )

    def _isInMotion(self) -> bool:
        """
        Returns whether a sliding animation is in progress.
        """

        return self._slide_animation.state() == QVariantAnimation.State.Running

    @Slot()
    def _onAnimationMaybeComplete(self) -> None:
        """
        Check if the animation just completed. If so, clean up transient,
        inactive panes.
        """

        if not self._isInMotion():
            # Make the target pane of the switching anination active.

            if (current_pane := self._currentActivePane()) is not None:
                self._makePaneActive(current_pane)

            # Tidy up transient panes that are no longer active.

            self._garbageCollectPanes()

    @Slot()
    def _enforceXScrollPosition(self) -> None:
        """
        Force the horizontal scroll position to be whatever this widget thinks
        it should be. Prevents spurious scrolling.
        """

        if self.horizontalScrollBar().value() != self._x_scroll_enforced_value:
            self.horizontalScrollBar().setValue(self._x_scroll_enforced_value)

    @Slot()
    def _enforceYScrollPosition(self) -> None:
        """
        Force the vertical scroll position to be whatever this widget thinks
        it should be. Prevents spurious scrolling.
        """

        if self.verticalScrollBar().value() != self._y_scroll_enforced_value:
            self.verticalScrollBar().setValue(self._y_scroll_enforced_value)

    @Slot(float)
    def _enforceXScrollPositionForValue(self, value: float) -> None:
        """
        Compute and update the horizontal scroll position based on the given
        value, where the value is a possibly non-integer index into the pane
        list.
        """

        width = self.viewport().size().width()
        self._x_scroll_enforced_value = round(value * width)
        self._enforceXScrollPosition()

    def _resizeContainer(self) -> None:
        """
        Ensures the container widget of the scroll area has the right size to
        show its subwidgets.
        """
        # Note that the *viewport* is the element whose size we care about here.

        size = self.viewport().size()
        self.widget().resize(size.width() * max(len(self), 1), size.height())

    def _garbageCollectPanes(self) -> None:
        """
        Delete the transient panes in this container that are not currently
        active.
        """

        if self._isInMotion():
            # Don't actually garbage collect anything if an animation is in
            # progress. A garbage collection will run at the end of the
            # animation.

            return

        remaining_panes: list[Pane] = []
        current_pane = self._currentActivePane()

        for i, pane in enumerate(self._panes):
            if pane is current_pane or pane.pane_is_persistent:
                remaining_panes.append(pane)
            else:
                self._deletePane(pane)

        self._panes.clear()
        self._active_pane_index = -1

        for i, pane in enumerate(remaining_panes):
            self._panes.append(pane)
            if pane is current_pane:
                self._active_pane_index = i

        self._layoutPanesInViewport()
        self._enforceXScrollPositionForValue(self._active_pane_index)

    def _layoutPanesInViewport(self) -> None:
        """
        Lays out the container's panes in the viewport in order, left to right.
        """
        # Note that the *viewport* is the element whose size we care about here.

        size = self.viewport().size()

        for i, pane in enumerate(self._panes):
            pane.move(size.width() * i, 0)
            pane.resize(size.width(), size.height())

    def resizeEvent(self, arg__1: QResizeEvent) -> None:
        """
        Propagate resize events to the child panes and update the scrollbar
        position to stay fixed relative to the panes.
        """

        self._resizeContainer()
        self._layoutPanesInViewport()

        if not self._isInMotion():
            self._enforceXScrollPositionForValue(self._active_pane_index)

            # WORKAROUND: Qt 6.5.0 doesn't update the scrollbar value if the
            # pane is not currently visible, including if the resize event is
            # because we're switching to the pane right now. So, schedule a
            # scrollbar update for immediately after.

            QTimer.singleShot(0, self._enforceXScrollPosition)  # type: ignore

        super().resizeEvent(arg__1)

    def wheelEvent(self, arg__1: QWheelEvent) -> None:
        """
        Override QScrollArea's mouse wheel handling. We never want to scroll
        this widget from mouse events. Instead, pass down the mouse event to the
        current pane.
        """

        if (current_pane := self._currentActivePane()) is not None:
            current_pane.wheelEvent(arg__1)

    def __len__(self) -> int:
        return len(self._panes)

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )
