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
Provides facilities to record the properties of a game session that are relevant
across all the actors involved in the session.
"""

from PySide6.QtCore import QObject, Slot

from spyrit.network.connection import Status
from spyrit.settings.spyrit_settings import SpyritSettings


class InstanceProperties(QObject):
    _world_name: str
    _character_name: str
    _connection_status: Status

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self.reset()

    def setWorldName(self, name: str) -> None:
        self._world_name = name

    def worldName(self) -> str:
        return self._world_name

    def setCharacterName(self, name: str) -> None:
        self._character_name = name

    def characterName(self) -> str:
        return self._character_name

    def title(self) -> str:
        character = self.characterName()
        world = self.worldName()

        if character:
            return f"{character} ({world})"

        return world

    def blockTitle(self) -> str:
        character = self.characterName()
        world = self.worldName()

        if character:
            return f"{character}\n{world}"

        return world

    @Slot(Status)
    def updateConnectionStatus(self, status: Status) -> None:
        self._connection_status = status

    def isConnected(self) -> bool:
        return self._connection_status == Status.CONNECTED

    def setPropertiesFromSettings(self, settings: SpyritSettings) -> None:

        if settings.isCharacter():
            self.setCharacterName(settings.login.name.get())

        if settings.isCharacter() or settings.isWorld():
            world = settings.name.get()
            if not world:
                server = settings.net.server.get()
                port = settings.net.port.get()
                world = f"{server}:{port}"

            self.setWorldName(world)

    @Slot()
    def reset(self) -> None:
        self.setWorldName("")
        self.setCharacterName("")
        self.updateConnectionStatus(Status.DISCONNECTED)
