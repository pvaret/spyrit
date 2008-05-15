# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
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
## EndLineFilter.py
##
## This file holds the EndLineFilter class, whose purpose is to parse out end
## of line characters (\r\n, in accordance with the Telnet specs) into a
## specific chunk, as the info will for instance be needed by the highlight
## filter.
##


import re

from BaseFilter     import BaseFilter
from PipelineChunks import chunktypes


class EndLineFilter( BaseFilter ):
  
  relevant_types = [ chunktypes.BYTES ]

  unix_like_cr   = re.compile( r'(?<!\r)\n' )

  match          = re.compile( r'(\r\n)|\n' )
  unfinished     = "\r"

  def processChunk( s, chunk ):
    
    type, text = chunk

    if type != chunktypes.BYTES:

      yield chunk
      raise StopIteration

    while len( text ) > 0:

      cr = s.match.search( text )
      
      if cr:
        head = text[ :cr.start() ]
        tail = text[ cr.end():   ]

        text = tail

        if head:
          yield ( chunktypes.BYTES, head )

        yield ( chunktypes.ENDOFLINE, None )

      else:
        ## The remaining text doesn't contain any identifiable carriage
        ## return. So we quit the loop.
        break

    if text:
      
      if text.endswith( s.unfinished ):
        s.postpone( ( chunktypes.BYTES, text ) )
        
      else:
        yield ( chunktypes.BYTES, text )


  def formatForSending( s, data ):

    return s.unix_like_cr.sub( "\r\n", data )
