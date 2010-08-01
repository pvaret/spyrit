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
## Pipeline.py
##
## This file defines the class Pipeline, which manages the tokenization of
## a network stream into typed chunks: telnet code, ANSI code, etc...
## It works by assembling a series of Filters.
##


from localqt import *

from PipelineChunks   import ByteChunk
from PipelineChunks   import thePacketStartChunk, thePacketEndChunk
from PipelineChunks   import thePromptSweepChunk
from PipelineChunks   import chunktypes
from CallbackRegistry import CallbackRegistry


class Pipeline:

  PROMPT_TIMEOUT = 700 ## ms


  def __init__( s, parent=None ):

    s.parent       = parent
    s.filters      = []
    s.outputBuffer = []
    s.sinks        = dict( ( type, CallbackRegistry() )
                           for type in chunktypes.list() )

    s.notification_registry = {}

    s.prompt_timer = QtCore.QTimer()
    s.prompt_timer.setSingleShot( True )
    s.prompt_timer.setInterval( s.PROMPT_TIMEOUT )
    connect( s.prompt_timer, SIGNAL( "timeout()" ), s.sweepPrompt )


  def feedBytes( s, packet ):

    ## 'packet' is a block of raw, unprocessed bytes. We make a chunk out of it
    ## and feed that to the real chunk sink.

    s.feedChunk( thePacketStartChunk )
    s.feedChunk( ByteChunk( packet ) )

    ## Then we notify the filters that this is the end of the packet.

    s.feedChunk( thePacketEndChunk )
    s.prompt_timer.start()


  def sweepPrompt( s ):

    s.feedChunk( thePromptSweepChunk )


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

    for chunk in s.outputBuffer:
      s.sinks[ chunk.chunktype ].triggerAll( chunk )

    s.outputBuffer = []


  def addFilter( s, filterclass, **kwargs ):

    kwargs.setdefault( 'context', s ) ## Set up context if not already present.

    filter = filterclass( **kwargs )

    filter.setSink( s.appendToOutputBuffer )

    if s.filters:
      s.filters[-1].setSink( filter.feedChunk )

    s.filters.append( filter )


  def addSink( s, callback, types=chunktypes.ALL_TYPES ):

    ## 'callback' should be a callable that accepts and handles a chunk.

    for type in chunktypes.list():

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

    s.parent  = None
    s.filters = None
    s.sinks   = None

    s.notification_registry = None
