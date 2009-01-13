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
## BaseFilter.py
##
## This file holds the base class for pipeline filters, which holds the core
## logic for processing chunks of hopefully parsable data.
##


from PipelineChunks import theEndOfPacketChunk, ChunkTypeMismatch


class BaseFilter:

  ## This class attribute lists the chunk types that this filter will process.
  ## Those unlisted will be passed down the filter chain untouched.
  relevant_types = []
  

  def __init__( s, context=None ):

    s.sink           = None
    s.context        = context
    s.postponedChunk = []

    s.resetInternalState()


  def setContext( s, context ):

    s.context = context


  def setSink( s, sink ):

    s.sink = sink


  def postpone( s, chunk ):

    if s.postponedChunk:
      raise Exception( "Whoa, there should NOT be a chunk in there already..." )
    
    else:
      s.postponedChunk = chunk


  def processChunk( s, chunk ):
    ## This is the default implementation, which does nothing.
    ## Override this to implement your filter.
    ## Note that this must be a generator or return a list.
    yield chunk


  def resetInternalState( s ):
    ## Initialize the filter at the beginning of a connection (or when
    ## reconnecting). For instance the Telnet filter would drop all negociated
    ## options.
    ## Override this when implementing your filter if your filter uses any
    ## internal data.
    s.postponedChunk = []


  def concatPostponed( s, chunk ):

    if not s.postponedChunk:
      return chunk

    if chunk is theEndOfPacketChunk:
      ## The End Of Packet chunk is a special case, and is never merged
      ## with other chunks.
      return chunk
      
    ## If there was some bit of chunk that we postponed earlier...
    postponed = s.postponedChunk
    s.postponedChunk = None
    ## We retrieve it...
    
    try:
      ## And try to merge it with the new chunk.
      postponed.concat( chunk )
      chunk = postponed
      
    except ChunkTypeMismatch:
      ## If they're incompatible, it means the postponed chunk was really
      ## complete, so we send it downstream.
      s.sink( postponed )

    return chunk


  def feedChunk( s, chunk ):
    
    chunk = s.concatPostponed( chunk )
    
    ## At this point, the postponed chunk has either been merged with
    ## the new one, or been sent downstream. At any rate, it's been dealt
    ## with, and s.postponedChunk is empty.
    ## This mean that the postponed chunk should ALWAYS have been cleared
    ## when processChunk() is called. If not, there's something shifty
    ## going on...
    
    if chunk.chunktype in s.relevant_types:

      chunks = s.processChunk( chunk )
      for chunk in chunks: s.sink( chunk )
      
    else:
      s.sink( chunk )


  def formatForSending( s, data ):
    ## Reimplement this function if the filter inherently requires the data
    ## sent to the world to be modified. I.e., the telnet filter would escape
    ## occurences of the IAC in the data.

    return data
