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
Provides a class that knows how to load a SunsetSetting from a file and write it
back.
"""

import pathlib

from typing import Any

import sunset

from PySide6 import QtCore

from spyrit.constants import SETTINGS_SAVE_DELAY_MS
from spyrit.safe_signal import safe_signal


class Exporter(QtCore.QObject):

    _SAVE_DELAY_MS = SETTINGS_SAVE_DELAY_MS

    def __init__(
        self,
        app: QtCore.QCoreApplication,
        settings: sunset.Settings,
        settings_file: pathlib.Path,
    ) -> None:

        super().__init__(parent=app)

        self._file = settings_file
        self._settings = settings
        self._settings.onSettingModifiedCall(self._triggerDelayedSave)

        self._timer = QtCore.QTimer()
        self._timer.setInterval(self._SAVE_DELAY_MS)
        self._timer.setSingleShot(True)

        safe_signal(self._timer, "timeout").connect(self.save)
        safe_signal(app, "aboutToQuit").connect(self.save)

    def load(self):

        if not self._file.exists():
            return

        self._settings.load(self._file.open())

    def save(self):

        if not self.ensureFolderExists():
            return

        self._settings.save(self._file.open(mode="w"))

    def ensureFolderExists(self) -> bool:

        folder = self._file.parent

        if folder.exists():
            return folder.is_dir()

        folder.mkdir(parents=True)

        return True

    def _triggerDelayedSave(self, _: Any = None) -> None:

        self._timer.stop()
        self._timer.start()
