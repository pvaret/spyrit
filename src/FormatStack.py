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
# FormatStack.py
#
# This file implements the FormatStack helper class, which can absorb
# formatting information from a variety of chunk sources, computes the
# resulting format, and feed the information to a formatter object that knows
# how to apply it.
#


from collections import defaultdict

# TODO: Remove custom OrderedDict, use that from collections. (Requires a
# replacement for the .lastvalue() method.)
from OrderedDict import OrderedDict

from pipeline.ChunkData import ChunkType


BASE = 0
ANSI = 1


class FormatStack:
    def __init__(self, formatter):
        self.formatter = formatter
        self.stacks = defaultdict(OrderedDict)

    def processChunk(self, chunk):
        chunk_type, payload = chunk

        if chunk_type == ChunkType.ANSI:
            self._applyFormat(ANSI, payload)

        elif chunk_type == ChunkType.HIGHLIGHT:
            id, format = payload
            self._applyFormat(id, format)

    def setBaseFormat(self, format):
        actual_format = dict((k, None) for k in self.stacks)
        actual_format.update(format)

        self._applyFormat(BASE, actual_format)

    def _applyFormat(self, id, format):
        if not format:
            self._clearFormat(id)
            return

        for property, value in format.items():
            stack = self.stacks[property]

            old_end_value = stack.lastvalue()

            if value:
                if id not in stack and id in (BASE, ANSI):
                    stack.insert(id, id, value)

                else:
                    stack[id] = value

            else:
                if id in stack:
                    del stack[id]

                else:
                    continue

            new_end_value = stack.lastvalue()

            if new_end_value == old_end_value:
                continue

            if new_end_value:
                self.formatter.setProperty(property, new_end_value)

            else:
                self.formatter.clearProperty(property)

    def _clearFormat(self, id):
        for property, stack in self.stacks.items():
            if id in stack:
                old_end_value = stack.lastvalue()
                del stack[id]
                new_end_value = stack.lastvalue()

                if new_end_value == old_end_value:
                    continue

                if new_end_value:
                    self.formatter.setProperty(property, new_end_value)

                else:
                    self.formatter.clearProperty(property)
