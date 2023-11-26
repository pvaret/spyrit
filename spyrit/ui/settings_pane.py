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
Implements an application settings pane.
"""

from typing import Sequence, TypeVar

from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QTabWidget,
    QSizePolicy,
    QWidget,
)

from sunset import List, Settings

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.bars import HBar
from spyrit.ui.base_dialog_pane import BaseDialogPane
from spyrit.ui.layout_widgets import HBox, VBox
from spyrit.ui.sizer import Sizer


_SettingsT = TypeVar("_SettingsT", bound=Settings)


def _root(settings: _SettingsT) -> _SettingsT:
    """
    Returns the topmost parent of the given settings object.

    Args:
        The settings object whose topmost parent should be returned.

    Returns:
        The topmost settings in the hierarchy.
    """

    if (parent := settings.parent()) is None:
        return settings
    return _root(parent)


def _is_root(settings: Settings) -> bool:
    """
    Returns whether the settings object is the topmost one.

    Args:
        settings: The settings object to check.

    Returns:
        Whether the given settings is the topmost one.
    """

    return settings.parent() is None


def _name_for_settings(settings: SpyritSettings) -> str:
    """
    Creates a human-friendly name for the given settings.

    Args:
        settings: The settings instance for which to create a human-friendly
            name.

    Returns:
        A human-friendly name that identifies the given settings.
    """

    return "All worlds" if _is_root(settings) else settings.name.get()


class SettingsComboBox(QComboBox):
    """
    This class is a combo box specialization that lets the user pick which world
    to update settings for.

    Args:
        settings_choices: A sequence of settings objects for the user to pick
            from.

        current_settings: The settings object that is currently selected.
    """

    # This signal fires when the user chooses a setting from the combo box.

    settingsSelected: Signal = Signal(SpyritSettings)

    def __init__(
        self,
        settings_choices: Sequence[SpyritSettings],
        current_settings: SpyritSettings,
    ) -> None:
        super().__init__()

        for i, settings in enumerate(settings_choices):
            label = _name_for_settings(settings)
            if not _is_root(settings):
                label = f"  {label}"
            self.addItem(label, settings)
            if settings is current_settings:
                self.setCurrentIndex(i)

        self.currentIndexChanged.connect(self._emitSettingsSelected)

    @Slot()
    def _emitSettingsSelected(self) -> None:
        """
        Emits the settingsSelected signal with the currently selected settings
        object as its parameter.
        """

        data = self.currentData()
        if isinstance(data, SpyritSettings):
            self.settingsSelected.emit(data)


class SettingsPane(BaseDialogPane):
    """
    An UI to configure all aspects of the application.

    Args:
        settings: The settings object to configure. This can be the
            application-global one, or one of the world-specific ones.
    """

    _settings: SpyritSettings
    _settings_ui: QWidget

    def __init__(
        self,
        settings: SpyritSettings,
    ) -> None:
        super().__init__()

        margin = Sizer(self).marginSize()

        # Close the pane when the user clicks the "Ok" button.

        self.okClicked.connect(self.slideLeft)

        # Computes the list of all world settings, in alphabetical order,
        # starting with the toplevel, "All worlds" settings object.

        toplevel = _root(settings)

        all_settings = [toplevel]
        all_settings += sorted(
            toplevel.sections(),
            key=lambda settings: settings.name.get().lower(),
        )

        # Create the main pane for the settings UI. It will contain a combo box
        # to select which world whose settings to edit (can be the toplevel
        # all-worlds settings), and a settings pane for the selected world.

        pane_widget = VBox()
        pane_widget.layout().setSpacing(margin)
        pane_widget.addWidget(menu_box := HBox())

        menu_box.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        menu_box.addWidget(QLabel("Settings for:"))
        menu_box.layout().addSpacing(margin)
        menu_box.addWidget(
            settings_menu := SettingsComboBox(all_settings, settings)
        )
        menu_box.layout().addStretch()

        settings_menu.settingsSelected.connect(self._updateUIForSettings)

        pane_widget.layout().addWidget(HBar())

        self._settings_ui = self._uiForSettings(settings)
        pane_widget.layout().addWidget(self._settings_ui)

        self.setWidget(pane_widget)

    @Slot(SpyritSettings)
    def _updateUIForSettings(self, settings: SpyritSettings) -> None:
        """
        Constructs the UI to let the user edit the contents of the given
        settings object. Sets this UI as the current one.

        Args:
            settings: The settings object for which to build and display a UI.
        """

        ui = self._uiForSettings(settings)
        self.widget().layout().replaceWidget(self._settings_ui, ui)
        self._settings_ui.setParent(None)
        self._settings_ui = ui

    def _uiForSettings(self, settings: SpyritSettings) -> QWidget:
        """
        Constructs and returns a UI for the given settings object.

        Args:
            settings: The settings object for which to build a UI.

        Returns:
            A widget set up to let a user edit the contents of the given
            settings object.
        """

        ui = QTabWidget()

        if not _is_root(settings):
            ui.addTab(
                self._serverSettingsUI(settings.net),
                f"Server: {settings.name.get()}",
            )
            ui.addTab(
                self._triggersSettingsUI(settings.patterns),
                f"Triggers: {settings.name.get()}",
            )

        ui.addTab(self._appearanceSettingsUI(_root(settings).ui), "Appearance")
        ui.addTab(
            self._shortcutsSettingsUI(_root(settings).shortcuts),
            "Shortcuts",
        )

        return ui

    def _serverSettingsUI(self, settings: SpyritSettings.Network) -> QWidget:
        label = QLabel("Not implemented!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _appearanceSettingsUI(self, settings: SpyritSettings.UI) -> QWidget:
        label = QLabel("Not implemented!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _triggersSettingsUI(
        self, settings: List[SpyritSettings.Pattern]
    ) -> QWidget:
        label = QLabel("Not implemented!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _shortcutsSettingsUI(
        self, settings: SpyritSettings.KeyShortcuts
    ) -> QWidget:
        label = QLabel("Not implemented!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label
