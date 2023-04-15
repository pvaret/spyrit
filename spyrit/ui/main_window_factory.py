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
Class that specializes a generic tabbed UI container into the actual application
window.
"""


from PySide6.QtWidgets import QWidget

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.tabbed_ui_container import TabbedUiContainer
from spyrit.ui.shortcut_with_key_setting import ShortcutWithKeySetting


class MainWindow(TabbedUiContainer):
    """
    An implementation of the top-level tabbed UI container that's aware of
    things like Spyrit settings.
    """

    def __init__(
        self,
        settings: SpyritSettings,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Set up keyboard shortcuts.

        key_settings = settings.shortcuts
        for shortcut, slot in (
            (key_settings.new_tab, self.newTabRequested),
            (key_settings.new_window, self.newWindowRequested),
            (key_settings.close_current_tab, self.maybeCloseCurrentTab),
            (key_settings.switch_to_next_tab, self.switchToNextTab),
            (key_settings.switch_to_previous_tab, self.switchToPreviousTab),
            (key_settings.move_current_tab_right, self.moveCurrentTabRight),
            (key_settings.move_current_tab_left, self.moveCurrentTabLeft),
        ):
            ShortcutWithKeySetting(parent=self, key=shortcut, slot=slot)


class SpyritMainWindowFactory:
    """
    Provides a factory for our main application window that can be used by the
    generic tabbed UI factory.
    """

    _settings: SpyritSettings

    def __init__(self, settings: SpyritSettings) -> None:
        self._settings = settings

    def __call__(self) -> MainWindow:
        return MainWindow(self._settings)
