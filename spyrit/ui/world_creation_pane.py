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


from PySide6.QtWidgets import QLabel

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.base_dialog_pane import BaseDialogPane
from spyrit.ui.main_ui_remote_protocol import UIRemoteProtocol
from spyrit.ui.world_pane import WorldPane


class WorldCreationPane(BaseDialogPane):
    _settings: SpyritSettings
    _remote: UIRemoteProtocol

    def __init__(
        self, settings: SpyritSettings, remote: UIRemoteProtocol
    ) -> None:
        super().__init__(QLabel("Creating a new world!"))

        self._settings = settings
        self._remote = remote

        self.okClicked.connect(self._openWorld)
        self.cancelClicked.connect(self._remote.pop)

        # TODO: Implement.

    def _openWorld(self) -> None:
        world_pane = WorldPane(self._settings)
        self._remote.append(world_pane)
