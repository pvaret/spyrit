# Copyright (c) 2007-2022 Pascal Varet <p.varet@gmail.com>
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

#
# Serializers.py
#
# Serializers are small classes that know how to serialize and deserialize
# settings values to and from strings, and can also compute a default value
# from the default string.
#


"""
:doctest:

>>> from settings.Serializers import *

"""

import re
import abc

from typing import Any
from typing import Dict
from typing import Generic
from typing import Iterable
from typing import List as ListType
from typing import Optional
from typing import TypeVar

from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QKeySequence

from Globals import FORMAT_PROPERTIES
from Matches import BaseMatch
from Matches import MatchCreationError
from Matches import RegexMatch
from Matches import SmartMatch
from Utilities import BS
from Utilities import quote
from Utilities import unquote


def split(
    string: str, sep: str = ",", esc: str = BS, quotes: str = '"'
) -> Iterable[str]:
    r"""
    Splits a string along the given single-character separator (by default, a
    comma).

    Only split if the separator is not escaped or inside a quoted section.

    >>> print( len( list( split( ' "A", "B" ' ) ) ) )
    2

    >>> print( len( list( split( r' "A"\, "B" ') ) ) )
    1

    >>> print( len( list( split( ' "A, B" ') ) ) )
    1

    """

    last_pos = 0
    in_escape = False
    current_quote = None

    for pos, c in enumerate(string):

        if in_escape:
            # Current character is escaped. Move on.
            in_escape = False
            continue

        if c == esc:
            # Next character will be escaped.
            in_escape = True
            continue

        if current_quote is None:
            # Not in a quoted section.

            if c == sep:
                # Found an unquoted separator! Split.
                yield string[last_pos:pos]
                last_pos = pos + 1  # Skip the separator itself.

            elif c in quotes:
                # This is the start of a quoted section.
                current_quote = c

            continue

        # In a quoted section. Do nothing until the section ends.

        if c == current_quote:
            # This is the end of the quoted section.
            current_quote = None

    if last_pos < len(string):
        yield string[last_pos:]


Value = TypeVar("Value")


class BaseSerializer(abc.ABC, Generic[Value]):
    @abc.abstractmethod
    def serialize(self, value: Value) -> str:
        pass

    @abc.abstractmethod
    def deserialize(self, string: str) -> Optional[Value]:
        pass

    # TODO: Not very clean. Find a way to make it cleaner? Or maybe remove it
    # entirely?
    def deserializeDefault(self, default):

        if isinstance(default, str):
            return self.deserialize(default)

        return default


class Int(BaseSerializer[int]):
    def deserialize(self, string: str) -> int:

        try:
            return int(string)

        except ValueError:
            return 0

    def serialize(self, value: int) -> str:

        assert isinstance(value, int)
        return "%d" % value


class Str(BaseSerializer[str]):
    def deserialize(self, string: str) -> Optional[str]:

        # The empty string deserializes to None.
        if not string:
            return None

        return unquote(string)

    def serialize(self, value: str) -> str:

        # None serializes to the empty string.
        if value is None:
            return ""

        return quote(value)


class Bool(BaseSerializer[bool]):
    def deserialize(self, string: str) -> bool:

        return string.strip().lower() in ("1", "y", "yes", "on", "true")

    def serialize(self, value: bool) -> str:

        return "True" if value else "False"


class List(BaseSerializer[ListType[Value]]):

    SEP = ","
    QUOTE = '"'

    def __init__(self, sub_serializer: BaseSerializer[Value]):

        self.sub_serializer = sub_serializer
        super().__init__()

    def serialize(self, value: ListType[Value]) -> str:

        result = []

        for item in value:

            s = self.sub_serializer.serialize(item)

            result.append(
                s if self.SEP not in s else self.QUOTE + s + self.QUOTE
            )

        return self.SEP.join(result)

    def deserialize(self, string: str) -> ListType[Value]:

        result = []

        for item in split(string, sep=self.SEP, quotes=self.QUOTE):

            # Because the string serializer uses quote(), which escapes the "
            # character, the following is guaranteed to only be true when we've
            # added the quotes ourselves in serialize().

            if item[0] == self.QUOTE and item[-1] == self.QUOTE:
                item = item[1:-1]

            result.append(self.sub_serializer.deserialize(item))

        return result


