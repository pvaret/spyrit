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
Implements a pane that shows basic information about the application.
"""

from textwrap import dedent

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from spyrit import constants
from spyrit.ui.base_dialog_pane import BaseDialogPane
from spyrit.ui.sizer import Sizer
from spyrit.ui.spyrit_logo import SpyritLogo


class AboutPane(BaseDialogPane):
    """
    A pane that shows basic information about the application.
    """

    def __init__(self) -> None:
        super().__init__()

        sizer = Sizer(self)

        self.okClicked.connect(self.slideLeft)

        text = f"""
            <b>{constants.APPLICATION_NAME}</b>: a MUD/MUSH/MUCK/MOO client.<br>
            """

        text = dedent(text.strip())
        label = QLabel(text)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        label.setOpenExternalLinks(True)

        pane = QWidget()
        pane.setLayout(hlayout := QHBoxLayout())
        hlayout.addStretch()
        hlayout.addLayout(vlayout := QVBoxLayout())
        hlayout.addStretch()

        vlayout.addStretch(1)

        vlayout.addWidget(SpyritLogo())
        vlayout.addSpacing(4 * sizer.unitSize())
        vlayout.addWidget(label)

        vlayout.addStretch(2)

        self.setWidget(pane)
