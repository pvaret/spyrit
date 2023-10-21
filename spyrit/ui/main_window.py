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
import weakref

from PySide6.QtCore import QObject, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QCloseEvent, QResizeEvent
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


class TabProxy(QObject):
    """
    This class provides an interface to directly set properties on a tab
    associated with a widget. It keeps a reference to the tab, but not the
    widget itself.

    Args:
        tab_widget: The QTabWidget instance that the tab being proxied belongs
            to.

        widget: The widget associated with the tab being proxied.
    """

    # This signal is emitted when the proxied tab becomes active or,
    # respectively, inactive.

    active: Signal = Signal(bool)

    # This signal is emitted when a user action is requesting that this tab be
    # closed.

    closeRequested: Signal = Signal()  # noqa: N815

    _tab_widget: QTabWidget
    _widget: weakref.ref[QWidget]
    _active: bool = False

    def __init__(self, tab_widget: QTabWidget, widget: QWidget) -> None:
        # Using the widget itself as the parent here guarantees that this
        # TabProxy will be dereferenced when the widget is destroyed, provided
        # nothing else keep a reference to this TabProxy. (Which they
        # shouldn't.)

        super().__init__(parent=widget)

        self._tab_widget = tab_widget
        self._widget = weakref.ref(widget)

        self._setActiveIndex(tab_widget.currentIndex())
        tab_widget.currentChanged.connect(self._setActiveIndex)
        tab_widget.tabCloseRequested.connect(self._maybeRequestClosing)

    def _index(self) -> int:
        """
        Returns the index of the proxied tab.

        Returns:
            The index of the proxied tab in its QTabWidget, or -1 if the tab
            being proxied no longer exists.
        """

        widget = self._widget()
        if widget is None:
            return -1
        return self._tab_widget.indexOf(widget)

    @Slot(str)
    def setTitle(self, title: str) -> None:
        """
        Sets the title of the proxied tab.

        Args:
            title: The title to give this tab.
        """

        if (index := self._index()) >= 0:
            self._tab_widget.setTabText(index, title)

    def window(self) -> QWidget | None:
        """
        Returns the toplevel window object for this tab's widget, if any.

        Returns:
            A toplevel widget if one exists for this tab, else None.
        """

        if (widget := self._widget()) is not None:
            return widget.window()

        return None

    def close(self) -> None:
        """
        Detaches this tab's widget from its parent. Causes the widget -- and
        therefore this tab -- to be garbage collected, if nothing else is
        keeping a reference to it. Which it shouldn't.
        """

        if (widget := self._widget()) is not None:
            widget.setParent(None)  # type: ignore

    @Slot(int)
    def _setActiveIndex(self, active_index: int) -> None:
        """
        Updates this TabProxy's activity status based on the provided current
        active tab index and this tab's index.

        Args:
            active_index: The index of the tab that just became active.
        """

        active = active_index == self._index()
        if active != self._active:
            self._active = active
            self.active.emit(active)

    @Slot(int)
    def _maybeRequestClosing(self, index: int) -> None:
        """
        Request closing this tab if the given index is that of this tab.

        Args:
            index: The index of the tab to be closed.
        """

        if index == self._index():
            # Note that we don't execute the closing immediately. If we did then
            # the index of next tabs would change before the processing of the
            # signal that triggered this slot is complete, which may cause other
            # tabs to be unexpectedly closed.

            QTimer.singleShot(0, self.closeRequested.emit)  # type: ignore


class TabWidget(QTabWidget):
    """
    A QTabWidget with extra helper methods, tailored for use in this
    application.

    Args:
        parent: The parent widget for this widget.
    """

    # This signal fires whenever a tab is added or removed. Its argument is the
    # new number of tabs.

    tabCountChanged: Signal = Signal(int)  # noqa: N815

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

    # We fire this signal when the window is being asked to close, since there
    # is no native Qt signal for that.

    closing: Signal = Signal(QObject)

    # We fire this signal when the user triggered an action requesting that a
    # new window is opened.

    newWindowRequested: Signal = Signal()  # noqa: N815

    # We fire this signal when the user triggered an action requesting that a
    # new tab is opened in this window.

    newTabRequested: Signal = Signal()  # noqa: N815

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
            new_tab_action := ActionWithKeySetting(
                self, "New tab", shortcuts.new_tab, self.newTabRequested.emit
            ),
            ActionWithKeySetting(
                self,
                "Close tab",
                shortcuts.close_current_tab,
                self._tab_widget.maybeCloseCurrentTab,
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

    def tabs(self) -> QTabWidget:
        """
        Returns a reference to the central TabWidget in this window.

        Returns:
            The TabWidget hosted in this window.
        """

        return self._tab_widget

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
        Overrides the default close event handler to raise an explicit closing
        signal, since Qt doesn't do that by default.

        Args:
            event: The close event being processed.
        """

        self.closing.emit(self)

        return super().closeEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Overrides the default resize event to store the new size in the state.

        Args:
            event: The resize event being processed.
        """

        # Store the new window size on resize.

        self._state.ui.window_size.set(event.size())

        return super().resizeEvent(event)

    def __del__(self) -> None:
        logging.debug(
            "%s (%s) destroyed.", self.__class__.__name__, hex(id(self))
        )
