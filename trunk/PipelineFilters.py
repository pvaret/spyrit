##
## PipelineFilters.py
##
## This file holds the various filter classes that will parse chunks of data
## and move them through the pipeline.
##

import re

from PipelineChunks import *

## ---[ Class BaseFilter ]---------------------------------------------

class BaseFilter:

  ## This class attribute lists the chunk types that this filter will process.
  ## Those unlisted will be passed down the filter chain untouched.
  relevant_types = []
  

  def __init__( s, context=None ):

    s.sink           = None
    s.context        = context
    s.postponedChunk = []


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


## ---[ Class AnsiFilter ]---------------------------------------------

class AnsiFilter( BaseFilter ):

  relevant_types = [ chunktypes.BYTES ]

  ## For the time being, we only catch the SGR (Set Graphics Rendition) part
  ## of the ECMA 48 specification (a.k.a. ANSI escape codes).

  ESC   = "\x1b"
  CSI8b = "\x9b"

  CSI = "(" + ESC + r"\[" + "|" + CSI8b + ")"

  match = re.compile( CSI + r"(\d+;?)*" + "m" )

  unfinished = re.compile( "|".join( [ "(" + code + "$)" for code in
                               ESC,
                               CSI + r"[\d;]*"
                         ] ) )

  def processChunk( s, chunk ):
    
    text = chunk.data

    while len( text ) > 0:

      ansi = s.match.search( text )
      
      if ansi:

        head = text[ :ansi.start() ]
        tail = text[ ansi.end():   ]

        text = tail

        if head:
          yield ByteChunk( head )

        parameters = ansi.groups()[ 1 ]

        if not parameters:
          parameters = "0"  ## ESC [ m is an alias for ESC [ 0 m.

        for param in parameters.split( ';' ):

          format = FormatChunk.ANSI_TO_FORMAT.get( param )

          if format:
            yield( FormatChunk( format ) )

      else:
        ## The remaining text doesn't contain any complete ANSI sequence.
        ## So we quit the loop.
        break

    if text:
      
      if s.unfinished.search( text ): ## Remaining text is an unfinished ANSI
                                      ## sequence!
        s.postpone( ByteChunk( text ) )
        
      else:
        yield( ByteChunk( text ) )






## ---[ Class EndLineFilter ]------------------------------------------

class EndLineFilter( BaseFilter ):
  
  relevant_types = [ chunktypes.BYTES ]

  match      = re.compile( r'(\r\n)|\n' )
  unfinished = "\r"

  def processChunk( s, chunk ):
    
    text = chunk.data

    while len( text ) > 0:

      cr = s.match.search( text )
      
      if cr:
        head = text[ :cr.start() ]
        tail = text[ cr.end():   ]

        text = tail

        if head:
          yield ByteChunk( head )

        yield theEndOfLineChunk

      else:
        ## The remaining text doesn't contain any identifiable carriage
        ## return. So we quit the loop.
        break

    if text:
      
      if text.endswith( s.unfinished ):
        s.postpone( ByteChunk( text ) )
        
      else:
        yield( ByteChunk( text ) )


## ---[ Class UnicodeTextFilter ]--------------------------------------

class UnicodeTextFilter( BaseFilter ):
  
  relevant_types = [ chunktypes.BYTES ]
  
  def __init__(s, *args):
    
    BaseFilter.__init__( s, *args )
    s.encoding = "ascii"


  def processChunk( s, chunk ):
 
    ## FIXME: this may break if the chunk ends with an unfinished UTF-8
    ## sequence. I.e., the character whose UTF-8 encoding is split over
    ## two packets (is that even possible?), would be ignored.
    ## Mostly a theorical concern, though, since the default encoding here is
    ## ASCII.
 
    if chunk.chunktype == chunktypes.BYTES:
      chunk = UnicodeTextChunk( chunk.data.decode( s.encoding, "ignore" ) )
    
    yield chunk



## TODO: Implement TelnetFilter and AnsiFilter.

