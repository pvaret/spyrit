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
from PySide6.QtGui import QAction, QIcon

from sunset import Key

from spyrit.settings.key_shortcut import Shortcut


class ActionWithKeySetting(QAction):
    """
    A QAction wrapper class that uses a SunsetSettings Key to store its keyboard
    shortcut.

    Args:
        parent: The object to use as this action's parent, for lifetime duration
            purposes.

        text: The user-facing name to give this action.

        key: The SunsetSettings Key containing the keyboard shortcut to use for
            this action.

        slot: The callable to trigger when this action is invoked.

        checkable: Whether this action is a check, i.e. togglable.
            Default: False.

        icon: The icon to use for this action when added to a toolbar or menu.
            Default: None.
    """

    _key: Shortcut

    def __init__(
        self,
        parent: QObject,
        text: str,
        key: Key[Shortcut],
        slot: Slot | SignalInstance | Callable[[], None],
        checkable: bool = False,
        icon: QIcon | None = None,
    ) -> None:
        super().__init__(parent=parent)

        self.setText(text)
        self.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        key.onValueChangeCall(self.updateShortcut)
        self.updateShortcut(key.get())

        self.setCheckable(checkable)

        if icon is not None:
            self.setIcon(icon)

        self.triggered.connect(self._debug)
        self.triggered.connect(slot)

    def updateShortcut(self, key: Shortcut) -> None:
        """
        Sets up the given keyboard shortcut to be used for this action.

        Args:
            key: The keyboard shortcut.
        """

        self._key = key
        self.setShortcut(key)
        self.setToolTip(f"{self.text()} ({key.toString()})")

    @Slot()
    def _debug(self) -> None:
        """
        Logs debug information when this action is invoked.
        """

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
