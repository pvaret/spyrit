# Copyright (c) 2007-2021 Pascal Varet <p.varet@gmail.com>
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

#
# This file holds the WorldsManager class, which manages world properties and
# looks up, creates or deletes world configuration objects.
#


from typing import Optional

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject

# TODO: Using BaseNode directly kind of sucks. Find a way to make this cleaner?
# Settings "derived" from the root setting graph should be accessible through a
# dedicated API, without poking at the low-level details of settings Nodes.
# from settings.Settings import BaseNode
from SpyritSettings import WORLDS
from Utilities import normalize_text
from World import World


class WorldsSettings:
    """
    This class encapsulates the deep knowledge about settings objects that
    WorldsManager requires.
    """

    def __init__(self, settings, state):

        self.settings = settings[WORLDS]
        self.state = state[WORLDS]

    def getAllWorldSettings(self):

        return self.settings.nodes.values()

    def newWorldSettings(self):

        # TODO: Add createSection() to nodes that would do the right thing?
        return self.settings.proto.build("*", self.settings)

    def newWorldState(self):

        return self.state.proto.build("*", self.state)

    def lookupStateForSettings(self, settings):

        if settings._name:
            key = normalize_text(settings._name)
            if key in self.state:
                return self.state[key]

        return self.newWorldState()

    def saveWorldSettings(self, key, settings, state):

        # TODO: Guarantee unicity?
        self.settings.nodes[key] = settings
        self.state.nodes[key] = state


class WorldsManager(QObject):

    worldListChanged = pyqtSignal()

    def __init__(self, settings, state):

        super().__init__()

        self.ws = WorldsSettings(settings, state)

        # Safety measure: ensure all worlds have a valid name.
        n = 0

        for settings in self.ws.getAllWorldSettings():

            if not settings._name:
                n += 1
                settings._name = "(Unnamed %d)" % n

        self.generateMappings()

    def generateMappings(self):

        # Provide mappings to lookup worlds based on their name and based on
        # their (host, port) connection pair.

        self.name_mapping = dict(
            (self.normalize(settings._name), settings)
            for settings in self.ws.getAllWorldSettings()
        )

        self.hostport_mapping = {}

        for settings in self.ws.getAllWorldSettings():
            self.hostport_mapping.setdefault(
                (settings._net._host, settings._net._port), []
            ).append(settings)

    def normalize(self, name):

        return normalize_text(name.strip())

    def worldList(self):

        # Return world names, sorted by normalized value.
        worlds = (world._name for world in self.ws.getAllWorldSettings())
        return sorted(worlds, key=lambda s: self.normalize(s))

    def newWorldSettings(self, host="", port=0, ssl=False, name=""):

        wsettings = self.ws.newWorldSettings()

        if name:
            wsettings._name = name
        if host:
            wsettings._net._host = host
        if port:
            wsettings._net._port = port
        if ssl:
            wsettings._net._ssl = ssl

        return wsettings

    def newWorldState(self):

        return self.ws.newWorldState()

    def saveWorld(self, world: World):

        settings = world.settings
        state = world.state
        key = self.normalize(settings._name)  # TODO: Ensure unicity!

        self.ws.saveWorldSettings(key, settings, state)

        self.generateMappings()
        self.worldListChanged.emit()

    def newWorld(self, settings) -> World:

        state = self.ws.lookupStateForSettings(settings)

        return World(settings, state)

    def newAnonymousWorld(self, host="", port=0, ssl=False) -> World:

        settings = self.newWorldSettings(host, port, ssl)

        return self.newWorld(settings)

    def lookupWorldByName(self, name) -> Optional[World]:

        settings = self.name_mapping.get(self.normalize(name))

        if settings:
            return self.newWorld(settings)

        return None

    def lookupWorldByHostPort(self, host: str, port: int) -> Optional[World]:

        settings = self.hostport_mapping.get((host, port))

        if settings and len(settings) == 1:

            # One matching configuration found, and only one.
            return self.newWorld(settings[0])

        return None
