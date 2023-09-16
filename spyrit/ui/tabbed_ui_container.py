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
Class that provides a tabbed main window container.
"""


from typing import cast

from PySide6.QtCore import QEvent, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QWidget,
)

from spyrit import constants
from spyrit.ui.tabbed_ui_element import TabbedUIElement


class TabbedUIContainer(QMainWindow):
    """
    A top-level window class intended to just serve as a container for
    individual UIs.

    It makes no application-centric decisions. It just contains individual
    application UIs. Those UIs are in charge of requesting window-level changes.
    """

    # This signal is emitted when this window newly received the focus.

    focusIn: Signal = Signal()  # noqa: N815

    # This signal is emitted when this window is in the process of closing.

    closing: Signal = Signal()

    # This signal is emitted when a user interaction with this window should
    # result in a new tab being opened.

    newTabRequested: Signal = Signal()  # noqa: N815

    # This signal is emitted when a user interaction with this window should
    # result in a new window being opened.

    newWindowRequested: Signal = Signal()  # noqa: N815

    _tab_widget: QTabWidget

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle(constants.APPLICATION_NAME)

        # Create and set up the QTabWidget that's going to contain the
        # individual UIs.

        self._tab_widget = QTabWidget(self)
        self._tab_widget.setMovable(True)
        self._tab_widget.setTabsClosable(True)
        self.setCentralWidget(self._tab_widget)

        self._tab_widget.tabCloseRequested.connect(self._onTabCloseRequested)

        # Set up the button that requests creation of new tabs. The default
        # layout is not great, so we have to create a container for the button
        # and give it a better layout.

        self._tab_widget.setCornerWidget(
            new_tab_corner_widget := QWidget(), corner=Qt.Corner.TopLeftCorner
        )

        new_tab_corner_widget.setLayout(new_tab_corner_layout := QHBoxLayout())
        new_tab_corner_layout.setContentsMargins(2, 2, 2, 2)

        new_tab_corner_layout.addWidget(new_tab_button := QPushButton("+"))
        new_tab_button.setToolTip("New tab")

        new_tab_corner_layout.activate()  # Force the height to be computed.
        new_tab_button.setFixedWidth(new_tab_button.height())
        new_tab_button.clicked.connect(self.newTabRequested)

    def pin(self, widget: TabbedUIElement) -> None:
        """
        Pin the given UI to this window and give it focus.
        """

        widget.setParent(self._tab_widget)
        widget.wantToBeUnpinned.connect(self._onUIRequestedClosing)

        self._tab_widget.addTab(widget, "")
        self._tab_widget.setCurrentWidget(widget)

    def unpin(self, widget: TabbedUIElement) -> None:
        """
        Unpin the given UI element from this window. It can then be dropped or
        pinned to a different window.
        """

        index = self._tab_widget.indexOf(widget)
        if index != -1:
            self._tab_widget.removeTab(index)

            # WORKAROUND: setParent() type hint mistakenly thinks that the
            # method cannot take a None argument.

            widget.setParent(cast(QWidget, None))
            widget.hide()

            if self._tab_widget.count() == 0:
                self.close()

    @Slot()
    def maybeCloseCurrentTab(self) -> None:
        """
        Ask the currently active UI element to close itself. It is allowed to
        decline.
        """

        widget = self._tab_widget.currentWidget()

        if isinstance(widget, TabbedUIElement):
            widget.maybeClose()

    @Slot()
    def switchToNextTab(self) -> None:
        """
        Make the tab immediately to the right of the currently active one
        active, if any.
        """

        index = self._tab_widget.currentIndex()

        if index < 0 or index >= self._tab_widget.count() - 1:
            return

        self._tab_widget.setCurrentIndex(index + 1)

    @Slot()
    def switchToPreviousTab(self) -> None:
        """
        Make the tab immediately to the left of the currently active one
        active, if any.
        """

        index = self._tab_widget.currentIndex()

        if index < 1 or index >= self._tab_widget.count():
            return

        self._tab_widget.setCurrentIndex(index - 1)

    @Slot()
    def moveCurrentTabRight(self) -> None:
        """
        Swap the currently active tab and the one immediately to the right, if
        any.
        """

        index = self._tab_widget.currentIndex()

        if index < 0 or index >= self._tab_widget.count() - 1:
            return

        widget_left = self._tab_widget.widget(index)
        widget_right = self._tab_widget.widget(index + 1)

        if isinstance(widget_left, TabbedUIElement) and isinstance(
            widget_right, TabbedUIElement
        ):
            self._tab_widget.removeTab(index)
            self._tab_widget.removeTab(index)
            self._tab_widget.insertTab(index, widget_left, "")
            self._tab_widget.insertTab(index, widget_right, "")
            self._tab_widget.setCurrentIndex(index + 1)

    @Slot()
    def moveCurrentTabLeft(self) -> None:
        """
        Swap the currently active tab and the one immediately to the left, if
        any.
        """

        index = self._tab_widget.currentIndex()

        if index < 1 or index >= self._tab_widget.count():
            return

        widget_left = self._tab_widget.widget(index - 1)
        widget_right = self._tab_widget.widget(index)

        if isinstance(widget_left, TabbedUIElement) and isinstance(
            widget_right, TabbedUIElement
        ):
            self._tab_widget.removeTab(index - 1)
            self._tab_widget.removeTab(index - 1)
            self._tab_widget.insertTab(index - 1, widget_left, "")
            self._tab_widget.insertTab(index - 1, widget_right, "")
            self._tab_widget.setCurrentIndex(index - 1)

    def event(self, event: QEvent) -> bool:
        """
        Emit relevant signals when the corresponding events are received.
        """

        if event.type() == QEvent.Type.WindowActivate:
            if self.isActiveWindow():
                self.focusIn.emit()

        if event.type() == QEvent.Type.Close:
            self.closing.emit()

        return super().event(event)

    @Slot(int)
    def _onTabCloseRequested(self, index: int) -> None:
        """
        This signal handler should be called when a UI element was interacted
        with by the user in order to close a tab. The decision of whether to
        close is however up to the widget in the tab.
        """

        widget = self._tab_widget.widget(index)

        if isinstance(widget, TabbedUIElement):
            widget.maybeClose()

    @Slot()
    def _onUIRequestedClosing(self) -> None:
        """
        This signal handler should be called when the widget in a tab agrees to
        be closed.
        """

        widget = self.sender()

        if isinstance(widget, TabbedUIElement):
            self.unpin(widget)
