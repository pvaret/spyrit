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

import regex

from PySide6.QtCore import QObject, Signal, Slot
from sunset import Key

from spyrit.network.connection import Connection, Status
from spyrit.network.fragments import (
    ANSIFragment,
    ByteFragment,
    FlowControlCode,
    FlowControlFragment,
    Fragment,
    FragmentList,
    NetworkFragment,
    TextFragment,
)
from spyrit.ui.colors import ANSIColor, NoColor, RGBColor
from spyrit.ui.format import CharFormat
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


class ANSIProcessor(BaseProcessor):
    """
    This processor implements parsing of the SGR part of the ANSI specification.
    """

    ESC = b"\033"
    CSI = ESC + regex.escape(rb"[")

    _pending_data: bytes

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._pending_data = b""

        self._re = regex.compile(
            self.CSI
            + rb"(?P<sgr>"
            + rb"("  # Start SGR codes
            + rb"\d+"  # First code
            + rb"(;\d+)*"  # Extra codes
            + rb")?"  # End SGR codes
            + rb")"
            + rb"m"  # SGR marker
        )

    def processFragment(self, fragment: Fragment) -> Iterator[Fragment]:
        match fragment:
            case ByteFragment(data):
                data = self._pending_data + data
                self._pending_data = b""

                while data:
                    match = regex.search(self._re, data, partial=True)

                    if match is None:
                        yield ByteFragment(data)
                        return

                    if match.start() > 0:
                        yield ByteFragment(data[: match.start()])

                    if match.partial:
                        self._pending_data += data[match.start() :]
                        return

                    data = data[match.end() :]

                    code_bytes = match.group("sgr")
                    codes = (
                        [int(item) for item in code_bytes.split(b";")]
                        if code_bytes
                        else []
                    )

                    yield self.fragmentFromSGRCodes(codes)

            case _:
                yield fragment

    def fragmentFromSGRCodes(self, codes: list[int]) -> ANSIFragment:
        if not codes:  # An empty SGR sequence should be treated as a reset.
            codes = [0]

        format_ = CharFormat()

        while codes:
            match code := codes.pop(0):
                case 0:
                    format_.resetAll()

                case 1:
                    # TODO: Add setting to decide if this should be bold or a
                    # lighter color or both.
                    format_.setBold()
                case 3:
                    format_.setItalic()
                case 4:
                    format_.setUnderline()
                case 7:
                    format_.setReverse()
                case 9:
                    format_.setStrikeout()

                case 21 | 22:
                    format_.setBold(False)
                case 23:
                    format_.setItalic(False)
                case 24:
                    format_.setUnderline(False)
                case 27:
                    format_.setReverse(False)
                case 29:
                    format_.setStrikeout(False)

                case _ if 30 <= code <= 37:
                    format_.setForeground(ANSIColor(code - 30))

                case 38:
                    match codes:
                        case [2, r, g, b, *codes]:
                            format_.setForeground(RGBColor(r, g, b))
                        case [5, n, *codes]:
                            format_.setForeground(ANSIColor(n))
                        case _:
                            seq = ";".join(str(i) for i in [code] + codes)
                            logging.debug(
                                "Received invalid ANSI SGR sequence: %s", seq
                            )
                            continue

                case 39:
                    format_.setForeground(NoColor())

                case _ if 40 <= code <= 47:
                    format_.setBackground(ANSIColor(code - 40))

                case 48:
                    match codes:
                        case [2, r, g, b, *codes]:
                            format_.setBackground(RGBColor(r, g, b))
                        case [5, n, *codes]:
                            format_.setBackground(ANSIColor(n))
                        case _:
                            seq = ";".join(str(i) for i in [code] + codes)
                            logging.debug(
                                "Received invalid ANSI SGR sequence: %s", seq
                            )
                            continue

                case 49:
                    format_.setBackground(NoColor())

                # TODO: Support extra colors in the 90-100 range?

                case _:
                    logging.debug(
                        "Unsupported ANSI SGR code received: %d", code
                    )

        return ANSIFragment(format_)


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
            codec = codecs.lookup(encoding)
        except LookupError:
            logging.error(
                "Couldn't find decoder for encoding '%s'; reverting to default"
                " encoding 'ASCII'.",
                encoding,
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
                    yield TextFragment(text)

            case _:
                yield fragment


def _flush(buffer: list[str]) -> Iterator[TextFragment]:
    if buffer:
        yield TextFragment("".join(buffer))
        buffer.clear()


class FlowControlProcessor(BaseProcessor):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._cr = FlowControlFragment(code=FlowControlCode.CR)
        self._lf = FlowControlFragment(code=FlowControlCode.LF)

    def processFragment(self, fragment: Fragment) -> Iterator[Fragment]:
        match fragment:
            case TextFragment(text):
                buffer: list[str] = []

                for c in text:
                    match c:
                        case "\r":
                            yield from _flush(buffer)
                            yield self._cr

                        case "\n":
                            yield from _flush(buffer)
                            yield self._lf

                        case _ if c.isprintable():
                            buffer.append(c)

                        case _:
                            pass

                yield from _flush(buffer)

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
