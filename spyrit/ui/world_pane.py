# Copyright (c) 2007-2024 Pascal Varet <p.varet@gmail.com>
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

import threading

from PySide6.QtCore import QObject, QSize, Qt, Signal, Slot
from PySide6.QtGui import QAction, QIcon, QTextCursor
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QToolBar, QWidget

from spyrit.network.autologin import Autologin
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
from spyrit.settings.default_patterns import get_default_patterns
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.autocompleter import Autocompleter, CompletionModel, Tokenizer
from spyrit.ui.layout_widgets import HBox, Splitter, VBox
from spyrit.ui.action_with_key_setting import ActionWithKeySetting
from spyrit.ui.base_pane import Pane
from spyrit.ui.input_box import InputBox, Postman
from spyrit.ui.input_history import Historian
from spyrit.ui.output_view import OutputView
from spyrit.ui.scribe import Scribe
from spyrit.ui.scroller import Scroller
from spyrit.ui.search_bar import SearchBar
from spyrit.ui.settings.settings_pane import SettingsPane
from spyrit.ui.sizer import Sizer


class ConnectionToggleAction(QAction):
    """
    A QAction whose visual checked status reflects whether its attached
    Connection is connected, and whose toggling can request for the connection
    to be started or stopped.

    Args:
        parent: This object's parent. Used for lifetime management purposes.

        connection: The Connection whose status is reflected by, and can be
            changed through, this action.

        on_icon: The icon to use in UIs that show this action when the
            connection is on.

        off_icon: The icon to use in UIs that show this action when the
            connection is off.
    """

    _CONNECTED_TOOLTIP = "Disconnect"
    _DISCONNECTED_TOOLTIP = "Connect"

    # This signal fires when a user interaction with this action requests that a
    # connection be initiated.

    connectRequested: Signal = Signal()

    # This signal fires when a user interaction with this action requests that a
    # connection be terminated.

    disconnectRequested: Signal = Signal()

    _connection: Connection
    _prevent_connection_changes: threading.Lock
    _on_icon: QIcon
    _off_icon: QIcon

    def __init__(
        self,
        parent: QObject,
        connection: Connection,
        on_icon: QIcon,
        off_icon: QIcon,
    ) -> None:
        super().__init__(parent)

        self._connection = connection
        self._prevent_connection_changes = threading.Lock()
        self._on_icon = on_icon
        self._off_icon = off_icon

        self.setCheckable(True)

        self.toggled.connect(self._toggleConnection)
        self._connection.statusChanged.connect(self._updateVisualCheckedness)

        self._updateVisualCheckedness()

    @Slot(bool)
    def _toggleConnection(self, connect: bool) -> None:
        """
        Signals that the user requested a change to the connection state, that
        being either to initiate the connection or to terminate it.

        Args:
            connect: Whether the user interaction is requesting a connection. If
                not, it's a disconnection.
        """

        if self._prevent_connection_changes.locked():
            return

        (self.connectRequested if connect else self.disconnectRequested).emit()

        # Re-apply the appearance of the action based on the connection status.
        # By default, Qt updated the appearance whenever the action is toggled;
        # but in our case, we allow the user to cancel the outcome of the
        # action, e.g. if they are in fact not ready to disconnect, and in this
        # case the appearance is not automatically changed back.

        self._updateVisualCheckedness()

    @Slot()
    def _updateVisualCheckedness(self) -> None:
        """
        Updates the visual checked status of the action based on the state of
        the connection.

        The action is checked if and only if the connection is active, whether
        that means fully established or in the process of coming up.
        """

        is_connecting = self._connection.isConnecting()

        self.setToolTip(
            self._DISCONNECTED_TOOLTIP
            if not is_connecting
            else self._CONNECTED_TOOLTIP
        )
        self.setIcon(self._off_icon if not is_connecting else self._on_icon)

        if is_connecting != self.isChecked():
            with self._prevent_connection_changes:
                # Note the use of the lock. Calling setChecked() unfortunately
                # triggers the same signal handler as user actions. There is no
                # way to only update the visual aspect of the action. So we use
                # a lock to prevent the handler from taking actions when we call
                # setChecked() here.

                self.setChecked(is_connecting)


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

    # This signal fires when a user action requests for the pane to be closed in
    # order to return to the main menu.

    returnToMenuRequested: Signal = Signal()

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

        self._setupGameWidgets(view, search_bar, inputbox, extra_inputbox)

        # Set up the network connection.

        connection = Connection(settings.net, parent=self)

        # Inform the instance about this connection so it can keep track of its
        # status.

        instance.setConnection(connection)

        # Set up keepalives for the connection.

        Keepalive(connection, settings.net.keepalive)

        # Set up the tool bar icons and related shortcuts.

        self._setUpToolbarActions(
            instance, toolbar, search_bar, extra_inputbox, connection
        )

        # Set up the inputs' behavior and plug them into the connection.

        self._setUpInput(connection, inputbox)
        self._setUpInput(connection, extra_inputbox)

        # Set up autocompletion for the input widgets.

        completion_model = CompletionModel()
        Autocompleter(
            inputbox, completion_model, self._settings.shortcuts.autocomplete
        )
        Autocompleter(
            extra_inputbox,
            completion_model,
            self._settings.shortcuts.autocomplete,
        )

        # Plug the connection into the data parsing logic.

        processor = self._createGameDataProcessor(connection)

        # Create the game view update helper.

        scribe = Scribe(
            QTextCursor(view.document()),
            settings=settings.ui.output,
            parent=self,
        )

        # Plug the parsing logic into the game view update logic.

        processor.fragmentsReady.connect(scribe.inscribe)

        # Ingest world-specific vocabulary into the completion model.

        tokenizer = Tokenizer(parent=completion_model)
        tokenizer.tokenFound.connect(completion_model.addExtraWord)
        processor.fragmentsReady.connect(tokenizer.processFragments)

        # Update the instance's state from the processed fragment stream.

        processor.fragmentsReady.connect(instance.updateStateFromFragments)

        # Set up automatic login if the world's settings are bound to a specific
        # character.

        if settings.isCharacter():
            autologin = Autologin(settings.login, connection.send, self)
            processor.fragmentsReady.connect(autologin.awaitLoginPrecondition)

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
        toolbar.setIconSize(QSize(unit + margin, unit + margin))
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

        # Update the instance title with this world's name and, if relevant, the
        # current character's name.

        title = self._settings.title()
        if self._settings.isCharacter() and (
            name := self._settings.login.name.get()
        ):
            title = name + "\n" + title
        self._instance.setTitle(title)

    def _setupGameWidgets(
        self,
        view: OutputView,
        search_bar: SearchBar,
        inputbox: InputBox,
        extra_inputbox: InputBox,
    ) -> None:
        """
        Sets up the behavior of the game UI widgets and the shortcuts for user
        interactions.

        Args:
            view: The output view that displays contents from the game.

            search_bar: The text search UI.

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

    def _setUpToolbarActions(
        self,
        instance: SessionInstance,
        toolbar: QToolBar,
        search_bar: SearchBar,
        extra_inputbox: InputBox,
        connection: Connection,
    ) -> None:
        """
        Sets up the user interactions that have icons in the toolbar.

        Args:
            instance: the session instance on which to trigger user-requested
                actions.

            toolbar: The toolbar in which to add the interaction icons.

            search_bar: The SearchBar for which to add a toggle button.

            extra_inputbox: The InputBox to make visible/hidden with a toggle
                button.

            connection: The connection object used for this game, so it can be
               controlled from a toggle button.
        """

        shortcuts = self._settings.shortcuts

        # Set up the connection toggle.

        toolbar.addAction(
            connection_toggle := ConnectionToggleAction(
                self,
                connection,
                on_icon=QIcon(Icon.SWITCH_ON),
                off_icon=QIcon(Icon.SWITCH_OFF),
            )
        )
        connection_toggle.connectRequested.connect(instance.doConnect)
        connection_toggle.disconnectRequested.connect(instance.maybeDisconnect)

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

        # Add the extra input toggle.

        self.addAction(
            extra_input_toggle := ActionWithKeySetting(
                self,
                "Toggle second input",
                self._settings.shortcuts.toggle_second_input,
                extra_inputbox.toggleVisibility,
                checkable=True,
                icon=QIcon(Icon.INPUT_FIELD_SVG),
            )
        )
        extra_inputbox.toggleVisibility(False)

        # And add the button to the toolbar.

        toolbar.addAction(extra_input_toggle)

        # Set up the settings button.

        self.addAction(
            settings := ActionWithKeySetting(
                self,
                "Settings",
                shortcuts.open_settings,
                self._showSettings,
                icon=QIcon(Icon.SETTINGS_SVG),
            )
        )
        toolbar.addAction(settings)

        # Add space so the close button is isolated at the bottom.

        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        toolbar.addWidget(spacer)

        # Set up the close button.

        self.addAction(
            close := ActionWithKeySetting(
                self,
                "Close and return to menu",
                shortcuts.return_to_menu,
                self.returnToMenuRequested.emit,
                icon=QIcon(Icon.CLOSE_SVG),
            )
        )
        toolbar.addAction(close)

        self.returnToMenuRequested.connect(instance.maybeClosePane)

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
            UserPatternProcessor(
                self._settings.patterns, get_default_patterns()
            ),
            parent=self,
        )

        bind_processor_to_connection(processor, connection)

        return processor

    def doClose(self) -> None:
        """
        Closes this pane and returns to the menu.
        """

        self.pane_is_persistent = False
        self.slideLeft()

    @Slot()
    def _showSettings(self) -> None:
        """
        Opens the settings pane for this world.
        """

        self.addPaneRight(SettingsPane(self._settings))
