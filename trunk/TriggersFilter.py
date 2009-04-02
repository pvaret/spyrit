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
## TriggersFilter.py
##
## This file holds the TriggersFilter class, which bufferizes the incoming
## chunks until a line is complete, and then matches that line with the
## world's registered match patterns and triggers the corresponding action
## as needed.
##


import re

from BaseFilter     import BaseFilter
from PipelineChunks import chunktypes, FlowControlChunk



class TriggersFilter( BaseFilter ):
  
  def __init__( s, context=None ):

    s.buffer  = []
    s.manager = None

    if context:
      s.setManager( context.parent.triggersmanager )

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

    #assert s.manager is not None

    s.buffer.append( chunk )

    type = chunk.chunktype

    if type == chunktypes.NETWORK \
      or ( type == chunktypes.FLOWCONTROL \
           and chunk.data == FlowControlChunk.LINEFEED ):

      line = u"".join( [ chunk.data
                         for chunk in s.buffer
                         if chunk.chunktype == chunktypes.TEXT ] )


      if line:

        m = s.manager.lookupMatch( line )

        if m:
          print m.results

      for chunk in s.buffer:
        
        yield chunk

      s.buffer = []