# TODO: Make format properties an actual type.
FormatType = Dict[Any, Any]


class Format(BaseSerializer[FormatType]):

    # FORMAT describes the formatting for a given piece of text: color,
    # italic, underlined...
    # Its string serialization is a semicolon-separated list of tokens and
    # looks like this: "color:#ffffff; italic; bold".
    # Its deserialized form is a dictionary.
    # We also store format-related constants on it.

    def serialize(self, value: FormatType) -> str:

        props: ListType[str] = []

        for k, v in value.items():

            if k == FORMAT_PROPERTIES.COLOR:
                props.insert(0, "color: %s" % v)

            elif k == FORMAT_PROPERTIES.ITALIC:
                props.append("italic")

            elif k == FORMAT_PROPERTIES.BOLD:
                props.append("bold")

            elif k == FORMAT_PROPERTIES.UNDERLINE:
                props.append("underlined")

        return " ; ".join(props)

    def deserialize(self, string: str) -> FormatType:

        d: FormatType = {}

        for item in string.split(";"):

            item = item.strip().lower()

            if ":" in item and item.startswith("c"):

                item, string = item.split(":", 1)
                item = item.strip()
                string = string.strip()
                d[FORMAT_PROPERTIES.COLOR] = string

            elif item.startswith("i"):
                d[FORMAT_PROPERTIES.ITALIC] = True

            elif item.startswith("b"):
                d[FORMAT_PROPERTIES.BOLD] = True

            elif item.startswith("u"):
                d[FORMAT_PROPERTIES.UNDERLINE] = True

        return d


class KeySequence(BaseSerializer[QKeySequence]):
    def deserializeDefault(self, default: str) -> Optional[QKeySequence]:

        # QKeySequence.fromString uses PortableText by default, and so do our
        # defaults:
        return QKeySequence.fromString(default) if default is not None else None

    def serialize(self, value: Optional[QKeySequence]) -> str:

        if value is not None:
            return value.toString(QKeySequence.NativeText)

        return ""

    def deserialize(self, string: str) -> QKeySequence:

        return QKeySequence.fromString(string, QKeySequence.NativeText)


class Size(BaseSerializer[QSize]):

    SEP = r"[x,]"

    def serialize(self, value: QSize) -> str:

        return "%dx%d" % (value.width(), value.height())

    def deserialize(self, string: str) -> QSize:

        string = string.lower().strip()

        if re.search(self.SEP, string):

            w, h = re.split(self.SEP, string, 1)

            try:
                return QSize(int(w), int(h))

            except TypeError:
                pass

        return QSize()


class Point(BaseSerializer[QPoint]):
    def serialize(self, value: QPoint) -> str:

        return "%dx%d" % (value.x(), value.y())

    def deserialize(self, string: str) -> QPoint:

        string = string.lower().strip()

        if "x" in string:

            x, y = string.split("x", 1)

            try:
                return QPoint(int(x), int(y))

            except TypeError:
                pass

        return QPoint()


class Pattern(BaseSerializer[BaseMatch]):
    def serialize(self, value: BaseMatch) -> str:

        # TODO: Not great. Replace the repr() with a proper serialization
        # function.
        return quote(repr(value))

    def deserialize(self, string: str) -> Optional[BaseMatch]:

        string = unquote(string)

        if not string:
            return None

        if ":" in string:

            prefix, suffix = string.split(":", 1)
            prefix = prefix.lower()

            for class_ in (RegexMatch, SmartMatch):

                if prefix == class_.matchtype:
                    string = suffix
                    break

        else:
            class_ = SmartMatch

        try:
            return class_(string)  # type: ignore - class_ is in fact set.

        except MatchCreationError:
            return None
