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
Implements the UI that is first displayed when opening a new window.
"""


from PySide6.QtWidgets import QHBoxLayout, QWidget

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.bars import VBar
from spyrit.ui.main_menu import MainMenuLayout


class WelcomePane(QWidget):
    """
    Implements the UI entry point from where the users can start using the
    software.
    """

    def __init__(self, settings: SpyritSettings) -> None:
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addLayout(MainMenuLayout(settings))
        layout.addWidget(VBar())

        layout.addStretch()
