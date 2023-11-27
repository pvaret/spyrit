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
Implements a base class that provides the common functionality between panes
contained in a SlidingPaneContainer.
"""


from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class Pane(QWidget):
    """
    Base class for widget that go into a SlidingPaneContainer.
    """

    # These signals allow this pane to request that a new pane is added to the
    # parent container, respectively to the left and to the right of this
    # container.

    addPaneLeftRequested: Signal = Signal(QWidget)
    addPaneRightRequested: Signal = Signal(QWidget)

    # These signals allow this pane to request that the container makes the
    # pane to the left or, respectively, to the right of this one, the
    # currently visible pane.

    slideLeftRequested: Signal = Signal()
    slideRightRequested: Signal = Signal()

    # Whether the Pane will be garbage-collected when out of view.

    pane_is_persistent: bool = False

    def addPaneLeft(self, pane: "Pane") -> None:
        """
        Request that the given pane be inserted to the left of this one.
        """
        self.addPaneLeftRequested.emit(pane)

    def addPaneRight(self, pane: "Pane") -> None:
        """
        Request that the given pane be inserted to the right of this one.
        """
        self.addPaneRightRequested.emit(pane)

    def slideLeft(self) -> None:
        """
        Request that the container slides to the pane to the left of this one.
        """
        self.slideLeftRequested.emit()

    def slideRight(self) -> None:
        """
        Request that the container slides to the pane to the right of this one.
        """
        self.slideRightRequested.emit()

    def onActive(self) -> None:
        """
        This method is called by the pane container when this pane becomes
        active. Override in subclasses that need to take action when that
        happens.
        """
