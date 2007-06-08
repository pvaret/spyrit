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

    s.firstFilter  = None
    s.lastFilter   = None
    s.sinks        = []
    s.outputBuffer = []


  def feedBytes( s, packet ):
    ## 'packet' is a block of raw, unprocessed bytes. We make a chunk out of it
    ## and feed that to the real chunk sink.
    
    s.feedChunk( ByteChunk( packet ) )
    
    ## Then we notify the filters that this is the end of the packet.
    s.feedChunk( theEndOfPacketChunk )
  

  def feedChunk( s, chunk ):
  
    s.firstFilter.feedChunk( chunk )
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
    
    if not s.firstFilter:
      s.firstFilter = s.lastFilter = filter
      
    else:
      s.lastFilter.addSink( filter.feedChunk )
      s.lastFilter = filter


  def finalize(s):
    
    s.lastFilter.addSink( s.appendToOutputBuffer )


  def addSink( s, callback ):
    ## 'callback' should be a callable that takes a list of chunks.
    s.sinks.append( callback )


## ---[ Main ]---------------------------------------------------------

if __name__ == '__main__':

  pipe = Pipeline()
  
  pipe.addFilter( BaseFilter() )
  pipe.addFilter( EndLineFilter() )
  pipe.addFilter( UnicodeTextFilter() )
  pipe.finalize()
  
  def output( chunks ):
    for chunk in chunks:
      if chunk.chunktype != chunktypes.ENDOFPACKET:
        print chunk
  
  pipe.addSink( output )
  print "Begin..."

  pipe.feedBytes( "Ceci est un test." )
  pipe.feedBytes( "Mrehw!\r\n\r" )
  pipe.feedBytes( "\nMrahw!\r\n" )
  pipe.feedBytes( "Plus dur maintenant." )
  pipe.feedBytes( "\r" )
  pipe.feedBytes( "\n" )

