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
A class that binds a QShortcut to a SunsetSettings key containing a
QKeySequence.
"""


from PySide6 import QtCore, QtGui

from sunset import Key

from spyrit.safe_signal import safe_signal
from spyrit.settings import key_shortcut


class ShortcutWithKeySetting(QtCore.QObject):
    _shortcut: QtGui.QShortcut
    _key: Key[key_shortcut.KeyShortcut]

    def __init__(
        self,
        parent: QtCore.QObject,
        key: Key[key_shortcut.KeyShortcut],
        slot: QtCore.Slot | QtCore.SignalInstance,
    ) -> None:
        super().__init__(parent=parent)

        self._shortcut = QtGui.QShortcut(parent)
        self._key = key
        self._key.onValueChangeCall(self.updateShortcut)
        self.updateShortcut(self._key.get())

        safe_signal(self._shortcut, "activated").connect(slot)

    def updateShortcut(self, key: key_shortcut.KeyShortcut) -> None:
        self._shortcut.setKey(key)
