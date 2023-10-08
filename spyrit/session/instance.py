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

from PySide6.QtCore import QObject, Signal, Slot

from spyrit.network.connection import Status
from spyrit.network.fragments import Fragment, FragmentList, NetworkFragment


class SessionInstance(QObject):
    """
    If the main game UI can be said to be both a view and controller, then
    an SessionInstance is its associated model.
    """

    # This signal fires when the instance's title is updated.

    titleChanged: Signal = Signal(str)  # noqa: N815

    _title: str = ""
    _active: bool = False
    _connected: bool = False

    def title(self) -> str:
        return self._title

    def setTitle(self, title: str) -> None:
        if title != self._title:
            self._title = title
            self.titleChanged.emit(title)

    @Slot(bool)
    def setActive(self, active: bool) -> None:
        self._active = active

    @Slot(FragmentList)
    def updateStateFromFragments(self, fragments: list[Fragment]) -> None:
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
