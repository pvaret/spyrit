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
## BaseFilter.py
##
## This file holds the base class for pipeline filters, which holds the core
## logic for processing chunks of hopefully parsable data.
##


import ChunkData


class BaseFilter:

  ## This class attribute lists the chunk types that this filter will process.
  ## Those unlisted will be passed down the filter chain untouched.

  relevant_types = ChunkData.ALL_TYPES


  def __init__( self, context=None ):

    self.sink           = None
    self.context        = context
    self.postponedChunk = []

    self.resetInternalState()


  def setSink( self, sink ):

    self.sink = sink


  def postpone( self, chunk ):

    if self.postponedChunk:
      raise Exception( u"Duplicate postponed chunk!" )

    else:
      self.postponedChunk = chunk


  def processChunk( self, chunk ):

    ## This is the default implementation, which does nothing.
    ## Override this to implement your filter.
    ## Note that this must be a generator or return a list.

    yield chunk


  def resetInternalState( self ):

    ## Initialize the filter at the beginning of a connection (or when
    ## reconnecting). For instance the Telnet filter would drop all negociated
    ## options.
    ## Override this when implementing your filter if your filter uses any
    ## internal data.

    self.postponedChunk = []


  def concatPostponed( self, chunk ):

    if not self.postponedChunk:
      return chunk

    chunk_type, _ = chunk

    if chunk_type == ChunkData.PACKETBOUND:
      ## This chunk type is a special case, and is never merged with other
      ## chunks.
      return chunk

    ## If there was some bit of chunk that we postponed earlier...
    postponed = self.postponedChunk
    self.postponedChunk = None
    ## We retrieve it...

    try:
      ## And try to merge it with the new chunk.
      chunk = ChunkData.concat_chunks( postponed, chunk )

    except ChunkData.ChunkTypeMismatch:
      ## If they're incompatible, it means the postponed chunk was really
      ## complete, so we send it downstream.
      self.sink( postponed )

    return chunk


  def feedChunk( self, chunk ):

    chunk_type, _ = chunk

    if chunk_type & self.relevant_types:

      if self.postponedChunk:
        chunk = self.concatPostponed( chunk )

      ## At this point, the postponed chunk has either been merged with
      ## the new one, or been sent downstream. At any rate, it's been dealt
      ## with, and self.postponedChunk is empty.
      ## This mean that the postponed chunk should ALWAYS have been cleared
      ## when processChunk() is called. If not, there's something shifty
      ## going on...

      for chunk in self.processChunk( chunk ):
        self.sink( chunk )

    else:
      self.sink( chunk )


  def formatForSending( self, data ):

    ## Reimplement this function if the filter inherently requires the data
    ## sent to the world to be modified. I.e., the telnet filter would escape
    ## occurences of the IAC in the data.

    return data


  def notifify( self, notification, *args ):

    if not self.context:
      return

    self.context.notify( notification, *args )


  def bindNotificationListener( self, notification, callback ):

    if not self.context:
      return

    self.context.bindNotificationListener( notification, callback )
