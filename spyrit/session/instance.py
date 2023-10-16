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

from typing import Iterable

from PySide6.QtCore import QObject, Slot

from spyrit.network.connection import Status
from spyrit.network.fragments import Fragment, FragmentList, NetworkFragment
from spyrit.ui.main_window import TabProxy


class SessionInstance(QObject):
    """
    If the main game UI can be said to be both a view and controller, then
    an SessionInstance is its associated model.
    """

    _title: str = ""
    _active: bool = False
    _connected: bool = False
    _tab: TabProxy | None = None

    def setTab(self, tab: TabProxy) -> None:
        """
        Attaches this SessionInstance to the given TabProxy.

        Args:
            tab: The TabProxy that this SessionInstance will use to update the
                tab's status.
        """

        self._tab = tab

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
                case _:
                    pass

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )
