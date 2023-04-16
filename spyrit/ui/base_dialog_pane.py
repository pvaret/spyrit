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
Implements a dialog widget that can be used as a container pane.
"""


from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from spyrit.ui.bars import HBar
from spyrit.ui.base_pane import Pane


class BaseDialogPane(Pane):
    # Signal emitted when the user clicks the dialog acceptance button.

    okClicked = Signal()  # noqa: N815

    # Signal emitted when the user clicks the dialog cancel button.

    cancelClicked = Signal()  # noqa: N815

    def __init__(
        self,
        widget: QWidget,
        ok_button_text: str = "Ok",
        cancel_button_text: str = "Cancel",
    ) -> None:
        super().__init__()

        pane_layout = QVBoxLayout()
        self.setLayout(pane_layout)

        # Add the dialog's main widget.

        pane_layout.addWidget(widget)

        # Add a separator.

        pane_layout.addWidget(HBar())

        # Add the dialog buttons.

        button_layout = QHBoxLayout()
        pane_layout.addLayout(button_layout)

        button_layout.addStretch()

        cancel_button = QPushButton(cancel_button_text)
        cancel_button.clicked.connect(self.cancelClicked)
        button_layout.addWidget(cancel_button)

        ok_button = QPushButton(ok_button_text)
        ok_button.clicked.connect(self.okClicked)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
