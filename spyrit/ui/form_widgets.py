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
Implements custom widgets to be used in configuration forms.
"""


from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QLineEdit, QSizePolicy
from sunset import Key

from spyrit.settings.widget_connector import Connector

# TODO: make this a function of the font size.
_UNIT = 16


class LineEdit(QLineEdit):
    def __init__(self) -> None:
        super().__init__()

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )


class TextLineEdit(LineEdit):
    _connector: Connector[str]

    def setKey(self, key: Key[str]) -> None:
        self._connector = Connector[str](
            key,
            widget_value_getter=self.text,
            widget_value_setter=self.setText,
            widget_value_changed_signal=self.editingFinished,
            to_value_converter=lambda text: text.strip(),
            from_value_converter=lambda text: text,
        )


class PortLineEdit(LineEdit):
    _connector: Connector[int]

    def __init__(self) -> None:
        super().__init__()

        self.setFixedWidth(_UNIT * 4)
        self.setValidator(QIntValidator(1, 65535))

    def setKey(self, key: Key[int]) -> None:
        self._connector = Connector[int](
            key,
            widget_value_getter=self.text,
            widget_value_setter=self.setText,
            widget_value_changed_signal=self.editingFinished,
            to_value_converter=lambda text: int(text),
            from_value_converter=lambda value: str(value),
        )
