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
Implements a widget to display the text of a game.
"""


from typing import Any

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QFontMetrics, QTextCursor, QTextOption
from PySide6.QtWidgets import QTextEdit

from spyrit.settings.spyrit_settings import SpyritSettings


class OutputView(QTextEdit):
    """
    A widget that displays the output of a game.

    Args:
        settings: The settings object for this specific widget.
    """

    # This signal fires when the view wishes to scroll to the given position. As
    # it currently stands, scrolling is managed by the Scroller, so the view
    # can't just update its own scrollbar. Instead it needs to use this signal
    # to communicate.

    requestScrollToPosition: Signal = Signal(int)

    _settings: SpyritSettings.UI.Output

    def __init__(self, settings: SpyritSettings.UI.Output) -> None:
        super().__init__()
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._settings = settings

        # Set up the appearance of the output view.

        self._settings.font.onValueChangeCall(self.setFixedPitchFont)
        self.setFixedPitchFont(self._settings.font.get())

        self._settings.canvas_color.onValueChangeCall(self._applyStyleSheet)
        self._applyStyleSheet()

        self.setLineWrapMode(QTextEdit.LineWrapMode.FixedColumnWidth)
        self._settings.word_wrap_column.onValueChangeCall(self._setWrapColumn)
        self._setWrapColumn(self._settings.word_wrap_column.get())

        # Set up the scrollbar.

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

    def setFixedPitchFont(self, font: QFont) -> None:
        """
        Configures the given font to behave with a fixed pitch, and uses it to
        render this widget's contents.

        Args:
            font: The font to use for this widget's contents.
        """

        # Forced the pitch of the font to be fixed.

        font.setFixedPitch(True)

        # Disallow looking up missing characters from a different font.

        font.setStyleStrategy(font.StyleStrategy.NoFontMerging)

        # If the font is missing, at least, replace it with a monospace font.

        font.setStyleHint(font.StyleHint.Monospace)

        # Finally set the updated font.

        self.setFont(font)

        # And use its line height as the step increment when scrolling the view.

        step = QFontMetrics(font).lineSpacing() - 1
        self.verticalScrollBar().setSingleStep(step)

    @Slot(QTextCursor)
    def displaySearchResults(self, cursor: QTextCursor) -> None:
        """
        Makes the given cursor visible and scrolls the view so that the cursor
        is approximately centered.

        Args:
            cursor: The cursor to make visible.
        """

        self.setTextCursor(cursor)

        if cursor.isNull():
            self.requestScrollToPosition.emit(
                self.verticalScrollBar().maximum()
            )

        else:
            # This scrolls the view so that the given cursor is a bit above the
            # middle of the view. Works well aesthetically.

            self.requestScrollToPosition.emit(
                self.verticalScrollBar().value()
                + self.cursorRect().y()
                - self.viewport().height() // 2
                + self.verticalScrollBar().singleStep()
            )

    def _applyStyleSheet(self, *args: Any) -> None:
        """
        Creates and applies a stylesheet that uses the configured settings for
        this view as its properties.

        Args:
            Ignored.
        """

        del args

        background_color = self._settings.canvas_color.get().asHex()
        self.setStyleSheet(
            f"""
            QTextEdit{{ background-color: {background_color} }};
            """
        )

    def _setWrapColumn(self, column: int) -> None:
        """
        Sets up word wrapping at the given character column.

        Args:
            column: The character column at which to word-wrap. If 0, text will
                be wrapped at the widget's border.
        """

        if not column > 0:
            self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.setWordWrapMode(QTextOption.WrapMode.WordWrap)
            self.setLineWrapColumnOrWidth(column)
