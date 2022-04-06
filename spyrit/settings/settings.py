# Copyright (c) 2007-2022 Pascal Varet <p.varet@gmail.com>
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
Declaration of the Spyrit settings.
"""

import sunset

from . import key_shortcut


class Settings(sunset.Settings):
    class KeyShortcuts(sunset.Section):

        new_tab: sunset.Setting[key_shortcut.KeyShortcut] = sunset.NewSetting(
            key_shortcut.KeyShortcut.default("Ctrl+T")
        )

        close_current_tab: sunset.Setting[
            key_shortcut.KeyShortcut
        ] = sunset.NewSetting(key_shortcut.KeyShortcut.default("Ctrl+W"))

        switch_to_previous_tab: sunset.Setting[
            key_shortcut.KeyShortcut
        ] = sunset.NewSetting(key_shortcut.KeyShortcut.default("Ctrl+PgUp"))

        switch_to_next_tab: sunset.Setting[
            key_shortcut.KeyShortcut
        ] = sunset.NewSetting(key_shortcut.KeyShortcut.default("Ctrl+PgDown"))

        move_current_tab_left: sunset.Setting[
            key_shortcut.KeyShortcut
        ] = sunset.NewSetting(
            key_shortcut.KeyShortcut.default("Ctrl+Shift+PgUp")
        )

        move_current_tab_right: sunset.Setting[
            key_shortcut.KeyShortcut
        ] = sunset.NewSetting(
            key_shortcut.KeyShortcut.default("Ctrl+Shift+PgDown")
        )

    shortcuts: KeyShortcuts = sunset.NewSection(KeyShortcuts)
