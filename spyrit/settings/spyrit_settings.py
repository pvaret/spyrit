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
Declaration of the Spyrit settings.
"""


from sunset import Key, Bunch, SerializableEnum, Settings

from spyrit.settings import key_shortcut


class Encoding(SerializableEnum):
    ASCII = "ASCII"
    LATIN1 = "Latin 1"
    UTF8 = "UTF-8"


def _new_shortcut(combination: str) -> Key[key_shortcut.KeyShortcut]:
    return Key(default=key_shortcut.from_default(combination))


class SpyritSettings(Settings):
    class KeyShortcuts(Bunch):
        new_tab = _new_shortcut("Ctrl+T")
        new_window = _new_shortcut("Ctrl+Shift+N")
        close_current_tab = _new_shortcut("Ctrl+W")
        switch_to_previous_tab = _new_shortcut("Ctrl+PgUp")
        switch_to_next_tab = _new_shortcut("Ctrl+PgDown")
        move_current_tab_left = _new_shortcut("Ctrl+Shift+PgUp")
        move_current_tab_right = _new_shortcut("Ctrl+Shift+PgDown")

    class Network(Bunch):
        server = Key(default="")
        port = Key(default=0)
        encoding = Key(default=Encoding.ASCII)

    class UI(Bunch):
        theme = Key(default="")

    shortcuts = KeyShortcuts()
    net = Network()
    ui = UI()

    name = Key(default="")
