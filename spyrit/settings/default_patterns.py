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
Provides patterns to be used by default for all worlds.
"""


from spyrit import constants
from spyrit.regex_helpers import any_of, blocks_with_separator, optional
from spyrit.settings.pattern import Pattern, PatternScope, PatternType
from spyrit.ui.colors import ANSIColor, ANSIColorCodes
from spyrit.ui.format import FormatUpdate


_HOSTNAME_CHAR = r"-_a-zA-Z0-9"
_URL_PATH_CHARS = r"-a-zA-Z0-9~#/_=:)};"
_URL_PATH_INTERNAL_CHARS = _URL_PATH_CHARS + r"&({.!?"

# TODO: Add support for:
#   - IPv6 as the hostname.
#   - username/password.
URL_MATCH_RE: str = (
    # scheme
    any_of(
        r"https?://",
        r"www\.",
    )
    # hostname
    + blocks_with_separator(rf"[{_HOSTNAME_CHAR}]+", sep=r"\.")
    # port
    + optional(r":\d+")
    # path
    + optional(
        r"/"
        + optional(rf"[{_URL_PATH_INTERNAL_CHARS}]*" + rf"[{_URL_PATH_CHARS}]")
    )
)


def get_default_patterns() -> list[Pattern]:
    ret: list[Pattern] = []

    # Detect URLs and make them clickable.

    url_pattern = Pattern()
    url_pattern.format.set(
        FormatUpdate(
            italic=True,
            underline=True,
            underline_color=ANSIColor(ANSIColorCodes.Blue),
            href=constants.MATCH_PLACEHOLDER,
        )
    )
    url_pattern.scope.set(PatternScope.ANYWHERE_IN_LINE)
    url_match = url_pattern.fragments.appendOne()
    url_match.type.set(PatternType.REGEX)
    url_match.pattern_text.set(URL_MATCH_RE)

    ret.append(url_pattern)

    return ret
