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


from PySide6.QtWidgets import QWidget

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.base_pane import Pane
from spyrit.ui.sliding_pane_container import SlidingPaneContainer
from spyrit.ui.welcome_pane import WelcomePane
from spyrit.ui.tabbed_ui_element import TabbedUIElement


class _UIRemote:
    """
    A class that provides controls to update the main UI.
    """

    _ui: "MainUI"

    def __init__(self, ui: "MainUI") -> None:
        self._ui = ui

    def append(self, pane: Pane) -> None:
        self._ui.append(pane)

    def pop(self) -> None:
        self._ui.pop()

    def setWindowTitle(self, title: str) -> None:
        self._ui.setWindowTitle(title)

    def setTabTitle(self, title: str) -> None:
        self._ui.setTabTitle(title)


class MainUI(TabbedUIElement):
    """
    Class that puts together the application's UI elements.
    """

    _container: SlidingPaneContainer

    def __init__(
        self,
        settings: SpyritSettings,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)

        # Set up the main widget for this UI.

        self._container = SlidingPaneContainer()
        self._container.append(WelcomePane(settings, _UIRemote(self)))
        self.setWidget(self._container)

    def append(self, widget: Pane) -> None:
        return self._container.append(widget)

    def pop(self) -> None:
        return self._container.pop()


class SpyritMainUIFactory:
    def __init__(self, settings: SpyritSettings) -> None:
        self._settings = settings

    def __call__(self) -> MainUI:
        return MainUI(self._settings)
