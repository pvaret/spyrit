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
A QAction subclass that binds to a SunsetSettings key containing a QKeySequence.
"""

import logging

from typing import Callable

from PySide6.QtCore import QObject, Qt, SignalInstance, Slot
from PySide6.QtGui import QAction

from sunset import Key

from spyrit.settings.key_shortcut import Shortcut


class ActionWithKeySetting(QAction):
    _key: Shortcut

    def __init__(
        self,
        parent: QObject,
        text: str,
        key: Key[Shortcut],
        slot: Slot | SignalInstance | Callable[[], None],
    ) -> None:
        super().__init__(parent=parent)

        self.setText(text)
        self.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        key.onValueChangeCall(self.updateShortcut)
        self.updateShortcut(key.get())

        self.triggered.connect(self._debug)
        self.triggered.connect(slot)

    def updateShortcut(self, key: Shortcut) -> None:
        self._key = key
        self.setShortcut(key)

    @Slot()
    def _debug(self) -> None:
        if self.isCheckable():
            logging.debug(
                "Action '%s' (%s) toggled to %s.",
                self.text(),
                self._key.toString(),
                self.isChecked(),
            )

        else:
            logging.debug(
                "Action '%s' (%s) activated.", self.text(), self._key.toString()
            )
