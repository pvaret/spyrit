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

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import QApplication, QWidget

from spyrit import constants
from spyrit.network.autologin import Autologin
from spyrit.network.connection import Connection, ConnectionStatus
from spyrit.network.keepalive import Keepalive
from spyrit.resources.resources import Icon
from spyrit.session.properties import InstanceProperties
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.about_pane import AboutPane
from spyrit.ui.signals import CallWithArgs
from spyrit.ui.widget_activity_monitor import ActivityMonitor, AttentionPinger
from spyrit.ui.base_pane import Pane
from spyrit.ui.dialogs import maybeAskUserIfReadyToClose
from spyrit.ui.settings.settings_pane import SettingsPane
from spyrit.ui.sliding_pane_container import SlidingPaneContainer
from spyrit.ui.tab_proxy import TabUpdate
from spyrit.ui.welcome_pane import WelcomePane
from spyrit.ui.world_creation_pane import WorldCreationPane
from spyrit.ui.world_pane import WorldPane, make_processor, make_world_pane


class InstanceUI(SlidingPaneContainer):
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
    _properties: InstanceProperties

    def __init__(
        self,
        parent: QWidget,
        settings: SpyritSettings,
        state: SpyritState,
        properties: InstanceProperties,
    ) -> None:
        super().__init__(parent)

        self._settings = settings
        self._state = state
        self._properties = properties

        self.currentPaneChanged.connect(self._updateTabForPane)

        self._createWelcomePane()

    def _createWelcomePane(self) -> None:
        if len(self) > 0:
            return

        self.addPaneRight(pane := WelcomePane(self._settings))

        pane.openWorldCreationUIRequested.connect(self._openWorldCreationUI)
        pane.openWorldRequested.connect(self._openWorld)
        pane.openSettingsUIRequested.connect(self._openSettingsUI)
        pane.openAboutRequested.connect(self._openAbout)
        pane.quitRequested.connect(self.quitRequested)

    @Slot(SpyritSettings)
    def _openSettingsUI(self, settings: SpyritSettings) -> None:
        self.addPaneRight(pane := SettingsPane(settings))

        pane.okClicked.connect(self.slideLeft)

    @Slot()
    def _openAbout(self) -> None:
        self.addPaneRight(pane := AboutPane())

        pane.okClicked.connect(self.slideLeft)

    @Slot()
    def _openWorldCreationUI(self) -> None:
        self.addPaneRight(pane := WorldCreationPane(self._settings))

        pane.cancelClicked.connect(self.slideLeft)
        pane.openWorldRequested.connect(self._openWorld)

    @Slot(SpyritSettings)
    def _openWorld(self, world_settings: SpyritSettings) -> None:
        self._properties.setPropertiesFromSettings(world_settings)

        world_state = self._state.getStateSectionForSettingsSection(
            world_settings
        )

        # Create the connection.

        connection = Connection(world_settings.net)
        status = ConnectionStatus(connection)
        status.connected.connect(self._properties.setConnected)

        # Create the network input processor.

        processor = make_processor(connection, world_settings)

        # Set up automatic login if the world's settings are bound to a specific
        # character.

        if world_settings.isCharacter():
            autologin = Autologin(world_settings.login, connection)
            processor.fragmentsReady.connect(autologin.awaitLoginPrecondition)

        # Set up keepalives for the connection.

        Keepalive(connection, world_settings.net.keepalive)

        # Create the UI and plug it in.

        self.addPaneRight(
            pane := make_world_pane(
                world_settings, world_state, status, processor
            )
        )

        pane.closePaneRequested.connect(self._maybeCloseWorldPane)
        pane.showSettingsUI.connect(self._openSettingsUI)
        pane.destroyed.connect(self._properties.reset)

        # Bind the lifetime of the connection to that of the pane.

        connection.setParent(pane)

        # Plug the connection control signals into the relevant connection
        # methods.

        pane.sendUserInput.connect(connection.sendText)
        pane.startConnection.connect(connection.start)
        pane.stopConnection.connect(connection.stop)

        # Highlight the tab and window if the network connection is doing
        # something in a tab that is not active.

        pinger = AttentionPinger(pane)
        connection.dataReceived.connect(pinger.maybeCallForAttention)
        connection.statusChanged.connect(pinger.maybeCallForAttention)

        monitor = ActivityMonitor(pane)
        monitor.activityChanged.connect(pinger.setActive)
        pinger.setActive(monitor.active())

        pinger.callForAttention.connect(
            CallWithArgs(
                self.tabUpdateRequested.emit,
                TabUpdate(color=QColor(Qt.GlobalColor.red)),
            )
        )
        pinger.callForAttention.connect(self._highlightWindow)
        pinger.clearAttentionCall.connect(
            CallWithArgs(
                self.tabUpdateRequested.emit, TabUpdate(color=QColor())
            )
        )

        # Update the icon depending on the connection status.

        status.connected.connect(self._updateTabIconForConnection)
        self._updateTabIconForConnection(status.isConnected())

        # Initiate the game connection.

        connection.start()

    @Slot()
    def _maybeCloseWorldPane(self) -> None:
        pane = self.sender()
        if not isinstance(pane, Pane):
            return
        if not self._properties.isConnected() or maybeAskUserIfReadyToClose(
            self, [self._properties.title()]
        ):
            pane.pane_is_persistent = False
            self.slideLeft()

    @Slot()
    def _highlightWindow(self) -> None:
        match app := QApplication.instance():
            case QApplication():
                app.alert(self)
            case _:
                pass

    @Slot(bool)
    def _updateTabIconForConnection(self, connected: bool) -> None:
        icon = QIcon(
            Icon.CONNECTION_ON_SVG if connected else Icon.CONNECTION_OFF_SVG
        )
        self.tabUpdateRequested.emit(TabUpdate(icon=icon))

    @Slot(Pane)
    def _updateTabForPane(self, pane: Pane | None) -> None:
        match pane:
            case WelcomePane():
                self.tabUpdateRequested.emit(
                    TabUpdate(
                        title=constants.DEFAULT_TAB_TITLE,
                        color=QColor(),
                        icon=QIcon(),
                    )
                )

            case AboutPane():
                self.tabUpdateRequested.emit(
                    TabUpdate(title=f"About {constants.APPLICATION_NAME}...")
                )

            case WorldCreationPane():
                self.tabUpdateRequested.emit(TabUpdate(title="New world..."))

            case WorldPane():
                self.tabUpdateRequested.emit(
                    TabUpdate(title=self._properties.blockTitle())
                )

            case _:
                pass
