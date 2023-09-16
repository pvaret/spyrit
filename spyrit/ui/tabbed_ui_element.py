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
The class providing the structure for tabbed UI component, to be used in a
tabbed container main window.
"""


from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QWidget


class TabbedUIElement(QWidget):
    """
    The base class for widgets meant to be contained in a tabbed main window.
    """

    # This signal is emitted when this UI wants to no longer be pinned to its
    # containing window.

    wantToBeUnpinned: Signal = Signal()  # noqa: N815

    # This signal is emitted when this UI wants to be detached from its current
    # containing window and into a new window.

    wantToDetachToNewWindow: Signal = Signal()  # noqa: N815

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Set up the layout of the UI element. Basically a horizontal layout,
        # but in practice we'll just want to add a single widget.

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

    def setWidget(self, widget: QWidget) -> None:
        """
        Sets the UI's main widget.

        Does nothing if there is already a widget set.
        """

        if self.layout().count() > 0:
            return

        self.layout().addWidget(widget)

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
            self.doClose()

    def doClose(self) -> None:
        """
        Actually close this tab unconditionally.
        """

        self.wantToBeUnpinned.emit()
        self.deleteLater()
