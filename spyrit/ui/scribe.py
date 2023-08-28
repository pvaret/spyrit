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
Implements a class that translates network fragments into text and formatting to
be applied to a cursor.
"""


import enum
import logging

from functools import reduce
from typing import Iterable

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor

from sunset import Key

from spyrit.network.connection import Status
from spyrit.network.fragments import (
    ANSIFragment,
    FlowControlCode,
    FlowControlFragment,
    Fragment,
    FragmentList,
    MatchBoundary,
    NetworkFragment,
    PatternMatchFragment,
    TextFragment,
)
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.colors import Color, NoColor
from spyrit.ui.format import FormatUpdate


_INFO_PREFIX = "•"
_ERROR_PREFIX = "‼"


class _MessageLevel(enum.Enum):
    INFO = enum.auto()
    ERROR = enum.auto()


class CharFormatUpdater:
    """
    Maintains a stack of currently active formats, so that the topmost value for
    each attribute can be applied to a QTextCharFormat.
    """

    _format_stack: dict[int, FormatUpdate]
    _default_text_color: Key[Color]
    _canvas_color: Key[Color]

    def __init__(
        self, default_text_color: Key[Color], canvas_color: Key[Color]
    ) -> None:
        self._format_stack = {}
        self._default_text_color = default_text_color
        self._canvas_color = canvas_color

    def pushFormat(self, format_: FormatUpdate) -> None:
        self._format_stack[id(format_)] = format_

    def popFormat(self, format_: FormatUpdate) -> None:
        try:
            del self._format_stack[id(format_)]
        except IndexError:
            return

    def applyFormat(self, char_format: QTextCharFormat) -> None:
        formats = list(self._format_stack.values())

        def not_none(this: bool, other: bool | None) -> bool:
            return other if other is not None else this

        def valid_color(this: Color, other: Color | None) -> Color:
            return other if other is not None and not other.isUnset() else this

        bold = reduce(not_none, (f.bold for f in formats), False)
        bright = reduce(not_none, (f.bright for f in formats), False)
        italic = reduce(not_none, (f.italic for f in formats), False)
        underline = reduce(not_none, (f.underline for f in formats), False)
        reverse = reduce(not_none, (f.reverse for f in formats), False)
        strikeout = reduce(not_none, (f.strikeout for f in formats), False)
        foreground = reduce(
            valid_color, (f.foreground for f in formats), NoColor()
        )
        background = reduce(
            valid_color, (f.background for f in formats), NoColor()
        )

        char_format.setFontWeight(
            QFont.Weight.Bold if bold else QFont.Weight.Medium
        )
        char_format.setFontItalic(italic)
        char_format.setFontUnderline(underline)
        char_format.setFontStrikeOut(strikeout)

        actual_foreground, actual_background = self._computeColors(
            bright, reverse, foreground, background
        )

        if actual_foreground.isUnset():
            # This should not normally happen, unless the user configured
            # NoColor() as their default text color. Qt will then use the
            # default system text color.
            char_format.clearForeground()
        else:
            char_format.setForeground(QColor(actual_foreground.asHex()))

        if actual_background.isUnset():
            char_format.clearBackground()
        else:
            char_format.setBackground(QColor(actual_background.asHex()))

    def _computeColors(
        self, bright: bool, reverse: bool, foreground: Color, background: Color
    ) -> tuple[Color, Color]:
        if foreground.isUnset():
            foreground = self._default_text_color.get()

        if bright:
            foreground = foreground.bright()

        if reverse:
            foreground, background = background, foreground

            if foreground.isUnset():
                foreground = self._canvas_color.get()

        return foreground, background


class Scribe(QObject):
    """
    A class that receives a stream of processed fragments and expresses it as
    formatted text on the given cursor.
    """

    _cursor: QTextCursor
    _settings: SpyritSettings.UI.Output
    _char_format: QTextCharFormat
    _format_updater: CharFormatUpdater
    _pending_newline: bool = False
    _at_line_start: bool = True

    def __init__(
        self,
        cursor: QTextCursor,
        settings: SpyritSettings.UI.Output,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self._cursor = cursor
        self._settings = settings
        self._char_format = QTextCharFormat()
        self._format_updater = CharFormatUpdater(
            settings.default_text_color, settings.canvas_color
        )
        self._ansi_format = FormatUpdate()
        self._format_updater.pushFormat(self._ansi_format)

    @Slot(FragmentList)
    def inscribe(self, fragments: Iterable[Fragment]) -> None:
        """
        Expresses the given fragments as formatted text on this Scribe's cursor.
        """

        for fragment in fragments:
            match fragment:
                case TextFragment(text):
                    self._insertText(text)

                case FlowControlFragment(code):
                    if code == FlowControlCode.LF:
                        self._insertNewLine()

                case ANSIFragment(format_update):
                    self._ansi_format.update(format_update)

                case NetworkFragment(event, text):
                    level = _MessageLevel.INFO
                    match event:
                        case Status.DISCONNECTED:
                            message = "Disconnected."
                        case Status.RESOLVING:
                            message = f"Looking up '{text}'..."
                        case Status.CONNECTING:
                            message = "Connecting..."
                        case Status.CONNECTED:
                            message = "Connected!"
                        case Status.ERROR:
                            message = f"Error: {text}!"
                            level = _MessageLevel.ERROR
                    self._insertStatusText(message, level)

                case PatternMatchFragment(format_, MatchBoundary.START):
                    self._format_updater.pushFormat(format_)

                case PatternMatchFragment(format_, MatchBoundary.END):
                    self._format_updater.popFormat(format_)

                case _:
                    logging.debug(
                        "Unexpected fragment type in Scribe: '%s'",
                        fragment.__class__.__name__,
                    )

    def _insertText(self, text: str) -> None:
        self._flushPendingNewLine()
        self._format_updater.applyFormat(self._char_format)
        self._cursor.insertText(text, self._char_format)
        self._at_line_start = False

    def _insertStatusText(
        self, text: str, level: _MessageLevel = _MessageLevel.INFO
    ) -> None:
        if not self._at_line_start:
            self._insertNewLine()
        self._flushPendingNewLine()

        prefix = {
            _MessageLevel.INFO: _INFO_PREFIX,
            _MessageLevel.ERROR: _ERROR_PREFIX,
        }[level]

        formatter = CharFormatUpdater(
            self._settings.default_text_color, self._settings.canvas_color
        )
        formatter.pushFormat(self._settings.status_text_format.get())
        formatter.applyFormat(status_text_format := QTextCharFormat())
        self._cursor.insertText(f"{prefix} {text}", status_text_format)
        self._at_line_start = False

        self._insertNewLine()

    def _insertNewLine(self) -> None:
        self._flushPendingNewLine()
        self._pending_newline = True
        self._at_line_start = True

    def _flushPendingNewLine(self) -> None:
        if self._pending_newline:
            self._cursor.insertText("\n")
            self._pending_newline = False
