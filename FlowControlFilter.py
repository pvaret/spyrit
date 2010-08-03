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
## FlowControlFilter.py
##
## This file holds the FlowControlFilter class, whose purpose is to parse out
## special characters relevant to the flow of text (\n, typically) into a
## specific chunk, as the info will for instance be needed by the highlight
## filter.
##


import re

from BaseFilter     import BaseFilter
from PipelineChunks import ChunkTypes, UnicodeTextChunk, FlowControlChunk


class FlowControlFilter( BaseFilter ):

  relevant_types = ChunkTypes.TEXT

  match          = re.compile( ur'(\r|\n)' )
  unix_like_cr   = re.compile( ur'(?<!\r)\n' )

  chunkmapping = {
    u'\n': FlowControlChunk( FlowControlChunk.LINEFEED ),
    u'\r': FlowControlChunk( FlowControlChunk.CARRIAGERETURN ),
  }


  def processChunk( s, chunk ):

    text = chunk.data

    ## Expand tabs to spaces:
    text = text.replace( u'\t', u' '*8 )

    while len( text ) > 0:

      fc = s.match.search( text )

      if fc:
        head = text[ :fc.start() ]
        tail = text[ fc.end():   ]

        text = tail

        if head:
          yield UnicodeTextChunk( head )

        yield s.chunkmapping[ fc.group() ]

      else:
        ## The remaining text doesn't contain any flow control character that
        ## we care about. So we quit the loop.
        break

    if text:
      yield( UnicodeTextChunk( text ) )


  def formatForSending( s, data ):

    ## Transform UNIX-like CR into telnet-like CRLF.
    return s.unix_like_cr.sub( u"\r\n", data )
