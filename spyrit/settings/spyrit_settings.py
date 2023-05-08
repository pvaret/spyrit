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
Declaration of the Spyrit settings.
"""


import enum

from PySide6.QtGui import QFont
from sunset import Key, Bunch, Settings

from spyrit import constants
from spyrit.settings import key_shortcut, serializers
from spyrit.ui.colors import ANSIColor, AnsiColorCodes, Color
from spyrit.ui.format import FormatUpdate


class Encoding(enum.StrEnum):
    ASCII = "ASCII"
    LATIN1 = "Latin 1"
    UTF8 = "UTF-8"
    CP437 = "CP437"


class ANSIBoldEffect(enum.Flag):
    BRIGHT = enum.auto()
    BOLD = enum.auto()
    BOTH = BRIGHT | BOLD


def _new_shortcut(combination: str) -> Key[key_shortcut.KeyShortcut]:
    return Key(default=key_shortcut.from_default(combination))


def _default_font() -> QFont:
    return QFont(
        constants.DEFAULT_FONT_FAMILY, constants.DEFAULT_FONT_POINT_SIZE
    )


def _color_key(ansi_color: AnsiColorCodes) -> Key[Color]:
    return Key(
        default=ANSIColor(ansi_color),
        serializer=serializers.ColorSerializer(),
    )


class SpyritSettings(Settings):
    class KeyShortcuts(Bunch):
        new_tab = _new_shortcut("Ctrl+T")
        new_window = _new_shortcut("Ctrl+Shift+N")
        close_current_tab = _new_shortcut("Ctrl+W")
        switch_to_previous_tab = _new_shortcut("Ctrl+PgUp")
        switch_to_next_tab = _new_shortcut("Ctrl+PgDown")
        move_current_tab_left = _new_shortcut("Ctrl+Shift+PgUp")
        move_current_tab_right = _new_shortcut("Ctrl+Shift+PgDown")
        toggle_second_input = _new_shortcut("Ctrl+M")
        history_previous = _new_shortcut("Ctrl+Up")
        history_next = _new_shortcut("Ctrl+Down")

    class Network(Bunch):
        server = Key(default="")
        port = Key(default=0)
        encoding = Key(default=Encoding.ASCII)

    class UI(Bunch):
        class Output(Bunch):
            font = Key(default=_default_font(), serializer=serializers.Font())
            background_color = _color_key(AnsiColorCodes.Black)
            default_text_color = _color_key(AnsiColorCodes.LightGray)
            status_text_format = Key(
                default=FormatUpdate(
                    foreground=ANSIColor(AnsiColorCodes.DarkGray), italic=True
                ),
                serializer=serializers.FormatSerializer(),
            )
            ansi_bold_effect = Key(default=ANSIBoldEffect.BOTH)

        output = Output()

        style = Key(default="")

    shortcuts = KeyShortcuts()
    net = Network()
    ui = UI()

    name = Key(default="")
