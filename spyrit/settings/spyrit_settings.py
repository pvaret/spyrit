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
Declaration of the Spyrit settings.
"""


import enum

from PySide6.QtGui import QFont
from sunset import Bunch, Key, List, Settings

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


class KeepaliveMessage(enum.Enum):
    CARRIAGE_RETURN = b"\n"


class ANSIBoldEffect(enum.Flag):
    BRIGHT = enum.auto()
    BOLD = enum.auto()
    BOTH = BRIGHT | BOLD


class PatternScope(enum.Enum):
    # A pattern with this scope will match if and only it matches the entire
    # line.
    ENTIRE_LINE = enum.auto()

    # Every subset of a line of text that matches a pattern with this scope will
    # be considered an independent match.
    ANYWHERE_IN_LINE = enum.auto()


class PatternType(enum.Enum):
    # An ANYTHING pattern matches any characters, as *few* as possible,
    # including none at all.
    ANYTHING = enum.auto()

    # An EXACT_MATCH pattern matches the pattern string exactly, after
    # normalisation.
    EXACT_MATCH = enum.auto()

    # An ANY_OF pattern matches any of the characters in the pattern string in
    # any order, as many as possible.
    ANY_OF = enum.auto()

    # An ANY_NOT_IN pattern matches any characters not in the pattern string, as
    # many as possible.
    ANY_NOT_IN = enum.auto()

    # A REGEX pattern uses the pattern string as a regex, matching as many
    # characters as possible.
    REGEX = enum.auto()


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
        value_type=Color,
    )


def _format_key(
    color: ANSIColorCodes | None = None,
    italic: bool = False,
    bold: bool = False,
) -> Key[FormatUpdate]:
    format_ = FormatUpdate()
    if color is not None:
        format_.setForeground(ANSIColor(color))
    if italic:
        format_.setItalic(True)
    if bold:
        format_.setBold(True)
    return Key(default=format_, serializer=serializers.FormatSerializer())


def _valid_port_number(port: int) -> bool:
    """
    Checks whether a given number represents a valid TCP port.
    """

    return constants.MIN_TCP_PORT <= port <= constants.MAX_TCP_PORT


class SpyritSettings(Settings):
    class KeyShortcuts(Bunch):
        """
        Records the keyboard shortcuts for common UI actions.
        """

        new_window: Key[Shortcut] = _shortcut_key("Ctrl+Shift+N")
        close_window: Key[Shortcut] = _shortcut_key("Alt+F4")
        new_tab: Key[Shortcut] = _shortcut_key("Ctrl+T")
        close_current_tab: Key[Shortcut] = _shortcut_key("Ctrl+W")
        switch_to_previous_tab: Key[Shortcut] = _shortcut_key("Ctrl+PgUp")
        switch_to_next_tab: Key[Shortcut] = _shortcut_key("Ctrl+PgDown")
        move_current_tab_left: Key[Shortcut] = _shortcut_key("Ctrl+Shift+PgUp")
        move_current_tab_right: Key[Shortcut] = _shortcut_key(
            "Ctrl+Shift+PgDown"
        )
        page_up: Key[Shortcut] = _shortcut_key("PgUp")
        page_down: Key[Shortcut] = _shortcut_key("PgDown")
        line_up: Key[Shortcut] = _shortcut_key("Ctrl+Shift+Up")
        line_down: Key[Shortcut] = _shortcut_key("Ctrl+Shift+Down")
        scroll_to_top: Key[Shortcut] = _shortcut_key("Ctrl+Home")
        scroll_to_bottom: Key[Shortcut] = _shortcut_key("Ctrl+End")
        toggle_second_input: Key[Shortcut] = _shortcut_key("Ctrl+M")
        history_previous: Key[Shortcut] = _shortcut_key("Ctrl+Up")
        history_next: Key[Shortcut] = _shortcut_key("Ctrl+Down")
        find: Key[Shortcut] = _shortcut_key("Ctrl+F")
        open_settings: Key[Shortcut] = _shortcut_key("Ctrl+Shift+S")
        return_to_menu: Key[Shortcut] = _shortcut_key("Ctrl+Shift+Q")
        quit: Key[Shortcut] = _shortcut_key("Ctrl+Q")

    class Network(Bunch):
        """
        Records the necessary information to connect to a game.
        """

        class Keepalive(Bunch):
            """
            Records parameters for the network keep-alive function.
            """

            enabled: Key[bool] = Key(default=False)
            period_secs: Key[int] = Key(default=5 * 60)
            message: Key[KeepaliveMessage] = Key(
                default=KeepaliveMessage.CARRIAGE_RETURN
            )

        # Server address and port for the game. Server can be an IPv4, IPv6 or a
        # resolvable DNS address.
        server: Key[str] = Key(default=constants.EXAMPLE_SERVER)
        port: Key[int] = Key(
            default=constants.EXAMPLE_PORT, validator=_valid_port_number
        )

        # Stores a game's expected text encoding. It most cases it will be
        # ASCII, but some games get fancy with extended characters.
        encoding: Key[Encoding] = Key(default=Encoding.ASCII)

        keepalive: Keepalive = Keepalive()

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

            # How many characters to display in a line before wrapping to the
            # next line. If 0, wrapping occurs at the width of the output view.
            word_wrap_column: Key[int] = Key(
                constants.OUTPUT_VIEW_WORD_WRAP_COLUMN
            )

            # The color of the UI canvas onto which game text is rendered.
            canvas_color: Key[Color] = _color_key(ANSIColorCodes.Black)

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

    class Pattern(Bunch):
        """
        Records a compound user-defined pattern, to be matched against game text
        so e.g. custom formatting can be applied.
        """

        class Fragment(Bunch):
            # The type of pattern stored in this fragment.
            type: Key[PatternType] = Key(default=PatternType.ANYTHING)

            # The text of the pattern in this fragment. Unused if the pattern
            # type is ANYTHING.
            pattern_text: Key[str] = Key(default="")

            # Which format to apply to the given fragment.
            format: Key[FormatUpdate] = _format_key()

        # Whether to match entire lines, or anywhere in lines.
        scope: Key[PatternScope] = Key(default=PatternScope.ENTIRE_LINE)

        # The sub-pattern fragments that make up this pattern.
        fragments: List[Fragment] = List(Fragment())

        # The format to apply to the fragment matches that don't have their own
        # specific format.
        format: Key[FormatUpdate] = _format_key()

    shortcuts: KeyShortcuts = KeyShortcuts()
    net: Network = Network()
    patterns: List[Pattern] = List(Pattern())
    ui: UI = UI()

    # The display name of the game.
    name: Key[str] = Key(default=constants.UNNAMED_WORLD_NAME)

    def __post_init__(self) -> None:
        """
        Sets up application-specific behavior.
        """

        super().__post_init__()

        self.name.onUpdateCall(self._updateSectionName)

    def _updateSectionName(self, name_key: Key[str]) -> None:
        """
        Sets a new name for the section based on a name key, if set. Else sets
        the section name to the empty string, which makes it so this section
        won't be saved.

        Args:
            name_key: A SunsetSettings Key containing the world's name.
        """

        self.setSectionName(name_key.get() if name_key.isSet() else "")

    def title(self) -> str:
        """
        Returns a name that can be used to represent the world to a human.

        Returns:
            A name for the world.
        """

        name = self.name.get().strip()

        if self.name.isSet():
            return name

        if self.net.server.isSet() and self.net.port.isSet():
            return f"{name} ({self.net.server.get()}:{self.net.port.get()})"

        return name
