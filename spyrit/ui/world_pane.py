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

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLayout,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from sunset import Key

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
from spyrit.resources.resources import Icon
from spyrit.session.instance import SessionInstance
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.layout_widgets import HBox, Splitter, VBox
from spyrit.ui.action_with_key_setting import ActionWithKeySetting
from spyrit.ui.base_pane import Pane
from spyrit.ui.input_box import InputBox, Postman
from spyrit.ui.input_history import Historian
from spyrit.ui.output_view import OutputView
from spyrit.ui.scribe import Scribe
from spyrit.ui.scroller import Scroller
from spyrit.ui.search_bar import SearchBar
from spyrit.ui.sizer import Sizer


class WorldPane(Pane):
    """
    The main game pane.

    Here is where we put together the UI to display game output and let the user
    enter their input. This is where many of the components that make up the
    behavior of the app are put together.

    Args:
        settings: The specific settings object for this game.

        state: The specific state object for this game.

        instance: The instance object to bind to this game.
    """

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

        # Create the game UI's widgets.

        view = OutputView(self._settings.ui.output)
        search_bar = SearchBar(view.document())
        toolbar = QToolBar()
        inputbox = InputBox()
        extra_inputbox = InputBox()

        # Assemble the game UI layout.

        self._layoutWidgets(view, search_bar, toolbar, inputbox, extra_inputbox)

        # Set up the interconnections between the widgets.

        self._setupGameWidgets(
            view, search_bar, toolbar, inputbox, extra_inputbox
        )

        # Set up the network connection.

        connection = Connection(settings.net, parent=self)

        # Set up keepalives for the connection.

        Keepalive(connection, settings.net.keepalive)

        # Set up the inputs' behavior and plug them into the connection.

        self._setUpInput(connection, inputbox)
        self._setUpInput(connection, extra_inputbox)

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

    def _layoutWidgets(
        self,
        view: OutputView,
        search_bar: SearchBar,
        toolbar: QToolBar,
        inputbox: InputBox,
        extra_inputbox: InputBox,
    ) -> None:
        """
        Lays out the widgets of the game UI.

        Args:
            view: The output view that displays contents from the game.

            search_bar: The text search UI.

            toolbar: The bar that contains the buttons for common actions.

            inputbox: The main user text entry box.

            extra_input: A secondary text entry box.
        """

        sizer = Sizer(self)
        unit = sizer.unitSize()
        margin = sizer.marginSize()

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        outputs = VBox()
        outputs.addWidget(view)
        outputs.addWidget(search_bar)

        inputs = HBox()
        toolbar.setOrientation(Qt.Orientation.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        toolbar.setIconSize(QSize(unit, unit))
        inputs.addWidget(toolbar)

        inputs.addWidget(
            input_splitter := Splitter(
                self._state.ui.input_splitter_sizes, inputbox, extra_inputbox
            )
        )
        input_splitter.setContentsMargins(0, 0, margin, margin)

        self.layout().addWidget(
            Splitter(self._state.ui.output_splitter_sizes, outputs, inputs)
        )

    def onActive(self) -> None:
        """
        Overrides the parent method to set the instance's title when this pane
        becomes active.
        """

        # Update the instance title with this world's name.

        self._instance.setTitle(self._settings.name.get())

    def _setupGameWidgets(
        self,
        view: OutputView,
        search_bar: SearchBar,
        toolbar: QToolBar,
        inputbox: InputBox,
        extra_inputbox: InputBox,
    ) -> None:
        """
        Sets up the behavior of the game UI widgets and the shortcuts for user
        interactions.

        Args:
            view: The output view that displays contents from the game.

            search_bar: The text search UI.

            toolbar: The icon toolbar for this UI.

            inputbox: The main user text entry box.

            extra_input: A secondary text entry box.
        """

        # Install up the user-friendly scrollbar helper.

        scroller = Scroller(view.verticalScrollBar())

        view.requestScrollToPosition.connect(scroller.smoothScrollToPosition)

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

        # Set up the search bar toggle.

        self.addAction(
            find := ActionWithKeySetting(
                parent=self,
                text="Find",
                key=shortcuts.find,
                slot=search_bar.toggle,
                checkable=True,
                icon=QIcon(Icon.SEARCH_SVG),
            )
        )

        # Let the find button status reflect the visibility status of the search
        # bar.

        search_bar.visibilityChanged.connect(find.setChecked)

        # Add the find button to the toolbar.

        toolbar.addAction(find)

        # Set up the focus logic for the game UI. TL;DR: the pane just forwards
        # its focus to the main input.

        self.setFocusProxy(inputbox)

        # Plug search results into the output view.

        search_bar.searchResultReady.connect(view.displaySearchResults)

        # The second input transfers its focus to the main input when the second
        # input no longer wants it.

        extra_inputbox.expelFocus.connect(inputbox.setFocus)

        # And so does the search bar.

        search_bar.expelFocus.connect(inputbox.setFocus)

        # Search bar is hidden by default.

        search_bar.hide()

        # Plug in the second input toggling logic.

        input_visible_key = self._state.ui.extra_input_visible
        extra_inputbox.toggleVisibility(input_visible_key.get())
        input_visible_key.onValueChangeCall(extra_inputbox.toggleVisibility)

        self.addAction(
            extra_input_toggle := ActionWithKeySetting(
                self,
                "Toggle second input",
                self._settings.shortcuts.toggle_second_input,
                input_visible_key.toggle,
                checkable=True,
                icon=QIcon(Icon.INPUT_FIELD_SVG),
            )
        )

        # Set the action's initial status from the stored visibility value.

        extra_input_toggle.setChecked(input_visible_key.get())

        # And add the button to the toolbar.

        toolbar.addAction(extra_input_toggle)

    def _setUpInput(self, connection: Connection, inputbox: InputBox) -> None:
        """
        Configures the given input box against the given connection. I.e. makes
        it so the input box can be used to send its input in the connection.

        Also installs the text history helper on the input box.

        Args:
            connection: The network connection to which to send user input.

            inputbox: The text box from which to read the input to send on the
                network.
        """

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
        """
        Constructs and returns the processor to parse the network output from
        the game.

        Args:
            connection: The connection whose output to feed into the processor.

        Returns:
            A processor, configured to parse game output, and bound to the given
            connection.
        """

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
