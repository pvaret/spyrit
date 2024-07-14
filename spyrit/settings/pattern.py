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
Provides a compound setting type for patterns used to match and format lines of
text from game worlds.
"""

import enum

from sunset import Bunch, Key, List

from spyrit.settings import serializers
from spyrit.ui.format import FormatUpdate


class PatternType(enum.Enum):
    # An ANYTHING pattern matches any characters, as *few* as possible,
    # including none at all.
    ANYTHING = enum.auto()

    # An EXACT_MATCH pattern matches the pattern string exactly, after
    # normalisation.
    EXACT_MATCH = enum.auto()

    # An ANY_OF pattern matches any of the characters in the pattern string in
    # any order, as many as possible.
    ANY_OF = enum.auto()

    # An ANY_NOT_IN pattern matches any characters not in the pattern string, as
    # many as possible.
    ANY_NOT_IN = enum.auto()

    # A REGEX pattern uses the pattern string as a regex, matching as many
    # characters as possible.
    REGEX = enum.auto()


class PatternScope(enum.Enum):
    # A pattern with this scope will match if and only it matches the entire
    # line.
    ENTIRE_LINE = enum.auto()

    # Every subset of a line of text that matches a pattern with this scope will
    # be considered an independent match.
    ANYWHERE_IN_LINE = enum.auto()


class Pattern(Bunch):
    """
    Records a compound user-defined pattern, to be matched against game text
    so e.g. custom formatting can be applied.
    """

    class Fragment(Bunch):
        # The type of pattern stored in this fragment.
        type: Key[PatternType] = Key(default=PatternType.ANYTHING)

        # The text of the pattern in this fragment. Unused if the pattern
        # type is ANYTHING.
        pattern_text: Key[str] = Key(default="")

        # Which format to apply to the given fragment.
        format: Key[FormatUpdate] = Key(
            default=FormatUpdate(), serializer=serializers.FormatSerializer
        )

    # Whether to match entire lines, or anywhere in lines.
    scope: Key[PatternScope] = Key(default=PatternScope.ENTIRE_LINE)

    # The sub-pattern fragments that make up this pattern.
    fragments: List[Fragment] = List(Fragment())

    # The format to apply to the fragment matches that don't have their own
    # specific format.
    format: Key[FormatUpdate] = Key(
        default=FormatUpdate(), serializer=serializers.FormatSerializer
    )
