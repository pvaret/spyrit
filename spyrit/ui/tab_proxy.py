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
Implements a class that provides direct access to the properties of a single tab
in a QTabWidget.
"""

import weakref

from PySide6.QtCore import QObject, QTimer, Qt, Signal, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTabWidget, QWidget


class TabProxy(QObject):
    """
    This class provides an interface to directly set properties on a tab
    associated with a widget. It keeps a reference to the tab, but not the
    widget itself.

    Args:
        tab_widget: The QTabWidget instance that the tab being proxied belongs
            to.

        widget: The widget associated with the tab being proxied.
    """

    # This signal is emitted when the proxied tab becomes active or,
    # respectively, inactive.

    active: Signal = Signal(bool)

    # This signal is emitted when a user action is requesting that this tab be
    # closed.

    closeRequested: Signal = Signal()

    _tab_widget: QTabWidget
    _widget: weakref.ref[QWidget]
    _active: bool = False

    def __init__(self, tab_widget: QTabWidget, widget: QWidget) -> None:
        # Using the widget itself as the parent here guarantees that this
        # TabProxy will be dereferenced when the widget is destroyed, provided
        # nothing else keep a reference to this TabProxy. (Which they
        # shouldn't.)

        super().__init__(parent=widget)

        self._tab_widget = tab_widget
        self._widget = weakref.ref(widget)

        self._setActiveIndex(tab_widget.currentIndex())
        tab_widget.currentChanged.connect(self._setActiveIndex)
        tab_widget.tabCloseRequested.connect(self._maybeRequestClosing)

    def _index(self) -> int:
        """
        Returns the index of the proxied tab.

        Returns:
            The index of the proxied tab in its QTabWidget, or -1 if the tab
            being proxied no longer exists.
        """

        widget = self._widget()
        if widget is None:
            return -1
        return self._tab_widget.indexOf(widget)

    @Slot(str)
    def setTitle(self, title: str) -> None:
        """
        Sets the title of the proxied tab.

        Args:
            title: The title to give this tab.
        """

        if (index := self._index()) >= 0:
            self._tab_widget.setTabText(index, title)

    def title(self) -> str:
        """
        Returns the current title of this tab.

        Returns:
            The tab's title.
        """

        return self._tab_widget.tabText(self._index())

    def setTextColor(self, color: QColor | Qt.GlobalColor) -> None:
        """
        Sets the color for the text of the tab's title.

        Args:
            color: The color to use.
        """

        self._tab_widget.tabBar().setTabTextColor(self._index(), color)

    def textColor(self) -> QColor:
        """
        Returns the color of the text in the tab's title.

        Returns:
            The text color in question.
        """

        return self._tab_widget.tabBar().tabTextColor(self._index())

    def window(self) -> QWidget | None:
        """
        Returns the toplevel window object for this tab's widget, if any.

        Returns:
            A toplevel widget if one exists for this tab, else None.
        """

        if (widget := self._widget()) is not None:
            return widget.window()

        return None

    def close(self) -> None:
        """
        Detaches this tab's widget from its parent. Causes the widget -- and
        therefore this tab -- to be garbage collected, if nothing else is
        keeping a reference to it. Which it shouldn't.
        """

        if (widget := self._widget()) is not None:
            widget.setParent(None)  # type: ignore

    @Slot(int)
    def _setActiveIndex(self, active_index: int) -> None:
        """
        Updates this TabProxy's activity status based on the provided current
        active tab index and this tab's index.

        Args:
            active_index: The index of the tab that just became active.
        """

        active = active_index == self._index()
        if active != self._active:
            self._active = active
            self.active.emit(active)

    @Slot(int)
    def _maybeRequestClosing(self, index: int) -> None:
        """
        Request closing this tab if the given index is that of this tab.

        Args:
            index: The index of the tab to be closed.
        """

        if index == self._index():
            # Note that we don't execute the closing immediately. If we did then
            # the index of next tabs would change before the processing of the
            # signal that triggered this slot is complete, which may cause other
            # tabs to be unexpectedly closed.

            QTimer.singleShot(0, self.closeRequested.emit)  # type: ignore
