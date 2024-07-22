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

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QPushButton

from spyrit.session.instance import SessionInstance
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.base_dialog_pane import BaseDialogPane
from spyrit.ui.settings.server_settings_ui import ServerSettingsUI


class SettingsValidator(QObject):
    """
    Monitors a settings object for changes and emits a signal when the settings
    object's contents can be used to start a connection.

    Args:
        parent: Used for lifetime management.

        settings: The settings object to monitor for changes and check for
            validity.
    """

    # This signal is sent when the validity of the settings object's contents
    # changes one way or another.

    validityChanged: Signal = Signal(bool)

    _valid: bool = False
    _settings: SpyritSettings

    def __init__(self, parent: QObject, settings: SpyritSettings) -> None:
        super().__init__(parent)

        self._settings = settings
        settings.onUpdateCall(self.checkSettings)
        self.checkSettings()

    def checkSettings(self, _: Any = None) -> None:
        if (valid := self.valid()) != self._valid:
            self._valid = valid
            self.validityChanged.emit(valid)

    def valid(self) -> bool:
        return (
            self._settings.net.port.isSet()
            and self._settings.net.server.isSet()
        )


class WorldCreationPane(BaseDialogPane):
    """
    Implements a pane that contains the new world creation form.

    Args:
        settings: The global application settings object.

        instance: The session model object for the tab that contains this pane.
    """

    # This signal is sent when the user asks for the world configured in this
    # pane to be opened. The arguments is the new world's settings object.

    openWorldRequested: Signal = Signal(SpyritSettings)

    _world_settings: SpyritSettings
    _instance: SessionInstance
    _connect_button: QPushButton
    _validator: SettingsValidator

    def __init__(
        self,
        settings: SpyritSettings,
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

        self.setWidget(ServerSettingsUI(self._world_settings))

        ok_button.setEnabled(False)

        self._validator = SettingsValidator(self, self._world_settings)
        self._validator.validityChanged.connect(ok_button.setEnabled)

        self.okClicked.connect(self._openWorld)

    @Slot()
    def _openWorld(self) -> None:
        """
        Signals that the settings in the pane should be used to open a game
        world.
        """

        if self._validator.valid():
            self._world_settings.setParent(self._root_settings)
            self.openWorldRequested.emit(self._world_settings)

    def onActive(self) -> None:
        """
        Overrides the parent handler to set the title of the tab that contains
        this pane when this pane becomes visible.
        """

        self._instance.setTitle("New world...")
