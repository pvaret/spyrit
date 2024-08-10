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

from spyrit import constants
from spyrit.session.instance import SessionInstance
from spyrit.session.properties import InstanceProperties
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.dialogs import maybeAskUserIfReadyToClose
from spyrit.ui.instance_ui import InstanceUI
from spyrit.ui.main_window import SpyritMainWindow
from spyrit.ui.tab_proxy import TabProxy


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

    # Keep track of this window's instances, without references. Lifetime
    # management happens through QObject parenting.

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
        window.closeRequested.connect(self._maybeCloseWindow)

    @Slot()
    def newInstance(self) -> None:
        """
        Creates a new SessionInstance, the corresponding UI, and adds the UI to
        the window and the instance to this SessionWindow.
        """

        # Create the UI for a game.

        properties = InstanceProperties()
        ui = InstanceUI(self._window, self._settings, self._state, properties)

        # Create and set up the instance.

        self._instances.add(instance := SessionInstance(self, ui, properties))

        # Plug quit requests from the game UI to the window.

        ui.quitRequested.connect(self._window.quitRequested)

        # Add the UI to a tab and bind the instance to that tab.

        self._window.tabs().addTab(ui, constants.DEFAULT_TAB_TITLE)

        tab = TabProxy(self._window.tabs(), ui)
        ui.tabUpdateRequested.connect(tab.updateTab)
        tab.closeRequested.connect(instance.maybeClose)

    @Slot()
    def _maybeCloseWindow(self) -> None:
        """
        Closes this window if it contains no connected games, or asks the user
        if they're fine closing them.
        """

        connected_instances = [
            instance.title() for instance in self if instance.connected()
        ]

        if maybeAskUserIfReadyToClose(self._window, connected_instances):
            self.close()

    def close(self) -> None:
        """
        Causes this SessionWindow to detach itself from its parent, which should
        trigger its garbage collection.
        """

        self.setParent(None)

    def __iter__(self) -> Iterator[SessionInstance]:
        yield from self._instances

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )
