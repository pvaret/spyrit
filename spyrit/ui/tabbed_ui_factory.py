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
Class that creates and sets up toplevel elements of the UI.
"""


from typing import Callable

from PySide6.QtCore import QObject

from spyrit.ui.tabbed_ui_container import TabbedUIContainer
from spyrit.ui.tabbed_ui_element import TabbedUIElement


class TabbedUIFactory(QObject):
    """
    The factory class that knows how to plug together tabbed UI containers and
    tabbed UI elements.
    """

    _tabbed_ui_container_factory: Callable[[], TabbedUIContainer]
    _tabbed_ui_element_factory: Callable[[], TabbedUIElement]
    _last_active_window: TabbedUIContainer | None
    _windows: set[TabbedUIContainer]

    def __init__(
        self,
        tabbed_ui_element_factory: Callable[[], TabbedUIElement],
        tabbed_ui_container_factory: Callable[
            [], TabbedUIContainer
        ] = TabbedUIContainer,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        # Remember the factories that knows how to create new UI elements and
        # containers.

        self._tabbed_ui_container_factory = tabbed_ui_container_factory
        self._tabbed_ui_element_factory = tabbed_ui_element_factory

        # self.windows is in charge of keeping a reference to the existing
        # top-level windows. Nothing else should, so this structure is
        # essentially the source of truth for which windows currently exist.

        self._windows = set()

        # Remember the last active window, i.e. the window that last had the
        # focus. It's the window where we'll want to create new tabs when not
        # otherwise specified.

        self._last_active_window = None

    def createNewUIInNewTab(
        self, window: TabbedUIContainer | None = None
    ) -> TabbedUIElement:
        """
        Instantiate a new UI element, and add it under a new tab in the
        currently active container.
        """

        if window is None:
            if self._last_active_window is None:
                return self.createNewUIInNewWindow()
            window = self._last_active_window

        new_ui = self._makeNewUI()
        window.pin(new_ui)

        return new_ui

    def createNewUIInNewWindow(self) -> TabbedUIElement:
        """
        Instantiate a new UI element, and add it under a new tab in a
        new container.
        """

        new_ui = self._makeNewUI()

        new_window = self._makeNewWindow()
        new_window.pin(new_ui)

        return new_ui

    def _makeNewWindow(self) -> TabbedUIContainer:
        """
        Instantiate and set up a new container.
        """

        new_window = self._tabbed_ui_container_factory()

        self._windows.add(new_window)
        self._last_active_window = new_window

        new_window.focusIn.connect(self._updateLastActiveWindowFromSignal)
        new_window.closing.connect(self._onWindowClosing)
        new_window.show()

        new_window.newTabRequested.connect(self._onNewTabRequestedByWindow)
        new_window.newWindowRequested.connect(self.createNewUIInNewWindow)

        return new_window

    def _makeNewUI(self) -> TabbedUIElement:
        """
        Instantiate and set up a new UI element.
        """

        new_ui = self._tabbed_ui_element_factory()
        new_ui.wantToDetachToNewWindow.connect(self._onTabDetachRequested)

        return new_ui

    def _updateLastActiveWindowFromSignal(self) -> None:
        """
        Take note of the last active container if that changed.
        """

        window = self.sender()

        if isinstance(window, TabbedUIContainer):
            self._last_active_window = window

    def _onWindowClosing(self) -> None:
        """
        Perform cleanup when a window is closing.
        """

        window = self.sender()

        if isinstance(window, TabbedUIContainer):
            # If a window is being closed, drop our reference to it.

            self._windows.discard(window)

            # But also pick a new window to be considered the last active, if
            # any.

            if self._last_active_window is window:
                if self._windows:
                    self._last_active_window = self._windows.copy().pop()

                else:
                    self._last_active_window = None

    def _onNewTabRequestedByWindow(self) -> None:
        """
        Enact request to create a new tab. Instantiates a new UI element.
        """

        window = self.sender()

        if isinstance(window, TabbedUIContainer):
            self.createNewUIInNewTab(window=window)

    def _onTabDetachRequested(self) -> None:
        """
        Enact a UI element's request to have its tab detached into a new
        container.
        """

        widget = self.sender()

        if isinstance(widget, TabbedUIElement):
            widget.wantToBeUnpinned.emit()

            new_window = self._makeNewWindow()
            new_window.pin(widget)
