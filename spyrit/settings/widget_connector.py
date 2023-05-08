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
Implements a helper that automatically updates values between a widget and a
SunsetSettings Key.
"""


from typing import Callable, Generic, TypeVar

from PySide6.QtCore import SignalInstance, Slot
from sunset import Key


_T = TypeVar("_T", bound=int | str)


class Connector(Generic[_T]):
    """
    Generic helper that takes a SunsetSettings Key and setters / getters /
    converters for a Qt widget, and binds the widget to the Key.
    """

    _key: Key[_T]
    _widget_value_getter: Callable[[], str]
    _widget_value_setter: Callable[[str], None]
    _to_value_converter: Callable[[str], _T]
    _from_value_converter: Callable[[_T], str]

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        key: Key[_T],
        widget_value_getter: Callable[[], str],
        widget_value_setter: Callable[[str], None],
        widget_value_changed_signal: SignalInstance,
        to_value_converter: Callable[[str], _T],
        from_value_converter: Callable[[_T], str],
    ) -> None:
        self._key = key
        self._widget_value_getter = widget_value_getter
        self._widget_value_setter = widget_value_setter
        self._to_value_converter = to_value_converter
        self._from_value_converter = from_value_converter

        # When the widget signals that it's value changed, update the Key.

        widget_value_changed_signal.connect(self._updateKeyValueFromWidget)

        # When they Key's value changes, update the widget.

        key.onUpdateCall(self._updateWidgetValueFromKey)
        self._updateWidgetValueFromKey(key)

    @Slot()
    def _updateKeyValueFromWidget(self) -> None:
        text_value = self._widget_value_getter()
        value = self._to_value_converter(text_value)

        if value != self._key.get():
            self._key.set(value)

    def _updateWidgetValueFromKey(self, key: Key[_T]) -> None:
        if not key.isSet():
            self._widget_value_setter("")
            return

        text_value = self._from_value_converter(key.get())

        if text_value != self._widget_value_getter():
            self._widget_value_setter(text_value)
