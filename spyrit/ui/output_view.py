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
    _settings: SpyritSettings.UI.Output

    def __init__(self, settings: SpyritSettings.UI.Output) -> None:
        super().__init__()
        self.setReadOnly(True)

        self._settings = settings

        self._settings.font.onValueChangeCall(self.setFont)
        self.setFont(self._settings.font.get())

        self._settings.background_color.onValueChangeCall(self._applyStyleSheet)
        self._applyStyleSheet()

    def _applyStyleSheet(self, _: Any = None) -> None:
        background_color = self._settings.background_color.asHex()
        self.setStyleSheet(
            f"""
            background-color: {background_color} ;
            """
        )
