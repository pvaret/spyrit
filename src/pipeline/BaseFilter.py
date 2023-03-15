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
# BaseFilter.py
#
# This file holds the base class for pipeline filters, which holds the core
# logic for processing chunks of hopefully parsable data.
#


from typing import Callable, Iterable, Optional

from .ChunkData import ChunkType, ChunkT
from .ChunkData import concat_chunks
from .ChunkData import ChunkTypeMismatch
from .Pipeline import Pipeline


class BaseFilter:
    # This class attribute lists the chunk types that this filter will process.
    # Those unlisted will be passed down the filter chain untouched.

    relevant_types: int = ChunkType.all()

    def __init__(self, context: Pipeline):
        self.sink: Callable[[ChunkT], None] = lambda _: None
        self.context: Pipeline = context
        self.postponedChunk: Optional[ChunkT] = None

        self.resetInternalState()

    def setSink(self, sink: Callable[[ChunkT], None]) -> None:
        self.sink = sink

    def postpone(self, chunk: ChunkT) -> None:
        if self.postponedChunk:
            raise Exception("Duplicate postponed chunk!")

        else:
            self.postponedChunk = chunk

    def processChunk(self, chunk: ChunkT) -> Iterable[ChunkT]:
        # This is the default implementation, which does nothing.
        # Override this to implement your filter.
        # Note that this must be a generator or return a list.

        yield chunk

    def resetInternalState(self) -> None:
        # Initialize the filter at the beginning of a connection (or when
        # reconnecting). For instance the Telnet filter would drop all
        # negociated options.
        # Override this when implementing your filter if your filter uses any
        # internal data.

        self.postponedChunk = None

    def concatPostponed(self, chunk: ChunkT):
        if not self.postponedChunk:
            return chunk

        chunk_type, _ = chunk

        if chunk_type == ChunkType.PACKETBOUND:
            # This chunk type is a special case, and is never merged with other
            # chunks.
            return chunk

        # If there was some bit of chunk that we postponed earlier...
        postponed = self.postponedChunk
        self.postponedChunk = None
        # We retrieve it...

        try:
            # And try to merge it with the new chunk.
            chunk = concat_chunks(postponed, chunk)

        except ChunkTypeMismatch:
            # If they're incompatible, it means the postponed chunk was really
            # complete, so we send it downstream.
            self.sink(postponed)

        return chunk

    def feedChunk(self, chunk: ChunkT):
        chunk_type, _ = chunk

        if chunk_type & self.relevant_types:
            if self.postponedChunk:
                chunk = self.concatPostponed(chunk)

            # At this point, the postponed chunk has either been merged with
            # the new one, or been sent downstream. At any rate, it's been dealt
            # with, and self.postponedChunk is empty.
            # This mean that the postponed chunk should ALWAYS have been cleared
            # when processChunk() is called. If not, there's something shifty
            # going on...

            for chunk in self.processChunk(chunk):
                self.sink(chunk)

        else:
            self.sink(chunk)

    def formatForSending(self, data: bytes) -> bytes:
        # Reimplement this function if the filter inherently requires the data
        # sent to the world to be modified. I.e., the telnet filter would escape
        # occurences of the IAC in the data.

        return data

    # TODO: Check if this is used anywhere. Else, delete.
    def notify(self, notification: str, *args: str) -> None:
        if not self.context:
            return

        self.context.notify(notification, *args)

    def bindNotificationListener(
        self, notification: str, callback: Callable[..., None]
    ):
        if not self.context:
            return

        self.context.bindNotificationListener(notification, callback)
