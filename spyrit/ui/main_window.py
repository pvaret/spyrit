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
A class that implements the main window of the application.
"""

import logging
from typing import Callable

from PySide6.QtCore import QEvent, QObject, Qt, Signal, Slot
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QTabWidget,
    QToolButton,
    QWidget,
)

from spyrit import constants
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.action_with_key_setting import ActionWithKeySetting
from spyrit.ui.main_ui_factory import SpyritMainUIFactory


class CornerWidgetWrapper(QWidget):
    """
    Lays out a widget so that it looks tidy as a QTabWidget corner widget.
    """

    def __init__(self, widget: QWidget) -> None:
        super().__init__()

        self.setLayout(layout := QHBoxLayout())
        layout.addWidget(widget)
        layout.setContentsMargins(2, 2, 2, 4)


class TabWidget(QTabWidget):
    """
    A QTabWidget with extra helper methods.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        # Remove the border around the widget.

        self.setDocumentMode(True)

        # Add a close button to the tabs.

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)

        # Set the focus explicitly when the current tab changes.

        self.currentChanged.connect(self._setTabWidgetFocus)

    def appendTab(self, widget: QWidget, title: str) -> int:
        index = super().addTab(widget, title)
        self.setCurrentIndex(index)
        return index

    @Slot()
    def closeCurrentTab(self) -> None:
        self.closeTab(self.currentIndex())

    @Slot(int)
    def closeTab(self, index: int) -> None:
        if (widget := self.widget(index)) is not None:  # type: ignore
            widget.setParent(None)  # type: ignore

    @Slot()
    def switchToPreviousTab(self) -> None:
        current_index = self.currentIndex()
        self.setCurrentIndex(current_index - 1)

    @Slot()
    def switchToNextTab(self) -> None:
        current_index = self.currentIndex()
        self.setCurrentIndex(current_index + 1)

    @Slot()
    def moveCurrentTabLeft(self) -> None:
        current_index = self.currentIndex()
        self._swapTabs(current_index, current_index - 1)

    @Slot()
    def moveCurrentTabRight(self) -> None:
        current_index = self.currentIndex()
        self._swapTabs(current_index, current_index + 1)

    def _swapTabs(self, index_from: int, index_to: int) -> None:
        index_from = max(0, index_from)
        index_from = min(self.count() - 1, index_from)
        index_to = max(0, index_to)
        index_to = min(self.count() - 1, index_to)

        if index_from == index_to:
            return

        widget_from = self.widget(index_from)
        widget_to = self.widget(index_to)
        title_from = self.tabText(index_from)
        title_to = self.tabText(index_to)
        assert widget_from is not None
        assert widget_to is not None

        # Note that inserting a tab with an existing widget at a new position
        # removes it from its previous position. So we don't need to do that
        # explicitly.

        self.insertTab(index_from, widget_to, title_to)
        self.insertTab(index_to, widget_from, title_from)

        self.setCurrentIndex(index_to)

    @Slot(int)
    def _setTabWidgetFocus(self, index: int) -> None:
        widget = self.widget(index)
        if widget is not None:  # type: ignore
            widget.setFocus()


class SpyritMainWindow(QMainWindow):
    # We fire this signal when the window is being asked to close, since there
    # is no native Qt signal for that.

    closing: Signal = Signal(QObject)

    _settings: SpyritSettings
    _state: SpyritState
    _tab_widget: TabWidget
    _window_factory: Callable[[], None]
    _ui_factory: Callable[[], QWidget]

    def __init__(
        self,
        settings: SpyritSettings,
        state: SpyritState,
        window_factory: Callable[[], None],
        ui_factory: Callable[[], QWidget],
    ) -> None:
        super().__init__()

        self._settings = settings
        self._state = state
        self._window_factory = window_factory
        self._ui_factory = ui_factory

        # Set up the main widget.

        self._tab_widget = TabWidget(self)
        self.setCentralWidget(self._tab_widget)

        # Set up the window properties.

        self.setWindowTitle(constants.APPLICATION_NAME)
        size = state.ui.window_size.get()
        if size.isValid() and not size.isEmpty():
            self.resize(size)

        # Set up keyboard shortcuts.

        shortcuts = settings.shortcuts
        for action in (
            ActionWithKeySetting(
                self, "New window", shortcuts.new_window, self.newWindow
            ),
            new_tab_action := ActionWithKeySetting(
                self, "New tab", shortcuts.new_tab, self.newTab
            ),
            ActionWithKeySetting(
                self,
                "Close tab",
                shortcuts.close_current_tab,
                self._tab_widget.closeCurrentTab,
            ),
            ActionWithKeySetting(
                self,
                "Next tab",
                shortcuts.switch_to_next_tab,
                self._tab_widget.switchToNextTab,
            ),
            ActionWithKeySetting(
                self,
                "Previous tab",
                shortcuts.switch_to_previous_tab,
                self._tab_widget.switchToPreviousTab,
            ),
            ActionWithKeySetting(
                self,
                "Move tab right",
                shortcuts.move_current_tab_right,
                self._tab_widget.moveCurrentTabRight,
            ),
            ActionWithKeySetting(
                self,
                "Move tab left",
                shortcuts.move_current_tab_left,
                self._tab_widget.moveCurrentTabLeft,
            ),
        ):
            self.addAction(action)

        # Bind the "new tab" action above to the tab widget's corner button.

        corner_button = QToolButton()
        self._tab_widget.setCornerWidget(
            CornerWidgetWrapper(corner_button), Qt.Corner.TopLeftCorner
        )
        corner_button.setDefaultAction(new_tab_action)
        corner_button.setText("+")

        # And finally, create one starting game UI.

        self.newTab()

    def newTab(self) -> None:
        title = f"Welcome to {constants.APPLICATION_NAME}!"
        self._tab_widget.appendTab(widget := self._ui_factory(), title)
        widget.destroyed.connect(self._closeIfEmpty)

    def newWindow(self) -> None:
        self._window_factory()

    @Slot()
    def _closeIfEmpty(self) -> None:
        if self._tab_widget.count() == 0:
            self.close()

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Close:
            self.closing.emit(self)

        return super().event(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        # Store the new window size on resize.

        self._state.ui.window_size.set(event.size())

        return super().resizeEvent(event)

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )


class SpyritMainWindowFactory:
    """
    Creates, shows and maintains a reference to the application's main windows.
    """

    _settings: SpyritSettings
    _state: SpyritState
    _windows: set[QObject]
    _ui_factory: Callable[[], QWidget]

    def __init__(self, settings: SpyritSettings, state: SpyritState) -> None:
        self._settings = settings
        self._state = state
        self._windows = set()

        factory = SpyritMainUIFactory(self._settings, self._state)
        self._ui_factory = factory.newUI

    def newWindow(self) -> None:
        # Keep a reference to the new window so it's not immediately garbage
        # collected.

        self._windows.add(
            window := SpyritMainWindow(
                self._settings, self._state, self.newWindow, self._ui_factory
            )
        )

        # But do remove its reference when its getting closed so the
        # object does not leak.

        window.closing.connect(self._forget_window)

        window.show()

    @Slot(QObject)
    def _forget_window(self, obj: QObject) -> None:
        try:
            self._windows.remove(obj)
        except ValueError:
            pass
