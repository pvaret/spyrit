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
Implements a UI to play in a world.
"""


from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QLabel

from spyrit import constants
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.base_pane import Pane
from spyrit.ui.main_ui_remote_protocol import UIRemoteProtocol


class WorldPane(Pane):
    _settings: SpyritSettings
    _remote: UIRemoteProtocol

    def __init__(
        self, settings: SpyritSettings, remote: UIRemoteProtocol
    ) -> None:
        super().__init__()

        self._settings = settings
        self._remote = remote

        self.setLayout(QHBoxLayout())
        name = settings.name.get() or "unnamed"
        self.layout().addWidget(QLabel(f"Playing world {name}!"))

        self.active.connect(self._setTitles)

        # TODO: Implement.

    @Slot()
    def _setTitles(self) -> None:
        world_name = self._settings.name.get() or "Unnamed"
        self._remote.setTabTitle(world_name)
        self._remote.setWindowTitle(
            f"{constants.APPLICATION_NAME} - {world_name}"
        )
