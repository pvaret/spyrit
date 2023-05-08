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

"""
Implements a simple logo for the application.
"""


from math import ceil

from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from spyrit import constants

# TODO: make this a function of the font size.
_UNIT = 16
_WIDTH = 20 * _UNIT


class SpyritLogo(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout()
        self.setLayout(layout)

        spyrit_label = QSvgWidget()
        spyrit_label.load(":/logos/spyrit-logo.svg")
        spyrit_label.renderer().setAspectRatioMode(
            Qt.AspectRatioMode.KeepAspectRatio
        )

        svg_size = spyrit_label.renderer().defaultSize()
        aspect_ratio = svg_size.height() / svg_size.width()
        spyrit_label.setMinimumWidth(_WIDTH)
        spyrit_label.setMinimumHeight(int(ceil(_WIDTH * aspect_ratio)))

        layout.addWidget(spyrit_label)
        layout.addSpacing(_UNIT)

        version_label = QLabel()
        version_label.setText(f"v{constants.SPYRIT_VERSION}")

        version_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        layout.addWidget(version_label)
