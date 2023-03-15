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
# Pipeline.py
#
# This file defines the class Pipeline, which manages the tokenization of
# a network stream into typed chunks: telnet code, ANSI code, etc...
# It works by assembling a series of Filters.
#


from typing import Callable

from PyQt6.QtCore import QObject
from PyQt6.QtCore import pyqtSignal

from .ChunkData import ChunkType, ChunkT
from .ChunkData import thePromptSweepChunk
from .ChunkData import thePacketStartChunk, thePacketEndChunk

from SingleShotTimer import SingleShotTimer
from CallbackRegistry import CallbackRegistry


class Pipeline(QObject):
    PROMPT_TIMEOUT = 700  # ms

    flushBegin = pyqtSignal()
    flushEnd = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.filters = []
        self.outputBuffer: list[ChunkT] = []
        self.sinks = dict((type_, CallbackRegistry()) for type_ in ChunkType)

        self.notification_registry = {}

        self.prompt_timer = SingleShotTimer(self.sweepPrompt)
        self.prompt_timer.setInterval(self.PROMPT_TIMEOUT)

    def feedBytes(self, packet: bytes, blocksize: int = 2048) -> None:
        # 'packet' is a block of raw, unprocessed bytes. We make a chunk out of
        # it and feed that to the real chunk sink.

        while packet:
            # Splitting the packet into chunks of limited size makes for
            # slightly slower processing overall, but better responsiveness,
            # when processing large packets.
            newbytes, packet = packet[:blocksize], packet[blocksize:]

            self.feedChunk(thePacketStartChunk, autoflush=False)
            self.feedChunk((ChunkType.BYTES, newbytes), autoflush=False)
            self.feedChunk(thePacketEndChunk)

        self.prompt_timer.start()

    def sweepPrompt(self) -> None:
        self.feedChunk(thePromptSweepChunk)

    def feedChunk(self, chunk, autoflush=True):
        if not self.filters:
            return

        self.filters[0].feedChunk(chunk)

        # When the above call returns, the chunk as been fully processed through
        # the chain of filters, and the resulting chunks are waiting in the
        # output bucket. So we can flush it.

        if autoflush:
            self.flushOutputBuffer()

    def appendToOutputBuffer(self, chunk) -> None:
        self.outputBuffer.append(chunk)

    def flushOutputBuffer(self) -> None:
        self.flushBegin.emit()

        for chunk in self.outputBuffer:
            chunk_type, _ = chunk
            self.sinks[chunk_type].triggerAll(chunk)

        self.flushEnd.emit()

        self.outputBuffer = []

    def addFilter(self, filterclass, **kwargs) -> None:
        kwargs.setdefault("context", self)  # Set up context if needed.

        filter = filterclass(**kwargs)

        filter.setSink(self.appendToOutputBuffer)

        if self.filters:
            self.filters[-1].setSink(filter.feedChunk)

        self.filters.append(filter)

    def addSink(
        self,
        callback: Callable[[ChunkType], None],
        types: int = ChunkType.all(),
    ) -> None:
        # 'callback' should be a callable that accepts and handles a chunk.

        for type in ChunkType:
            if type & types:
                self.sinks[type].add(callback)

    def formatForSending(self, data: bytes) -> bytes:
        for filter in reversed(self.filters):
            data = filter.formatForSending(data)

        return data

    def resetInternalState(self) -> None:
        for f in self.filters:
            f.resetInternalState()

    def notify(self, notification: str, *args: str) -> None:
        callbacks = self.notification_registry.get(notification)

        if callbacks:
            callbacks.triggerAll(*args)

    def bindNotificationListener(
        self, notification: str, callback: Callable[..., None]
    ) -> None:
        if notification not in self.notification_registry:
            self.notification_registry[notification] = CallbackRegistry()

        self.notification_registry[notification].add(callback)
