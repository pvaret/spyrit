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
## UnicodeTextFilter.py
##
## This file holds the UnicodeTextFilter class, which converts the incoming
## byte stream on the fly into Unicode text.
##


import re
import codecs

from Messages       import messages
from BaseFilter     import BaseFilter

import ChunkData




class UnicodeTextFilter( BaseFilter ):

  relevant_types = ChunkData.BYTES


  def __init__( s, context, encoding ):

    s.decoder  = None
    s.encoding = "ascii"

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
    s.decoder  = codecs.getincrementaldecoder( s.encoding ) ( "replace" )


  def resetInternalState( s ):

    BaseFilter.resetInternalState( s )

    if s.decoder:
      s.decoder.reset()


  def processChunk( s, chunk ):

    _, payload = chunk

    text = s.decoder.decode( payload )

    if text:
      yield ( ChunkData.TEXT, text )


  def formatForSending( s, data ):

    return data.encode( s.encoding, "replace" )
