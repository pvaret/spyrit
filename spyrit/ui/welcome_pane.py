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
from spyrit.session.instance import SessionInstance
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.about_pane import AboutPane
from spyrit.ui.bars import HBar, VBar
from spyrit.ui.base_pane import Pane
from spyrit.ui.buttons import Button, WorldButton
from spyrit.ui.settings_pane import SettingsPane
from spyrit.ui.sizer import Sizer
from spyrit.ui.spyrit_logo import SpyritLogo
from spyrit.ui.world_creation_pane import WorldCreationPane
from spyrit.ui.world_pane import WorldPane


class WelcomePane(Pane):
    """
    Implements the UI entry point from where the users can start using the
    software.

    Args:
        settings: The global application settings object. It will be used to
            create or look up a world-specific settings subset when the user
            creates or picks a world to play.

        state: The global application state object. Ditto.

        instance: The session model object for the tab that contains this pane.
    """

    # This pane is never garbage collected.

    pane_is_persistent = True

    _settings: SpyritSettings
    _state: SpyritState
    _instance: SessionInstance

    def __init__(
        self,
        settings: SpyritSettings,
        state: SpyritState,
        instance: SessionInstance,
    ) -> None:
        super().__init__()

        self._settings = settings
        self._state = state
        self._instance = instance

        unit = Sizer(self).unitSize()

        # Create the main layout.

        self.setLayout(pane_layout := QHBoxLayout())

        # Create and set up the menu layout.

        pane_layout.addLayout(menu_layout := QVBoxLayout())

        # Logo!

        menu_layout.addWidget(SpyritLogo())

        menu_layout.addWidget(HBar())

        menu_layout.addSpacing(unit)

        # New world button!

        menu_layout.addWidget(new_world_button := Button("New world..."))
        new_world_button.clicked.connect(self._openWorldCreationPane)

        menu_layout.addSpacing(unit)

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

            menu_layout.addSpacing(unit)

        # Important application buttons (settings and about)!

        menu_layout.addWidget(HBar())
        menu_layout.addSpacing(unit)

        menu_layout.addLayout(button_layout := QHBoxLayout())

        button_layout.addWidget(settings_button := Button("Settings"))
        settings_button.clicked.connect(self._showSettings)

        button_layout.addWidget(
            about_button := Button(f"About {constants.APPLICATION_NAME}...")
        )
        about_button.clicked.connect(self._showAbout)

        # Fill out the remaining space.

        menu_layout.addStretch()

        # And finalize the main layout.

        pane_layout.addWidget(VBar())
        pane_layout.addStretch()

    def onActive(self) -> None:
        """
        Overrides the parent handler to set the instance title when this pane
        becomes visible.
        """

        self._instance.setTitle(f"Welcome to {constants.APPLICATION_NAME}!")

    @Slot()
    def _openWorldCreationPane(self) -> None:
        """
        Creates a world creation pane and switches to it.
        """

        pane = WorldCreationPane(self._settings, self._state, self._instance)
        self.addPaneRight(pane)

    @Slot()
    def _openWorldPane(self) -> None:
        """
        Creates a game pane for an existing world and switches to it.
        """

        button = self.sender()
        if not isinstance(button, WorldButton):
            return

        world = button.settings()
        state = self._state.getStateSectionForSettingsSection(world)

        self.addPaneRight(WorldPane(world, state, self._instance))

    @Slot()
    def _showSettings(self) -> None:
        """
        Shows the settings pane.
        """

        self.addPaneRight(SettingsPane(self._settings))

    @Slot()
    def _showAbout(self) -> None:
        """
        Shows the application about pane.
        """

        self.addPaneRight(AboutPane())
