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
Implements container classes for typed fragments of network data.
"""

import enum

from abc import ABC
from typing import Any

from spyrit.network.connection import Status
from spyrit.ui.format import CharFormat


class Fragment(ABC):
    ...


class FragmentList(list[Fragment]):
    # Work around an issue where Signals and Slots cannot use a typed list as
    # their type. So instead of list[Fragment], we use this FragmentList in the
    # Signal and Slot declarations.

    pass


class ByteFragment(Fragment):
    __match_args__ = ("data",)

    data: bytes

    def __init__(self, data: bytes) -> None:
        self.data = data

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ByteFragment) and self.data == other.data


class TextFragment(Fragment):
    __match_args__ = ("text",)

    text: str

    def __init__(self, text: str) -> None:
        self.text = text

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, TextFragment) and self.text == other.text


class ANSIFragment(Fragment):
    __match_args__ = ("format",)

    format: CharFormat

    # pylint: disable-next=redefined-builtin
    def __init__(self, format: CharFormat) -> None:
        self.format = format

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ANSIFragment) and self.format == other.format


class FlowControlCode(enum.Enum):
    CR = enum.auto()
    LF = enum.auto()


class FlowControlFragment(Fragment):
    __match_args__ = ("code",)

    code: FlowControlCode

    def __init__(self, code: FlowControlCode) -> None:
        self.code = code

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, FlowControlFragment) and self.code == other.code
        )


class NetworkFragment(Fragment):
    __match_args__ = ("event", "text")

    event: Status
    text: str

    def __init__(self, event: Status, text: str) -> None:
        self.event = event
        self.text = text

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, NetworkFragment) and self.event == other.event
