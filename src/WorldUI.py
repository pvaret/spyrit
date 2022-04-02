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
# WorldUI.py
#
# Contains the WorldUI class, which manages a world's widget for reading and
# writing.
#


from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSize
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import pyqtSignal

from PyQt6.QtWidgets import QStyle
from PyQt6.QtWidgets import QToolBar
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QSplitter
from PyQt6.QtWidgets import QApplication

from pipeline.ChunkData import ChunkType
from ActionSet import ActionSet
from Autocompleter import Autocompleter
from ConfirmDialog import confirmDialog
from OutputManager import OutputManager
from SplittableTextView import SplittableTextView
from World import World
from WorldInputUI import WorldInputUI


class WorldUI(QSplitter):

    requestAttention = pyqtSignal()

    def __init__(self, world: World, parent: Optional[QWidget] = None):

        super().__init__(Qt.Orientation.Vertical, parent)

        self.world: World = world

        self.world.socketpipeline.addSink(
            self.windowAlert, ChunkType.PACKETBOUND | ChunkType.NETWORK
        )

        # Setup input and output UI.

        self.outputui = SplittableTextView(self)
        self.addWidget(self.outputui)

        self.outputui.setFocusProxy(self)

        self.output_manager = OutputManager(world, self.outputui)

        self.inputui = WorldInputUI(self, world)
        self.addWidget(self.inputui)

        self.secondaryinputui = WorldInputUI(
            self, world, shouldsavehistory=False
        )
        self.addWidget(self.secondaryinputui)
        self.secondaryinputui.hide()

        self.inputui.returnPressed.connect(self.outputui.pingPage)
        self.secondaryinputui.returnPressed.connect(self.outputui.pingPage)

        self.world.socketpipeline.pipeline.flushBegin.connect(
            self.output_manager.textcursor.beginEditBlock
        )

        self.world.socketpipeline.pipeline.flushEnd.connect(
            self.output_manager.textcursor.endEditBlock
        )

        self.world.socketpipeline.pipeline.flushEnd.connect(
            self.outputui.repaint
        )

        world.socketpipeline.addSink(
            self.output_manager.processChunk,
            ChunkType.TEXT | ChunkType.FLOWCONTROL | ChunkType.NETWORK,
        )

        world.socketpipeline.addSink(
            self.output_manager.textformatmanager.processChunk,
            ChunkType.ANSI | ChunkType.HIGHLIGHT,
        )

        self.setFocusProxy(self.inputui)

        self.inputui.focusChanged.connect(self.setFocusProxy)
        self.secondaryinputui.focusChanged.connect(self.setFocusProxy)

        # Setup autocompleter.

        self.autocompleter = Autocompleter()
        world.socketpipeline.addSink(self.autocompleter.sink)

        # Setup splitter.

        self.setChildrenCollapsible(False)
        self.setSizes(world.state._ui._splitter._sizes)

        self.splitterMoved.connect(self.saveSplitterPosition)  # type: ignore

        # Create toolbar and bind World-related actions.

        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setContextMenuPolicy(
            Qt.ContextMenuPolicy.PreventContextMenu
        )
        self.toolbar.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon
        )

        self.toolbar.setWindowTitle(world.title())

        self.actionset = ActionSet(self)

        self.actionset.bindAction("stepup", self.outputui.stepUp)
        self.actionset.bindAction("stepdown", self.outputui.stepDown)
        self.actionset.bindAction("pageup", self.outputui.pageUp)
        self.actionset.bindAction("pagedown", self.outputui.pageDown)
        self.actionset.bindAction("home", self.outputui.moveScrollbarToTop)
        self.actionset.bindAction("end", self.outputui.moveScrollbarToBottom)

        self.actionset.bindAction("toggle2ndinput", self.toggleSecondaryInput)

        connect_action = self.actionset.bindAction(
            "connect", self.world.connectToWorld
        )

        disconnect_action = self.actionset.bindAction(
            "disconnect", self.world.confirmDisconnectFromWorld
        )

        connect_action.setEnabled(False)
        disconnect_action.setEnabled(False)

        startlog_action = self.actionset.bindAction(
            "startlog", self.world.startLogging
        )

        stoplog_action = self.actionset.bindAction(
            "stoplog", self.world.stopLogging
        )

        startlog_action.setEnabled(True)
        stoplog_action.setEnabled(False)

        world.disconnected.connect(connect_action.setEnabled)
        world.disconnected.connect(disconnect_action.setDisabled)

        world.nowLogging.connect(startlog_action.setDisabled)
        world.nowLogging.connect(stoplog_action.setEnabled)

        self.toolbar.addAction(connect_action)
        self.toolbar.addAction(disconnect_action)

        self.toolbar.addSeparator()

        self.toolbar.addAction(startlog_action)
        self.toolbar.addAction(stoplog_action)

        self.toolbar.addSeparator()

        self.world.setUI(self)

        app = QApplication.instance()
        assert app is not None
        for line in app.core.motd:  # type: ignore
            self.world.info(line)

    def updateToolBarIcons(self, size):

        if not size:
            size = QApplication.style().pixelMetric(
                QStyle.PixelMetric.PM_ToolBarIconSize
            )

        new_size = QSize(size, size)
        self.toolbar.setIconSize(new_size)

    def toggleSecondaryInput(self):

        if self.secondaryinputui.isHidden():
            self.secondaryinputui.show()
            self.secondaryinputui.setFocus()

        else:
            self.secondaryinputui.hide()
            self.inputui.setFocus()

    def onTabChanged(self, is_now_visible):

        if is_now_visible:

            # Ensure the currently visible world has focus.
            self.setFocus()

    def windowAlert(self):

        # TODO: Pass app instance cleanly somehow.
        app = QApplication.instance()
        if not self.world or app is None:
            return

        if self.world.settings._ui._window._alert:
            app.alert(self.window())  # type: ignore

        self.requestAttention.emit()

    def saveSplitterPosition(self):

        self.world.state._ui._splitter._sizes = self.sizes()

    def close(self) -> bool:

        if self.world.isConnected():

            if not confirmDialog(
                "Confirm close",
                "You are still connected to this world. "
                "Disconnect and close this tab?",
                "Close tab",
                self,
            ):
                return False

        # The following line is outside the above if statement because the
        # world, even if not connected, might be *trying* to connect.

        self.world.disconnectFromWorld()

        # Then, schedule the closing of the world.
        QTimer.singleShot(0, self.doClose)

        return True

    def doClose(self):

        self.world.stopLogging()

        self.setParent(None)  # type: ignore - actually a valid call.

        # Manual cleanup. We want to avoid leaking references all over the
        # place.
        # TODO: Add some kind of test to check whether this is still needed.
        del self.world.worldui
        del self.world.logger
        del self.output_manager.world
        del self.actionset.parent
        del self.inputui.world
        del self.inputui.history
        del self.inputui
        del self.secondaryinputui.world
        del self.secondaryinputui.history
        del self.secondaryinputui
        del self.outputui

        for f in self.world.socketpipeline.pipeline.filters:
            del f.context
            del f.sink

        del self.world.socketpipeline.pipeline
        del self.world.socketpipeline
        del self.output_manager

        del self.world
        self.deleteLater()

    def setFocusProxy(self, *args):

        # WORKAROUND: PyQt doesn't seem to properly declare the slot for this
        # method, so we must override it. :/
        # TODO: Reevalute this workaround in the present (2022).

        super().setFocusProxy(*args)
