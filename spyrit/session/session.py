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
"""

import logging

from PySide6.QtCore import QObject, Signal, Slot

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
    """

    closing: Signal = Signal(QObject)  # noqa: N815

    _settings: SpyritSettings
    _state: SpyritState

    # Keep a reference to the window associated to this SessionWindow. Otherwise
    # the window would be garbage-collected immediately.

    _window: SpyritMainWindow

    def __init__(
        self,
        settings: SpyritSettings,
        state: SpyritState,
        window: SpyritMainWindow,
    ) -> None:
        super().__init__()

        self._settings = settings
        self._state = state
        self._window = window

        window.newTabRequested.connect(self._newInstance)
        window.closing.connect(self._onWindowClosing)

    @Slot()
    def _newInstance(self) -> None:
        window = self.sender()
        if isinstance(window, SpyritMainWindow):
            self.newInstanceForWindow(window)

    def newInstanceForWindow(self, window: SpyritMainWindow) -> None:
        instance = SessionInstance()

        widget = SlidingPaneContainer(window)
        widget.addPaneRight(WelcomePane(self._settings, self._state, instance))

        tab_proxy = window.appendTab(widget, instance.title())
        tab_proxy.active.connect(instance.setActive)

        instance.titleChanged.connect(tab_proxy.setTitle)

    @Slot()
    def _onWindowClosing(self) -> None:
        self.closing.emit(self)

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )


class Session(QObject):
    """
    A class that keeps tracks of the windows that make up the current play
    session, and can respond to requests to create more windows.
    """

    _settings: SpyritSettings
    _state: SpyritState

    # Keep track of SessionWindows so they're not immediately garbage collected,
    # along with their window.

    _session_windows: set[SessionWindow]

    def __init__(self, settings: SpyritSettings, state: SpyritState) -> None:
        super().__init__()

        self._settings = settings
        self._state = state
        self._session_windows = set()

    def newWindow(self) -> None:
        window = SpyritMainWindow(self._settings, self._state)

        window.newWindowRequested.connect(self.newWindow)

        session_window = SessionWindow(self._settings, self._state, window)
        session_window.closing.connect(self._forgetSessionWindow)

        self._session_windows.add(session_window)

        session_window.newInstanceForWindow(window)

        window.show()

    @Slot(SessionWindow)
    def _forgetSessionWindow(self, session_window: SessionWindow) -> None:
        try:
            self._session_windows.remove(session_window)
        except KeyError:
            pass
