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
from spyrit.network.connection import Connection, Status
from spyrit.network.processors import (
    ANSIProcessor,
    BaseProcessor,
    ConnectionProcessor,
    PacketSplitterProcessor,
    ChainProcessor,
    FlowControlProcessor,
    UnicodeProcessor,
    UserPatternProcessor,
)
from spyrit.resources.resources import Icon
from spyrit.settings.default_patterns import get_default_patterns
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.autocompleter import Autocompleter, CompletionModel, Tokenizer
from spyrit.ui.dialogs import askUserIfReadyToDisconnect
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

    # This signal is sent when a user interaction with this action requests that
    # a connection be initiated.

    connectRequested: Signal = Signal()

    # This signal is sent when a user interaction with this action requests that
    # a connection be terminated.

    disconnectRequested: Signal = Signal()

    _status: Status = Status.DISCONNECTED
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

        self._prevent_connection_changes = threading.Lock()
        self._on_icon = on_icon
        self._off_icon = off_icon

        self.setCheckable(True)

        self.toggled.connect(self._toggleConnection)
        connection.statusChanged.connect(self._updateVisualCheckedness)

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

        if connect:
            self.connectRequested.emit()
        else:
            self.disconnectRequested.emit()

        # Re-apply the appearance of the action based on the connection status.
        # By default, Qt updated the appearance whenever the action is toggled;
        # but in our case, we allow the user to cancel the outcome of the
        # action, e.g. if they are in fact not ready to disconnect, and in this
        # case the appearance is not automatically changed back.

        self._updateVisualCheckedness()

    @Slot(Status)
    def _updateVisualCheckedness(self, status: Status | None = None) -> None:
        """
        Updates the visual checked status of the action based on the state of
        the connection.

        The action is checked if and only if the connection is active, whether
        that means fully established or in the process of coming up.
        """

        if status is not None:
            self._status = status

        is_disconnected = self._status in (Status.DISCONNECTED, Status.ERROR)

        self.setToolTip(
            self._DISCONNECTED_TOOLTIP
            if is_disconnected
            else self._CONNECTED_TOOLTIP
        )
        self.setIcon(self._off_icon if is_disconnected else self._on_icon)

        connecting_or_connected = not is_disconnected
        if connecting_or_connected != self.isChecked():
            with self._prevent_connection_changes:
                # Note the use of the lock. Calling setChecked() unfortunately
                # triggers the same signal handler as user actions. There is no
                # way to only update the visual aspect of the action. So we use
                # a lock to prevent the handler from taking actions when we call
                # setChecked() here.

                self.setChecked(connecting_or_connected)


