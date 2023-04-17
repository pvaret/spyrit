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
Implements a UI to set up a new world.
"""


from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from spyrit import constants
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.bars import VBar
from spyrit.ui.base_dialog_pane import BaseDialogPane
from spyrit.ui.form_widgets import (
    FixedSizeLabel,
    PortLineEdit,
    ServerLineEdit,
    TextLineEdit,
)
from spyrit.ui.main_ui_remote_protocol import UIRemoteProtocol
from spyrit.ui.world_pane import WorldPane


# TODO: make this a function of the font size.
_UNIT = 16
_FORM_WIDTH = _UNIT * 20


class WorldCreationForm(QWidget):
    updated = Signal()  # noqa: N815

    def __init__(self, settings: SpyritSettings) -> None:
        super().__init__()

        # Lay out the form.

        self.setLayout(layout := QHBoxLayout())

        layout.addLayout(form_layout := QVBoxLayout())

        form_layout.addStrut(_FORM_WIDTH)

        form_layout.addWidget(QLabel("Name"))
        form_layout.addWidget(name_edit := TextLineEdit())
        form_layout.addSpacing(_UNIT)

        form_layout.addLayout(server_port_layout := QGridLayout())

        server_port_layout.addWidget(QLabel("Server"), 0, 0)
        server_port_layout.addWidget(QLabel("Port"), 0, 2)
        server_port_layout.addWidget(server_edit := ServerLineEdit(), 1, 0)
        server_port_layout.addWidget(FixedSizeLabel(":"), 1, 1)
        server_port_layout.addWidget(port_edit := PortLineEdit(), 1, 2)

        form_layout.addStretch()

        layout.addWidget(VBar())
        layout.addStretch()

        # Connect the input widgets with the relevant settings.

        name_edit.setKey(settings.name)
        server_edit.setKey(settings.net.server)
        port_edit.setKey(settings.net.port)

        # Report updates of the form contents.

        name_edit.textEdited.connect(self.updated)
        server_edit.textEdited.connect(self.updated)
        port_edit.textEdited.connect(self.updated)


class WorldCreationPane(BaseDialogPane):
    _settings: SpyritSettings
    _ui: UIRemoteProtocol
    _connect_button: QPushButton

    def __init__(self, settings: SpyritSettings, ui: UIRemoteProtocol) -> None:
        super().__init__(
            ok_button := QPushButton("Connect!"),
            cancel_button=QPushButton("Cancel"),
        )

        self._connect_button = ok_button
        self._settings = settings
        self._ui = ui

        self.setWidget(form := WorldCreationForm(settings))
        form.updated.connect(self._maybeEnableConnectButton)

        self.okClicked.connect(self._openWorld)
        self.cancelClicked.connect(self._ui.pop)
        self.active.connect(self._setTitles)

        self._maybeEnableConnectButton()

    @Slot()
    def _openWorld(self) -> None:
        if not self._areSettingsValid():
            return

        self._settings.setSectionName(self._settings.name.get())
        world_pane = WorldPane(self._settings, self._ui)
        self._ui.append(world_pane)

    @Slot()
    def _setTitles(self) -> None:
        self._ui.setTabTitle("New world")
        self._ui.setWindowTitle(constants.APPLICATION_NAME)

    @Slot()
    def _maybeEnableConnectButton(self) -> None:
        self._connect_button.setEnabled(self._areSettingsValid())

    def _areSettingsValid(self) -> bool:
        return (
            self._settings.name.isSet()
            and self._settings.name.get().strip() != ""
            and self._settings.net.port.isSet()
            and constants.MIN_TCP_PORT
            <= self._settings.net.port.get()
            <= constants.MAX_TCP_PORT
            and self._settings.net.server.isSet()
            and self._settings.net.server.get() != ""
        )
