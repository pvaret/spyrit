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

"""
Implements an input box for the user to type text in.
"""


from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QTextEdit, QWidget

from spyrit.network.connection import Connection


_CRLF = "\r\n"


class InputBox(QTextEdit):
    # This signal fires when the user presses Enter in the input box.

    returnPressed = Signal()  # noqa: N815

    # This signal fires when this input box no longer wants to have the focus.

    expelFocus = Signal()  # noqa: N815

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Use tabs to change the focus instead of entering them as character in
        # the input box.

        self.setTabChangesFocus(True)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        # Handle the Enter/Return special case.

        if (
            e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            and e.modifiers() == Qt.KeyboardModifier.NoModifier
        ):
            self.returnPressed.emit()
            e.accept()
            return

        # Else let the event proceed.

        super().keyPressEvent(e)

    @Slot(bool)
    def toggleVisibility(self, visible: bool) -> None:
        has_focus = self.hasFocus()

        self.setVisible(visible)
        self.setEnabled(visible)  # Note that this may clear the focus.

        if visible:
            self.setFocus()
        elif has_focus:
            self.expelFocus.emit()


class Postman(QObject):
    """
    Manages posting from an InputBox to a Connection.
    """

    # This signal fires when we successfully sent an input to the connection.

    inputSent = Signal(str)  # noqa: N815

    _inputbox: InputBox
    _connection: Connection

    def __init__(self, inputbox: InputBox, connection: Connection) -> None:
        super().__init__(parent=connection)

        self._inputbox = inputbox
        self._connection = connection

        self._inputbox.returnPressed.connect(self._sendInput)

    @Slot()
    def _sendInput(self) -> None:
        text = self._inputbox.toPlainText()
        if self._connection.send(text + _CRLF):
            self._inputbox.clear()
            self.inputSent.emit(text)
