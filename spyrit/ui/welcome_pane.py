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
Implements the UI that is first displayed when opening a new window.
"""


from typing import Callable, ParamSpec

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QAbstractButton,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
)

from spyrit import constants
from spyrit.session.instance import SessionInstance
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.about_pane import AboutPane
from spyrit.ui.bars import HBar, VBar
from spyrit.ui.base_pane import Pane
from spyrit.ui.settings.settings_pane import SettingsPane
from spyrit.ui.sizer import Sizer
from spyrit.ui.spyrit_logo import SpyritLogo
from spyrit.ui.world_creation_pane import WorldCreationPane
from spyrit.ui.world_pane import WorldPane


_P = ParamSpec("_P")


class CallWithArgs:
    """
    Creates a callable that applies the given arguments to the given callable.

    Args:
        callable: The callable to invoke with the given arguments.

        args, kwargs: The arguments to pass to the callable when invoked.
    """

    def __init__(
        self, callable: Callable[_P, None], *args: _P.args, **kwargs: _P.kwargs
    ) -> None:
        self._callable = callable
        self._args = args
        self._kwargs = kwargs

    def __call__(self) -> None:
        """
        Invokes the given callable with the given arguments.
        """

        self._callable(*self._args, **self._kwargs)


def _set_button_size_properties(button: QAbstractButton) -> None:
    """
    Configures a Qt button with the desired size properties for the welcome
    pane.

    Args:
        button: A Qt button.
    """

    unit = Sizer(button).unitSize()
    button.setSizePolicy(
        QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
    )
    button.setStyleSheet(
        f"QAbstractButton {{ padding: {unit/1.5} {unit} {unit/1.5} {unit} }}"
    )


class MenuButton(QToolButton):
    """
    A button that displays a menu when clicked.

    If the menu is empty, the button will be disabled.

    Args:
        label: The button's label.

        menu: The menu to display when the button is clicked.
    """

    def __init__(self, label: str, menu: QMenu) -> None:
        super().__init__()
        _set_button_size_properties(self)
        self.setText(label)
        self.setCheckable(True)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.setMenu(menu)
        if menu.isEmpty():
            self.setEnabled(False)


class Button(QPushButton):
    """
    A QPushButton with a standardized size.

    Args:
        label: The text to use for the button.
    """

    def __init__(self, label: str) -> None:
        super().__init__(label)
        _set_button_size_properties(self)


class WelcomePane(Pane):
    """
    Implements the UI entry point from where the users can start using the
    software.

    Args:
        settings: The global application settings object. It will be used to
            create or look up a world-specific settings subset when the user
            creates or picks a world to play.

        state: The global application state object. Ditto.

        instance: The session model object for the tab that contains this pane.
    """

    # This pane is never garbage collected.

    pane_is_persistent = True

    # This signal fires when the user requests to quit the application.

    quitRequested: Signal = Signal()

    _settings: SpyritSettings
    _state: SpyritState
    _instance: SessionInstance

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

        unit = Sizer(self).unitSize()

        # Create the main layout.

        self.setLayout(pane_layout := QHBoxLayout())

        # Create and set up the menu layout.

        pane_layout.addLayout(menu_layout := QVBoxLayout())
        menu_layout.setContentsMargins(0, 0, 0, 0)

        # Logo!

        menu_layout.addWidget(SpyritLogo())

        menu_layout.addWidget(HBar())

        menu_layout.addSpacing(unit)

        # New world button!

        menu_layout.addWidget(new_world_button := Button("New world..."))
        new_world_button.clicked.connect(self._openWorldCreationPane)

        menu_layout.addSpacing(unit)

        # "Connect to..." button.

        menu = self._buildWorldMenu()
        menu_layout.addWidget(MenuButton("Connect to...", menu))

        menu_layout.addSpacing(unit)

        # Important application buttons (settings and about)!

        menu_layout.addWidget(HBar())
        menu_layout.addSpacing(unit)

        menu_layout.addLayout(button_layout := QHBoxLayout())

        button_layout.addWidget(settings_button := Button("Settings"))
        settings_button.clicked.connect(self._showSettings)

        button_layout.addWidget(
            about_button := Button(f"About {constants.APPLICATION_NAME}...")
        )
        about_button.clicked.connect(self._showAbout)

        menu_layout.addWidget(quit_button := Button("Quit"))
        quit_button.clicked.connect(self.quitRequested)

        # Fill out the remaining space.

        menu_layout.addStretch()

        # And finalize the main layout.

        pane_layout.addWidget(VBar())
        pane_layout.addStretch()

    def onActive(self) -> None:
        """
        Overrides the parent handler to set the instance title when this pane
        becomes visible.
        """

        self._instance.setTitle(f"Welcome to {constants.APPLICATION_NAME}!")

    def _buildWorldMenu(self) -> QMenu:
        """
        Constructs a menu with the currently configured worlds.

        Each entry in the menu comes with an action that opens the corresponding
        world when selected.

        Returns:
            A QMenu listing the currently configured worlds.
        """

        worlds_menu = QMenu(self)

        for world in sorted(
            self._settings.sections(),
            key=lambda world: world.title().lower(),
        ):
            action = worlds_menu.addAction(world.title())  # type: ignore
            action.triggered.connect(CallWithArgs(self._openWorld, world))

        return worlds_menu

    @Slot()
    def _openWorldCreationPane(self) -> None:
        """
        Creates a world creation pane and switches to it.
        """

        pane = WorldCreationPane(self._settings, self._state, self._instance)
        self.addPaneRight(pane)

    @Slot()
    def _openWorld(self, world: SpyritSettings) -> None:
        """
        Creates a game pane for the given world and switches to it.

        Args:
            world: The settings that represent a game world.
        """

        state = self._state.getStateSectionForSettingsSection(world)

        self.addPaneRight(WorldPane(world, state, self._instance))

    @Slot()
    def _showSettings(self) -> None:
        """
        Shows the settings pane.
        """

        self.addPaneRight(SettingsPane(self._settings))

    @Slot()
    def _showAbout(self) -> None:
        """
        Shows the application about pane.
        """

        self.addPaneRight(AboutPane())
