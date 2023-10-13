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
Implements container classes for typed fragments of network data.
"""

import enum

from abc import ABC
from typing import Any, Sequence

from spyrit.network.connection import Status
from spyrit.ui.format import FormatUpdate


class Fragment(ABC):
    """
    Base class for all Fragments.

    A Fragment is a bit of typed, processed data coming from the game. Fragments
    pass through Processor that potentially further transform them, so they can
    be ingested by interested parties down the road -- most importantly, the UI
    that displays text from the game.
    """

    __match_args__: Sequence[str]

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        args: list[str] = []

        for argname in self.__match_args__:
            args.append(argname + "=" + repr(getattr(self, argname, "?")))

        return f"{classname}({','.join(args)})"


class FragmentList(list[Fragment]):
    # Work around an issue where Signals and Slots cannot use a typed list as
    # their type. So instead of list[Fragment], we use this FragmentList in the
    # Signal and Slot declarations.

    pass


class ByteFragment(Fragment):
    """
    A Fragment that represents raw binary data read from the game's connection.

    Args:
        data: A piece of raw data from the game.
    """

    __match_args__ = ("data",)

    data: bytes

    def __init__(self, data: bytes) -> None:
        self.data = data

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ByteFragment) and self.data == other.data


class TextFragment(Fragment):
    """
    A Fragment that contains decoded text.

    Args:
        text: A string of text decoded from the game.
    """

    __match_args__ = ("text",)

    text: str

    def __init__(self, text: str) -> None:
        self.text = text

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, TextFragment) and self.text == other.text


class ANSIFragment(Fragment):
    """
    A Fragment that contains ANSI formatting instructions.

    Args:
        format_update: The description of a formatting instruction parsed from
            ANSI.
    """

    __match_args__ = ("format_update",)

    format_update: FormatUpdate

    def __init__(self, format_update: FormatUpdate) -> None:
        self.format_update = format_update

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, ANSIFragment)
            and self.format_update == other.format_update
        )


class FlowControlCode(enum.Enum):
    """
    A flow control code, i.e. a non-printable character that still needs to be
    accounted for when rendering text.
    """

    CR = enum.auto()
    LF = enum.auto()


class FlowControlFragment(Fragment):
    """
    A Fragment that contains a text flow control code.

    Args:
        code: A flow control code, i.e. (broadly) a non-printable character that
           still affects how the text is rendered.
    """

    __match_args__ = ("code",)

    code: FlowControlCode

    def __init__(self, code: FlowControlCode) -> None:
        self.code = code

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, FlowControlFragment) and self.code == other.code
        )


class NetworkFragment(Fragment):
    """
    A Fragment that contains a network status change event.

    Args:
        event: A network status event.

        text: A text associated with the event. Optional.
    """

    __match_args__ = ("event", "text")

    event: Status
    text: str

    def __init__(self, event: Status, text: str = "") -> None:
        self.event = event
        self.text = text

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NetworkFragment):
            return False

        return self.event == other.event and self.text == other.text


class MatchBoundary(enum.Enum):
    """
    A marker that indicates the start or respectively the end of a found match.
    """

    START = enum.auto()
    END = enum.auto()


class PatternMatchFragment(Fragment):
    """
    A Fragment that marks either the start or the end of the match for a
    user-provided pattern, and contains the format to apply to the matched text.

    Meant to be used in pairs surrounding the matched text.

    Args:
        format_: The format to apply to the matched text.

        boundary: An indication of whether this fragment marks the beginning or
            the end of the matched text.
    """

    __match_args__ = ("format", "boundary")

    format: FormatUpdate
    boundary: MatchBoundary

    def __init__(self, format_: FormatUpdate, boundary: MatchBoundary) -> None:
        self.format = format_
        self.boundary = boundary

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PatternMatchFragment):
            return False

        return self.format == other.format and self.boundary == other.boundary


class DummyFragment(Fragment):
    """
    A Fragment that can contain any value and is used for testing.

    Args:
        value: Anything.
    """

    __match_args__ = ("value",)

    value: Any

    def __init__(self, value: Any) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DummyFragment):
            return False

        return self.value == other.value
