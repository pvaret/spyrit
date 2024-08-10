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
Provides classes to manage and maintain the status of an application session,
where a session is made of windows, and a window is made of game instances.

Essentially, sessions are the model counterpart to the UI's view/controller. The
fact that the UI is both view and controller makes things a little finicky, but
broadly here's the design we're going for:
  - Session, SessionWindow and SessionInstance are models for respectively, the
    application, one window, and one tab.
  - View update mechanisms are implemented as methods on UI elements.
  - User interactions, so the controller part, are reported by UI elements with
    signals.
"""

import weakref

from typing import cast

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication

from spyrit.session.window import SessionWindow
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.dialogs import maybeAskUserIfReadyToQuit
from spyrit.ui.main_window import SpyritMainWindow


class Session(QObject):
    """
    A class that keeps tracks of the windows that make up the current play
    session, and can respond to requests to create more windows.

    Args:
        settings: The application-wide settings object.

        state: The application-wide state object.
    """

    _settings: SpyritSettings
    _state: SpyritState

    # Store only weak references to the window session objects. Lifetime
    # management happens through QObject parenting.

    _windows: weakref.WeakSet[SessionWindow]

    def __init__(self, settings: SpyritSettings, state: SpyritState) -> None:
        super().__init__()

        self._settings = settings
        self._state = state
        self._windows = weakref.WeakSet()

    def newWindow(self) -> None:
        """
        Creates a new app window and its attached SessionWindow.
        """

        # Create and set up the window.

        window = SpyritMainWindow(self._settings, self._state)
        window.newWindowRequested.connect(self.newWindow)
        window.quitRequested.connect(self.maybeQuitApplication)

        # Create the session to go with the window, and create a new instance in
        # it so it's not empty.

        session_window = SessionWindow(
            self, self._settings, self._state, window
        )
        session_window.newInstance()
        self._windows.add(session_window)

        # And show the window.

        window.show()

    @Slot()
    def maybeQuitApplication(self) -> None:
        """
        Quits the application if no window contains connected games, else asks
        the user if they're fine closing them and quitting.
        """

        app = cast(QApplication | None, QApplication.instance())
        active_window = app and app.activeWindow()
        connected_instances = [
            instance.title()
            for window in self._windows
            for instance in window
            if instance.connected()
        ]

        if maybeAskUserIfReadyToQuit(active_window, connected_instances):
            self.quit()

    def quit(self) -> None:
        """
        Closes all the session windows. This will cause the application to
        terminate.
        """

        for window in self._windows:
            window.close()
