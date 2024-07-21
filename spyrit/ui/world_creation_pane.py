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
Implements a UI to set up a new world.
"""


from typing import Any

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QPushButton

from spyrit.session.instance import SessionInstance
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.base_dialog_pane import BaseDialogPane
from spyrit.ui.settings.server_settings_ui import ServerSettingsUI


class WorldCreationPane(BaseDialogPane):
    """
    Implements a pane that contains the new world creation form.

    Args:
        settings: The global application settings object.

        state: The global application state object.

        instance: The session model object for the tab that contains this pane.
    """

    # This signal is sent when the user asks for the world configured in this
    # pane to be opened. The arguments are the new world's settings and state
    # objects.

    openWorldRequested: Signal = Signal(SpyritSettings, SpyritState)

    _world_settings: SpyritSettings
    _state: SpyritState
    _instance: SessionInstance
    _connect_button: QPushButton

    def __init__(
        self,
        settings: SpyritSettings,
        state: SpyritState,
        instance: SessionInstance,
    ) -> None:
        super().__init__(
            ok_button := QPushButton("Connect!"),
            cancel_button=QPushButton("Cancel"),
        )

        self._connect_button = ok_button
        self._root_settings = settings
        self._world_settings = SpyritSettings()
        self._instance = instance
        self._state = state

        self.setWidget(ServerSettingsUI(self._world_settings))

        self._world_settings.onUpdateCall(self._maybeEnableConnectButton)
        self._maybeEnableConnectButton()

        self.okClicked.connect(self._openWorld)

    @Slot()
    def _openWorld(self) -> None:
        """
        Creates a game pane for the newly configured world, and switches to it.
        """

        if not self._areSettingsValid():
            return

        self._world_settings.setParent(self._root_settings)
        state = self._state.getStateSectionForSettingsSection(
            self._world_settings
        )

        self.openWorldRequested.emit(self._world_settings, state)

    @Slot()
    def _maybeEnableConnectButton(self, entity: Any = None) -> None:
        """
        Enables the connect button if the current world settings are valid.

        Args:
            entity: Which settings entity was updated, that triggered the call
                to this function. Unused.
        """

        self._connect_button.setEnabled(self._areSettingsValid())

    def _areSettingsValid(self) -> bool:
        """
        Validates the settings currently entered in the form.

        Returns:
            Whether the current world settings can be used to connect to a
            world.
        """

        return (
            self._world_settings.net.port.isSet()
            and self._world_settings.net.server.isSet()
        )

    def onActive(self) -> None:
        """
        Overrides the parent handler to set the title of the tab that contains
        this pane when this pane becomes visible.
        """

        self._instance.setTitle("New world...")
