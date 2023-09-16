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
Provide the main UI of Spyrit, to be embedded in a tabbed container.
"""


from PySide6.QtWidgets import QWidget

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.base_pane import Pane
from spyrit.ui.sliding_pane_container import SlidingPaneContainer
from spyrit.ui.welcome_pane import WelcomePane
from spyrit.ui.tabbed_ui_element import TabbedUIElement


class MainUI(TabbedUIElement):
    """
    Class that puts together the application's UI elements.
    """

    _container: SlidingPaneContainer

    def __init__(
        self,
        settings: SpyritSettings,
        state: SpyritState,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)

        # Set up the main widget for this UI.

        self._container = SlidingPaneContainer()
        self._container.addPaneRight(WelcomePane(settings, state))
        self.setWidget(self._container)
        self.setFocusProxy(self._container)

    def append(self, widget: Pane) -> None:
        return self._container.addPaneRight(widget)

    def pop(self) -> None:
        return self._container.slideLeft()


class SpyritMainUIFactory:
    _settings: SpyritSettings
    _state: SpyritState

    def __init__(self, settings: SpyritSettings, state: SpyritState) -> None:
        self._settings = settings
        self._state = state

    def __call__(self) -> MainUI:
        return MainUI(self._settings, self._state)
