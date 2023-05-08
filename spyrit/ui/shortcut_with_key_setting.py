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
A class that binds a QShortcut to a SunsetSettings key containing a
QKeySequence.
"""

import logging

from typing import Callable

from PySide6.QtCore import QObject, Qt, SignalInstance, Slot
from PySide6.QtGui import QShortcut

from sunset import Key

from spyrit.settings.key_shortcut import KeyShortcut


class ShortcutWithKeySetting(QObject):
    _shortcut: QShortcut
    _key: Key[KeyShortcut]

    def __init__(
        self,
        parent: QObject,
        key: Key[KeyShortcut],
        slot: Slot | SignalInstance | Callable[[], None],
    ) -> None:
        super().__init__(parent=parent)

        self._shortcut = QShortcut(parent)
        self._shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._key = key
        self._key.onValueChangeCall(self.updateShortcut)
        self.updateShortcut(self._key.get())

        self._shortcut.activated.connect(slot)
        self._shortcut.activated.connect(self._debug)

    def updateShortcut(self, key: KeyShortcut) -> None:
        self._shortcut.setKey(key)

    @Slot()
    def _debug(self) -> None:
        logging.debug("Shortcut %s activated.", self._shortcut.key().toString())
