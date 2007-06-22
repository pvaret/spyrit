##
## Pipeline.py
##
## This file defines the class Pipeline, which manages the tokenization of
## a network stream into typed chunks: telnet code, ANSI code, etc...
## It works by assembling a series of Filters.
##


from PipelineChunks  import *
from PipelineFilters import *

## ---[ Class Pipeline ]-----------------------------------------------

class Pipeline:
  
  def __init__(s):

    s.filters      = []
    s.sinks        = []
    s.outputBuffer = []


  def feedBytes( s, packet ):
    ## 'packet' is a block of raw, unprocessed bytes. We make a chunk out of it
    ## and feed that to the real chunk sink.
    
    s.feedChunk( ByteChunk( packet ) )
    
    ## Then we notify the filters that this is the end of the packet.
    s.feedChunk( theEndOfPacketChunk )
  

  def feedChunk( s, chunk ):
  
    if not s.filters:
      return

    s.filters[ 0 ].feedChunk( chunk )

    ## When the above call returns, the chunk as been fully processed through
    ## the chain of filters, and the resulting chunks are waiting in the
    ## output bucket. So we can flush it.

    s.flushOutputBuffer()
  
  
  def appendToOutputBuffer( s, chunk ):
  
    s.outputBuffer.append( chunk )
  
  
  def flushOutputBuffer( s ):
  
    for callback in s.sinks:
      callback( s.outputBuffer )

    s.outputBuffer = []

    
  def addFilter( s, filter ):

    filter.setContext( s )
    filter.setSink( s.appendToOutputBuffer )

    if s.filters:
      s.filters[ -1 ].setSink( filter.feedChunk )

    s.filters.append( filter )


  def addSink( s, callback ):

    ## 'callback' should be a callable that takes a list of chunks.
    s.sinks.append( callback )


  def formatForSending( s, data ):

   for filter in reversed( s.filters ):
      data = filter.formatForSending( data )

   return data
