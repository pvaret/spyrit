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
## Pipeline.py
##
## This file defines the class Pipeline, which manages the tokenization of
## a network stream into typed chunks: telnet code, ANSI code, etc...
## It works by assembling a series of Filters.
##


from PipelineChunks   import ByteChunk, theEndOfPacketChunk
from CallbackRegistry import CallbackRegistry


class Pipeline:
  
  def __init__( s, parent=None ):

    s.parent       = parent
    s.filters      = []
    s.outputBuffer = []
    s.sinks        = CallbackRegistry()

    s.notification_registry = {}


  def feedBytes( s, packet ):

    ## 'packet' is a block of raw, unprocessed bytes. We make a chunk out of it
    ## and feed that to the real chunk sink.
    
    s.feedChunk( ByteChunk( packet ) )
    
    ## Then we notify the filters that this is the end of the packet.

    s.feedChunk( theEndOfPacketChunk )
  

  def feedChunk( s, chunk ):
  
    if not s.filters:
      return

    s.filters[0].feedChunk( chunk )

    ## When the above call returns, the chunk as been fully processed through
    ## the chain of filters, and the resulting chunks are waiting in the
    ## output bucket. So we can flush it.

    s.flushOutputBuffer()
  
  
  def appendToOutputBuffer( s, chunk ):
  
    s.outputBuffer.append( chunk )
  
  
  def flushOutputBuffer( s ):
  
    s.sinks.triggerAll( s.outputBuffer )

    s.outputBuffer = []

    
  def addFilter( s, filterclass, *params, **kwargs ):

    kwargs.setdefault( 'context', s )

    filter = filterclass( *params, **kwargs )

    filter.setSink( s.appendToOutputBuffer )

    if s.filters:
      s.filters[-1].setSink( filter.feedChunk )

    s.filters.append( filter )


  def addSink( s, callback ):

    ## 'callback' should be a callable that takes a list of chunks.
    s.sinks.add( callback )


  def formatForSending( s, data ):

   for filter in reversed( s.filters ):
      data = filter.formatForSending( data )

   return data


  def resetInternalState( s ):

    for f in s.filters:
      f.resetInternalState()


  def notify( s, notification, *args ):

    callbacks = s.notification_registry.get( notification )

    if callbacks:
      callbacks.triggerAll( *args )


  def bindNotificationListener( s, notification, callback ):

    if notification not in s.notification_registry:
      s.notification_registry[ notification ] = CallbackRegistry()

    s.notification_registry[ notification ].add( callback )


  def __del__( s ):

    s.parent  = None
    s.filters = None
    s.sinks   = None

    s.notification_registry = None
