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
from sunset import Bunch, Key, Settings

from spyrit import constants
from spyrit.settings import serializers
from spyrit.settings.key_shortcut import shortcut_from_default, Shortcut
from spyrit.ui.colors import ANSIColor, ANSIColorCodes, Color
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


def _shortcut_key(combination: str) -> Key[Shortcut]:
    return Key(default=shortcut_from_default(combination))


def _font_key(font_family: list[str], font_size: int) -> Key[QFont]:
    return Key(
        default=QFont(font_family, font_size), serializer=serializers.Font()
    )


def _color_key(ansi_color: ANSIColorCodes) -> Key[Color]:
    return Key(
        default=ANSIColor(ansi_color),
        serializer=serializers.ColorSerializer(),
    )


def _format_key(
    color: ANSIColorCodes | None, italic: bool = False, bold: bool = False
) -> Key[FormatUpdate]:
    format_ = FormatUpdate()
    if color is not None:
        format_.setForeground(ANSIColor(color))
    if italic:
        format_.setItalic(True)
    if bold:
        format_.setBold(True)
    return Key(default=format_, serializer=serializers.FormatSerializer())


class SpyritSettings(Settings):
    class KeyShortcuts(Bunch):
        """
        Records the keyboard shortcuts for common UI actions.
        """

        new_tab: Key[Shortcut] = _shortcut_key("Ctrl+T")
        new_window: Key[Shortcut] = _shortcut_key("Ctrl+Shift+N")
        close_current_tab: Key[Shortcut] = _shortcut_key("Ctrl+W")
        switch_to_previous_tab: Key[Shortcut] = _shortcut_key("Ctrl+PgUp")
        switch_to_next_tab: Key[Shortcut] = _shortcut_key("Ctrl+PgDown")
        move_current_tab_left: Key[Shortcut] = _shortcut_key("Ctrl+Shift+PgUp")
        move_current_tab_right: Key[Shortcut] = _shortcut_key(
            "Ctrl+Shift+PgDown"
        )
        toggle_second_input: Key[Shortcut] = _shortcut_key("Ctrl+M")
        history_previous: Key[Shortcut] = _shortcut_key("Ctrl+Up")
        history_next: Key[Shortcut] = _shortcut_key("Ctrl+Down")

    class Network(Bunch):
        """
        Records the necessary information to connect to a game.
        """

        # Server address and port for the game. Server can be an IPv4, IPv6 or a
        # resolvable DNS address.
        server: Key[str] = Key(default="")
        port: Key[int] = Key(default=0)

        # Stores a game's expected text encoding. It most cases it will be
        # ASCII, but some games get fancy with extended characters.
        encoding: Key[Encoding] = Key(default=Encoding.ASCII)

    class UI(Bunch):
        """
        Records the visual properties of the UI.
        """

        class Output(Bunch):
            """
            Records the visual properties of the main game view.
            """

            # The font use to render game text. Should be a monotype font.
            font: Key[QFont] = _font_key(
                constants.DEFAULT_FONT_FAMILY, constants.DEFAULT_FONT_POINT_SIZE
            )

            # The background color of the window where game text is rendered.
            background_color: Key[Color] = _color_key(ANSIColorCodes.Black)

            # The color used to render game text when no other color is applied
            # through e.g. ANSI codes or user-defined formatting.
            default_text_color: Key[Color] = _color_key(
                ANSIColorCodes.LightGray
            )

            # Rendering properties of the text used for status messages.
            status_text_format: Key[FormatUpdate] = _format_key(
                color=ANSIColorCodes.DarkGray,
                italic=True,
                bold=True,
            )

            # How to interpret the 'bold' ANSI code. There is no clear standard
            # between actually using a heavier font weight and a lighter font
            # color, so by default we do both.
            ansi_bold_effect: Key[ANSIBoldEffect] = Key(
                default=ANSIBoldEffect.BOTH
            )

        output: Output = Output()

        # The name of the Qt style to use for the UI. If none, use the default
        # for the platform.
        style: Key[str] = Key(default="")

    shortcuts: KeyShortcuts = KeyShortcuts()
    net: Network = Network()
    ui: UI = UI()

    # The display name of the game.
    name: Key[str] = Key(default="")
