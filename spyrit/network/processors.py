# Copyright (c) 2007-2023 Pascal Varet <p.varet@gmail.com>
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

"""
Implements classes that transform raw byte data from the network into something
that makes semantic sense and can be fed into e.g. a text display widget.
"""


import codecs
import logging

from typing import Iterable, Iterator

from PySide6.QtCore import QObject, Signal, Slot
from sunset import Key

from spyrit.network.connection import Connection, Status
from spyrit.network.fragments import (
    ByteFragment,
    Fragment,
    FragmentList,
    NetworkFragment,
    TextFragment,
)
from spyrit.settings.spyrit_settings import Encoding


class BaseProcessor(QObject):
    """
    Processors take fragments of network data, potentially already processed,
    and process them further by parsing / decoding / filtering them.

    This class implements the logic common to all processors.
    """

    # This signal fires when a processor has some output ready.

    fragmentsReady = Signal(FragmentList)  # noqa: N815

    _output_buffer: list[Fragment]

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._output_buffer = []

    def feed(self, fragments: Iterable[Fragment]) -> None:
        """
        Feed Fragments into this processor for processing.
        """

        for fragment in fragments:
            self._output_buffer.extend(self.processFragment(fragment))

        self._maybeSignalOutputReady()

    def processFragment(self, fragment: Fragment) -> Iterator[Fragment]:
        """
        Default implementation. Just passes Fragments along unprocessed.
        """

        yield fragment

    def _maybeSignalOutputReady(self) -> None:
        if self._output_buffer:
            self.fragmentsReady.emit(self._output_buffer)
            self._output_buffer.clear()


class UnicodeProcessor(BaseProcessor):
    """
    This processor turns byte fragments into proper text, using the configured
    encoding.
    """

    _encoding_key: Key[Encoding]
    _decoder: codecs.IncrementalDecoder

    def __init__(
        self, encoding_key: Key[Encoding], parent: QObject | None = None
    ) -> None:
        super().__init__(parent)

        self._encoding_key = encoding_key
        self._encoding_key.onValueChangeCall(self._setUpDecoder)
        self._setUpDecoder(encoding_key.get())

    def _setUpDecoder(self, encoding: Encoding) -> None:
        try:
            codec = codecs.lookup(encoding.value)
        except LookupError:
            logging.error(
                "Couldn't find decoder for encoding '%s'; reverting to default"
                " encoding 'ASCII'.",
                encoding.value,
            )
            codec = codecs.lookup("ascii")

        # Note: this discards the current internal state of the encoder. Since
        # that state probably doesn't make sense to the new encoder, that's
        # acceptable.

        self._decoder = codec.incrementaldecoder(errors="ignore")

    def processFragment(self, fragment: Fragment) -> Iterator[Fragment]:
        match fragment:
            case ByteFragment(data):
                text = self._decoder.decode(data)
                if text:
                    # TODO: filter out non-printable characters?

                    yield TextFragment(text)

            case _:
                yield fragment


class ChainProcessor(BaseProcessor):
    """
    This processor doesn't do any processing of its own, but it assembles its
    given processors into a chain where the fragments produced by one processor
    are fed into the next.
    """

    _entry_processor: BaseProcessor
    _exit_processor: BaseProcessor

    def __init__(
        self,
        processor: BaseProcessor,
        *processors: BaseProcessor,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        processor.setParent(self)
        self._entry_processor = processor

        current_processor = processor

        for next_processor in processors:
            next_processor.setParent(self)
            current_processor.fragmentsReady.connect(next_processor.feed)
            current_processor = next_processor

        self._exit_processor = current_processor
        self._exit_processor.fragmentsReady.connect(self.fragmentsReady)

    def feed(self, fragments: Iterable[Fragment]) -> None:
        self._entry_processor.feed(fragments)


def bind_processor_to_connection(
    processor: BaseProcessor, connection: Connection
) -> None:
    """
    This helper sets up a feed of the byte data and connection status changes
    from a connection into a processor.
    """

    @Slot(bytes)
    def _feed_data_to_processor(data: bytes) -> None:
        processor.feed([ByteFragment(data)])

    @Slot(Status, str)
    def _feed_status_to_processor(status: Status, text: str) -> None:
        processor.feed([NetworkFragment(status, text)])

    connection.dataReceived.connect(_feed_data_to_processor)
    connection.statusChanged.connect(_feed_status_to_processor)
