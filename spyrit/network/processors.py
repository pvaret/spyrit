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
Implements classes that transform raw byte data from the network into something
that makes semantic sense and can be fed into e.g. a text display widget.
"""


import codecs
import logging

from collections import deque
from typing import Iterable, Iterator, cast

import regex

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from sunset import Key, List

from spyrit import constants
from spyrit.network.connection import Connection, Status
from spyrit.network.fragments import (
    ANSIFragment,
    ByteFragment,
    FlowControlCode,
    FlowControlFragment,
    Fragment,
    FragmentList,
    MatchBoundary,
    NetworkFragment,
    PatternMatchFragment,
    TextFragment,
)
from spyrit.network.pattern import find_matches
from spyrit.regex_helpers import any_of, blocks_with_separator, optional
from spyrit.ui.colors import ANSIColor, NoColor, RGBColor
from spyrit.ui.format import FormatUpdate
from spyrit.settings.spyrit_settings import (
    ANSIBoldEffect,
    Encoding,
    PatternScope,
    PatternType,
    SpyritSettings,
)


class BaseProcessor(QObject):
    """
    Processors take fragments of network data, potentially already processed,
    and process them further by parsing / decoding / filtering them.

    This class implements the logic common to all processors.
    """

    # This signal fires when a processor has some output ready.

    fragmentsReady: Signal = Signal(FragmentList)

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


class PacketSplitterProcessor(BaseProcessor):
    """
    This processor splits incoming packets into smaller chunks and makes sure
    the Qt event loop has time to run between each chunk. This helps the UI feel
    snappier.
    """

    _BLOCK_SIZE: int = constants.PROCESSOR_BLOCK_SIZE_BYTES

    _chunk_processing_timer: QTimer
    _input_buffer: deque[Fragment]

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._input_buffer = deque()
        self._chunk_processing_timer = QTimer()
        self._chunk_processing_timer.setSingleShot(True)
        self._chunk_processing_timer.timeout.connect(self.processOneChunk)

    def feed(self, fragments: Iterable[Fragment]) -> None:
        self._input_buffer.extend(fragments)
        self._chunk_processing_timer.start()

    @Slot()
    def processOneChunk(self) -> None:
        if not self._input_buffer:
            return

        fragment = self._input_buffer.popleft()

        match fragment:
            case ByteFragment(data):
                if len(data) > self._BLOCK_SIZE:
                    fragment = ByteFragment(data[: self._BLOCK_SIZE])
                    self._input_buffer.appendleft(
                        ByteFragment(data[self._BLOCK_SIZE :])
                    )
            case _:
                pass

        self._output_buffer.append(fragment)
        self._maybeSignalOutputReady()

        self._chunk_processing_timer.start()


class ANSIProcessor(BaseProcessor):
    """
    This processor implements parsing of the SGR part of the ANSI specification.
    """

    ESC = b"\033"
    CSI = ESC + regex.escape(rb"[")

    _SGR_re = regex.compile(
        CSI
        + rb"(?P<sgr>"
        + rb"("  # Start SGR codes
        + rb"\d+"  # First code
        + rb"(;\d+)*"  # Extra codes
        + rb")?"  # End SGR codes
        + rb")"
        + rb"m"  # SGR marker
    )

    _SGR_reset = FormatUpdate(
        bold=False,
        bright=False,
        italic=False,
        underline=False,
        reverse=False,
        strikeout=False,
        foreground=NoColor(),
        background=NoColor(),
    )

    _ansi_bold_effect: Key[ANSIBoldEffect]
    _pending_data: bytes

    def __init__(
        self,
        ansi_bold_effect: Key[ANSIBoldEffect],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self._ansi_bold_effect = ansi_bold_effect
        self._pending_data = b""

    def processFragment(self, fragment: Fragment) -> Iterator[Fragment]:
        match fragment:
            case ByteFragment(data):
                data = self._pending_data + data
                self._pending_data = b""

                while data:
                    match = regex.search(self._SGR_re, data, partial=True)

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
            codes.append(0)

        ansi_bold_effect = self._ansi_bold_effect.get()

        format_update = FormatUpdate()

        while codes:
            # This cast shouldn't be necessary, but without it the pattern
            # matching below confuses some versions of Pylance.
            codes = cast(list[int], codes)
            match code := codes.pop(0):
                case 0:
                    format_update.update(self._SGR_reset)

                case 1:
                    if ansi_bold_effect & ANSIBoldEffect.BOLD:
                        format_update.setBold()
                    if ansi_bold_effect & ANSIBoldEffect.BRIGHT:
                        format_update.setBright()
                case 3:
                    format_update.setItalic()
                case 4:
                    format_update.setUnderline()
                case 7:
                    format_update.setReverse()
                case 9:
                    format_update.setStrikeout()

                case 21 | 22:
                    format_update.setBold(False)
                    format_update.setBright(False)
                case 23:
                    format_update.setItalic(False)
                case 24:
                    format_update.setUnderline(False)
                case 27:
                    format_update.setReverse(False)
                case 29:
                    format_update.setStrikeout(False)

                case _ if 30 <= code <= 37:
                    format_update.setForeground(ANSIColor(code - 30))

                case 38:
                    match codes:
                        case [2, r, g, b, *codes]:
                            format_update.setForeground(RGBColor(r, g, b))
                        case [5, n, *codes]:
                            format_update.setForeground(ANSIColor(n))
                        case _:
                            seq = ";".join(str(i) for i in [code] + codes)
                            logging.debug(
                                "Received invalid ANSI SGR sequence: %s", seq
                            )
                            continue

                case 39:
                    format_update.setForeground(NoColor())

                case _ if 40 <= code <= 47:
                    format_update.setBackground(ANSIColor(code - 40))

                case 48:
                    match codes:
                        case [2, r, g, b, *codes]:
                            format_update.setBackground(RGBColor(r, g, b))
                        case [5, n, *codes]:
                            format_update.setBackground(ANSIColor(n))
                        case _:
                            seq = ";".join(str(i) for i in [code] + codes)
                            logging.debug(
                                "Received invalid ANSI SGR sequence: %s", seq
                            )
                            continue

                case 49:
                    format_update.setBackground(NoColor())

                case _ if 90 <= code <= 97:
                    format_update.setForeground(ANSIColor(code - 90 + 8))

                case _ if 100 <= code <= 107:
                    format_update.setBackground(ANSIColor(code - 100 + 8))

                case _:
                    logging.debug(
                        "Unsupported ANSI SGR code received: %d", code
                    )

        return ANSIFragment(format_update)


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


def inject_fragments_into_buffer(
    fragments: Iterable[tuple[int, Fragment]], buffer: list[Fragment]
) -> list[Fragment]:
    """
    Injects the given fragments at their associated positions into the given
    fragment buffer, where a position is measured from character counts in
    TextFragment fragments.

    The buffer is emptied as part of the processing.
    """

    # This is guaranteed to preserve the order in which the matches were found.
    # This order can be important in case the associated formatting instructions
    # override each other. I.e., if a low priority match formats the text red
    # and a high priority match formats it blue at the same position, then the
    # text should consistently be blue.
    fragments_in_order: dict[int, list[Fragment]] = {}
    for fragment_pos, buffer_fragment in fragments:
        fragments_in_order.setdefault(fragment_pos, []).append(buffer_fragment)

    ret: list[Fragment] = []
    current_pos = 0

    for fragment_pos in sorted(fragments_in_order.keys()):
        while current_pos < fragment_pos:
            if not buffer:
                break

            match buffer_fragment := buffer.pop(0):
                case TextFragment(text):
                    fragment_offset = fragment_pos - current_pos
                    assert fragment_offset > 0

                    if len(text) < fragment_offset:
                        current_pos += len(text)
                        ret.append(buffer_fragment)
                        continue

                    if len(text) > fragment_offset:
                        buffer.insert(0, TextFragment(text[fragment_offset:]))

                    ret.append(TextFragment(text[:fragment_offset]))
                    current_pos += fragment_offset

                case _:
                    ret.append(buffer_fragment)

        ret.extend(fragments_in_order[fragment_pos])

    while buffer:
        ret.append(buffer.pop(0))

    return ret


def expand_url(format: FormatUpdate, text: str) -> FormatUpdate:
    """
    Returns a FormatUpdate where the HREF match placeholder, if any, is
    replaced with the text that was matched, if any.
    """

    if format.href is not None and constants.MATCH_PLACEHOLDER in format.href:
        ret = FormatUpdate()
        ret.update(format)
        ret.href = format.href.replace(constants.MATCH_PLACEHOLDER, text)
        return ret

    return format


class UserPatternProcessor(BaseProcessor):
    """
    This processor batches entire lines of text and searches them for
    user-provided patterns, in order to apply conditional user-provided
    formatting.
    """

    _patterns: List[SpyritSettings.Pattern]
    _fragment_buffer: list[Fragment]
    _line_so_far: str = ""
    _url_pattern: SpyritSettings.Pattern

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
        + blocks_with_separator(r"[-_a-zA-Z0-9]+", sep=r"\.")
        # port
        + optional(r":\d+")
        # path
        + optional(
            r"/"
            + optional(
                r"[-a-zA-Z0-9~#/&_=:(){}.!?]*" + r"[-a-zA-Z0-9~#/&_=:)}]"
            )
        )
    )

    def __init__(self, patterns: List[SpyritSettings.Pattern]) -> None:
        super().__init__()

        self._patterns = patterns
        self._fragment_buffer = []

        self._url_pattern = SpyritSettings.Pattern()
        self._url_pattern.format.set(
            FormatUpdate(
                italic=True, underline=True, href=constants.MATCH_PLACEHOLDER
            )
        )
        self._url_pattern.scope.set(PatternScope.ANYWHERE_IN_LINE)
        url_match = self._url_pattern.fragments.appendOne()
        url_match.type.set(PatternType.REGEX)
        url_match.pattern_text.set(self.URL_MATCH_RE)

    def processFragment(self, fragment: Fragment) -> Iterator[Fragment]:
        self._fragment_buffer.append(fragment)

        match fragment:
            case TextFragment(text):
                self._line_so_far += text

            case NetworkFragment() | FlowControlFragment(FlowControlCode.LF):
                patterns: list[tuple[int, PatternMatchFragment]] = []
                for format_, start, end in self._findUserPatterns(
                    self._line_so_far
                ):
                    pattern = PatternMatchFragment(format_, MatchBoundary.START)
                    patterns.append((start, pattern))
                    pattern = PatternMatchFragment(format_, MatchBoundary.END)
                    patterns.append((end, pattern))

                yield from inject_fragments_into_buffer(
                    patterns, self._fragment_buffer
                )
                self._line_so_far = ""
                self._fragment_buffer.clear()

            case _:
                pass

    def _findUserPatterns(
        self, line: str
    ) -> Iterator[tuple[FormatUpdate, int, int]]:
        for pattern in self._getPatterns():
            for start, end, format_ in find_matches(pattern, line):
                if start != end and not format_.empty():
                    matched_text = line[start:end]
                    yield (expand_url(format_, matched_text), start, end)

    def _getPatterns(self) -> Iterator[SpyritSettings.Pattern]:
        yield self._url_pattern
        yield from self._patterns.iter(List.PARENT_FIRST)


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
    processor: BaseProcessor,
    connection: Connection,
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
