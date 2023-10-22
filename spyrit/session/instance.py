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
A class that keeps track of the current status of an individual game session,
independantly of any UI consideration.
"""

import logging

from typing import Iterable, Sequence

from PySide6.QtCore import Qt, QObject, Signal, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMessageBox, QPushButton, QWidget

from spyrit.network.connection import Status
from spyrit.network.fragments import (
    FlowControlCode,
    FlowControlFragment,
    Fragment,
    FragmentList,
    NetworkFragment,
)
from spyrit.ui.tab_proxy import TabProxy


def askUserIfReadyToClose(
    window: QWidget | None, instances: Sequence["SessionInstance"]
) -> bool:
    """
    Asks the user to confirm they are really ready to close still connected
    games.

    Args:
        window: The widget to use as the message box's parent.

        instances: The game instances to ask the user about.

    Returns:
        Whether the user accepted to close the connected games.
    """

    dialog = QMessageBox(window)
    dialog.setIcon(QMessageBox.Icon.Question)
    dialog.setWindowTitle("Really close?")
    dialog.setTextFormat(Qt.TextFormat.RichText)

    if len(instances) == 1:
        dialog.setText(
            f"You are still connected to <b>{instances[0].title()}</b>."
            " Really close?"
        )
    else:
        dialog.setText(
            "You are still connected to the following games:<br>"
            + "".join(
                f"<b> • {instance.title()}</b><br>" for instance in instances
            )
            + "<br>"
            + "Really close?"
        )

    dialog.addButton(
        close := QPushButton("Close"), QMessageBox.ButtonRole.AcceptRole
    )
    dialog.addButton(
        cancel := QPushButton("Cancel"), QMessageBox.ButtonRole.RejectRole
    )
    dialog.setDefaultButton(cancel)

    dialog.exec()

    return dialog.clickedButton() is close


class SessionInstance(QObject):
    """
    If the main game UI can be said to be both a view and controller, then
    an SessionInstance is its associated model.
    """

    # This signal is emitted when the number of unread lines in this instance
    # changes, one way or another.

    unreadLinesChanged: Signal = Signal()  # noqa: N815

    _title: str = ""
    _active: bool = True
    _focused: bool = True
    _connected: bool = False
    _unread_lines: int = 0
    _tab: TabProxy | None = None

    def setTab(self, tab: TabProxy) -> None:
        """
        Attaches this SessionInstance to the given TabProxy.

        Args:
            tab: The TabProxy that this SessionInstance will use to update the
                tab's status.
        """

        self._tab = tab

        tab.active.connect(self.setActive)
        tab.closeRequested.connect(self.maybeCloseTab)

    def title(self) -> str:
        """
        Gets the title of the instance, e.g. so it can be applied to the tab.

        Returns:
            The current title for the instance.
        """

        return self._title

    def setTitle(self, title: str) -> None:
        """
        Sets the title for this instance.

        Args:
            title: The title to be set.
        """

        self._title = title
        self._updateTabTitle()

    @Slot(bool)
    def setActive(self, active: bool) -> None:
        """
        Marks this instance as currently active/inactive, i.e. whether its tab
        is currently the visible one.

        Args:
            active: Whether the instance is active.
        """

        self._active = active
        self._updateUnreadLineCount()

    @Slot(bool)
    def setFocused(self, focused: bool) -> None:
        """
        Records whether the window this instance is in currently has the desktop
        focus.

        Args:
            focused: Whether the window is focused.
        """

        self._focused = focused
        self._updateUnreadLineCount()

    def unreadLines(self) -> int:
        """
        Returns the number of unread lines of game text in this instance.

        Returns:
            A number of lines.
        """

        return self._unread_lines

    def _updateUnreadLineCount(self, delta: int = 0) -> None:
        """
        Updates the current count of unread lines in this instance.

        If the instance is the active tab in a focused window, then the current
        count is set to 0.

        Else the given delta is added to the current unread line count.

        Args:
            delta: The number of new unread lines.
        """

        if self._active and self._focused:
            self._unread_lines = 0
        else:
            self._unread_lines += delta

        self._updateTabTitle()

        self.unreadLinesChanged.emit()

    @Slot(FragmentList)
    def updateStateFromFragments(self, fragments: Iterable[Fragment]) -> None:
        """
        Consumes a stream of Fragments to update the internal state of this
        instance.

        Args:
            fragments: An iterable of Fragments, from which to infer updates to
                the instance's state.
        """

        for fragment in fragments:
            match fragment:
                case NetworkFragment(event):
                    self._connected = event == Status.CONNECTED

                case FlowControlFragment(code=FlowControlCode.LF):
                    self._updateUnreadLineCount(delta=1)

                case _:
                    pass

    def connected(self) -> bool:
        """
        Returns whether this instance is currently connected to a game.

        Returns:
            Whether this instance is connected.
        """

        return self._connected

    @Slot()
    def maybeCloseTab(self) -> None:
        """
        Closes the tab for this instance. If the tab is for a game with an
        active connection, asks the user for confirmation first.
        """

        if (tab := self._tab) is None:
            return

        if not self._connected or askUserIfReadyToClose(tab.window(), [self]):
            tab.close()

    def _updateTabTitle(self) -> None:
        """
        Updates the tab's title and text color based on the instance title and
        the number of unread lines, if any.
        """

        if self._tab is None:
            return

        new_title = (
            f"({self._unread_lines}) {self._title}"
            if self._unread_lines
            else self._title
        )

        new_color = Qt.GlobalColor.red if self._unread_lines else QColor()

        if self._tab.title() != new_title:
            self._tab.setTitle(new_title)

        if new_color != self._tab.textColor():
            self._tab.setTextColor(new_color)

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )
