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

#
# TabWidget.py
#
# Holds our QTabWidget customizations.
#


from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QTabBar
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtWidgets import QStackedWidget


class TabBar(QTabBar):
    "A QTabBar with a few added features."

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.last_middle_click_index = None

    def mousePressEvent(self, event):  # type: ignore

        if (
            event.button() == Qt.MouseButton.MiddleButton
            and self.tabsClosable()
        ):

            i = self.tabAt(event.pos())
            self.last_middle_click_index = i

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):  # type: ignore

        i = self.tabAt(event.pos())

        if (
            event.button() == Qt.MouseButton.MiddleButton
            and self.tabsClosable()
            and i == self.last_middle_click_index
        ):

            self.tabCloseRequested.emit(i)  # type: ignore
            event.accept()

        else:
            super().mouseReleaseEvent(event)

        self.last_middle_click_index = None


class TabWidget(QTabWidget):
    "A QTabWidget with a few added features."

    numberOfTabChanged = pyqtSignal(int)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setTabBar(TabBar(self))

    def tabInserted(self, index):

        # Ensures that the 'currentChanged( int )' signal is sent when the tab
        # bar is modified, even if Qt doesn't think it should.

        self.currentChanged.emit(self.currentIndex())  # type: ignore
        self.numberOfTabChanged.emit(self.count())

    def tabRemoved(self, index):

        # Ensures that the 'currentChanged( int )' signal is sent when the tab
        # bar is modified, even if Qt doesn't think it should.

        self.currentChanged.emit(self.currentIndex())  # type: ignore
        self.numberOfTabChanged.emit(self.count())

    def previousTab(self):

        i = self.currentIndex()
        if i > 0:
            self.setCurrentIndex(i - 1)

    def nextTab(self):

        i = self.currentIndex()
        if i < self.count() - 1:
            self.setCurrentIndex(i + 1)

    def closeTab(self):

        i = self.currentIndex()
        if i >= 0:
            self.tabCloseRequested.emit(i)  # type: ignore


class FallbackTabWidget(QStackedWidget):
    """A widget that takes a tabwidget and a fallback widget and displays the
    latter when the former has no tab."""

    def __init__(self, parent=None, tabwidget=None, fallback=None):

        super().__init__(parent)

        if fallback is None:
            fallback = QWidget(parent)

        if tabwidget is None:
            tabwidget = TabWidget(parent)

        assert isinstance(tabwidget, TabWidget)

        self.tabwidget = tabwidget
        self.fallback = fallback

        self.addWidget(self.tabwidget)
        self.addWidget(self.fallback)

        self.setCurrentWidget(self.fallback)

        self.tabwidget.numberOfTabChanged.connect(self.switchView)

    def switchView(self, tabcount: int):

        current = self.tabwidget if tabcount > 0 else self.fallback
        self.setCurrentWidget(current)
