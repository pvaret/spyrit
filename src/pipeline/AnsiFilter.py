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
# AnsiFilter.py
#
# This file contains the AnsiFilter class, which parses out ANSI format codes
# from the stream, generates the corresponding chunks and sends them
# downstream.
#


import re

from typing import Optional, Tuple, cast

from Globals import ANSI_COLORS_EXTENDED
from Globals import FORMAT_PROPERTIES
from Globals import ESC

from .BaseFilter import BaseFilter
from .ChunkData import ChunkType
from .ChunkData import ANSI_TO_FORMAT


class AnsiFilter(BaseFilter):
    relevant_types = ChunkType.BYTES

    # For the time being, we only catch the SGR (Set Graphics Rendition) part
    # of the ECMA 48 specification (a.k.a. ANSI escape codes).

    CSI8b = b"\x9b"

    CSI = b"(?:" + ESC + rb"\[" + b"|" + CSI8b + b")"

    match = re.compile(CSI + rb"((?:\d+;?)*)" + b"m")

    unfinished = re.compile(
        b"|".join([b"(" + code + b"$)" for code in (ESC, CSI + rb"[\d;]*")])
    )

    highlighted: bool
    current_colors: tuple[Optional[str], Optional[str]]

    def resetInternalState(self):
        # Note: this method is called by the base class's __init__, so we're
        # sure that self.highlighted and self.current_colors are defined.

        self.highlighted, self.current_colors = self.defaultColors()
        super().resetInternalState()

    def defaultColors(self) -> tuple[bool, tuple[str, str]]:
        return (
            False,  # highlight
            # default colors
            ANSI_TO_FORMAT.get(b"39")[1],  # type: ignore
        )

    def processChunk(self, chunk):
        current_colors = self.current_colors
        highlighted = self.highlighted

        _, text = chunk

        while text:
            ansi = self.match.search(text)

            if not ansi:
                # Done with the ANSI parsing in this chunk! Bail out.
                break

            head, text = text[: ansi.start()], text[ansi.end() :]

            if head:
                yield (ChunkType.BYTES, head)

            parameters = bytes(ansi.groups()[0])

            if not parameters:  # ESC [ m, like ESC [ 0 m, resets the format.
                yield (ChunkType.ANSI, {})

                highlighted, current_colors = self.defaultColors()
                continue

            format = {}

            list_params = parameters.split(b";")

            while list_params:
                param = list_params.pop(0)

                # Special case: extended 256 color codes require special
                # treatment.

                if len(list_params) >= 2 and param in [b"38", b"48"]:
                    prop = ANSI_TO_FORMAT.get(param)[0]  # type: ignore
                    param = list_params.pop(0)

                    if param == b"5":
                        color = ANSI_COLORS_EXTENDED.get(
                            int(list_params.pop(0))
                        )
                        format[prop] = color

                        continue

                # Carry on with the standard cases.

                if param == b"0":  # ESC [ 0 m -- reset the format!
                    yield (ChunkType.ANSI, {})

                    highlighted, current_colors = self.defaultColors()
                    format = {}

                    continue

                if param not in ANSI_TO_FORMAT:
                    # Unknown ANSI code. Ignore.
                    continue

                prop, value = ANSI_TO_FORMAT[param]  # type: ignore

                if prop == FORMAT_PROPERTIES.COLOR:
                    # TODO: refactor to add proper type safety.
                    current_colors = cast(
                        tuple[Optional[str], Optional[str]], value
                    )
                    (c_unhighlighted, c_highlighted) = current_colors

                    if highlighted:
                        format[FORMAT_PROPERTIES.COLOR] = c_highlighted

                    else:
                        format[FORMAT_PROPERTIES.COLOR] = c_unhighlighted

                    continue

                if prop == FORMAT_PROPERTIES.BOLD:
                    # According to spec, this actually means highlighted colors.

                    highlighted = cast(bool, value)

                    # TODO: Clean up the property system to be type safe.
                    current_colors = cast(Tuple[str, str], current_colors)

                    c_unhighlighted, c_highlighted = current_colors

                    if value:  # Colors are now highlighted.
                        format[FORMAT_PROPERTIES.COLOR] = c_highlighted

                    else:
                        format[FORMAT_PROPERTIES.COLOR] = c_unhighlighted

                    if False:  # Ignore 'bold' meaning of this ANSI code?
                        continue  # TODO: Make it a parameter.

                # Other cases: italic, underline and such. Just pass the value
                # along.

                if prop is not None:
                    format[prop] = cast(str, value)

            if format:
                yield (ChunkType.ANSI, format)

        # Done searching for complete ANSI sequences.

        self.current_colors = current_colors
        self.highlighted = highlighted

        if text:
            possible_unfinished = self.unfinished.search(text)

            if possible_unfinished:
                # Remaining text ends with an unfinished ANSI sequence!
                # So we feed what remains of the raw text, if any, down the
                # pipe, and then postpone the unfinished ANSI sequence.

                startmatch = possible_unfinished.start()

                if startmatch > 0:
                    yield (ChunkType.BYTES, text[:startmatch])

                self.postpone((ChunkType.BYTES, text[startmatch:]))

            else:
                yield (ChunkType.BYTES, text)
