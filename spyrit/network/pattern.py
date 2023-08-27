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
Implements the algorithm to match Spyrit patterns to lines of text.
"""


from typing import Iterator

import regex

from spyrit.settings.spyrit_settings import (
    PatternScope,
    SpyritSettings,
    PatternType,
)
from spyrit.ui.format import FormatUpdate

# A match is made of a start position, an end position, and the format to apply
# between the two.
Match = tuple[int, int, FormatUpdate]


def _normalize(text: str) -> str:
    """
    Transform a string so that it can be compared to another string reliably,
    and ignoring unimportant differences. Currently only normalizes the case.
    """
    return text.lower()


def match_fragment_to_text(
    fragment: SpyritSettings.Pattern.Fragment, text: str, start: int
) -> Iterator[Match]:
    """
    Returns the possible matches of the given pattern fragment to the given text
    at the given position. Depending on the fragment's pattern type, the matches
    will be returned in longest to shortest order, or the other way around.
    Currently only matches for pattern type ANYTHING are returned in shortest to
    longest order.
    """

    format_ = fragment.format.get()

    match fragment.type.get():
        case PatternType.ANYTHING:
            end = len(text)
            current = start
            while current <= end:
                yield (start, current, format_)
                current += 1

        case PatternType.EXACT_MATCH:
            pattern_chars = fragment.pattern_text.get()
            end = start + len(pattern_chars)
            if _normalize(text[start:end]) == _normalize(pattern_chars):
                yield (start, end, format_)

        case PatternType.ANY_OF:
            end = start
            text = _normalize(text)
            pattern_chars = set(_normalize(fragment.pattern_text.get()))
            while end < len(text) and text[end] in pattern_chars:
                end += 1
            while end > start:
                yield (start, end, format_)
                end -= 1

        case PatternType.ANY_NOT_IN:
            end = start
            text = _normalize(text)
            pattern_chars = set(_normalize(fragment.pattern_text.get()))
            while end < len(text) and text[end] not in pattern_chars:
                end += 1
            while end > start:
                yield (start, end, format_)
                end -= 1

        case PatternType.REGEX:
            compiled = regex.compile(fragment.pattern_text.get())
            matches: list[int] = []

            for end in range(start, len(text) + 1):
                m = regex.fullmatch(
                    compiled,
                    text,
                    pos=start,
                    endpos=end,
                    partial=True,
                )

                if m is None:
                    break
                if m.partial:
                    continue
                matches.append(end)

            while matches:
                yield (start, matches.pop(), format_)


def match_pattern_to_text(
    pattern: SpyritSettings.Pattern, text: str, start: int
) -> Iterator[tuple[list[Match], int]]:
    """
    Takes a complex pattern made of simple consecutive pattern fragments, and a
    string to be matched to that pattern. Yields possible lists of found matches
    where each match corresponds to one fragment, as well as the position where
    the last match ends. It's up to the caller to decide which of the yielded
    lists of matches makes the most sense in context.
    """

    stack: list[
        tuple[
            int,
            list[Match],
            Iterator[Match] | None,
            list[SpyritSettings.Pattern.Fragment],
        ]
    ] = [(start, [], None, list(pattern.fragments))]

    while stack:
        (
            pos,
            found_matches,
            candidate_matches,
            fragments,
        ) = stack.pop()

        if candidate_matches is None and not fragments:
            if found_matches:
                # We've successfully applied all the pattern fragments to the
                # text and found a list of valid matches. Yield that.
                yield found_matches, pos

            continue

        if candidate_matches is None:
            candidate_matches = match_fragment_to_text(fragments[0], text, pos)
            fragments = fragments[1:]

        try:
            current_match = next(candidate_matches)
        except StopIteration:
            continue

        stack.append(
            (
                pos,
                found_matches,
                candidate_matches,
                fragments,
            )
        )

        match_start, match_end, _ = current_match
        if match_start != match_end:
            found_matches = found_matches + [current_match]

        stack.append(
            (
                match_end,
                found_matches,
                None,
                fragments,
            )
        )


def find_matches(pattern: SpyritSettings.Pattern, text: str) -> list[Match]:
    """
    Matches the given pattern to the given text. Depending on the pattern's
    scope, this may mean matching the pattern to the entire line, or finding the
    pattern wherever it occurs in the line, including if it occurs multiple
    times.
    """

    start = 0
    line_end = len(text)
    done = False
    ret: list[Match] = []

    while not done:
        done = True
        last_start = start

        for matches, last_match_end in match_pattern_to_text(
            pattern, text, start
        ):
            if not matches:
                continue

            match pattern.scope.get():
                case PatternScope.ENTIRE_LINE:
                    # If we must match the whole line, then this match is only
                    # valid if it ends at the line's end.
                    if last_match_end != line_end:
                        continue

                case PatternScope.ANYWHERE_IN_LINE:
                    # If we're matching anywhere in the line, then let's start
                    # over from the end of the current match in case the pattern
                    # occurs later on too.
                    start = last_match_end
                    done = False

            ret.append((last_start, last_match_end, pattern.format.get()))
            ret.extend(matches)
            break

        else:
            # If this point is reached, then no match was found at all. This can
            # mean the end of the process if this is a whole-line match, or this
            # can mean a match may still be found further into the string if
            # this is an anywhere-in-line match.

            start += 1
            if (
                pattern.scope.get() == PatternScope.ANYWHERE_IN_LINE
                and start < line_end
            ):
                done = False

    return ret
