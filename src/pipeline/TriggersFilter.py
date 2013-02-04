# -*- coding: utf-8 -*-

## Copyright (c) 2007-2013 Pascal Varet <p.varet@gmail.com>
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


from BaseFilter import BaseFilter

import ChunkData



class TriggersFilter( BaseFilter ):

  def __init__( self, context=None, manager=None ):

    self.buffer  = []
    self.setManager( manager )

    BaseFilter.__init__( self, context )


  def setManager( self, manager ):

    self.manager = manager

    if manager is None:
      self.processChunk = self.defaultProcessChunk

    else:
      self.processChunk = self.activatedProcessChunk


  def resetInternalState( self ):

    self.buffer = []
    BaseFilter.resetInternalState( self )


  def defaultProcessChunk( self, chunk ):

    yield chunk


  def activatedProcessChunk( self, chunk ):

    self.buffer.append( chunk )

    chunk_type, _ = chunk

    if chunk_type in ( ChunkData.NETWORK, ChunkData.PROMPTSWEEP ) \
       or chunk == ( ChunkData.FLOWCONTROL, ChunkData.LINEFEED ):

      line = u"".join( chunk[1]
                       for chunk in self.buffer
                       if chunk[0] == ChunkData.TEXT )


      if line:
        self.manager.performMatchingActions( line, self.buffer )

      for chunk in self.buffer:
        yield chunk

      self.buffer = []
