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
Implements custom widgets to be used in configuration forms.
"""


from PySide6.QtGui import QIntValidator, QRegularExpressionValidator
from PySide6.QtWidgets import QLabel, QLineEdit, QSizePolicy

from sunset import Key

from spyrit import constants
from spyrit.ui.settings.connector import Connector
from spyrit.ui.sizer import Sizer


# LineEdits.


class LineEdit(QLineEdit):
    """
    A line edit widget with a custom size policy.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )


class TextLineEdit(LineEdit):
    """
    A line edit widget bound to a SunsetSettings string Key. The widget's
    contents is populated from the Key's value on creation, and updates the Key
    when the user edits the widget's contents.
    """

    _connector: Connector[str]

    def setKey(self, key: Key[str]) -> None:
        """
        Binds this widget to the given SunsetSettings Key.

        Args:
            key: The SunsetSettings Key to bind to this widget.
        """

        self._connector = Connector[str](
            key,
            widget_value_getter=self.text,
            widget_value_setter=self.setText,
            widget_value_changed_signal=self.textEdited,
            to_value_converter=lambda text: text,
            from_value_converter=lambda text: text,
        )


class ServerLineEdit(TextLineEdit):
    """
    A TextLineEdit that specifically validates that the input looks like a valid
    server address.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setValidator(
            QRegularExpressionValidator(r"[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*")
        )


class PortLineEdit(LineEdit):
    """
    A LineEdit that specifically validates that the input looks like a valid
    port number.
    """

    _connector: Connector[int]

    def __init__(self) -> None:
        super().__init__()

        self.setFixedWidth(4 * Sizer(self).unitSize())
        self.setValidator(
            QIntValidator(constants.MIN_TCP_PORT, constants.MAX_TCP_PORT)
        )

    def setKey(self, key: Key[int]) -> None:
        """
        Binds this widget to the given SunsetSettings Key.

        Args:
            key: The SunsetSettings Key to bind to this widget.
        """

        self._connector = Connector[int](
            key,
            widget_value_getter=self.text,
            widget_value_setter=self.setText,
            widget_value_changed_signal=self.textEdited,
            to_value_converter=lambda text: int(text) if text.isdigit() else 0,
            from_value_converter=str,
        )


# Labels.


class FixedSizeLabel(QLabel):
    """
    A QLabel with a fixed size.

    Args:
        text: The text to use as this label's contents.
    """

    def __init__(self, text: str) -> None:
        super().__init__(text)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
