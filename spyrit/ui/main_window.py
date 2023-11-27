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

from typing import cast

from PySide6.QtCore import Qt, QEvent, QSize, QTimer, Signal, Slot
from PySide6.QtGui import QCloseEvent, QEnterEvent, QIcon, QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QTabWidget,
    QToolButton,
    QWidget,
)

from spyrit import constants
from spyrit.resources.resources import Icon
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.action_with_key_setting import ActionWithKeySetting
from spyrit.ui.sizer import Sizer


class CornerWidgetWrapper(QWidget):
    """
    Lays out a widget so that it looks tidy as a QTabWidget corner widget.

    Args:
        widget: The widget to the used as the QTabWidget's corner.
    """

    def __init__(self, widget: QWidget) -> None:
        super().__init__()

        self.setLayout(layout := QHBoxLayout())
        layout.addWidget(widget)
        layout.setContentsMargins(2, 2, 2, 4)


class TabWidget(QTabWidget):
    """
    A QTabWidget with extra helper methods, tailored for use in this
    application.

    Args:
        parent: The parent widget for this widget.
    """

    # This signal fires whenever a tab is added or removed. Its argument is the
    # new number of tabs.

    tabCountChanged: Signal = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Remove the border around the widget.

        self.setDocumentMode(True)

        # Add a close button to the tabs.

        self.setTabsClosable(True)

        # Set the focus explicitly when the current tab changes.

        self.currentChanged.connect(self._setTabWidgetFocus)

    def addTab(  # type: ignore  # wrong arg annotation in parent.
        self, widget: QWidget, title: str
    ) -> int:
        """
        Appends a tab to the TabWidget, and then switches to it.

        Args:
            widget: The widget to append in a new tab.

            title: The title of that tab.

        Returns:
            The index of the new tab.
        """

        index = super().addTab(widget, title)
        self.setCurrentIndex(index)
        return index

    @Slot()
    def maybeCloseCurrentTab(self) -> None:
        """
        Looks up the currently active tab and closes it if there is no reason
        not to.
        """

        self.tabCloseRequested.emit(self.currentIndex())

    @Slot()
    def switchToPreviousTab(self) -> None:
        """
        Make the previous tab active.
        """

        current_index = self.currentIndex()
        self.setCurrentIndex(current_index - 1)

    @Slot()
    def switchToNextTab(self) -> None:
        """
        Make the next tab active.
        """

        current_index = self.currentIndex()
        self.setCurrentIndex(current_index + 1)

    @Slot()
    def moveCurrentTabLeft(self) -> None:
        """
        Move the current tab one tab to the left.
        """

        current_index = self.currentIndex()
        self._swapTabs(current_index, current_index - 1)

    @Slot()
    def moveCurrentTabRight(self) -> None:
        """
        Move the current tab one tab to the right.
        """

        current_index = self.currentIndex()
        self._swapTabs(current_index, current_index + 1)

    def _swapTabs(self, index_from: int, index_to: int) -> None:
        """
        Swaps the positions of the tabs at the given indexes.

        Args:
            index_from, index_to: The indexes of the tabs to be swapped.
        """

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
        """
        Give the widget whose tab is at the given index the focus.

        Args:
            index: The index of the tab whose widget should get the focus.
        """

        widget = self.widget(index)
        if widget is not None:  # type: ignore
            widget.setFocus()

    def tabInserted(self, index: int) -> None:
        """
        Reimplemented from parent class to emit a signal when a tab is added.

        Args:
            index: The index of the inserted tab.
        """

        self.tabCountChanged.emit(self.count())

        super().tabInserted(index)

    def tabRemoved(self, index: int) -> None:
        """
        Reimplemented from parent class to emit a signal when a tab is removed.

        Args:
            index: The index of the removed tab.
        """

        self.tabCountChanged.emit(self.count())

        super().tabRemoved(index)


