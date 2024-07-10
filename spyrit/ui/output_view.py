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

from PySide6.QtCore import QEvent, QObject, QPoint, Qt, Signal, Slot
from PySide6.QtGui import (
    QDesktopServices,
    QFont,
    QFontMetrics,
    QMouseEvent,
    QTextCharFormat,
    QTextCursor,
    QTextOption,
)
from PySide6.QtWidgets import QTextEdit, QWidget

from spyrit import constants
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
        self.document().setUndoRedoEnabled(False)
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self.setToolTipDuration(constants.OUTPUT_VIEW_LINK_TOOLTIP_DURATION_MS)

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

        # Detect clicks.

        ClickDetector(self.viewport()).mouseClick.connect(self.onClick)

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
        Makes the given cursor visible as a selection and scrolls the view so
        that the cursor is approximately centered. If the cursor is null, scroll
        to the bottom instead.

        Args:
            cursor: The cursor to make visible.
        """

        if cursor.isNull():

            # A null cursor means that we're resetting the search. Clear all the
            # selections, and scroll to the bottom.

            self.setExtraSelections([])
            self.requestScrollToPosition.emit(
                self.verticalScrollBar().maximum()
            )
            return

        cursor.setKeepPositionOnInsert(True)

        search_result_format = QTextCharFormat()
        search_result_format.setForeground(self.palette().highlightedText())
        search_result_format.setBackground(self.palette().highlight())

        search_result = QTextEdit.ExtraSelection()
        search_result.cursor = cursor  # type: ignore
        search_result.format = search_result_format  # type: ignore

        self.setExtraSelections([search_result])

        # This scrolls the view so that the given cursor is a bit above the
        # middle of the view. Works well aesthetically.

        self.requestScrollToPosition.emit(
            self.verticalScrollBar().value()
            + self.cursorRect(cursor).y()
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

    @Slot(QPoint, Qt.MouseButton)
    def onClick(self, pos: QPoint, button: Qt.MouseButton) -> None:
        """
        Opens the URL at the clicked position, if there is one, and if it's the
        left button that was clicked.
        """

        if button == Qt.MouseButton.LeftButton:
            if anchor := self.anchorAt(pos):
                QDesktopServices.openUrl(anchor)

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        """
        Update the mouse cursor and show a tooltip when hovering a clickable
        link.
        """

        if anchor := self.anchorAt(e.pos()):
            self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
            self.setToolTip(anchor)
        else:
            self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
            self.setToolTip("")

        return super().mouseMoveEvent(e)


class ClickDetector(QObject):
    """
    Filters events on the target widget to detect single clicks.

    Emits mouseClick(QPoint, Qt.MouseButton) when a click is detected.

    Args:
        target: The widget on which to detect clicks.
    """

    # This signal fires when a proper click is detected on the target widget.

    mouseClick: Signal = Signal(QPoint, Qt.MouseButton)

    _click_pos: QPoint | None = None
    _click_button: Qt.MouseButton | None = None

    def __init__(self, target: QWidget) -> None:
        super().__init__(parent=target)
        target.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """
        Detects single clicks on this ClickDetector's target widget.
        """

        if watched is self.parent():
            match event:
                case (
                    QMouseEvent()
                ) if event.type() == QEvent.Type.MouseButtonPress:
                    self._click_pos = event.pos()
                    self._click_button = event.button()

                case (
                    QMouseEvent()
                ) if event.type() == QEvent.Type.MouseButtonRelease:
                    if (
                        self._click_pos is not None
                        and event.button() == self._click_button
                    ):
                        if (
                            self._click_pos - event.pos()
                        ).manhattanLength() <= constants.CLICK_DISTANCE_THRESHOLD:
                            self.mouseClick.emit(event.pos(), event.button())

                    self._click_pos = None
                    self._click_button = None

                case _:
                    pass

        return super().eventFilter(watched, event)
