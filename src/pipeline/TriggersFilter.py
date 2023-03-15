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
# TriggersFilter.py
#
# This file holds the TriggersFilter class, which bufferizes the incoming
# chunks until a line is complete, and then matches that line with the
# world's registered match patterns and triggers the corresponding action
# as needed.
#


from typing import Iterable

from .BaseFilter import BaseFilter

from .ChunkData import ChunkT
from .ChunkData import ChunkType
from .ChunkData import FlowControl

from .Pipeline import Pipeline


class TriggersFilter(BaseFilter):
    def __init__(self, context: Pipeline, manager=None):
        self.buffer: list[ChunkT] = []
        self.setManager(manager)

        super().__init__(context)

    def setManager(self, manager):
        self.manager = manager

    def resetInternalState(self):
        self.buffer.clear()
        super().resetInternalState()

    def processChunk(self, chunk: ChunkT) -> Iterable[ChunkT]:
        if self.manager:
            yield from self.doProcessChunk(chunk)
        else:
            yield from self.noOp(chunk)

    def noOp(self, chunk):
        yield chunk

    def doProcessChunk(self, chunk):
        self.buffer.append(chunk)

        chunk_type, _ = chunk

        if chunk_type in (
            ChunkType.NETWORK,
            ChunkType.PROMPTSWEEP,
        ) or chunk == (
            ChunkType.FLOWCONTROL,
            FlowControl.LINEFEED,
        ):
            line = "".join(
                chunk[1] for chunk in self.buffer if chunk[0] == ChunkType.TEXT
            )

            if line:
                self.manager.performMatchingActions(line, self.buffer)

            for chunk in self.buffer:
                yield chunk

            self.buffer = []
