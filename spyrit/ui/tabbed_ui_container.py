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
Class that provides a tabbed main window container.
"""

from typing import Optional, cast

from PySide6 import QtCore, QtGui, QtWidgets

from spyrit.constants import MINIMUM_WINDOW_HEIGHT, MINIMUM_WINDOW_WIDTH

from . import tabbed_ui_element


class TabbedUiContainer(QtWidgets.QMainWindow):
    """
    A top-level window class intended to just serve as a container for
    individual UIs.

    It makes no application-centric decisions. It just contains individual
    application UIs. Those UIs are in charge of requesting window-level changes,
    such as setting a new title.
    """

    # This signal is emitted when this window newly received the focus.

    focusIn = QtCore.Signal()

    # This signal is emitted when this window is in the process of closing.

    closing = QtCore.Signal()

    # This signal is emitted when a user interaction with this window should
    # result in a new tab being opened.

    newTabRequested = QtCore.Signal()

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumSize(MINIMUM_WINDOW_WIDTH, MINIMUM_WINDOW_HEIGHT)
        self.setWindowTitle("")

        # Create and set up the QTabWidget that's going to contain the
        # individual UIs.

        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabsClosable(True)
        self.setCentralWidget(self.tabWidget)

        self.propertyRefreshTimer = QtCore.QTimer()
        self.propertyRefreshTimer.setSingleShot(True)
        self.propertyRefreshTimer.setInterval(0)

        # WORKAROUND(PySide6 v6.2.4): the QTimer.timeout() signal is not
        # properly declared in PySide6 but does work fine. Just ignore typing
        # errors.

        self.propertyRefreshTimer.timeout.connect(  # type: ignore
            self._applyCurrentTabProperties
        )

        # WORKAROUND(PySide6 v6.2.4): the QTabWidget.currentChanged() and
        # tabCloseRequested() signals are not properly declared in PySide6 but
        # do work fine. Just ignore typing errors.

        self.tabWidget.currentChanged.connect(  # type: ignore
            self._onCurrentTabChanged
        )
        self.tabWidget.tabCloseRequested.connect(  # type: ignore
            self._onTabCloseRequested
        )

        # Set up the button that requests creation of new tabs. The default
        # layout is not great, so we have to create a container for the button
        # and give it a better layout.

        cornerWidget = QtWidgets.QWidget(self.tabWidget)

        newTabButton = QtWidgets.QPushButton("+", parent=cornerWidget)
        newTabButton.setToolTip("New tab")
        newTabButton.setFixedWidth(newTabButton.height())

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(newTabButton)
        layout.setContentsMargins(2, 2, 2, 2)
        cornerWidget.setLayout(layout)

        self.tabWidget.setCornerWidget(
            cornerWidget, corner=QtCore.Qt.TopLeftCorner
        )

        # WORKAROUND(PySide6 v6.2.4): the QPushButton.clicked() signal is
        # not properly declared in PySide6 but does work fine. Just ignore
        # typing errors.

        newTabButton.clicked.connect(self.newTabRequested)  # type: ignore

    def pin(self, widget: tabbed_ui_element.TabbedUiElement) -> None:
        """
        Pin the given UI to this window and give it focus.
        """

        widget.setParent(self.tabWidget)
        widget.tabTitleChanged.connect(self._onTabTitleChanged)
        widget.windowTitleChanged.connect(self._onWindowTitleChanged)
        widget.wantToBeUnpinned.connect(self._onUiRequestedClosing)

        self.tabWidget.addTab(widget, widget.tabTitle())
        self.tabWidget.setCurrentWidget(widget)
        self._applyTabProperties(widget)

    def unpin(self, widget: tabbed_ui_element.TabbedUiElement) -> None:
        """
        Unpin the given UI element from this window. It can then be dropped or
        pinned to a different window.
        """

        index = self.tabWidget.indexOf(widget)
        if index != -1:
            self.tabWidget.removeTab(index)

            # WORKAROUND: setParent() type hint mistakenly thinks that the
            # method cannot take a None argument.

            widget.setParent(cast(QtWidgets.QWidget, None))
            widget.hide()

            if self.tabWidget.count() == 0:
                self.close()

    def event(self, event: QtCore.QEvent) -> bool:
        """
        Emit relevant signals when the corresponding events are received.
        """

        if event.type() == QtCore.QEvent.WindowActivate:
            if self.isActiveWindow():
                self.focusIn.emit()

        if event.type() == QtCore.QEvent.Close:
            self.closing.emit()

        return super().event(event)

    def showEvent(self, event: QtGui.QShowEvent) -> None:

        # WORKAROUND: There is a race condition wherein Qt fails to set the
        # window title before the window is shown. So we explicitly re-apply the
        # current tab's properties on the next iteration of the main loop after
        # the window is shown.

        self.propertyRefreshTimer.start()

        return super().showEvent(event)

    def _applyTabProperties(
        self, widget: tabbed_ui_element.TabbedUiElement
    ) -> None:
        """
        Apply the given tab's properties to the containing window.
        """

        # WORKAROUND: Qt does not update the title if it thinks the new title is
        # identical to the previous one. Which is a problem when the title was
        # not in fact set due to the race condition mentioned above. So we
        # change the title twice to force the update.

        self.setWindowTitle("")
        self.setWindowTitle(widget.windowTitle())

    def _applyCurrentTabProperties(self) -> None:

        widget = self.tabWidget.currentWidget()

        if isinstance(widget, tabbed_ui_element.TabbedUiElement):
            self._applyTabProperties(widget)

    def _onTabTitleChanged(self, title: str) -> None:
        """
        Enact a tab's request to change its title.
        """

        widget = self.sender()

        if isinstance(widget, tabbed_ui_element.TabbedUiElement):

            index = self.tabWidget.indexOf(widget)
            if index != -1:
                self.tabWidget.setTabText(index, title)

    def _onWindowTitleChanged(self, title: str) -> None:
        """
        Enact a tab's request to change the window's title.
        """

        widget = self.sender()

        if isinstance(widget, tabbed_ui_element.TabbedUiElement):
            if self.tabWidget.currentWidget() is widget:
                self.setWindowTitle(title)

    def _onCurrentTabChanged(self) -> None:
        """
        Update the window's properties on the basis of the currently visible
        tab.
        """

        widget = self.tabWidget.currentWidget()

        if isinstance(widget, tabbed_ui_element.TabbedUiElement):
            self._applyTabProperties(widget)

    def _onTabCloseRequested(self, index: int) -> None:
        """
        This signal handler should be called when a UI element was interacted
        with by the user in order to close a tab. The decision of whether to
        close is however up to the widget in the tab.
        """

        widget = self.tabWidget.widget(index)

        if isinstance(widget, tabbed_ui_element.TabbedUiElement):
            widget.maybeClose()

    def _onUiRequestedClosing(self) -> None:
        """
        This signal handler should be called when the widget in a tab agrees to
        be closed.
        """

        widget = self.sender()

        if isinstance(widget, tabbed_ui_element.TabbedUiElement):
            self.unpin(widget)
