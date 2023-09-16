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

    # This pane is never garbage collected.

    pane_is_persistent = True

    _settings: SpyritSettings
    _state: SpyritState

    def __init__(self, settings: SpyritSettings, state: SpyritState) -> None:
        super().__init__()

        self._settings = settings
        self._state = state

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

    @Slot()
    def _openWorldCreationPane(self) -> None:
        pane = WorldCreationPane(self._settings, self._state)
        self.addPaneRight(pane)

    @Slot()
    def _openWorldPane(self) -> None:
        button = self.sender()
        if not isinstance(button, WorldButton):
            return

        world = button.settings()
        state = self._state.getStateSectionForSettingsSection(world)

        self.addPaneRight(WorldPane(world, state))
