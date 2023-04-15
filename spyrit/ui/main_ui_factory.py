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
Provide the main UI of Spyrit, to be embedded in a tabbed container.
"""


from PySide6.QtWidgets import QHBoxLayout, QWidget

from spyrit import constants
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.sliding_pane_container import SlidingPaneContainer
from spyrit.ui.welcome_pane import WelcomePane
from spyrit.ui.tabbed_ui_element import TabbedUIElement


class MainUI(TabbedUIElement):
    def __init__(
        self,
        settings: SpyritSettings,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Set up the main widget for this UI.

        self.setLayout(QHBoxLayout())
        container = SlidingPaneContainer()
        container.append(WelcomePane(settings))
        self.layout().addWidget(container)

        # Set up the title texts for this UI.

        self.setTabTitle(f"Welcome to {constants.APPLICATION_NAME}!")
        self.setWindowTitle(constants.APPLICATION_NAME)


class SpyritMainUIFactory:
    def __init__(self, settings: SpyritSettings) -> None:
        self._settings = settings

    def __call__(self) -> MainUI:
        return MainUI(self._settings)
