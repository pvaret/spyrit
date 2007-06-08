##
## PipelineChunks.py
##
## This file holds the various types of chunks that are going to be treated
## through our pipeline.
##


from IterHelpers import iter_and_peek_next, endOfIterationMarker, done

## ---[ Exception ChunkTypeMismatch ]----------------------------------


class ChunkTypeMismatch( Exception ):
  """
  Exception ChunkTypeMismatch
  
  Raised when a combining operation is attempted on two chunks of incompatible
  types.
  """
  pass



## ---[ Class ChunkTypes ]---------------------------------------------

class ChunkTypes:

  NETWORK     = 0
  ENDOFPACKET = 1
  BYTES       = 2
  TELNET      = 3
  ANSI        = 4
  ENDLINE     = 5
  TEXT        = 6


  def __init__( s ):
    
    ## The following is an ugly hack to generate the reverse mapping from value
    ## to chunk type name based on the above information.
    ## It allows you to look up ChunkTypes by value, for instance:
    ## ChunkType.name[ 0 ] returns the string "NETWORK"
    ## This is mostly intended for debugging purposes.
    
    IntegerType = type( 1 )
    
    chunkTypeList = [ name for name in dir( ChunkTypes )
                      if  name.isalpha()
                      and name.isupper()
                      and type( getattr( ChunkTypes, name ) ) is IntegerType ]
    
    s.name = dict( ( getattr( ChunkTypes, name ), name ) 
                             for name in chunkTypeList )

chunktypes = ChunkTypes()


## ---[ Class BaseChunk ]----------------------------------------------

class BaseChunk:
  """
  This is the base class for all chunks. It should never be used on its own.
  """

  chunktype = None

  def __init__( s, data=None ):

    s.data = data


  def concat( s, other ):
  
    if s.chunktype != other.chunktype:
    
      chunktypename      = chunktypes.name[     s.chunktype ]
      otherchunktypename = chunktypes.name[ other.chunktype ]
      
      raise ChunkTypeMismatch( "Trying to concat %s chunk with %s chunk!" % \
                               ( chunktypename, otherchunktypename ) )
    
    ## The chunks are compatible, so we concatenate their data.
    ## We just need to be careful in case one of the two is None,
    ## because None and strings don't add up too well.
    if s.data is None:
      s.data = other.data or None

    else:
      s.data += other.data or ""


  def __repr__( s ):

    chunktype = chunktypes.name[ s.chunktype ]

    if s.data:
      return '<Chunk Type: %s; Data: "%s">' % ( chunktype, s.data )
      
    else:
      return '<Chunk Type: %s>' % chunktype


## ---[ Class ByteChunk ]----------------------------------------------

class ByteChunk( BaseChunk ):
  """
  This chunk type represents a chunk of raw bytes, typically ASCII
  characters, but telnet or ANSI codes or otherwise can also be encoded in
  there. Those will have to be decoded at some point through the pipeline.
  """

  chunktype = chunktypes.BYTES


## ---[ Class UnicodeTextChunk ]---------------------------------------

class UnicodeTextChunk( BaseChunk ):
  
  chunktype = chunktypes.TEXT


## ---[ Class EndOfPacketChunk ]---------------------------------------

class EndOfPacketChunk( BaseChunk ):
  """
  This chunk type represents the end of a given packet. It is necessary
  because some filters in the pipeline need to be informed that the current
  packet is done, so they can wrap up their processing.
  """

  chunktype = chunktypes.ENDOFPACKET

theEndOfPacketChunk = EndOfPacketChunk()


## ---[ Class EndLineChunk ]-------------------------------------------

class EndLineChunk( BaseChunk ):
  
  chunktype = chunktypes.ENDLINE

theEndLineChunk = EndLineChunk()

