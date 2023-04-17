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


from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QWidget

from spyrit import constants
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.bars import VBar
from spyrit.ui.base_dialog_pane import BaseDialogPane
from spyrit.ui.form_widgets import PortLineEdit, TextLineEdit
from spyrit.ui.main_ui_remote_protocol import UIRemoteProtocol
from spyrit.ui.world_pane import WorldPane


# TODO: make this a function of the font size.
_UNIT = 16


class WorldCreationForm(QWidget):
    def __init__(self, settings: SpyritSettings) -> None:
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        form_layout = QGridLayout()

        row = 0

        form_layout.addWidget(QLabel("Name"), row, 0)

        row += 1
        name_edit = TextLineEdit()
        name_edit.setKey(settings.name)
        form_layout.addWidget(name_edit, row, 0, row, 3)

        row += 1
        form_layout.setRowMinimumHeight(row, _UNIT)

        row += 1
        form_layout.addWidget(QLabel("Server"), row, 0)
        form_layout.addWidget(QLabel("Port"), row, 2)

        row += 1
        server_edit = TextLineEdit()
        server_edit.setKey(settings.net.server)
        port_edit = PortLineEdit()
        port_edit.setKey(settings.net.port)

        form_layout.addWidget(server_edit, row, 0)
        form_layout.addWidget(QLabel(":"), row, 1)
        form_layout.addWidget(port_edit, row, 2)

        row += 1
        form_layout.setRowStretch(row, 1)

        layout.addLayout(form_layout)

        layout.addWidget(VBar())
        layout.addStretch()


class WorldCreationPane(BaseDialogPane):
    _settings: SpyritSettings
    _ui: UIRemoteProtocol

    def __init__(self, settings: SpyritSettings, ui: UIRemoteProtocol) -> None:
        super().__init__(WorldCreationForm(settings))

        self._settings = settings
        self._ui = ui

        self.okClicked.connect(self._openWorld)
        self.cancelClicked.connect(self._ui.pop)
        self.active.connect(self._setTitles)

    @Slot()
    def _openWorld(self) -> None:
        self._settings.setSectionName(self._settings.name.get())
        world_pane = WorldPane(self._settings, self._ui)
        self._ui.append(world_pane)

    @Slot()
    def _setTitles(self) -> None:
        self._ui.setTabTitle("New world")
        self._ui.setWindowTitle(constants.APPLICATION_NAME)
