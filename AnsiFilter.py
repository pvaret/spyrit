# -*- coding: utf-8 -*-

## Copyright (c) 2007-2010 Pascal Varet <p.varet@gmail.com>
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
## from the stream, generates the corresponding chunks and sends them
## downstream.
##

import re

from BaseFilter     import BaseFilter
from Globals        import FORMAT_PROPERTIES

import ChunkData


class AnsiFilter( BaseFilter ):

  relevant_types = ChunkData.BYTES

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


  def resetInternalState( s ):

    ## Note: this method is called by the base class's __init__, so we're
    ## sure that s.highlighted and s.current_colors are defined.

    s.highlighted, s.current_colors = s.defaultColors()
    BaseFilter.resetInternalState( s )


  def defaultColors( s ):

    return ( False,  ## highlight
             ChunkData.ANSI_TO_FORMAT.get( "39" )[1] ) ## default colors


  def processChunk( s, chunk ):

    current_colors = s.current_colors
    highlighted    = s.highlighted

    chunk_type, text = chunk

    currentpos = 0

    while True:

      ansi = s.match.search( text, currentpos )

      if not ansi:

        ## Done with the ANSI parsing in this chunk! Bail out.
        break

      startmatch = ansi.start()

      if startmatch > currentpos:
        yield ( ChunkData.BYTES, text[ currentpos:startmatch ] )

      currentpos = ansi.end()
      parameters = ansi.groups() [0]

      if not parameters:  ## ESC [ m, like ESC [ 0 m, resets the format.

        yield ( ChunkData.ANSI, {} )

        highlighted, current_colors = s.defaultColors()
        continue

      format = {}

      for param in parameters.split( ';' ):

        if param == "0":  ## ESC [ 0 m -- reset the format!

          yield ( ChunkData.ANSI, {} )

          highlighted, current_colors = s.defaultColors()
          format = {}

          continue

        prop, value = ChunkData.ANSI_TO_FORMAT.get( param, ( None, None ) )

        if not prop:  ## Unknown ANSI code. Ignore.
          continue

        if prop == FORMAT_PROPERTIES.BOLD:

          ## According to spec, this actually means highlighted colors.

          highlighted = value

          c_unhighlighted, c_highlighted = current_colors

          if value:  ## Colors are now highlighted.
            format[ FORMAT_PROPERTIES.COLOR ] = c_highlighted

          else:
            format[ FORMAT_PROPERTIES.COLOR ] = c_unhighlighted

          continue

        if prop == FORMAT_PROPERTIES.COLOR:

          ( c_unhighlighted, c_highlighted ) = current_colors = value

          if highlighted:
            format[ FORMAT_PROPERTIES.COLOR ] = c_highlighted

          else:
            format[ FORMAT_PROPERTIES.COLOR ] = c_unhighlighted

          continue

        ## Other cases: italic, underline and such. Just pass the value along.

        format[ prop ] = value

      if format:
        yield ( ChunkData.ANSI, format )


    ## Done searching for complete ANSI sequences.

    s.current_colors = current_colors
    s.highlighted    = highlighted

    if currentpos < len( text ):

      possible_unfinished = s.unfinished.search( text, currentpos )

      if possible_unfinished:

        ## Remaining text ends with an unfinished ANSI sequence!
        ## So we feed what remains of the raw text, if any, down the pipe, and
        ## then postpone the unfinished ANSI sequence.

        startmatch = possible_unfinished.start()

        if startmatch > currentpos:
          yield ( ChunkData.BYTES, text[ currentpos:startmatch ] )

        s.postpone( ( ChunkData.BYTES, text[ startmatch: ] ) )

      else:
        yield ( ChunkData.BYTES, text[ currentpos: ] )
