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


from typing import Any, cast

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QAbstractButton,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from sunset import Key

from spyrit import constants
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.signals import CallWithArgs
from spyrit.ui.bars import HBar, VBar
from spyrit.ui.base_pane import Pane
from spyrit.ui.sizer import Sizer
from spyrit.ui.spyrit_logo import SpyritLogo




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


def _is_ancestor(possible_ancestor: Key[Any], key: Key[Any]) -> bool:
    """
    Determines whether the given key transitively inherits from the given
    possible ancestor.

    Args:
        possible_ancestor: The key that may be the ancestor.

        key: The key that may inherit directly or indirectly from the ancestor.

    Returns:
        True if and only if the key is the same object as the ancestor, or one
        of the key's transitive parents is.
    """

    if key is possible_ancestor:
        return True

    if (parent := key.parent()) is None:
        return False

    return _is_ancestor(possible_ancestor, parent)


class WorldsMenu(QMenu):
    """
    A QMenu that contains a list of configured worlds.

    Automatically refreshes itself when worlds are added or modified.

    Args:
        parent: The widget on which to attach the menu, for lifetime management
            purposes.

        settings: The root settings object on which to look up the world list.
    """

    # This signal is sent when a world is selected in the menu.

    worldSelected: Signal = Signal(SpyritSettings)

    # This signal is sent when the item count of the menu changed.

    itemCountChanged: Signal = Signal(int)

    _settings: SpyritSettings
    _count: int = 0

    def __init__(self, parent: QWidget, settings: SpyritSettings) -> None:
        super().__init__(parent=parent)
        self._settings = settings
        self._settings.onUpdateCall(self._refreshMenu)
        self._refreshMenu()

    def _refreshMenu(self, entity: Any = None) -> None:
        """
        Refreshes the menu if the entity that triggers the update means that
        either the world list or a world name changed.

        Args:
            entity: The entity whose update triggered the call to this function.
        """

        if (
            entity is None
            or isinstance(entity, SpyritSettings)
            or (
                isinstance(entity, Key)
                and _is_ancestor(self._settings.name, cast(Key[Any], entity))
            )
        ):
            self.clear()
            self._count = 0

            for world in self._settings.worlds():
                action = self.addAction(world.title())  # type: ignore
                action.triggered.connect(
                    CallWithArgs(self.worldSelected.emit, world)
                )
                self._count += 1

                for character in world.characters():
                    name = character.login.name.get()
                    if name:
                        action = self.addAction(f"    … as {name}")  # type: ignore
                        action.triggered.connect(
                            CallWithArgs(self.worldSelected.emit, character)
                        )
                        self._count += 1

            self.itemCountChanged.emit(self._count)

    def count(self) -> int:
        """
        Returns how many items there currently are in the menu. May be 0.

        Returns:
            An item count.
        """

        return self._count


class MenuButton(QToolButton):
    """
    A button that displays a menu when clicked.

    If the menu is empty, the button will be disabled.

    Args:
        label: The button's label.

        menu: The menu to display when the button is clicked.
    """

    def __init__(self, label: str, menu: WorldsMenu) -> None:
        super().__init__()
        _set_button_size_properties(self)
        self.setText(label)
        self.setCheckable(True)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.setMenu(menu)
        menu.itemCountChanged.connect(self.setEnableStatus)
        self.setEnableStatus(menu.count())

    @Slot(int)
    def setEnableStatus(self, item_count: int) -> None:
        """
        Enables or disables this widget based on the item count.

        Args:
            item_count: How many items are in the menu attached to this widget.
        """

        self.setEnabled(item_count > 0)


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
    """

    # This pane is never garbage collected.

    pane_is_persistent = True

    # This signal is sent when a user action asks for the world creation UI to
    # be opened.

    openWorldCreationUIRequested: Signal = Signal()

    # This signal is sent when a user action asks for a game world to be opened.
    # The argument is the *world's* settings objects.

    openWorldRequested: Signal = Signal(SpyritSettings)

    # This signal is sent when a user action asks to open the settings panel.

    openSettingsUIRequested: Signal = Signal(SpyritSettings)

    # This signal is sent when a user action asks to open the About... pane.

    openAboutRequested: Signal = Signal()

    # This signal is sent when the user requests to quit the application.

    quitRequested: Signal = Signal()

    def __init__(self, settings: SpyritSettings) -> None:
        super().__init__()

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
        new_world_button.clicked.connect(self.openWorldCreationUIRequested)

        menu_layout.addSpacing(unit)

        # "Connect to..." button.

        menu_layout.addWidget(
            MenuButton("Connect to...", menu := WorldsMenu(self, settings))
        )
        menu.worldSelected.connect(self.openWorldRequested)

        menu_layout.addSpacing(unit)

        # Important application buttons (settings and about)!

        menu_layout.addWidget(HBar())
        menu_layout.addSpacing(unit)

        menu_layout.addLayout(button_layout := QHBoxLayout())

        button_layout.addWidget(settings_button := Button("Settings"))
        settings_button.clicked.connect(
            CallWithArgs(self.openSettingsUIRequested.emit, settings)
        )

        button_layout.addWidget(
            about_button := Button(f"About {constants.APPLICATION_NAME}...")
        )
        about_button.clicked.connect(self.openAboutRequested)

        menu_layout.addWidget(quit_button := Button("Quit"))
        quit_button.clicked.connect(self.quitRequested)

        # Fill out the remaining space.

        menu_layout.addStretch()

        # And finalize the main layout.

        pane_layout.addWidget(VBar())
        pane_layout.addStretch()
