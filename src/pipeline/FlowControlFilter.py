# -*- coding: utf-8 -*-

## Copyright (c) 2007-2020 Pascal Varet <p.varet@gmail.com>
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
## FlowControlFilter.py
##
## This file holds the FlowControlFilter class, whose purpose is to parse out
## special characters relevant to the flow of text (\n, typically) into a
## specific chunk, as the info will for instance be needed by the highlight
## filter.
##


import re

from .ChunkData import ChunkType
from .ChunkData import FlowControl

from .BaseFilter import BaseFilter


class FlowControlFilter( BaseFilter ):

  relevant_types = ChunkType.TEXT

  match        = re.compile( r'(\r|\n)' )
  unix_like_cr = re.compile( r'(?<!\r)\n' )

  chunkmapping = {
    u'\n': ( ChunkType.FLOWCONTROL, FlowControl.LINEFEED ),
    u'\r': ( ChunkType.FLOWCONTROL, FlowControl.CARRIAGERETURN ),
  }


  def processChunk( self, chunk ):

    _, text = chunk

    ## Expand tabs to spaces:
    text = text.replace( u'\t', u' '*8 )

    while len( text ) > 0:

      fc = self.match.search( text )

      if fc:
        head = text[ :fc.start() ]
        tail = text[ fc.end():   ]

        text = tail

        if head:
          yield ( ChunkType.TEXT, head )

        yield self.chunkmapping[ fc.group() ]

      else:
        ## The remaining text doesn't contain any flow control character that
        ## we care about. So we quit the loop.
        break

    if text:
      yield ( ChunkType.TEXT, text )


  def formatForSending( self, data ):

    ## Transform UNIX-like CR into telnet-like CRLF.
    return self.unix_like_cr.sub( u"\r\n", data )
