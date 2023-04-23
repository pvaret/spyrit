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
A class that applies a configured theme to the application.
"""


import logging

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QStyleFactory
from sunset import Key


class ThemeManager(QObject):
    _app: QApplication

    def __init__(self, app: QApplication, theme_key: Key[str]) -> None:
        super().__init__(parent=app)

        logging.debug(
            "Installed themes found: %s.", ", ".join(QStyleFactory.keys())
        )

        self._app = app
        theme_key.onValueChangeCall(self._updateTheme)
        self._updateTheme(theme_key.get())

    def _updateTheme(self, theme: str) -> None:
        theme = theme.strip().lower()

        if not theme:
            return

        logging.debug("Applying theme '%s'...", theme)

        if (style := QStyleFactory.create(theme)) is None:  # type: ignore
            logging.warning("Failed to load theme '%s'!", theme)
            return

        self._app.setStyle(style)
