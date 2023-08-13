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

from typing import Iterable

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from sunset import Key


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
    Applies extended format updates to a QTextCharFormat, including tricky ones
    like reverse video.
    """

    _char_format: QTextCharFormat
    _foreground: Color
    _background: Color
    _default_foreground: Color
    _default_background: Color
    _bright: bool = False
    _reverse: bool = False

    def __init__(
        self,
        foreground: Key[Color],
        background: Key[Color],
        char_format: QTextCharFormat,
    ) -> None:
        self._char_format = char_format

        # Set up the default colors for when the format's colors are not
        # otherwise overriden.

        self._default_foreground = foreground.get()
        self._default_background = background.get()
        foreground.onValueChangeCall(self._setDefaultForeground)
        background.onValueChangeCall(self._setDefaultBackground)

        # Apply the default colors once.

        self.setForeground(NoColor())
        self.setBackground(NoColor())

    def _setDefaultForeground(self, color: Color) -> None:
        self._default_foreground = color

    def _setDefaultBackground(self, color: Color) -> None:
        self._default_foreground = color

    def setBright(self, bright: bool) -> None:
        self._bright = bright
        self.setForeground()
        self.setBackground()

    def setReverse(self, reverse: bool) -> None:
        self._reverse = reverse
        self.setForeground()
        self.setBackground()

    def setForeground(self, color: Color | None = None) -> None:
        """
        Update the current foreground color. If reverse video is on, this will
        in fact update the background of the text.
        """

        if color is None:
            color = self._foreground
        else:
            self._foreground = color

        if color.isUnset():
            color = self._default_foreground

        if self._bright:
            color = color.bright()

        if self._reverse:
            self._char_format.setBackground(QColor(color.asHex()))
        else:
            self._char_format.setForeground(QColor(color.asHex()))

    def setBackground(self, color: Color | None = None) -> None:
        """
        Update the current background color. If reverse video is on, this will
        in fact update the foreground of the text.
        """

        if color is None:
            color = self._background
        else:
            self._background = color

        if color.isUnset():
            if not self._reverse:
                # As a special case, if the color is unset and we're not in
                # reverse video mode, then we outright clear the background
                # color of the format. That way the background of the output
                # view itself will be used.

                self._char_format.clearBackground()
                return

            color = self._default_background

        if self._reverse:
            self._char_format.setForeground(QColor(color.asHex()))
        else:
            self._char_format.setBackground(QColor(color.asHex()))

    def applyFormatUpdate(self, format_update: FormatUpdate) -> None:
        """
        Computes and applies the current format with the given update.
        """

        if format_update.bold is not None:
            self._char_format.setFontWeight(
                QFont.Weight.Bold if format_update.bold else QFont.Weight.Medium
            )

        if format_update.bright is not None:
            self.setBright(format_update.bright)

        if format_update.italic is not None:
            self._char_format.setFontItalic(format_update.italic)

        if format_update.underline is not None:
            self._char_format.setFontUnderline(format_update.underline)

        if format_update.reverse is not None:
            self.setReverse(format_update.reverse)

        if format_update.strikeout is not None:
            self._char_format.setFontStrikeOut(format_update.strikeout)

        if format_update.foreground is not None:
            self.setForeground(format_update.foreground)

        if format_update.background is not None:
            self.setBackground(format_update.background)


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
        self._format_updater = CharFormatUpdater(
            settings.default_text_color,
            settings.background_color,
            self._char_format,
        )

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
                    self._format_updater.applyFormatUpdate(format_update)

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
        self._cursor.insertText(text, self._char_format)

    def _insertStatusText(
        self, text: str, level: _MessageLevel = _MessageLevel.INFO
    ) -> None:
        self._flushPendingNewLine()

        prefix = {
            _MessageLevel.INFO: _INFO_PREFIX,
            _MessageLevel.ERROR: _ERROR_PREFIX,
        }[level]

        formatter = CharFormatUpdater(
            self._settings.default_text_color,
            self._settings.background_color,
            status_text_format := QTextCharFormat(),
        )
        formatter.applyFormatUpdate(self._settings.status_text_format.get())
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
