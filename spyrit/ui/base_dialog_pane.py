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
Implements a dialog widget that can be used as a container pane.
"""


from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from spyrit.ui.bars import HBar
from spyrit.ui.base_pane import Pane


class BaseDialogPane(Pane):
    """
    The base class for dialog panes to be used in a container. Set the dialog's
    main widget with setWidget() and pass the dialog's buttons as constructor
    arguments.

    Args:
        ok_button: A push button that the user should click to accept the
            dialog's content. If None, a default button will be created with the
            text "Ok".

        cancel_button: A push button that the user should click to decline the
            dialog's content.
    """

    # Signal emitted when the user clicks the dialog acceptance button.

    okClicked: Signal = Signal()

    # Signal emitted when the user clicks the dialog cancel button.

    cancelClicked: Signal = Signal()

    _widget: QWidget

    def __init__(
        self,
        ok_button: QPushButton | None = None,
        cancel_button: QPushButton | None = None,
    ) -> None:
        super().__init__()

        self.setLayout(pane_layout := QVBoxLayout())

        # Add the dialog's main widget.

        self._widget = QWidget()
        pane_layout.addWidget(self._widget)

        # Add a separator.

        pane_layout.addWidget(HBar())

        # Add the dialog buttons.

        pane_layout.addLayout(button_layout := QHBoxLayout())

        button_layout.addStretch()

        if cancel_button is not None:
            cancel_button.clicked.connect(self.cancelClicked)
            button_layout.addWidget(cancel_button)

        # We always create an Ok button if one was not provided.

        if ok_button is None:
            ok_button = QPushButton("Ok")

        ok_button.clicked.connect(self.okClicked)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)

    def widget(self) -> QWidget:
        """
        Returns the widget currently set as this dialog's central widget.

        Returns:
            A widget. This widget will still be parented to this dialog.
        """

        return self._widget

    def setWidget(self, widget: QWidget) -> None:
        """
        Sets a widget to be the central widget of this dialog.

        Args:
            widget: The widget to use as this dialog's central widget. It will
                be reparented to this dialog.
        """

        self.layout().replaceWidget(self._widget, widget)
        self._widget = widget
