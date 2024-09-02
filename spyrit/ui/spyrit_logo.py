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
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from spyrit import constants
from spyrit.resources.resources import Logo
from spyrit.ui.sizer import Sizer


def _render_svg(path: str, width: int) -> QSvgWidget:
    svg = QSvgWidget()
    svg.load(path)
    svg.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

    svg_size = svg.renderer().defaultSize()
    aspect_ratio = svg_size.height() / svg_size.width()
    svg.setFixedWidth(width)
    svg.setFixedHeight(int(ceil(width * aspect_ratio)))

    return svg


class SpyritLogo(QWidget):
    """
    Implements a visually pleasant application logo.
    """

    def __init__(self, width: int) -> None:
        super().__init__()

        self.setLayout(layout := QGridLayout())

        unit = Sizer(self).unitSize()

        title_width = width * 3 // 4
        icon_width = width - title_width

        layout.setContentsMargins(unit // 2, unit // 2, unit // 2, unit // 2)
        layout.setHorizontalSpacing(unit // 2)
        layout.setVerticalSpacing(unit)

        layout.addWidget(
            _render_svg(Logo.APPLICATION_ICON_SVG, icon_width),
            0,
            0,
            2,
            1,
            alignment=Qt.AlignmentFlag.AlignTop,
        )

        layout.addWidget(_render_svg(Logo.SPYRIT_SVG, title_width), 0, 1)

        version_label = QLabel()
        version_label.setText(f"<i>v{constants.SPYRIT_VERSION}</i>")
        version_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(version_label, 1, 1)
