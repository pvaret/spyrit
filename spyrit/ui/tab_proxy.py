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


class TabUpdate:
    """
    Contains the attributes of a desired tab appearance update.
    """

    title: str | None
    color: QColor | None

    def __init__(
        self, title: str | None = None, color: QColor | None = None
    ) -> None:
        self.title = title
        self.color = color


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

    # This signal is emitted when a user action is requesting that this tab be
    # closed.

    closeRequested: Signal = Signal()

    _tab_widget: QTabWidget
    _widget: weakref.ref[QWidget]

    def __init__(self, tab_widget: QTabWidget, widget: QWidget) -> None:
        # Using the widget itself as the parent here guarantees that this
        # TabProxy will be dereferenced when the widget is destroyed, provided
        # nothing else keep a reference to this TabProxy. (Which they
        # shouldn't.)

        super().__init__(parent=widget)

        self._tab_widget = tab_widget
        self._widget = weakref.ref(widget)

        tab_widget.tabCloseRequested.connect(self._maybeRequestClosing)

    def _index(self) -> int:
        """
        Returns the index of the proxied tab.

        Returns:
            The index of the proxied tab in its QTabWidget, or -1 if the tab
            being proxied no longer exists.
        """

        if (widget := self._widget()) is None:
            return -1
        return self._tab_widget.indexOf(widget)

    @Slot(TabUpdate)
    def updateTab(self, update: TabUpdate) -> None:
        """
        Sets the proxied tab's properties based on the contents of the update.
        """

        if update.title is not None:
            self.setTitle(update.title)

        if update.color is not None:
            self.setTextColor(update.color)

    @Slot(str)
    def setTitle(self, title: str) -> None:
        """
        Sets the title of the proxied tab.

        Args:
            title: The title to give this tab.
        """

        self._tab_widget.setTabText(self._index(), title)

    def setTextColor(self, color: QColor | Qt.GlobalColor) -> None:
        """
        Sets the color for the text of the tab's title.

        Args:
            color: The color to use.
        """

        self._tab_widget.tabBar().setTabTextColor(self._index(), color)

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
