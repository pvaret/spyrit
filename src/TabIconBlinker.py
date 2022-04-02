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
# TabIconBlinker.py
#
# Implements the tab icon blinking code.
#


from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QObject
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtCore import QTimeLine


class LED:
    def __init__(self):

        self.ON_UNLIT = QIcon(":/icon/unlit_green_led")
        self.ON_LIT = QIcon(":/icon/lit_green_led")
        self.OFF_UNLIT = QIcon(":/icon/unlit_red_led")
        self.OFF_LIT = QIcon(":/icon/lit_red_led")

    def select(self, on, lit):

        if on:
            return self.ON_LIT if lit else self.ON_UNLIT

        else:
            return self.OFF_LIT if lit else self.OFF_UNLIT


class TabIconBlinker(QObject):
    def __init__(self, tab):

        super().__init__(parent=tab)

        self.led = LED()
        self.tab = tab
        self.is_on = False
        self.visible = True

        self.tab.tabChanged.connect(self.onTabChanged)

        self.blinker = QTimeLine(50, self)  # ms
        self.blinker.setFrameRange(0, 1)
        # TODO: Fix the signal connection typing somehow.
        self.blinker.frameChanged.connect(self.iconBlink)  # type: ignore
        self.blinker.finished.connect(self.steadyIcon)  # type: ignore

    def startIconBlink(self):

        if self.blinker.state() == QTimeLine.State.NotRunning:
            self.blinker.start()

    @pyqtSlot(int)
    def iconBlink(self, frame):

        led = self.led.select(on=self.is_on, lit=(frame % 2 == 0))
        self.tab.setTabIcon(led)

    def steadyIcon(self):

        if self.blinker.state() == QTimeLine.State.Running:
            return

        led = self.led.select(on=self.is_on, lit=not self.visible)
        self.tab.setTabIcon(led)

    def onTabChanged(self, is_now_visible: bool):

        self.visible = is_now_visible

        if is_now_visible:
            self.steadyIcon()

    def setLedOn(self, is_on: bool = True):

        if is_on and not self.is_on:
            self.is_on = True
            self.startIconBlink()

    def setLedOff(self, is_off: bool = True):

        if is_off and self.is_on:
            self.is_on = False
            self.startIconBlink()
