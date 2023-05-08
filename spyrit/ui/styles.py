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
A class that applies a configured style to the application.
"""


import logging

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QStyleFactory
from sunset import Key


class StyleManager(QObject):
    _app: QApplication

    def __init__(self, app: QApplication, style_key: Key[str]) -> None:
        super().__init__(parent=app)

        logging.debug(
            "Installed styles found: %s.", ", ".join(QStyleFactory.keys())
        )
        logging.debug("Current style: %s", app.style().name())

        self._app = app
        style_key.onValueChangeCall(self._updateStyle)
        self._updateStyle(style_key.get())

    def _updateStyle(self, style: str) -> None:
        style = style.strip().lower()

        if not style:
            return

        logging.debug("Applying style '%s'...", style)

        if (style := QStyleFactory.create(style)) is None:  # type: ignore
            logging.warning("Failed to load style '%s'!", style)
            return

        self._app.setStyle(style)
