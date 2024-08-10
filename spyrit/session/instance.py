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
A class that keeps track of the current status of an individual game session,
and maintains its state, independantly of any UI consideration.
"""

import logging

from PySide6.QtCore import QObject, Slot

from spyrit.session.properties import InstanceProperties
from spyrit.ui.dialogs import maybeAskUserIfReadyToClose
from spyrit.ui.instance_ui import InstanceUI


class SessionInstance(QObject):
    """
    If the main game UI can be said to be both a view and controller, then
    an SessionInstance is its associated model.
    """

    _ui: InstanceUI
    _properties: InstanceProperties

    def __init__(
        self,
        parent: QObject,
        instance_ui: InstanceUI,
        properties: InstanceProperties,
    ) -> None:
        super().__init__(parent)

        self._ui = instance_ui
        self._properties = properties

    def title(self) -> str:
        return self._properties.title()

    def connected(self) -> bool:
        return self._properties.isConnected()

    @Slot()
    def maybeClose(self) -> None:
        if not self._properties.isConnected() or maybeAskUserIfReadyToClose(
            self._ui, [self.title()]
        ):
            # This will detach this instance's widget from its parent and should
            # invoke garbage collection.

            self.setParent(None)
            self._ui.setParent(None)

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )
