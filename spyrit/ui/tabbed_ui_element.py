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
The class providing the structure for tabbed UI component, to be used in a
tabbed container main window.
"""

from typing import Optional

from PySide6 import QtCore, QtWidgets


class TabbedUiElement(QtWidgets.QWidget):
    """
    The base class for widgets meant to be contained in a tabbed main window.
    """

    # This signal is emitted when the UI wants its tab title to be updated.

    tabTitleChanged = QtCore.Signal(str)

    # This signal is emitted when the UI wants its containing window's title to
    # be updated.

    windowTitleChanged = QtCore.Signal(str)

    # This signal is emitted when this UI wants to no longer be pinned to its
    # containing window.

    wantToBeUnpinned = QtCore.Signal()

    # This signal is emitted when this UI wants to be detached from its current
    # containing window and into a new window.

    wantToDetachToNewWindow = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:

        super().__init__(parent)

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._tabTitle: str = ""
        self._windowTitle: str = ""

    def tabTitle(self) -> str:

        return self._tabTitle

    def setTabTitle(self, title: str) -> None:

        self._tabTitle = title
        self.tabTitleChanged.emit(title)

    def windowTitle(self) -> str:

        return self._windowTitle

    def setParentWindowTitle(self, title: str) -> None:

        self._windowTitle = title
        self.windowTitleChanged.emit(title)

    def canCloseNow(self) -> bool:
        """
        Override this in subclasses to decide is the UI is ready to close, for
        instance by popping a confirmation dialog.
        """

        return True

    def maybeClose(self) -> None:

        if self.canCloseNow():

            # Unpinning the UI element without reattaching it causes it to
            # close.

            self.wantToBeUnpinned.emit()
