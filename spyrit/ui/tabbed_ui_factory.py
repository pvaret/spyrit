# Copyright (c) 2007-2022 Pascal Varet <p.varet@gmail.com>
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
Class that creates and sets up toplevel elements of the UI.
"""


from typing import Callable, Optional

from PySide6 import QtCore

from spyrit.ui import tabbed_ui_element

from . import tabbed_ui_container


class TabbedUiFactory(QtCore.QObject):
    def __init__(
        self,
        tabbed_ui_element_factory: Callable[
            [], tabbed_ui_element.TabbedUiElement
        ],
        parent: Optional[QtCore.QObject] = None,
    ) -> None:

        super().__init__(parent)

        self._tabbed_ui_element_factory = tabbed_ui_element_factory

        # self.windows is in charge of keeping a reference to the existing
        # top-level windows. Nothing else should, so this structure is
        # essentially the source of truth for which windows currently exist.

        self.windows: set[tabbed_ui_container.TabbedUiContainer] = set()

        # Remember the last active window, i.e. the window that last had the
        # focus. It's the window where we'll want to create new tabs when not
        # otherwise specified.

        self.lastActiveWindow: Optional[
            tabbed_ui_container.TabbedUiContainer
        ] = None

    def createNewUiInNewTab(
        self, window: Optional[tabbed_ui_container.TabbedUiContainer] = None
    ) -> tabbed_ui_element.TabbedUiElement:

        if window is None:
            if self.lastActiveWindow is None:
                return self.createNewUiInNewWindow()
            window = self.lastActiveWindow

        new_ui = self._makeNewUi()
        window.pin(new_ui)

        return new_ui

    def createNewUiInNewWindow(self) -> tabbed_ui_element.TabbedUiElement:

        new_ui = self._makeNewUi()

        new_window = self._makeNewWindow()
        new_window.pin(new_ui)

        return new_ui

    def _makeNewWindow(self) -> tabbed_ui_container.TabbedUiContainer:

        new_window = tabbed_ui_container.TabbedUiContainer()

        self.windows.add(new_window)
        self.lastActiveWindow = new_window

        new_window.focusIn.connect(self._updateLastActiveWindowFromSignal)
        new_window.closing.connect(self._onWindowClosing)
        new_window.show()

        new_window.newTabRequested.connect(self._onNewTabRequestedByWindow)

        return new_window

    def _makeNewUi(self) -> tabbed_ui_element.TabbedUiElement:

        new_ui = self._tabbed_ui_element_factory()
        new_ui.wantToDetachToNewWindow.connect(self._onTabDetachRequested)

        return new_ui

    def _updateLastActiveWindowFromSignal(self) -> None:

        window = self.sender()

        if isinstance(window, tabbed_ui_container.TabbedUiContainer):
            self.lastActiveWindow = window

    def _onWindowClosing(self) -> None:

        window = self.sender()

        if isinstance(window, tabbed_ui_container.TabbedUiContainer):

            # If a window is being closed, drop our reference to it.

            self.windows.discard(window)

            # But also pick a new window to be considered the last active, if
            # any.

            if self.lastActiveWindow is window:
                if self.windows:
                    self.lastActiveWindow = self.windows.copy().pop()

                else:
                    self.lastActiveWindow = None

    def _onNewTabRequestedByWindow(self) -> None:

        window = self.sender()

        if isinstance(window, tabbed_ui_container.TabbedUiContainer):
            self.createNewUiInNewTab(window=window)

    def _onTabDetachRequested(self) -> None:

        widget = self.sender()

        if isinstance(widget, tabbed_ui_element.TabbedUiElement):

            widget.wantToBeUnpinned.emit()

            new_window = self._makeNewWindow()
            new_window.pin(widget)
