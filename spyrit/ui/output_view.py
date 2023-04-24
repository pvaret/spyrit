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
Implements a widget to display the text of a game.
"""


from typing import Any

from PySide6.QtWidgets import QTextEdit

from spyrit.settings.spyrit_settings import SpyritSettings


class OutputView(QTextEdit):
    _settings: SpyritSettings

    def __init__(self, settings: SpyritSettings) -> None:
        super().__init__()
        self.setReadOnly(True)

        self._settings = settings

        self._settings.ui.font.onValueChangeCall(self._applyStyleSheet)
        self._applyStyleSheet()

    def _applyStyleSheet(self, _: Any = None) -> None:
        font = self._settings.ui.font.get()
        self.setStyleSheet(
            f"""
            font-family: {font.family()} ;
            font-size: {font.pointSize()}pt ;
            """
        )
