# Copyright (c) 2007-2022 Pascal Varet <p.varet@gmail.com>
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
A class that binds a QShortcut to a SunsetSettings setting containing a
QKeySequence.
"""


from typing import Union

from PySide6 import QtCore, QtGui

import sunset

from spyrit.safe_signal import safe_signal
from spyrit.settings import key_shortcut


class ShortcutWithKeySetting(QtCore.QObject):
    def __init__(
        self,
        parent: QtCore.QObject,
        setting: sunset.Setting[key_shortcut.KeyShortcut],
        slot: Union[QtCore.Slot, QtCore.SignalInstance],
    ) -> None:

        super().__init__(parent=parent)

        self._shortcut = QtGui.QShortcut(parent)
        self._setting = setting
        self._setting.onChangeCall(self.updateShortcut)
        self.updateShortcut(self._setting.get())

        safe_signal(self._shortcut, "activated").connect(slot)

    def updateShortcut(self, key: key_shortcut.KeyShortcut) -> None:

        self._shortcut.setKey(key)
