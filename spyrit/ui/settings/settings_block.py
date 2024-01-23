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
#

"""
Implements a widget that contains one or several settings widgets.
"""


from PySide6.QtCore import Signal
from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SettingsBlock(QWidget):
    """
    Groups a widgets with its label into a block that reports a relevant help
    text when active.

    Args:
        widget: The widget to add to this block. May have subwidgets of its own.

        label: The label to add above the given widget.

        help_text: The text to send when the block is active.
    """

    # This signal fires when this SettingsBlock wants its help text to be
    # displayed.

    helpTextDisplayRequested: Signal = Signal(str)

    _help_text: str

    def __init__(
        self, widget: QWidget, label: str = "", help_text: str = ""
    ) -> None:
        super().__init__()

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        if label:
            self.layout().addWidget(QLabel(f"<b>{label}</b>"))

        self.layout().addWidget(widget)
        self._help_text = help_text

    def enterEvent(self, event: QEnterEvent) -> None:
        """
        Overrides the default event handler to signal that a help text needs to
        be displayed.

        Args:
            event: The event to be handled.
        """

        if text := self._help_text:
            self.helpTextDisplayRequested.emit(text)

        return super().enterEvent(event)
