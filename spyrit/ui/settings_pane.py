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
Implements an application settings pane.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.base_dialog_pane import BaseDialogPane


class SettingsPane(BaseDialogPane):
    """
    An UI to configure all aspects of the application.

    Args:
        settings: The settings object to configure. This can be the
            application-global one, or one of the world-specific ones.
    """

    _settings: SpyritSettings

    def __init__(
        self,
        settings: SpyritSettings,
    ) -> None:
        super().__init__()

        self.setWidget(label := QLabel("TODO!"))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._settings = settings
        self.okClicked.connect(self.slideLeft)
