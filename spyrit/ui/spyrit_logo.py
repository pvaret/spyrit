# Copyright (c) 2007-2024 Pascal Varet <p.varet@gmail.com>
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
from spyrit.resources.resources import Logo
from spyrit.ui.sizer import Sizer


class SpyritLogo(QWidget):
    """
    Implements a visually pleasant application logo.
    """

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        unit = Sizer(self).unitSize()
        logo_width = constants.LOGO_WIDTH_UNITS * unit

        spyrit_label = QSvgWidget()
        spyrit_label.load(Logo.SPYRIT_SVG)
        spyrit_label.renderer().setAspectRatioMode(
            Qt.AspectRatioMode.KeepAspectRatio
        )

        svg_size = spyrit_label.renderer().defaultSize()
        aspect_ratio = svg_size.height() / svg_size.width()
        spyrit_label.setMinimumWidth(logo_width)
        spyrit_label.setMinimumHeight(int(ceil(logo_width * aspect_ratio)))

        layout.addWidget(spyrit_label)
        layout.addSpacing(unit)

        version_label = QLabel()
        version_label.setText(f"v{constants.SPYRIT_VERSION}")

        version_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        layout.addWidget(version_label)
