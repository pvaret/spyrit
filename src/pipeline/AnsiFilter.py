# -*- coding: utf-8 -*-

## Copyright (c) 2007-2015 Pascal Varet <p.varet@gmail.com>
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

from BaseFilter import BaseFilter
from Globals    import ANSI_COLORS_EXTENDED
from Globals    import FORMAT_PROPERTIES
from Globals    import ESC

import ChunkData


class AnsiFilter( BaseFilter ):

  relevant_types = ChunkData.BYTES

  ## For the time being, we only catch the SGR (Set Graphics Rendition) part
  ## of the ECMA 48 specification (a.k.a. ANSI escape codes).

  CSI8b = "\x9b"

  CSI = "(?:" + ESC + r"\[" + "|" + CSI8b + ")"

  match = re.compile( CSI + r"((?:\d+;?)*)" + "m" )

  unfinished = re.compile( "|".join( [ "(" + code + "$)" for code in
                               ESC,
                               CSI + r"[\d;]*"
                         ] ) )


  def resetInternalState( self ):

    ## Note: this method is called by the base class's __init__, so we're
    ## sure that self.highlighted and self.current_colors are defined.

    self.highlighted, self.current_colors = self.defaultColors()
    BaseFilter.resetInternalState( self )


  def defaultColors( self ):

    return ( False,  ## highlight
             ChunkData.ANSI_TO_FORMAT.get( "39" )[1] ) ## default colors


  def processChunk( self, chunk ):

    current_colors = self.current_colors
    highlighted    = self.highlighted

    chunk_type, text = chunk

    while text:

      ansi = self.match.search( text )

      if not ansi:

        ## Done with the ANSI parsing in this chunk! Bail out.
        break

      head, text = text[ :ansi.start() ], text[ ansi.end(): ]

      if head:
        yield ( ChunkData.BYTES, head )

      parameters = ansi.groups() [0]

      if not parameters:  ## ESC [ m, like ESC [ 0 m, resets the format.

        yield ( ChunkData.ANSI, {} )

        highlighted, current_colors = self.defaultColors()
        continue

      format = {}

      list_params = parameters.split( ';' )

      while list_params:

        param = list_params.pop( 0 )

        ## Special case: extended 256 color codes require special treatment.

        if len( list_params ) >= 2 and param in [ "38", "48" ]:

          prop = ChunkData.ANSI_TO_FORMAT.get( param )[0]
          param = list_params.pop( 0 )

          if param == "5":

            color = ANSI_COLORS_EXTENDED.get( int( list_params.pop( 0 ) ) )
            format[ prop ] = color

            continue

        ## Carry on with the standard cases.

        if param == "0":  ## ESC [ 0 m -- reset the format!

          yield ( ChunkData.ANSI, {} )

          highlighted, current_colors = self.defaultColors()
          format = {}

          continue

        prop, value = ChunkData.ANSI_TO_FORMAT.get( param, ( None, None ) )

        if not prop:  ## Unknown ANSI code. Ignore.
          continue

        if prop == FORMAT_PROPERTIES.COLOR:

          ( c_unhighlighted, c_highlighted ) = current_colors = value

          if highlighted:
            format[ FORMAT_PROPERTIES.COLOR ] = c_highlighted

          else:
            format[ FORMAT_PROPERTIES.COLOR ] = c_unhighlighted

          continue

        if prop == FORMAT_PROPERTIES.BOLD:

          ## According to spec, this actually means highlighted colors.

          highlighted = value

          c_unhighlighted, c_highlighted = current_colors

          if value:  ## Colors are now highlighted.
            format[ FORMAT_PROPERTIES.COLOR ] = c_highlighted

          else:
            format[ FORMAT_PROPERTIES.COLOR ] = c_unhighlighted

          if False:   ## Ignore 'bold' meaning of this ANSI code?
            continue  ## TODO: Make it a parameter.

        ## Other cases: italic, underline and such. Just pass the value along.

        format[ prop ] = value

      if format:
        yield ( ChunkData.ANSI, format )


    ## Done searching for complete ANSI sequences.

    self.current_colors = current_colors
    self.highlighted    = highlighted

    if text:

      possible_unfinished = self.unfinished.search( text )

      if possible_unfinished:

        ## Remaining text ends with an unfinished ANSI sequence!
        ## So we feed what remains of the raw text, if any, down the pipe, and
        ## then postpone the unfinished ANSI sequence.

        startmatch = possible_unfinished.start()

        if startmatch > 0:
          yield ( ChunkData.BYTES, text[ :startmatch ] )

        self.postpone( ( ChunkData.BYTES, text[ startmatch: ] ) )

      else:
        yield ( ChunkData.BYTES, text )