class WorldPane(Pane):
    """
    The main game pane.

    Here is where we put together the UI to display game output and let the user
    enter their input. This is where many of the components that make up the
    behavior of the app are put together.

    Args:
        settings: The specific settings object for this game.

        state: The specific state object for this game's UI.

        connection: The object that implements the network interface with a game
            server. This pane acquires ownership of the connection object.

        view, inputbox, extra_inputbox, search_bar, toolbar: The widgets to be
            used to assemble this UI.
    """

    # This signal is sent when this pane is ready to close.

    closeRequested: Signal = Signal()

    # This signal is sent when a user action requests for the settings pane to
    # the shown. The argument is this world's settings object.

    settingsUIRequested: Signal = Signal(SpyritSettings)

    _settings: SpyritSettings
    _connection: Connection

    # This pane is never garbage collected.

    pane_is_persistent = True

    def __init__(
        self,
        settings: SpyritSettings,
        state: SpyritState.UI,
        connection: Connection,
        view: OutputView,
        inputbox: InputBox,
        extra_inputbox: InputBox,
        search_bar: SearchBar,
        toolbar: QToolBar,
    ) -> None:
        super().__init__()

        self._settings = settings
        self._connection = connection

        # Assemble the game UI layout.

        self._layoutWidgets(
            state, view, search_bar, toolbar, inputbox, extra_inputbox
        )

        # Set up the interconnections between the widgets.

        self._setupGameWidgets(
            view, search_bar, inputbox, extra_inputbox, settings.shortcuts
        )

        # Set up the tool bar icons and related shortcuts.

        self._setUpToolbarActions(
            toolbar, search_bar, extra_inputbox, connection, settings.shortcuts
        )

    def _layoutWidgets(
        self,
        state: SpyritState.UI,
        view: OutputView,
        search_bar: SearchBar,
        toolbar: QToolBar,
        inputbox: InputBox,
        extra_inputbox: InputBox,
    ) -> None:
        """
        Lays out the widgets of the game UI.

        Args:
            state: The state holding UI properties to be bound to the widgets.

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
                state.input_splitter_sizes, inputbox, extra_inputbox
            )
        )
        input_splitter.setContentsMargins(0, 0, margin, margin)

        self.layout().addWidget(
            Splitter(state.output_splitter_sizes, outputs, inputs)
        )

    def _setupGameWidgets(
        self,
        view: OutputView,
        search_bar: SearchBar,
        inputbox: InputBox,
        extra_inputbox: InputBox,
        shortcuts: SpyritSettings.KeyShortcuts,
    ) -> None:
        """
        Sets up the behavior of the game UI widgets and the shortcuts for user
        interactions.

        Args:
            view: The output view that displays contents from the game.

            search_bar: The text search UI.

            inputbox: The main user text entry box.

            extra_input: A secondary text entry box.

            shortcuts: The key shortcuts to use for UI actions.
        """

        # Install up the user-friendly scrollbar helper.

        scroller = Scroller(view.verticalScrollBar())

        view.requestScrollToPosition.connect(scroller.smoothScrollToPosition)

        # Set up view-related shortcuts. Those need to be on the WorldPane
        # itself because the view never has focus.

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
        toolbar: QToolBar,
        search_bar: SearchBar,
        extra_inputbox: InputBox,
        connection: Connection,
        shortcuts: SpyritSettings.KeyShortcuts,
    ) -> None:
        """
        Sets up the user interactions that have icons in the toolbar.

        Args:
            toolbar: The toolbar in which to add the interaction icons.

            search_bar: The SearchBar for which to add a toggle button.

            extra_inputbox: The InputBox to make visible/hidden with a toggle
                button.

            connection: The connection object used for this game, so it can be
               controlled from a toggle button.

            shortcuts: The key shortcuts to use for UI actions.
        """

        # Set up the connection toggle.

        toolbar.addAction(
            connection_toggle := ConnectionToggleAction(
                self,
                connection,
                on_icon=QIcon(Icon.SWITCH_ON),
                off_icon=QIcon(Icon.SWITCH_OFF),
            )
        )
        connection_toggle.connectRequested.connect(connection.start)
        connection_toggle.disconnectRequested.connect(self._maybeDisconnect)

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
                shortcuts.toggle_second_input,
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
                self.closeRequested.emit,
                icon=QIcon(Icon.CLOSE_SVG),
            )
        )
        toolbar.addAction(close)

    @Slot()
    def _showSettings(self) -> None:
        """
        Opens the settings pane for this world.
        """

        self.settingsUIRequested.emit(self._settings)

    @Slot()
    def _maybeDisconnect(self) -> None:
        """
        Closes the connection, seeking the user's confirmation if the connection
        is currently established.
        """

        if not self._connection.isConnected() or askUserIfReadyToDisconnect(
            self
        ):
            self._connection.stop()


def make_processor(
    connection: Connection, settings: SpyritSettings
) -> BaseProcessor:
    """
    Constructs and returns the processor to parse the network output from the
    game.

    Args:
        connection: The connection whose output to feed into the processor.

        settings: The settings object for game world associated with the
            given connection.

    Returns:
        A processor, configured to parse game output, and bound to the given
        connection.
    """

    return ChainProcessor(
        ConnectionProcessor(connection),
        PacketSplitterProcessor(),
        ANSIProcessor(settings.ui.output.ansi_bold_effect),
        UnicodeProcessor(settings.net.encoding),
        FlowControlProcessor(),
        UserPatternProcessor(settings.patterns, get_default_patterns()),
        parent=connection,
    )


def bind_input_to_connection(
    shortcuts: SpyritSettings.KeyShortcuts,
    state: SpyritState.History,
    connection: Connection,
    inputbox: InputBox,
) -> None:
    """
    Configures the given input box against the given connection. I.e. makes
    it so the input box can be used to send its input in the connection.

    Also installs the text history helper on the input box.

    Args:
        shortcuts: The key shortcuts to use for UI actions.

        state: The state history object for the game world.

        connection: The network connection to which to send user input.

        inputbox: The text box from which to read the input to send on the
            network.
    """

    # Plug the input into the network connection.

    postman = Postman(inputbox, connection)

    # Set up history recording for the input box. Note that the
    # history state is shared between the boxes.

    historian = Historian(inputbox, state, parent=inputbox)
    postman.inputSent.connect(historian.recordNewInput)

    # Set up the key shortcuts for the history search.

    inputbox.addAction(
        ActionWithKeySetting(
            inputbox,
            "History next",
            shortcuts.history_next,
            historian.historyNext,
        )
    )
    inputbox.addAction(
        ActionWithKeySetting(
            inputbox,
            "History previous",
            shortcuts.history_previous,
            historian.historyPrevious,
        )
    )


def make_world_pane(
    settings: SpyritSettings, state: SpyritState, connection: Connection
) -> WorldPane:
    """
    Build the game world pane for the given world settings and state, using the
    given connection.
    """

    processor = make_processor(connection, settings)

    # Set up automatic login if the world's settings are bound to a specific
    # character.

    if settings.isCharacter():
        autologin = Autologin(settings.login, connection)
        processor.fragmentsReady.connect(autologin.awaitLoginPrecondition)

    # Create widgets to be assembled in the world pane.

    view = OutputView(settings.ui.output)
    inputbox = InputBox()
    extra_inputbox = InputBox()
    search_bar = SearchBar(view.document())
    toolbar = QToolBar()

    # Create the game view update helper.

    scribe = Scribe(
        QTextCursor(view.document()),
        settings=settings.ui.output,
        parent=view,
    )

    # Plug the parsing logic into the game view update logic.

    processor.fragmentsReady.connect(scribe.inscribe)

    # Connect the inputs to the connection object.

    bind_input_to_connection(
        settings.shortcuts, state.history, connection, inputbox
    )
    bind_input_to_connection(
        settings.shortcuts, state.history, connection, extra_inputbox
    )

    # Set up autocompletion for the input widgets.

    completion_model = CompletionModel()
    Autocompleter(inputbox, completion_model, settings.shortcuts.autocomplete)
    Autocompleter(
        extra_inputbox,
        completion_model,
        settings.shortcuts.autocomplete,
    )

    # Ingest world-specific vocabulary into the completion model.

    tokenizer = Tokenizer(parent=completion_model)
    tokenizer.tokenFound.connect(completion_model.addExtraWord)
    processor.fragmentsReady.connect(tokenizer.processFragments)

    # And create the world pane.

    return WorldPane(
        settings,
        state.ui,
        connection,
        view,
        inputbox,
        extra_inputbox,
        search_bar,
        toolbar,
    )
