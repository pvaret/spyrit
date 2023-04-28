# Copyright (c) 2007-2023 Pascal Varet <p.varet@gmail.com>
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
Implements a UI to play in a world.
"""


from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtWidgets import QSplitter, QHBoxLayout

from spyrit import constants
from spyrit.network.connection import Connection
from spyrit.network.processors import (
    ChainProcessor,
    FlowControlProcessor,
    UnicodeProcessor,
    bind_processor_to_connection,
)
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.base_pane import Pane
from spyrit.ui.input_box import InputBox
from spyrit.ui.main_ui_remote_protocol import UIRemoteProtocol
from spyrit.ui.output_view import OutputView
from spyrit.ui.scribe import Scribe
from spyrit.ui.shortcut_with_key_setting import ShortcutWithKeySetting


class Splitter(QSplitter):
    _state: SpyritState.UI

    def __init__(self, state: SpyritState.UI) -> None:
        super().__init__()

        self._state = state
        self.setSizes(state.splitter_sizes.get())
        self.splitterMoved.connect(self._saveSplitterSizes)

    @Slot()
    def _saveSplitterSizes(self) -> None:
        self._state.splitter_sizes.set(self.sizes())


class WorldPane(Pane):
    _settings: SpyritSettings
    _state: SpyritState
    _ui: UIRemoteProtocol
    _splitter: QSplitter

    def __init__(
        self, settings: SpyritSettings, state: SpyritState, ui: UIRemoteProtocol
    ) -> None:
        super().__init__()

        self._settings = settings
        self._state = state
        self._ui = ui

        self.active.connect(self._setTitles)

        # WIP test garbage follows.
        # TODO: finish.

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(splitter := Splitter(state.ui))

        splitter.addWidget(view := OutputView(settings.ui.output))
        splitter.addWidget(second_inputbox := InputBox(settings))
        splitter.addWidget(inputbox := InputBox(settings))
        splitter.setChildrenCollapsible(False)
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.setSizes(state.ui.splitter_sizes.get())

        self.setFocusProxy(inputbox)
        view.setFocusProxy(inputbox)
        QTimer.singleShot(0, self.setFocus)  # type: ignore

        second_inputbox.toggleVisibility(state.ui.second_input_visible.get())
        state.ui.second_input_visible.onValueChangeCall(
            second_inputbox.toggleVisibility
        )
        second_inputbox.expelFocus.connect(inputbox.setFocus)

        ShortcutWithKeySetting(
            self,
            settings.shortcuts.toggle_second_input,
            state.ui.second_input_visible.toggle,
        )

        cursor = view.textCursor()

        connection = Connection(settings.net, parent=self)

        processor = ChainProcessor(
            UnicodeProcessor(settings.net.encoding),
            FlowControlProcessor(),
            parent=self,
        )
        bind_processor_to_connection(processor, connection)

        scribe = Scribe(cursor, settings=settings.ui.output, parent=self)
        processor.fragmentsReady.connect(scribe.inscribe)

        connection.start()

        def on_text_entered() -> None:
            text = inputbox.toPlainText()
            if connection.send(text + "\r\n"):
                inputbox.clear()

        def on_secondary_text_entered() -> None:
            text = second_inputbox.toPlainText()
            if connection.send(text + "\r\n"):
                second_inputbox.clear()

        inputbox.returnPressed.connect(on_text_entered)
        second_inputbox.returnPressed.connect(on_secondary_text_entered)

    @Slot()
    def _setTitles(self) -> None:
        world_name = self._settings.name.get() or "Unnamed world"
        self._ui.setTabTitle(world_name)
        self._ui.setWindowTitle(f"{constants.APPLICATION_NAME} - {world_name}")
