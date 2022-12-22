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

from sunset import Key, Bundle, Settings

from spyrit.settings import key_shortcut


def default_key(combination: str) -> Key[key_shortcut.KeyShortcut]:

    return Key(default=key_shortcut.from_default(combination))


class SpyritSettings(Settings):
    class KeyShortcuts(Bundle):

        new_tab = default_key("Ctrl+T")
        close_current_tab = default_key("Ctrl+W")
        switch_to_previous_tab = default_key("Ctrl+PgUp")
        switch_to_next_tab = default_key("Ctrl+PgDown")
        move_current_tab_left = default_key("Ctrl+Shift+PgUp")
        move_current_tab_right = default_key("Ctrl+Shift+PgDown")

    shortcuts = KeyShortcuts()
