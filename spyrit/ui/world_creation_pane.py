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


from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from spyrit import constants
from spyrit.session.instance import SessionInstance
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.bars import VBar
from spyrit.ui.base_dialog_pane import BaseDialogPane
from spyrit.ui.settings.input_widgets import ServerPortEdit, TextLineEdit
from spyrit.ui.sizer import Sizer
from spyrit.ui.world_pane import WorldPane


class WorldCreationForm(QWidget):
    """
    Implements the UI to configure a new game world.

    Args:
        settings: The specific settings section to be used for the new game
            world, as opposed to the global settings object.
    """

    # This signal fires when any field in the form is edited.

    contentsEdited: Signal = Signal()

    def __init__(self, settings: SpyritSettings) -> None:
        super().__init__()

        unit = Sizer(self).unitSize()

        # Lay out the form.

        self.setLayout(layout := QHBoxLayout())

        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(form_layout := QVBoxLayout())

        form_layout.addStrut(constants.FORM_WIDTH_UNITS * unit)

        form_layout.addWidget(QLabel("<b>World name</b>"))
        form_layout.addWidget(world_name_edit := TextLineEdit(settings.name))
        form_layout.addSpacing(unit)

        form_layout.addWidget(
            server_port_edit := ServerPortEdit(
                server_key=settings.net.server, port_key=settings.net.port
            )
        )

        form_layout.addStretch()

        layout.addWidget(VBar())
        layout.addStretch()

        # Report updates of the form contents.

        world_name_edit.textEdited.connect(self.contentsEdited)
        server_port_edit.contentsEdited.connect(self.contentsEdited)


class WorldCreationPane(BaseDialogPane):
    """
    Implements a pane that contains the new world creation form.

    Args:
        settings: The global application settings object.

        state: The global application state object.

        instance: The session model object for the tab that contains this pane.
    """

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
        self._world_settings = settings.newSection()
        self._instance = instance
        self._state = state

        self.setWidget(form := WorldCreationForm(self._world_settings))

        form.contentsEdited.connect(self._maybeEnableConnectButton)
        self._maybeEnableConnectButton()

        self.okClicked.connect(self._openWorld)
        self.cancelClicked.connect(self.slideLeft)

    @Slot()
    def _openWorld(self) -> None:
        """
        Creates a game pane for the newly configured world, and switches to it.
        """

        if not self._areSettingsValid():
            return

        state = self._state.getStateSectionForSettingsSection(
            self._world_settings
        )
        world_pane = WorldPane(self._world_settings, state, self._instance)
        self.addPaneRight(world_pane)

    @Slot()
    def _maybeEnableConnectButton(self) -> None:
        """
        Enables the connect button if the current world settings are valid.
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
