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
Implements a UI to play in a world.
"""


from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QSplitter, QHBoxLayout

from spyrit.network.connection import Connection
from spyrit.network.keepalive import Keepalive
from spyrit.network.processors import (
    ANSIProcessor,
    BaseProcessor,
    PacketSplitterProcessor,
    ChainProcessor,
    FlowControlProcessor,
    UnicodeProcessor,
    UserPatternProcessor,
    bind_processor_to_connection,
)
from spyrit.session.session import SessionInstance
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.action_with_key_setting import ActionWithKeySetting
from spyrit.ui.base_pane import Pane
from spyrit.ui.input_box import InputBox, Postman
from spyrit.ui.input_history import Historian
from spyrit.ui.output_view import OutputView
from spyrit.ui.scribe import Scribe
from spyrit.ui.scroller import Scroller


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
    _instance: SessionInstance

    # This pane is never garbage collected.

    pane_is_persistent = True

    def __init__(
        self,
        settings: SpyritSettings,
        state: SpyritState,
        instance: SessionInstance,
    ) -> None:
        super().__init__()

        self._settings = settings
        self._state = state
        self._instance = instance

        # Set up the splitter widget that hosts the game UI.

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(splitter := Splitter(state.ui))
        splitter.setChildrenCollapsible(False)
        splitter.setOrientation(Qt.Orientation.Vertical)

        # Create and set up the game UI's widgets.

        view, inputbox, second_inputbox = self._addGameWidgets(splitter)

        # Set up the network connection.

        connection = Connection(settings.net, parent=self)

        # Set up keepalives for the connection.

        Keepalive(connection, settings.net.keepalive)

        # Set up the inputs' behavior and plug them into the connection.

        self._setUpInput(connection, inputbox)
        self._setUpInput(connection, second_inputbox)

        # Plug the connection into the data parsing logic.

        processor = self._createGameDataProcessor(connection)

        # Create the game view update helper.

        scribe = Scribe(
            view.textCursor(), settings=settings.ui.output, parent=self
        )

        # Plug the parsing logic into the game view update logic.

        processor.fragmentsReady.connect(scribe.inscribe)

        # Update the instance's state from the processed fragment stream.

        processor.fragmentsReady.connect(instance.updateStateFromFragments)

        # And start the connection.

        connection.start()

    def onActive(self) -> None:
        # Update the instance title with this world's name.

        self._instance.setTitle(self._settings.name.get())

    def _addGameWidgets(
        self, splitter: QSplitter
    ) -> tuple[OutputView, InputBox, InputBox]:
        # Add and set up the widgets of the game UI.

        splitter.addWidget(view := OutputView(self._settings.ui.output))
        splitter.addWidget(second_inputbox := InputBox())
        splitter.addWidget(inputbox := InputBox())

        splitter.setSizes(self._state.ui.splitter_sizes.get())

        # Install up the user-friendly scrollbar helper.

        scroller = Scroller(view.verticalScrollBar())

        # Set up view-related shortcuts. Those need to be on the WorldPane
        # itself because the view never has focus.

        shortcuts = self._settings.shortcuts
        for text, shortcut, slot in (
            ("Page up", shortcuts.page_up, scroller.scrollOnePageUp),
            ("Page down", shortcuts.page_down, scroller.scrollOnePageDown),
            ("Scroll up", shortcuts.line_up, scroller.scrollOneLineUp),
            ("Scroll down", shortcuts.line_down, scroller.scrollOneLineDown),
            ("Scroll to top", shortcuts.scroll_to_top, scroller.scrollToTop),
            (
                "Scroll to bottom",
                shortcuts.scroll_to_bottom,
                scroller.scrollToBottom,
            ),
        ):
            self.addAction(
                ActionWithKeySetting(
                    parent=self, text=text, key=shortcut, slot=slot
                )
            )

        # Set up the focus logic for the game UI. TL;DR: both the pane and the
        # view forward to the main input, and the second input comes after the
        # main input in the tab order.

        self.setFocusProxy(inputbox)
        view.setFocusProxy(inputbox)
        self.setTabOrder(inputbox, second_inputbox)

        # The second input transfers its focus to the main input when the second
        # input no longer wants it.

        second_inputbox.expelFocus.connect(inputbox.setFocus)

        # Plug in the second input toggling logic.

        input_visible_key = self._state.ui.second_input_visible
        second_inputbox.toggleVisibility(input_visible_key.get())
        input_visible_key.onValueChangeCall(second_inputbox.toggleVisibility)

        self.addAction(
            second_input_toggle := ActionWithKeySetting(
                self,
                "Toggle second input",
                self._settings.shortcuts.toggle_second_input,
                input_visible_key.toggle,
            )
        )
        second_input_toggle.setCheckable(True)

        return view, inputbox, second_inputbox

    def _setUpInput(self, connection: Connection, inputbox: InputBox) -> None:
        # Plug the input into the network connection.

        postman = Postman(inputbox, connection)

        # Set up history recording for the input box. Note that the
        # history state is shared between the boxes.

        historian = Historian(inputbox, self._state.history, parent=inputbox)
        postman.inputSent.connect(historian.recordNewInput)

        # Set up the key shortcuts for the history search.

        inputbox.addAction(
            ActionWithKeySetting(
                inputbox,
                "History next",
                self._settings.shortcuts.history_next,
                historian.historyNext,
            )
        )
        inputbox.addAction(
            ActionWithKeySetting(
                inputbox,
                "History previous",
                self._settings.shortcuts.history_previous,
                historian.historyPrevious,
            )
        )

    def _createGameDataProcessor(self, connection: Connection) -> BaseProcessor:
        processor = ChainProcessor(
            PacketSplitterProcessor(),
            ANSIProcessor(self._settings.ui.output.ansi_bold_effect),
            UnicodeProcessor(self._settings.net.encoding),
            FlowControlProcessor(),
            UserPatternProcessor(self._settings.patterns),
            parent=self,
        )

        bind_processor_to_connection(processor, connection)

        return processor
