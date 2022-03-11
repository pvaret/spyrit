# Copyright (c) 2007-2021 Pascal Varet <p.varet@gmail.com>
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
# Matches.py
#
# The SmartMatch class handles pattern matching for triggers, highlighs and
# such, with a convenient interface for the user. It provides facilities to
# let the user enter their patterns in the following form:
#   '[player] pages: [message]'
# ... and generates the corresponding regex.
#
# The RegexMatch provides the same interface but uses actual regexes.
#


import abc
import re


class MatchCreationError(Exception):
    pass


# TODO: Add the proper methods.
class BaseMatch(abc.ABC):
    pass


class RegexMatch(BaseMatch):

    matchtype = "regex"

    def __init__(self, pattern=""):

        self.pattern = pattern
        self.regex = None
        self.error = None
        self.name = None

        if pattern:
            self.setPattern(pattern)

    def compileRegex(self, regex):

        self.error = None

        try:
            self.regex = re.compile(regex)

        except re.error as e:
            self.regex = re.compile("$ ^")  # Clever regex that never matches.
            self.error = "%s" % e

    def setPattern(self, pattern):

        self.pattern = pattern
        regex_pattern = self.patternToRegex(pattern)

        self.compileRegex(regex_pattern)

    def patternToRegex(self, pattern):

        # This is a regex match, so the regex IS the pattern.
        return pattern

    def matches(self, string):

        if not self.regex:
            return None

        return list(self.regex.finditer(string))

    def matchtokens(self):

        if not self.regex:
            return None

        tokens = sorted([(v, k) for k, v in self.regex.groupindex.items()])

        return [tok[1] for tok in tokens]

    def __repr__(self):

        return self.matchtype + ":" + self.pattern

    def toString(self):

        return "'" + self.pattern + "' (regex)"

    def __unicode__(self):

        raise NotImplementedError("This method doesn't exist anymore!")


# This convoluted regex parses out either words (\w+) between square brackets
# or asterisks, if they aren't preceded by an odd number of backslashes.


TOKEN = r" *\w+ *"  # Non-null word with optional surrounding space.

BS = r"\\"  # Backslash
ASTER = r"\*"  # Asterisk
PERCENT = r"\%"  # Percent sign

LSB = r"\["  # Left square bracket
RSB = r"\]"  # Right square bracket

PARSER = re.compile(
    "(?:"  # Either...
    + "^"  # Beginning of string
    + "|"  # Or...
    + "[^"
    + BS
    + "]"  # Any one character other than a backslash
    + ")"  # Then...
    + "(?:"
    + BS * 2
    + ")"
    + "*"  # An even number of backslashes
    + "("  # And then, group-match either...
    + PERCENT  # A percent sign
    + "|"  # Or...
    + ASTER  # An asterisk
    + "|"  # Or...
    + LSB
    + TOKEN  # Something of the form [token].
    + RSB
    + ")"
)


class SmartMatch(RegexMatch):

    matchtype = "smart"

    def patternToRegex(self, pattern):

        regex = []
        tokens = set()

        while pattern:

            m = PARSER.search(pattern)

            if not m:

                regex.append(self.unescape_then_escape(pattern))
                break

            start, end = m.span(1)
            before, pattern = pattern[:start], pattern[end:]

            if before:
                regex.append(self.unescape_then_escape(before))

            token = m.group(1).lower().lstrip("[ ").rstrip(" ]")

            if token == "%":
                regex.append(".*?")  # Match anything, non-greedy

            elif token == "*":
                regex.append(".*")  # Match anything, greedy

            elif token in tokens:  # Token which is already known
                regex.append("(?P=%s)" % token)  # Insert backreference.

            else:  # New token
                tokens.add(token)

                # Named match for any non-null string, non-greedy.
                regex.append(r"(?P<%s>.+?)" % token)

        return "".join(regex)

    def unescape_then_escape(self, string):

        # Unescape string according to the SmartMatch parser's rules, then
        # re-escape according to the rules of Python's re module.

        replacements = (
            (r"\[", "["),
            (r"\]", "]"),
            (r"\*", "*"),
            ("\\" * 2, "\\"),
        )

        for from_, to in replacements:
            string = string.replace(from_, to)

        return re.escape(string)

    def toString(self):

        return "'" + self.pattern + "'"

    def __unicode__(self):

        raise NotImplementedError("This method doesn't exist anymore!")


def load_match_by_type(pattern, type="smart"):

    type = type.lower().strip()

    TYPES = {
        "smart": SmartMatch,
        "regex": RegexMatch,
    }

    klass = TYPES.get(type)

    if not klass:
        raise MatchCreationError("Unknown match type: %s" % type)

    match = klass(pattern)

    if match.error:
        raise MatchCreationError("Match pattern syntax error: %s" % match.error)

    return match
