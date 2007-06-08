##
## PipelineFilters.py
##
## This file holds the various filter classes that will parse chunks of data
## and move them through the pipeline.
##


from PipelineChunks import *

## ---[ Class BaseFilter ]---------------------------------------------

class BaseFilter:

  ## This class attribute lists the chunk types that this filter will process.
  ## Those unlisted will be passed down the filter chain untouched.
  relevant_types = []
  

  def __init__( s, context=None ):

    s.context        = context
    s.postponedChunk = []
    s.sinks          = []


  def setContext( s, context ):

    s.context = context


  def addSink( s, sink ):

    s.sinks.append( sink )


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


  def concatPostponed( s, chunk ):

    if chunk is theEndOfPacketChunk:
      ## The End Of Packet chunk is a special case, and is never merged
      ## with other chunks.
      return chunk
      
    if not s.postponedChunk:
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
      s.sendChunkDownstream( postponed )

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
      
    else:
      chunks = [ chunk ]
    
    for chunk, nextChunk in iter_and_peek_next( chunks ):
    
#      if nextChunk is endOfIterationMarker:
#        chunk.lastOfPacket = True
        
      s.sendChunkDownstream( chunk )


  def sendChunkDownstream( s, chunk ):

    for sink in s.sinks:
      sink( chunk )



## ---[ Class EndLineFilter ]------------------------------------------

class EndLineFilter( BaseFilter ):
  
  relevant_types = [ chunktypes.BYTES ]
  
  def processChunk( s, chunk ):
    
    assert chunk.chunktype == chunktypes.BYTES
    
    text = chunk.data

    if text.endswith( "\r" ):
      s.postpone( chunk )
      done()
    
    while len( text ) > 0:

      i = text.find( "\r\n" )
      
      if i == -1:
        yield ByteChunk( text )
        break
      
      else:
        
        if i != 0:
          yield ByteChunk( text[ :i ] )
         
        text = text[ i+2: ]
        yield theEndLineChunk




## ---[ Class UnicodeTextFilter ]--------------------------------------

class UnicodeTextFilter( BaseFilter ):
  
  relevant_types = [ chunktypes.BYTES ]
  
  def __init__(s, *args):
    
    s.encoding = "ascii"
    BaseFilter.__init__( s, *args )


  def processChunk( s, chunk ):
 
    ## FIXME: this may break if the chunk ends with an unfinished UTF-8
    ## sequence. I.e., the character whose UTF-8 encoding is split over
    ## two packets (is that even possible?), would be ignored.
    ## Waiting for an end of line might suffice, though!
 
    if chunk.chunktype == chunktypes.BYTES:
      chunk = UnicodeTextChunk( chunk.data.decode( s.encoding, "ignore" ) )
    
    yield chunk



## TODO: Implement TelnetFilter and AnsiFilter.

