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

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor

from spyrit.network.connection import Status
from spyrit.network.fragments import (
    ANSIFragment,
    FlowControlCode,
    FlowControlFragment,
    Fragment,
    FragmentList,
    NetworkFragment,
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
    _bold: bool = False
    _bright: bool = False
    _italic: bool = False
    _underline: bool = False
    _reverse: bool = False
    _strikeout: bool = False
    _foreground: Color = NoColor()
    _background: Color = NoColor()

    def __init__(self) -> None:
        self._format_stack = {}

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

        bold = reduce(not_none, (f.bold for f in formats), self._bold)
        bright = reduce(not_none, (f.bright for f in formats), self._bright)
        italic = reduce(not_none, (f.italic for f in formats), self._italic)
        underline = reduce(
            not_none, (f.underline for f in formats), self._underline
        )
        reverse = reduce(not_none, (f.reverse for f in formats), self._reverse)
        strikeout = reduce(
            not_none, (f.strikeout for f in formats), self._strikeout
        )
        foreground = reduce(
            valid_color, (f.foreground for f in formats), self._foreground
        )
        background = reduce(
            valid_color, (f.background for f in formats), self._background
        )

        if bold != self._bold:
            self._bold = bold
            char_format.setFontWeight(
                QFont.Weight.Bold if bold else QFont.Weight.Medium
            )

        if italic != self._italic:
            self._italic = italic
            char_format.setFontItalic(italic)

        if underline != self._underline:
            self._underline = underline
            char_format.setFontUnderline(underline)

        if strikeout != self._strikeout:
            self._strikeout = strikeout
            char_format.setFontStrikeOut(strikeout)

        if (bright, reverse, foreground, background) != (
            self._bright,
            self._reverse,
            self._foreground,
            self._background,
        ):
            self._bright = bright
            self._reverse = reverse
            self._foreground = foreground
            self._background = background

            fg_color, bg_color = self._computeColors(
                bright, reverse, foreground, background
            )
            if fg_color.isUnset():
                char_format.clearBackground()
            else:
                char_format.setForeground(QColor(fg_color.asHex()))

            if bg_color.isUnset():
                char_format.clearBackground()
            else:
                char_format.setBackground(QColor(bg_color.asHex()))

    @staticmethod
    def _computeColors(
        bright: bool, reverse: bool, foreground: Color, background: Color
    ) -> tuple[Color, Color]:
        if bright:
            foreground = foreground.bright()

        return (background, foreground) if reverse else (foreground, background)


class Scribe(QObject):
    """
    A class that receives a stream of processed fragments and expresses it as
    formatted text on the given cursor.
    """

    # This signal fires whenever a full line was inscribed into the cursor.

    newLineInscribed: Signal = Signal()  # noqa: N815

    _cursor: QTextCursor
    _settings: SpyritSettings.UI.Output
    _char_format: QTextCharFormat
    _format_updater: CharFormatUpdater
    _pending_newline: bool = False

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
        self._format_updater = CharFormatUpdater()
        self._ansi_format = FormatUpdate()

        base_format = FormatUpdate(
            foreground=settings.default_text_color.get(),
            background=settings.background_color.get(),
        )
        settings.default_text_color.onValueChangeCall(base_format.setForeground)
        settings.background_color.onValueChangeCall(base_format.setBackground)

        self._format_updater.pushFormat(base_format)
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

                case _:
                    logging.debug(
                        "Unexpected fragment type in Scribe: '%s'",
                        fragment.__class__.__name__,
                    )

    def _insertText(self, text: str) -> None:
        self._flushPendingNewLine()
        self._format_updater.applyFormat(self._char_format)
        self._cursor.insertText(text, self._char_format)

    def _insertStatusText(
        self, text: str, level: _MessageLevel = _MessageLevel.INFO
    ) -> None:
        self._flushPendingNewLine()

        prefix = {
            _MessageLevel.INFO: _INFO_PREFIX,
            _MessageLevel.ERROR: _ERROR_PREFIX,
        }[level]

        base_format = FormatUpdate(
            foreground=self._settings.default_text_color.get(),
            background=self._settings.background_color.get(),
        )
        formatter = CharFormatUpdater()
        formatter.pushFormat(base_format)
        formatter.pushFormat(self._settings.status_text_format.get())
        formatter.applyFormat(status_text_format := QTextCharFormat())
        self._cursor.insertText(f"{prefix} {text}", status_text_format)

        self._insertNewLine()

    def _insertNewLine(self) -> None:
        self._flushPendingNewLine()
        self._pending_newline = True
        self.newLineInscribed.emit()

    def _flushPendingNewLine(self) -> None:
        if self._pending_newline:
            self._cursor.insertText("\n")
            self._pending_newline = False
