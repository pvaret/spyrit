# -*- coding: utf-8 -*-

## Copyright (c) 2007-2009 Pascal Varet <p.varet@gmail.com>
##
## This file is part of Spyrit.
##
## Spyrit is free software; you can redistribute it and/or modify it under the
## terms of the GNU General Public License version 2 as published by the Free
## Software Foundation.
##
## You should have received a copy of the GNU General Public License along with
## Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
## Fifth Floor, Boston, MA  02110-1301  USA
##

##
## AnsiFilter.py
##
## This file contains the AnsiFilter class, which parses out ANSI format codes
## from the stream, generates the matching FormatChunks and sends them
## downstream.
##

import re

from BaseFilter     import BaseFilter
from PipelineChunks import chunktypes, ByteChunk, FormatChunk


class AnsiFilter( BaseFilter ):

  relevant_types = chunktypes.BYTES

  ## For the time being, we only catch the SGR (Set Graphics Rendition) part
  ## of the ECMA 48 specification (a.k.a. ANSI escape codes).

  ESC   = "\x1b"
  CSI8b = "\x9b"

  CSI = "(?:" + ESC + r"\[" + "|" + CSI8b + ")"

  match = re.compile( CSI + r"((?:\d+;?)*)" + "m" )

  unfinished = re.compile( "|".join( [ "(" + code + "$)" for code in
                               ESC,
                               CSI + r"[\d;]*"
                         ] ) )


  def processChunk( s, chunk ):
   
    text       = chunk.data
    currentpos = 0

    while True:

      ansi = s.match.search( text, currentpos )
      
      if not ansi:
        break

      startmatch = ansi.start()

      if startmatch > currentpos:
        yield ByteChunk( text[ currentpos:startmatch ] )

      currentpos = ansi.end()

      parameters = ansi.groups() [0]

      if not parameters:
        parameters = "0"  ## ESC [ m is an alias for ESC [ 0 m.

      formats = []

      for param in parameters.split( ';' ):

        format = FormatChunk.ANSI_TO_FORMAT.get( param )

        if format:
          formats.append( format )

      if formats:
        yield( FormatChunk( formats ) )

      ## Done searching for complete ANSI sequences.


    if currentpos < len( text ):

      possible_unfinished = s.unfinished.search( text, currentpos )

      if possible_unfinished:

        ## Remaining text ends with an unfinished ANSI sequence!
        ## So we feed what remains of the raw text, if any, down the pipe, and
        ## then postpone the unfinished ANSI sequence.

        startmatch = possible_unfinished.start()

        if startmatch > currentpos:
          yield( ByteChunk( text[ currentpos:startmatch ] ) )

        s.postpone( ByteChunk( text[ startmatch: ] ) )
        
      else:
        yield( ByteChunk( text[ currentpos: ] ) )
