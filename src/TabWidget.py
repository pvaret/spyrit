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


from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTabBar
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QStackedWidget


class TabBar(QTabBar):
    "A QTabBar with a few added features."

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.last_middle_click_index = None

    def mousePressEvent(self, e):

        if e.button() == Qt.MiddleButton and self.tabsClosable():

            i = self.tabAt(e.pos())
            self.last_middle_click_index = i

        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):

        i = self.tabAt(e.pos())

        if (
            e.button() == Qt.MiddleButton
            and self.tabsClosable()
            and i is not None
            and i == self.last_middle_click_index
        ):

            self.tabCloseRequested.emit(i)
            e.accept()

        else:
            super().mouseReleaseEvent(e)

        self.last_middle_click_index = None


class TabWidget(QTabWidget):
    "A QTabWidget with a few added features."

    numberOfTabChanged = pyqtSignal(int)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setTabBar(TabBar(self))

    def tabInserted(self, i):

        # Ensures that the 'currentChanged( int )' signal is sent when the tab bar
        # is modified, even if Qt doesn't think it should.

        self.currentChanged.emit(self.currentIndex())
        self.numberOfTabChanged.emit(self.count())

    def tabRemoved(self, i):

        # Ensures that the 'currentChanged( int )' signal is sent when the tab bar
        # is modified, even if Qt doesn't think it should.

        self.currentChanged.emit(self.currentIndex())
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
            self.tabCloseRequested.emit(i)


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

    @pyqtSlot(int)
    def switchView(self, tabcount):

        current = self.tabwidget if tabcount > 0 else self.fallback
        self.setCurrentWidget(current)
