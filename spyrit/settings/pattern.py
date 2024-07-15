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
import logging
import re

from typing import Any, Iterable

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


def _normalize(string: str) -> str:
    return string.lower()


def _fragment_identifier(fragment: Any) -> str:
    return f"f{id(fragment)}"


def _named_group(name: str, pattern: str) -> str:
    return rf"(?P<{name}>" + pattern + r")" if pattern else ""


def _fragment_to_pattern(fragment: "Pattern.Fragment") -> str:
    """
    Computes a regex pattern for the given fragment.
    """

    pattern = fragment.pattern_text.get()
    name = _fragment_identifier(fragment)

    match fragment.type.get():
        case PatternType.ANYTHING:
            # Note that this is a non-greedy match.
            return _named_group(name, r".*?")

        case PatternType.EXACT_MATCH:
            return _named_group(name, re.escape(_normalize(pattern)))

        case PatternType.ANY_OF:
            pattern = re.escape("".join(sorted(set(_normalize(pattern)))))
            return _named_group(name, r"[" + pattern + r"]+")

        case PatternType.ANY_NOT_IN:
            pattern = re.escape("".join(sorted(set(_normalize(pattern)))))
            return _named_group(name, r"[^" + pattern + r"]+")

        case PatternType.REGEX:
            return _named_group(name, pattern)


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

    _re: re.Pattern[str]

    def __post_init__(self) -> None:
        super().__post_init__()

        self.fragments.onUpdateCall(self._compile)
        self.onLoadedCall(self._compile)
        self._compile()

    def _compile(self, _: Any = None) -> None:
        pattern = ""

        for fragment in self.fragments:
            fragment_pattern = _fragment_to_pattern(fragment)
            if not fragment:
                continue

            try:
                re.compile(fragment_pattern)
            except re.error:
                logging.warning(
                    f"Failed to compile pattern fragment: {fragment}"
                )
                continue

            pattern += fragment_pattern

        if not pattern:
            pattern = r"$  ^"  # Never matches anything.

        self._re = re.compile(pattern, flags=re.IGNORECASE)

    def matches(self, line: str) -> list[tuple[int, int, FormatUpdate]]:
        """
        Matches this compound pattern to the given line.

        Args:
            line: A line of text to be matched against this pattern.

        Returns:
            A list of the start position, end position, and applicable format
            for each match of this pattern and its individual fragments.
        """

        ret: list[tuple[int, int, FormatUpdate]] = []
        matches: Iterable[re.Match[str]] = []

        match self.scope.get():
            case PatternScope.ENTIRE_LINE:
                m = self._re.fullmatch(line)
                matches = [m] if m is not None else []

            case PatternScope.ANYWHERE_IN_LINE:
                matches = self._re.finditer(line)

        for m in matches:
            if (end := m.end()) > (start := m.start()):
                ret.append((start, end, self.format.get()))

            for fragment in self.fragments:
                name = _fragment_identifier(fragment)
                if name not in m.groupdict():
                    continue
                if (end := m.end(name)) > (start := m.start(name)):
                    ret.append((start, end, fragment.format.get()))

        return ret
