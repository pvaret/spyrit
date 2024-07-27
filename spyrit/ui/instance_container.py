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
Implements a container widget that knows how to manage the various panes of the
app's UI.
"""

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget

from spyrit import constants
from spyrit.session.instance import SessionInstance
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.about_pane import AboutPane
from spyrit.ui.base_pane import Pane
from spyrit.ui.settings.settings_pane import SettingsPane
from spyrit.ui.sliding_pane_container import SlidingPaneContainer
from spyrit.ui.tab_proxy import TabUpdate
from spyrit.ui.welcome_pane import WelcomePane
from spyrit.ui.world_creation_pane import WorldCreationPane
from spyrit.ui.world_pane import WorldPane


class InstanceContainer(SlidingPaneContainer):
    """
    Implements a widget that creates, connects, and manages the lifetime of the
    panes that make up the UI of the application.
    """

    # This signal is sent when a user action is asking for the app to terminate.

    quitRequested: Signal = Signal()

    # This signal is sent when this container wants its tab's title updated.

    tabUpdateRequested: Signal = Signal(TabUpdate)

    _settings: SpyritSettings
    _state: SpyritState
    _instance: SessionInstance

    def __init__(
        self,
        settings: SpyritSettings,
        state: SpyritState,
        instance: SessionInstance,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._settings = settings
        self._state = state
        self._instance = instance

        self.currentPaneChanged.connect(self._updateTabForPane)

    def createWelcomePane(self) -> None:
        if len(self) > 0:
            return

        self.addPaneRight(pane := WelcomePane(self._settings))
        self._updateTabForPane(pane)

        pane.openWorldCreationUIRequested.connect(self._openWorldCreationUI)
        pane.openWorldRequested.connect(self._openWorld)
        pane.openSettingsUIRequested.connect(self._openSettingsUI)
        pane.openAboutRequested.connect(self._openAbout)
        pane.quitRequested.connect(self.quitRequested)

    @Slot()
    def _openWorldCreationUI(self) -> None:
        self.addPaneRight(pane := WorldCreationPane(self._settings))

        pane.cancelClicked.connect(self.slideLeft)
        pane.openWorldRequested.connect(self._openWorld)

    @Slot(SpyritSettings)
    def _openWorld(self, settings: SpyritSettings) -> None:
        state = self._state.getStateSectionForSettingsSection(settings)
        self.addPaneRight(pane := WorldPane(settings, state, self._instance))

        # TODO: Move the logic to seek user confirmation from SessionInstance to
        # a new method called as a slot for this signal.
        pane.closeRequested.connect(self.slideLeft)
        pane.settingsUIRequested.connect(self._openSettingsUI)

    @Slot(SpyritSettings)
    def _openSettingsUI(self, settings: SpyritSettings) -> None:
        self.addPaneRight(pane := SettingsPane(settings))

        pane.okClicked.connect(self.slideLeft)

    @Slot()
    def _openAbout(self) -> None:
        self.addPaneRight(pane := AboutPane())

        pane.okClicked.connect(self.slideLeft)

    @Slot(Pane)
    def _updateTabForPane(self, pane: Pane | None) -> None:
        match pane:
            case WelcomePane():
                self.tabUpdateRequested.emit(
                    TabUpdate(title=f"Welcome to {constants.APPLICATION_NAME}!")
                )

            case AboutPane():
                self.tabUpdateRequested.emit(
                    TabUpdate(title=f"About {constants.APPLICATION_NAME}...")
                )

            case WorldCreationPane():
                self.tabUpdateRequested.emit(TabUpdate(title="New world..."))

            case WorldPane(settings):
                title = settings.title()
                if settings.isCharacter() and (
                    name := settings.login.name.get()
                ):
                    title = name + "\n" + title
                self.tabUpdateRequested.emit(TabUpdate(title=title))

            case _:
                pass
