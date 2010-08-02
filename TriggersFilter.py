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
## TriggersFilter.py
##
## This file holds the TriggersFilter class, which bufferizes the incoming
## chunks until a line is complete, and then matches that line with the
## world's registered match patterns and triggers the corresponding action
## as needed.
##


import re

from BaseFilter     import BaseFilter
from PipelineChunks import chunktypes, FlowControlChunk, HighlightChunk



class TriggersFilter( BaseFilter ):

  relevant_types = chunktypes.ALL_TYPES & ~chunktypes.PACKETBOUND

  def __init__( s, context=None, manager=None ):

    s.buffer  = []
    s.setManager( manager )

    BaseFilter.__init__( s, context )


  def setManager( s, manager ):

    s.manager = manager

    if manager is None:
      s.processChunk = s.defaultProcessChunk

    else:
      s.processChunk = s.activatedProcessChunk


  def resetInternalState( s ):

    s.buffer = []
    BaseFilter.resetInternalState( s )


  def defaultProcessChunk( s, chunk ):

    yield chunk


  def activatedProcessChunk( s, chunk ):

    s.buffer.append( chunk )

    type = chunk.chunktype

    if type in ( chunktypes.NETWORK, chunktypes.PROMPTSWEEP ) \
      or   ( type       == chunktypes.FLOWCONTROL \
         and chunk.data == FlowControlChunk.LINEFEED ):

      line = u"".join( [ chunk.data
                         for chunk in s.buffer
                         if chunk.chunktype == chunktypes.TEXT ] )


      if line:
        s.manager.performMatchingActions( line, s.buffer )

      for chunk in s.buffer:
        yield chunk

      s.buffer = []
