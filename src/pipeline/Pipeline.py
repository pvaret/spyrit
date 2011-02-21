# -*- coding: utf-8 -*-

## Copyright (c) 2007-2011 Pascal Varet <p.varet@gmail.com>
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


from localqt import *

import ChunkData

from SingleShotTimer  import SingleShotTimer
from CallbackRegistry import CallbackRegistry


class Pipeline( QtCore.QObject ):

  PROMPT_TIMEOUT = 700 ## ms


  def __init__( s ):

    QtCore.QObject.__init__( s )

    s.filters      = []
    s.outputBuffer = []
    s.sinks        = dict( ( type, CallbackRegistry() )
                           for type in ChunkData.chunk_type_list() )

    s.notification_registry = {}

    s.prompt_timer = SingleShotTimer( s.sweepPrompt )
    s.prompt_timer.setInterval( s.PROMPT_TIMEOUT )


  def feedBytes( s, packet, blocksize=2048 ):

    ## 'packet' is a block of raw, unprocessed bytes. We make a chunk out of it
    ## and feed that to the real chunk sink.

    while packet:

      bytes, packet = packet[ :blocksize ], packet[ blocksize: ]

      s.feedChunk( ChunkData.thePacketStartChunk, autoflush=False )
      s.feedChunk( ( ChunkData.BYTES, bytes ), autoflush=False )
      s.feedChunk( ChunkData.thePacketEndChunk )

    s.prompt_timer.start()


  def sweepPrompt( s ):

    s.feedChunk( ChunkData.thePromptSweepChunk )


  def feedChunk( s, chunk, autoflush=True ):

    if not s.filters:
      return

    s.filters[0].feedChunk( chunk )

    ## When the above call returns, the chunk as been fully processed through
    ## the chain of filters, and the resulting chunks are waiting in the
    ## output bucket. So we can flush it.

    if autoflush:
      s.flushOutputBuffer()


  def appendToOutputBuffer( s, chunk ):

    s.outputBuffer.append( chunk )


  def flushOutputBuffer( s ):

    s.emit( SIGNAL( "flushBegin()" ) )

    for chunk in s.outputBuffer:

      chunk_type, _ = chunk
      s.sinks[ chunk_type ].triggerAll( chunk )

    s.emit( SIGNAL( "flushEnd()" ) )

    s.outputBuffer = []


  def addFilter( s, filterclass, **kwargs ):

    kwargs.setdefault( 'context', s ) ## Set up context if not already present.

    filter = filterclass( **kwargs )

    filter.setSink( s.appendToOutputBuffer )

    if s.filters:
      s.filters[-1].setSink( filter.feedChunk )

    s.filters.append( filter )


  def addSink( s, callback, types=ChunkData.ALL_TYPES ):

    ## 'callback' should be a callable that accepts and handles a chunk.

    for type in ChunkData.chunk_type_list():

      if type & types:
        s.sinks[ type ].add( callback )


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

    s.filters = None
    s.sinks   = None

    s.notification_registry = None
