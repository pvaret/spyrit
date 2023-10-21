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
Provides classes to manage and maintain the status of an application session,
where a session is made of windows, and a window is made of game instances.

Essentially, sessions are the model counterpart to the UI's view/controller. The
fact that the UI is both view and controller makes things a little finicky, but
broadly here's the design we're going for:
  - Session, SessionWindow and Instance are models for respectively, the
    application, one window, and one tab.
  - View update mechanisms are implemented as methods on UI elements.
  - User interactions, so the controller part, are reported by UI elements with
    signals.
"""

import logging

from PySide6.QtCore import QObject, Slot

from spyrit.session.instance import SessionInstance
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.main_window import SpyritMainWindow
from spyrit.ui.sliding_pane_container import SlidingPaneContainer
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

    def __init__(
        self,
        parent: QObject,
        settings: SpyritSettings,
        state: SpyritState,
        window: SpyritMainWindow,
    ) -> None:
        super().__init__(parent)

        self._settings = settings
        self._state = state
        self._window = window

        window.newTabRequested.connect(self.newInstance)
        window.closing.connect(self.close)

    @Slot()
    def newInstance(self) -> None:
        """
        Creates a new SessionInstance, the corresponding UI, and adds the UI to
        the window and the instance to this SessionWindow.
        """

        instance = SessionInstance()

        # Create the UI for a game.

        widget = SlidingPaneContainer(self._window)
        widget.addPaneRight(WelcomePane(self._settings, self._state, instance))

        # Add the UI to a tab and bind the instance to that tab.

        self._window.tabs().appendTab(widget, instance.title())
        tab_proxy = self._window.tabs().tabForWidget(widget)
        tab_proxy.active.connect(instance.setActive)

        instance.setTab(tab_proxy)

    @Slot()
    def close(self) -> None:
        """
        Causes this SessionWindow to detach itself from its parent, which should
        trigger its garbage collection.
        """

        self.setParent(None)  # type: ignore

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )


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

    def __init__(self, settings: SpyritSettings, state: SpyritState) -> None:
        super().__init__()

        self._settings = settings
        self._state = state

    def newWindow(self) -> None:
        """
        Creates a new app window and its attached SessionWindow.
        """

        window = SpyritMainWindow(self._settings, self._state)

        window.newWindowRequested.connect(self.newWindow)

        session_window = SessionWindow(
            self, self._settings, self._state, window
        )

        session_window.newInstance()

        window.show()
