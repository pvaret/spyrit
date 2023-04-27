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
Implements the UI that is first displayed when opening a new window.
"""


from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from spyrit import constants
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.bars import HBar, VBar
from spyrit.ui.base_pane import Pane
from spyrit.ui.buttons import Button, WorldButton
from spyrit.ui.main_ui_remote_protocol import UIRemoteProtocol
from spyrit.ui.spyrit_logo import SpyritLogo
from spyrit.ui.world_creation_pane import WorldCreationPane
from spyrit.ui.world_pane import WorldPane

# TODO: make this a function of the font size.
_UNIT = 16


class WelcomePane(Pane):
    """
    Implements the UI entry point from where the users can start using the
    software.
    """

    _settings: SpyritSettings
    _state: SpyritState
    _ui: UIRemoteProtocol

    def __init__(
        self, settings: SpyritSettings, state: SpyritState, ui: UIRemoteProtocol
    ) -> None:
        super().__init__()

        self._settings = settings
        self._state = state
        self._ui = ui

        # Create the main layout.

        self.setLayout(pane_layout := QHBoxLayout())

        # Create and set up the menu layout.

        pane_layout.addLayout(menu_layout := QVBoxLayout())

        # Logo!

        menu_layout.addWidget(SpyritLogo())

        menu_layout.addWidget(HBar())

        menu_layout.addSpacing(_UNIT)

        # New world button!

        menu_layout.addWidget(new_world_button := Button("New world..."))
        new_world_button.clicked.connect(self._openWorldCreationPane)

        menu_layout.addSpacing(_UNIT)

        # All world buttons!

        worlds = [
            world for world in settings.sections() if not world.isPrivate()
        ]
        worlds.sort(key=lambda w: w.name.get().strip().lower())

        if worlds:
            menu_layout.addWidget(QLabel("Return to..."))

            for world in worlds:
                menu_layout.addWidget(world_button := WorldButton(world))
                world_button.clicked.connect(self._openWorldPane)

            menu_layout.addSpacing(_UNIT)

        # Important application buttons (settings and about)!

        menu_layout.addWidget(HBar())
        menu_layout.addSpacing(_UNIT)

        menu_layout.addLayout(button_layout := QHBoxLayout())

        button_layout.addWidget(settings_button := Button("Settings"))
        settings_button.setEnabled(False)  # TODO: Implement.

        button_layout.addWidget(
            about_button := Button(f"About {constants.APPLICATION_NAME}...")
        )
        about_button.setEnabled(False)  # TODO: Implement.

        # Fill out the remaining space.

        menu_layout.addStretch()

        # And finalize the main layout.

        pane_layout.addWidget(VBar())
        pane_layout.addStretch()

        # Set up the window and tab title.

        self.active.connect(self._setTitles)

    @Slot()
    def _openWorldCreationPane(self) -> None:
        new_world = self._settings.newSection()
        pane = WorldCreationPane(new_world, self._ui)
        self._ui.append(pane)

    @Slot()
    def _openWorldPane(self) -> None:
        button = self.sender()
        if not isinstance(button, WorldButton):
            return

        world = button.settings()

        self._ui.append(WorldPane(world, self._ui))

    @Slot()
    def _setTitles(self) -> None:
        self._ui.setTabTitle(f"Welcome to {constants.APPLICATION_NAME}!")
        self._ui.setWindowTitle(constants.APPLICATION_NAME)
