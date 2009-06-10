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
## UnicodeTextFilter.py
##
## This file holds the UnicodeTextFilter class, which converts the incoming
## byte stream on the fly into Unicode text. It also contains the helper class
## StreamingDecoder for versions of Python < 2.5.
##

import re
import codecs

from Messages       import messages
from BaseFilter     import BaseFilter
from PipelineChunks import chunktypes, UnicodeTextChunk



class StreamingDecoder:

  ## WORKAROUND: Python 2.4 doesn't come with an incremental Unicode decoder,
  ## so we need to provide one until Python 2.5 is installed everywhere.
  ## For this purpose, we use the classic StreamReader class of the codecs
  ## module, and we feed data through a dummy file-like buffer object.
  ## This code will go when we stop supporting Python 2.4.

  class Buffer:

    ## Small file-like buffer class meant for use by the Unicode stream decoder.

    def __init__( s ):

      s._buffer = ""


    def write( s, str ):

      s._buffer = str


    def read( s ):

      data      = s._buffer
      s._buffer = ""
      return data


  def __init__( s, encoding, errors="strict" ):

    s.buffer  = s.Buffer()
    s.decoder = codecs.getreader( encoding ) ( s.buffer, errors )
  

  def decode( s, str ):

    s.buffer.write( str )
    return s.decoder.read()


  def reset( s ):

    s.buffer.read()
    s.decoder.reset()



class UnicodeTextFilter( BaseFilter ):
  
  relevant_types = chunktypes.BYTES


  def __init__( s, context, encoding ):

    BaseFilter.__init__( s, context )

    s.setEncoding( encoding )
    s.bindNotificationListener( "encoding_changed", s.setEncoding )


  def setEncoding( s, encoding ):

    encoding = encoding.encode( "ascii", "ignore" )  ## unicode -> str

    try:
      codecs.lookup( encoding )

    except LookupError:

      messages.warn( u"Unknown encoding '%s'; reverting to Latin1." \
                     % encoding )
      encoding = "latin1"

    s.encoding = encoding

    s.makeStreamDecoder()


  def makeStreamDecoder( s ):

    if hasattr( codecs, "getincrementaldecoder" ):  ## True as of Python 2.5
      s.decoder = codecs.getincrementaldecoder( s.encoding ) ( "replace" )

    else:
      s.decoder = StreamingDecoder( s.encoding, "replace" )


  def resetInternalState( s ):

    BaseFilter.resetInternalState( s )

    if hasattr( s, "decoder" ): s.decoder.reset()


  def processChunk( s, chunk ):
 
    text = s.decoder.decode( chunk.data )

    if text: yield UnicodeTextChunk( text )


  def formatForSending( s, data ):

    return data.encode( s.encoding, "replace" )