class SpyritMainWindow(QMainWindow):
    """
    The main window for the application.

    Args:
        settings: The application-wide settings object.

        state: The application-wide state object.
    """

    # We fire this signal when the window is being asked to close by a user
    # action.

    closeRequested: Signal = Signal()

    # We fire this signal when the user triggered an action requesting that a
    # new window is opened.

    newWindowRequested: Signal = Signal()

    # We fire this signal when the user triggered an action requesting that a
    # new tab is opened in this window.

    newTabRequested: Signal = Signal()

    # We fire this signal when the window's desktop focus status has changed.
    # Its parameter is True if the window now has focus, else False.

    focusChanged: Signal = Signal(bool)

    _settings: SpyritSettings
    _state: SpyritState
    _tab_widget: TabWidget

    def __init__(
        self,
        settings: SpyritSettings,
        state: SpyritState,
    ) -> None:
        super().__init__()

        self._settings = settings
        self._state = state

        # Set up the main widget.

        self._tab_widget = TabWidget(self)
        self._tab_widget.tabCountChanged.connect(self._closeIfEmpty)
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
                self,
                "New window",
                shortcuts.new_window,
                self.newWindowRequested.emit,
            ),
            ActionWithKeySetting(
                self,
                "Close window",
                shortcuts.close_window,
                self.closeRequested.emit,
            ),
            new_tab_action := ActionWithKeySetting(
                self,
                "New tab",
                shortcuts.new_tab,
                self.newTabRequested.emit,
                icon=QIcon(Icon.NEW_TAB_SVG),
            ),
            ActionWithKeySetting(
                self,
                "Next tab",
                shortcuts.switch_to_next_tab,
                self._tab_widget.switchToNextTab,
            ),
            ActionWithKeySetting(
                self,
                "Close tab",
                shortcuts.close_current_tab,
                self._tab_widget.maybeCloseCurrentTab,
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

        sizer = Sizer(self)
        icon_size = sizer.unitSize() + sizer.marginSize()

        corner_button = QToolButton()
        corner_button.setIconSize(QSize(icon_size, icon_size))
        self._tab_widget.setCornerWidget(
            CornerWidgetWrapper(corner_button), Qt.Corner.TopRightCorner
        )
        corner_button.setAutoRaise(True)  # Only draw raised edge on mouseover
        corner_button.setDefaultAction(new_tab_action)

        # Also bind the action to tab bar double-clicks.

        self._tab_widget.tabBarDoubleClicked.connect(new_tab_action.trigger)

    def tabs(self) -> QTabWidget:
        """
        Returns a reference to the central TabWidget in this window.

        Returns:
            The TabWidget hosted in this window.
        """

        return self._tab_widget

    def alert(self) -> None:
        """
        Makes the window call for user attention.
        """
        if (app := QApplication.instance()) is not None:
            cast(QApplication, app).alert(self, 0)

    @Slot(int)
    def _closeIfEmpty(self, tab_count: int) -> None:
        """
        Closes this window if it doesn't contain any tab.

        Args:
            tab_count: The number of tabs currently in this window's tab widget.
        """

        if tab_count == 0:
            # Note that we don't close the window right away, we only schedule
            # the closing, because the code path that triggers this may still
            # need the window around in order to complete without crashing.

            QTimer.singleShot(0, self.close)  # type: ignore # bad annotation.

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Overrides the default close event handler to raise an explicit signal,
        and lets the handler of that signal decide what to do with the window.

        Args:
            event: The close event being processed.
        """

        self.closeRequested.emit()

        # Don't actually follow up on the closing. It will be enacted, if
        # needed, by the SessionWindow instance that owns this window and will
        # handle the closeRequested signal.

        event.ignore()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Overrides the default resize event handler to store the new size in the
        state.

        Args:
            event: The resize event being processed.
        """

        # Store the new window size on resize.

        self._state.ui.window_size.set(event.size())

        return super().resizeEvent(event)

    def enterEvent(self, event: QEnterEvent) -> None:
        """
        Overrides the default enter event handler to raise a signal that the
        window now has focus.
        """

        self.focusChanged.emit(True)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """
        Overrides the default leave event handler to raise a signal that the
        window no longer has focus.
        """

        self.focusChanged.emit(False)
        super().leaveEvent(event)

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )
