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
Implements a class that translates network fragments into text and formatting to
be applied to a cursor.
"""


import logging

from typing import Iterable

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QColor, QFont, QTextCursor, QTextCharFormat

from spyrit.network.connection import Status
from spyrit.network.fragments import (
    FlowControlCode,
    FlowControlFragment,
    Fragment,
    FragmentList,
    NetworkFragment,
    TextFragment,
)
from spyrit.settings.spyrit_settings import SpyritSettings


class TextFormat(QTextCharFormat):
    def __init__(self, text_format: SpyritSettings.UI.Output.Format) -> None:
        super().__init__()

        if text_format.italic.get():
            self.setFontItalic(True)

        if text_format.bold.get():
            self.setFontWeight(QFont.Weight.Bold)

        if text_format.underlined.get():
            self.setFontUnderline(True)

        if href := text_format.href.get():
            self.setAnchorHref(href)

        self.setForeground(QColor(text_format.text_color.asHex()))


class Scribe(QObject):
    """
    A class that receives a stream of processed fragments and expresses it as
    formatted text on the given cursor.
    """

    _cursor: QTextCursor
    _settings: SpyritSettings.UI.Output
    _pending_newline: bool

    def __init__(
        self,
        cursor: QTextCursor,
        settings: SpyritSettings.UI.Output,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        cursor.setCharFormat(TextFormat(settings.text_format))
        self._cursor = cursor
        self._settings = settings
        self._pending_newline = False

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

                case NetworkFragment(event, text):
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
                    self._insertStatusText(message)

                case _:
                    logging.debug(
                        "Unexpected fragment type in Scribe: '%s'",
                        fragment.__class__.__name__,
                    )

    def _insertText(self, text: str) -> None:
        self._flushPendingNewLine()
        self._cursor.insertText(text)

    def _insertStatusText(self, text: str) -> None:
        self._flushPendingNewLine()

        format_ = self._cursor.charFormat()
        self._cursor.setCharFormat(
            TextFormat(self._settings.status_text_format)
        )
        self._cursor.insertText(f"→ {text}")
        self._cursor.setCharFormat(format_)

        self._insertNewLine()

    def _insertNewLine(self) -> None:
        self._flushPendingNewLine()
        self._pending_newline = True

    def _flushPendingNewLine(self) -> None:
        if self._pending_newline:
            self._cursor.insertText("\n")
            self._pending_newline = False
