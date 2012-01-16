# -*- coding: utf-8 -*-

## Copyright (c) 2007-2012 Pascal Varet <p.varet@gmail.com>
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


import codecs

from Messages       import messages
from BaseFilter     import BaseFilter

import ChunkData




class UnicodeTextFilter( BaseFilter ):

  relevant_types = ChunkData.BYTES


  def __init__( self, context, encoding ):

    self.decoder  = None
    self.encoding = "ascii"

    BaseFilter.__init__( self, context )

    self.setEncoding( encoding )
    self.bindNotificationListener( "encoding_changed", self.setEncoding )


  def setEncoding( self, encoding ):

    encoding = encoding.encode( "ascii", "ignore" )  ## unicode -> str

    try:
      codecs.lookup( encoding )

    except LookupError:

      messages.warn( u"Unknown encoding '%s'; reverting to Latin1." \
                     % encoding )
      encoding = "latin1"

    self.encoding = encoding
    self.decoder  = codecs.getincrementaldecoder( self.encoding ) ( "replace" )


  def resetInternalState( self ):

    BaseFilter.resetInternalState( self )

    if self.decoder:
      self.decoder.reset()


  def processChunk( self, chunk ):

    _, payload = chunk

    text = self.decoder.decode( payload )

    if text:
      yield ( ChunkData.TEXT, text )


  def formatForSending( self, data ):

    return data.encode( self.encoding, "replace" )
