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
    ANSIProcessor,
    ChainProcessor,
    FlowControlProcessor,
    LineBatchingProcessor,
    UnicodeProcessor,
    bind_processor_to_connection,
)
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.base_pane import Pane
from spyrit.ui.input_box import InputBox, Postman
from spyrit.ui.input_history import Historian
from spyrit.ui.main_ui_remote_protocol import UIRemoteProtocol
from spyrit.ui.output_view import OutputView
from spyrit.ui.scribe import Scribe
from spyrit.ui.scroller import Scroller
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

    def __init__(
        self, settings: SpyritSettings, state: SpyritState, ui: UIRemoteProtocol
    ) -> None:
        super().__init__()

        self._settings = settings
        self._state = state
        self._ui = ui

        self.active.connect(self._setTitles)

        # Set up the splitter widget that hosts the game UI.

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(splitter := Splitter(state.ui))
        splitter.setChildrenCollapsible(False)
        splitter.setOrientation(Qt.Orientation.Vertical)

        # Add and set up the widgets of the game UI.

        splitter.addWidget(view := OutputView(settings.ui.output))
        splitter.addWidget(second_inputbox := InputBox())
        splitter.addWidget(inputbox := InputBox())

        splitter.setSizes(state.ui.splitter_sizes.get())

        # Install up the user-friendly scrollbar helper.

        Scroller(view.verticalScrollBar())

        # Set up the focus logic for the game UI. TL;DR: both the pane and the
        # view forward to the main input, and also the focus is set when the
        # pane is first displayed.

        self.setFocusProxy(inputbox)
        view.setFocusProxy(inputbox)
        self.setTabOrder(inputbox, second_inputbox)

        # The second input transfers its focus to the main input when the second
        # input no longer wants it.

        second_inputbox.expelFocus.connect(inputbox.setFocus)

        # Plug in the second input toggling logic.

        second_inputbox.toggleVisibility(state.ui.second_input_visible.get())
        state.ui.second_input_visible.onValueChangeCall(
            second_inputbox.toggleVisibility
        )

        ShortcutWithKeySetting(
            self,
            settings.shortcuts.toggle_second_input,
            state.ui.second_input_visible.toggle,
        )

        # Set up the network connection.

        connection = Connection(settings.net, parent=self)

        # Set up the inputs and plug them into the connection.

        self._setUpInput(connection, inputbox)
        self._setUpInput(connection, second_inputbox)

        # Plug the connection into the data parsing logic

        processor = ChainProcessor(
            ANSIProcessor(settings.ui.output.ansi_bold_effect),
            UnicodeProcessor(settings.net.encoding),
            FlowControlProcessor(),
            line_processor := LineBatchingProcessor(),
            parent=self,
        )

        bind_processor_to_connection(processor, connection)

        # Refresh the display each time an entire line is processed.

        line_processor.lineProcessed.connect(view.repaint)

        # Plug the parsing logic into the game view update logic.

        scribe = Scribe(
            view.textCursor(), settings=settings.ui.output, parent=self
        )
        processor.fragmentsReady.connect(scribe.inscribe)

        # And start the connection.

        connection.start()

        # Make sure this widget gets the focus after getting displayed.

        QTimer.singleShot(0, self.setFocus)  # type: ignore

    def _setUpInput(self, connection: Connection, inputbox: InputBox) -> None:
        # Plug the input into the network connection.

        postman = Postman(inputbox, connection)

        # Set up history recording for the input box. Note that the
        # history state is shared between the boxes.

        historian = Historian(inputbox, self._state.history, parent=inputbox)
        postman.inputSent.connect(historian.recordNewInput)

        # Set up the key shortcuts for the history search.

        ShortcutWithKeySetting(
            inputbox,
            self._settings.shortcuts.history_next,
            historian.historyNext,
        )
        ShortcutWithKeySetting(
            inputbox,
            self._settings.shortcuts.history_previous,
            historian.historyPrevious,
        )

    @Slot()
    def _setTitles(self) -> None:
        world_name = self._settings.name.get() or "Unnamed world"
        self._ui.setTabTitle(world_name)
        self._ui.setWindowTitle(f"{constants.APPLICATION_NAME} - {world_name}")
