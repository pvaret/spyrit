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


from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QTextEdit

from spyrit.settings.spyrit_settings import SpyritSettings


class InputBox(QTextEdit):
    # This signal fires when the user presses Enter in the input box.

    returnPressed = Signal()  # noqa: N815

    _settings: SpyritSettings

    def __init__(self, settings: SpyritSettings) -> None:
        super().__init__()

        self._settings = settings

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if (
            e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            and e.modifiers() == Qt.KeyboardModifier.NoModifier
        ):
            self.returnPressed.emit()
            e.accept()
            return

        super().keyPressEvent(e)
