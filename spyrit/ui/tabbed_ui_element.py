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
The class providing the structure for tabbed UI component, to be used in a
tabbed container main window.
"""


from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QWidget


class TabbedUiElement(QWidget):
    """
    The base class for widgets meant to be contained in a tabbed main window.
    """

    # This signal is emitted when the UI wants its tab title to be updated.

    tabTitleChanged = Signal(str)  # noqa: N815

    # This signal is emitted when the UI wants its containing window's title to
    # be updated.

    windowTitleChanged = Signal(str)  # noqa: N815

    # This signal is emitted when this UI wants to no longer be pinned to its
    # containing window.

    wantToBeUnpinned = Signal()  # noqa: N815

    # This signal is emitted when this UI wants to be detached from its current
    # containing window and into a new window.

    wantToDetachToNewWindow = Signal()  # noqa: N815

    _tab_title: str
    _window_title: str

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Set up the layour of the UI element. Basically a horizontal layout,
        # but in practice we'll just want to add a single widget.

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        # Keep track of the UI's properties we'll want to propagate.

        self._tab_title = ""
        self._window_title = ""

    def tabTitle(self) -> str:
        """
        Return the currently desired tab title for this UI element.
        """

        return self._tab_title

    def setTabTitle(self, title: str) -> None:
        """
        Set and propagate the currently desired tab title for this UI element.
        """

        self._tab_title = title
        self.tabTitleChanged.emit(title)

    def windowTitle(self) -> str:
        """
        Return the currently desired window title for this UI element.
        """

        return self._window_title

    def setWindowTitle(self, arg__1: str) -> None:
        """
        Set and propagate the currently desired window title for this UI
        element.

        Note that this is an override of the QWidget method.
        """

        self._window_title = arg__1
        self.windowTitleChanged.emit(arg__1)

        super().setWindowTitle(arg__1)

    def canCloseNow(self) -> bool:
        """
        Override this in subclasses to decide is the UI is ready to close, for
        instance by popping a confirmation dialog.
        """

        return True

    def maybeClose(self) -> None:
        """
        Ask this UI element to close itself, politely. It is allowed to decline.
        """

        if self.canCloseNow():
            # Unpinning the UI element without reattaching it causes it to
            # close.

            self.wantToBeUnpinned.emit()
