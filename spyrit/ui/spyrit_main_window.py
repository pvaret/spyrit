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


class SpyritMainWindow(TabbedUiContainer):
    """
    An implementation of the top-level tabbed UI container that's aware of
    things like Spyrit settings.
    """

    _settings: SpyritSettings

    def __init__(
        self,
        main_settings: SpyritSettings,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._settings = main_settings

        # Set up keyboard shortcuts.

        ShortcutWithKeySetting(
            self, self._settings.shortcuts.new_tab, self.newTabRequested
        )
        ShortcutWithKeySetting(
            self, self._settings.shortcuts.new_window, self.newWindowRequested
        )
        ShortcutWithKeySetting(
            self,
            self._settings.shortcuts.close_current_tab,
            self.maybeCloseCurrentTab,
        )
        ShortcutWithKeySetting(
            self,
            self._settings.shortcuts.switch_to_next_tab,
            self.switchToNextTab,
        )
        ShortcutWithKeySetting(
            self,
            self._settings.shortcuts.switch_to_previous_tab,
            self.switchToPreviousTab,
        )
        ShortcutWithKeySetting(
            self,
            self._settings.shortcuts.move_current_tab_right,
            self.moveCurrentTabRight,
        )
        ShortcutWithKeySetting(
            self,
            self._settings.shortcuts.move_current_tab_left,
            self.moveCurrentTabLeft,
        )


class SpyritMainWindowFactory:
    """
    Provides a factory for our main application window that can be used by the
    generic tabbed UI factory.
    """

    _settings: SpyritSettings

    def __init__(self, settings: SpyritSettings) -> None:
        self._settings = settings

    def __call__(self) -> SpyritMainWindow:
        return SpyritMainWindow(self._settings)
