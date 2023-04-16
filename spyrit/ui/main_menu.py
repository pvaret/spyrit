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
Implements the main application menu.
"""


from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.bars import HBar
from spyrit.ui.buttons import Button, WorldButton
from spyrit.ui.sliding_pane_container import ContainerRemote
from spyrit.ui.spyrit_logo import SpyritLogo
from spyrit.ui.world_creation_pane import WorldCreationPane
from spyrit.ui.world_pane import WorldPane

# TODO: make this a function of the font size.
_UNIT = 16


class MainMenuLayout(QVBoxLayout):
    _settings: SpyritSettings
    _remote: ContainerRemote

    def __init__(
        self, settings: SpyritSettings, remote: ContainerRemote
    ) -> None:
        super().__init__()

        self._settings = settings
        self._remote = remote

        self.addWidget(SpyritLogo())

        self.addWidget(HBar())

        self.addSpacing(_UNIT)

        new_world_button = Button("New world...")
        new_world_button.clicked.connect(self._openWorldCreationPane)
        self.addWidget(new_world_button)

        self.addSpacing(_UNIT)

        worlds = [
            world for world in settings.sections() if not world.isPrivate()
        ]
        worlds.sort(key=lambda w: w.name.get().strip().lower())

        for world in worlds:
            world_button = WorldButton(world)
            world_button.clicked.connect(self._openWorldPane)
            self.addWidget(world_button)

        self.addStretch()

    @Slot()
    def _openWorldCreationPane(self) -> None:
        self._remote.append(WorldCreationPane(self._settings))

    @Slot()
    def _openWorldPane(self) -> None:
        button = self.sender()
        if not isinstance(button, WorldButton):
            return

        world = button.settings()

        self._remote.append(WorldPane(world))
