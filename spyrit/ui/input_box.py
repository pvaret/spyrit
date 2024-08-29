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

"""
Implements an input box for the user to type text in.
"""


from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFontMetrics, QKeyEvent
from PySide6.QtWidgets import QPlainTextEdit


CRLF = "\r\n"


class InputBox(QPlainTextEdit):
    """
    A text entry widget dedicated to letting a user send text to a game.

    Args:
        parent: The parent widget of this widget.
    """

    # This signal fires when this input box wants its contents sent to the game world.

    sendText: Signal = Signal(str)

    # This signal fires when this input box no longer wants to have the focus.

    expelFocus: Signal = Signal()

    _active: bool = False

    def __init__(self) -> None:
        super().__init__()

        # Update the minimum height of the box. Unlike default QPlainTextEdit,
        # we want to allow the box to be just high enough for one row of text.
        # Plus margins and frame, of course.

        margins = self.contentsMargins()
        doc_margins = self.document().documentMargin()
        frame_width = self.frameWidth()
        line_height = QFontMetrics(self.font()).height()

        self.setMinimumHeight(
            int(
                line_height
                + margins.top()
                + margins.bottom()
                + doc_margins * 2
                + frame_width * 2
            )
        )

        # Use tabs to change the focus instead of entering them as character in
        # the input box.

        self.setTabChangesFocus(True)

    @Slot(bool)
    def setActive(self, active: bool) -> None:
        """
        Sets whether this input box can be used to send text to a live
        connection.
        """

        self._active = active

    def keyPressEvent(self, e: QKeyEvent) -> None:
        """
        Overrides the key press event from the parent to emit a signal when
        Enter is pressed without modifiers.

        Args:
            e: The key event to process.
        """

        # Handle the Enter/Return special case.

        if (
            e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            and e.modifiers() == Qt.KeyboardModifier.NoModifier
        ):
            self._maybeSendContents()
            e.accept()
            return

        # Else let the event proceed.

        super().keyPressEvent(e)

    def _maybeSendContents(self) -> None:
        """
        Requests for the contents of the box to be sent to a world game if the
        box is currently active. If so, also clears the box.
        """

        if self._active:
            self.sendText.emit(self.toPlainText() + CRLF)
            self.clear()

    @Slot(bool)
    def toggleVisibility(self, visible: bool) -> None:
        """
        Switches the widget between visible and not, and acquires or expels the
        focus accordingly.

        Args:
            visible: Whether to now make the widget visible.
        """

        had_focus = self.hasFocus()

        self.setVisible(visible)

        if visible:
            self.setFocus()
        elif had_focus:
            self.expelFocus.emit()
