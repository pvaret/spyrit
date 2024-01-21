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
Provides a class that keeps track of the current status of a game window, and
reacts to changes to this status.
"""


import logging
import weakref

from typing import Iterator

from PySide6.QtCore import QObject, Slot

from spyrit.session.instance import SessionInstance
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.dialogs import askUserIfReadyToClose
from spyrit.ui.main_window import SpyritMainWindow
from spyrit.ui.sliding_pane_container import SlidingPaneContainer
from spyrit.ui.tab_proxy import TabProxy
from spyrit.ui.welcome_pane import WelcomePane


class SessionWindow(QObject):
    """
    A SessionWindow keeps track of the status of a game window, and the
    SessionInstance objects associated with it.

    It's in charge of keeping a reference to its game window. In other words, if
    a SessionWindow is deleted, its window gets deleted too.

    Args:
        parent: The object to use as this one's parent, for lifetime management
            purposes.

        settings: The application-wide settings object.

        state: The application-wide state object.

        window: The window that this SessionWindow is to be associated with.
    """

    _settings: SpyritSettings
    _state: SpyritState

    # Keep a reference to the window associated to this SessionWindow. Otherwise
    # the window would be garbage-collected immediately.

    _window: SpyritMainWindow

    # Keep track of this window's instances, without references.

    _instances: weakref.WeakSet[SessionInstance]

    def __init__(
        self,
        parent: QObject,
        settings: SpyritSettings,
        state: SpyritState,
        window: SpyritMainWindow,
    ) -> None:
        super().__init__(parent)

        self._instances = weakref.WeakSet()
        self._settings = settings
        self._state = state
        self._window = window

        window.newTabRequested.connect(self.newInstance)
        window.closeRequested.connect(self.maybeClose)

    @Slot()
    def newInstance(self) -> None:
        """
        Creates a new SessionInstance, the corresponding UI, and adds the UI to
        the window and the instance to this SessionWindow.
        """

        # Create and set up the instance.

        self._instances.add(instance := SessionInstance())

        instance.unreadLinesChanged.connect(self._maybeHighlightWindow)

        # Create the UI for a game.

        widget = SlidingPaneContainer(self._window)
        widget.addPaneRight(
            pane := WelcomePane(self._settings, self._state, instance)
        )

        # Plug quit requests from the welcome pane to the window.

        pane.quitRequested.connect(self._window.quitRequested)

        # Add the UI to a tab and bind the instance to that tab.

        self._window.tabs().addTab(widget, instance.title())
        self._window.focusChanged.connect(instance.setFocused)

        instance.setTab(TabProxy(self._window.tabs(), widget))

    @Slot()
    def _maybeHighlightWindow(self) -> None:
        """
        Makes the window call for attention if there are unread lines of text in
        one of its instances.
        """

        unread = sum(instance.unreadLines() for instance in self._instances)

        if unread:
            self._window.alert()

    @Slot()
    def maybeClose(self) -> None:
        """
        Closes this window if it contains no connected games, or asks the user
        if they're fine closing them.
        """

        connected = list(self.connectedInstances())

        if not connected or askUserIfReadyToClose(self._window, connected):
            self.close()

    def close(self) -> None:
        """
        Causes this SessionWindow to detach itself from its parent, which should
        trigger its garbage collection.
        """

        self.setParent(None)  # type: ignore

    def connectedInstances(self) -> Iterator[SessionInstance]:
        """
        Returns an iterator on the session instances held in this window that
        have an active connection to a game world.

        Returns:
            The session instances in this window that are currently connected.
        """

        yield from (
            instance for instance in self._instances if instance.connected()
        )

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )
