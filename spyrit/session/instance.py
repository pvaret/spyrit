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

from PySide6.QtCore import Qt, QObject, Slot
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

    _title: str = ""
    _active: bool = True
    _connected: bool = False
    _pending_lines: int = 0
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

        if title != self._title:
            self._title = title
            if self._tab is not None:
                self._tab.setTitle(self._title)

    @Slot(bool)
    def setActive(self, active: bool) -> None:
        """
        Marks this instance as currently active/inactive, i.e. whether its tab
        is currently the visible one.

        Args:
            active: Whether the instance is active.
        """

        self._active = active
        if active:
            self._pending_lines = 0

        self._updateTabTitle()

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
                    if not self._active:
                        self._pending_lines += 1
                        self._updateTabTitle()

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
            f"({self._pending_lines}) {self._title}"
            if self._pending_lines
            else self._title
        )

        new_color = Qt.GlobalColor.red if self._pending_lines else QColor()

        if self._tab.title() != new_title:
            self._tab.setTitle(new_title)

        if new_color != self._tab.textColor():
            self._tab.setTextColor(new_color)

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )
