# -*- coding: utf-8 -*-

## Copyright (c) 2007-2021 Pascal Varet <p.varet@gmail.com>
##
## This file is part of Spyrit.
##
## Spyrit is free software; you can redistribute it and/or modify it under the
## terms of the GNU General Public License version 2 as published by the Free
## Software Foundation.
##
## You should have received a copy of the GNU General Public License along with
## Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
## Fifth Floor, Boston, MA  02110-1301  USA
##

##
## TabDelegate.py
##
## Holds the TabDelegate class, a helper class which allows widgets contained
## in a QTabWidget to call QTabWidget methods that concern their own tab.
##


from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTabWidget


class TabDelegate(QObject):

    DELEGATES = set(
        [
            "removeTab",
            "isTabEnabled",
            "setTabEnabled",
            "tabIcon",
            "setTabIcon",
            "tabText",
            "setTabText",
            "tabToolTip",
            "setTabToolTip",
            "tabWhatsThis",
            "setTabWhatsThis",
        ]
    )

    tabChanged = pyqtSignal(bool)
    tabCloseRequested = pyqtSignal()

    def __init__(self, tabwidget, widget):

        super().__init__(parent=widget)

        self.widget = widget
        self.tabwidget = tabwidget

        assert isinstance(self.tabwidget, QTabWidget)

        self.is_current_tab = False

        self.tabwidget.currentChanged.connect(self.onTabChanged)
        self.tabwidget.tabCloseRequested.connect(self.onTabCloseRequested)

    @pyqtSlot(int)
    def onTabChanged(self, i):

        tabindex = self.tabwidget.indexOf(self.widget)

        is_now_current_tab = tabindex == i

        if is_now_current_tab != self.is_current_tab:

            self.tabChanged.emit(is_now_current_tab)
            self.is_current_tab = is_now_current_tab

    @pyqtSlot(int)
    def onTabCloseRequested(self, i):

        if i == self.tabwidget.indexOf(self.widget):
            self.tabCloseRequested.emit()

    def __getattr__(self, attr):

        if attr not in self.DELEGATES:
            raise AttributeError(attr)

        ## Might raise AttributeError, which is okay:
        method = getattr(self.tabwidget, attr)

        tabindex = self.tabwidget.indexOf(self.widget)

        def delegated_method(*args):
            return method(tabindex, *args)

        return delegated_method
