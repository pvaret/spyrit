##
## Pipeline.py
##
## This file defines the class Pipeline, which manages the tokenization of
## a network stream into typed chunks: telnet code, ANSI code, etc...
## It works by assembling a series of Filters.
##


from Helpers import iter_and_peek_next, endOfIterationMarker, done




## ---[ Exception ChunkTypeMismatch ]----------------------------------


class ChunkTypeMismatch(Exception):
  """
  Exception ChunkTypeMismatch
  
  Raised when a combinating operation is attempted on two chunks of incompatible
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

  def __init__(s):
    
    ## The following is an ugly hack to generate the reverse mapping from value
    ## to chunk type name based on the above information.
    ## It allows you to look up ChunkTypes by value, for instance:
    ## ChunkType.name[0] returns the string "NETWORK"
    ## This is mostly intended for debugging purposes.
    
    IntegerType = type(1)
    
    chunkTypeList = [name for name in dir(ChunkTypes)
                      if  name.isalpha()
                      and name.isupper()
                      and type(getattr(ChunkTypes, name)) is IntegerType]
    
    s.name = dict([(getattr(ChunkTypes, name), name) for name in chunkTypeList])

chunktypes = ChunkTypes()


## ---[ Class BaseChunk ]----------------------------------------------

class BaseChunk:
  """
  This chunk type represents a chunk of raw bytes, typically ASCII
  characters, but telnet or ANSI codes or otherwise can also be encoded in
  there. Those will have to be decoded at some point through the pipeline.
  """

  chunktype = chunktypes.BYTES

  def __init__(s, data=None):

    s.data = data
#    s.lastOfPacket = False


  def merge(s, otherchunk):
  
    if s.chunktype != otherchunk.chunktype:
    
      chunktypename      = chunktypes.name[         s.chunktype]
      otherchunktypename = chunktypes.name[otherchunk.chunktype]
      
      raise ChunkTypeMismatch("Trying to merge %s chunk with %s chunk!" % \
            (chunktypename, otherchunktypename))
    
    ## The chunks are compatible, so we concatenate their data.
    ## We just need to be careful in case one of the two is None,
    ## because None and strings don't add up too well.
    if s.data is None:
      s.data = otherchunk.data or None
    else:
      s.data += otherchunk.data or ""


  def __repr__(s):

    chunktype = chunktypes.name[s.chunktype]

    if s.data:
      return '<Chunk Type: %s; Data: "%s">' % (chunktype, s.data)
      
    else:
      return '<Chunk Type: %s>' % chunktype


## ---[ Class EndOfPacketChunk ]---------------------------------------

class EndOfPacketChunk(BaseChunk):
  """
  This chunk type represents the end of a given packet. It is necessary
  because some filters in the pipeline need to be informed that the current
  packet is done, so they can wrap up their processing.
  """

  chunktype = chunktypes.ENDOFPACKET

theEndOfPacketChunk = EndOfPacketChunk()


## ---[ Class UnicodeTextChunk ]---------------------------------------

class UnicodeTextChunk(BaseChunk):
  
  chunktype = chunktypes.TEXT


## ---[ Class EndLineChunk ]-------------------------------------------

class EndLineChunk(BaseChunk):
  
  chunktype = chunktypes.ENDLINE

theEndLineChunk = EndLineChunk()


## ---[ Class BaseFilter ]---------------------------------------------

class BaseFilter:

  ## This class attribute lists the chunk types that this filter will process.
  ## Those unlisted will be passed down the filter chain untouched.
  relevant_types = []
  

  def __init__(s):

    s.downstreamCallbacks = []
#    s.nextDownstreamChunk = None
    s.context = None
    s.postponedChunk = []


  def setContext(s, context):

    s.context = context


  def attachDownstreamSink(s, chunksink):

    s.downstreamCallbacks.append(chunksink)


  def postpone(s, chunk):

    if s.postponedChunk:
      raise Exception("Whoa, there should NOT be a chunk in there already...")
    
    else:
      s.postponedChunk = chunk



  def processChunk(s, chunk):
    ## This is the default implementation, which does nothing.
    ## Override this to implement your filter.
    ## Note that this must be a generator or return a list.
    yield chunk


  def mergePostponed(s, chunk):

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
      postponed.merge(chunk)
      chunk = postponed
      
    except ChunkTypeMismatch:
      ## If they're incompatible, it means the postponed chunk was really
      ## complete, so we send it downstream.
      s.sendChunkDownstream(postponed)

    return chunk


  def feedIn(s, chunk):
    
    chunk = s.mergePostponed(chunk)
    
    ## At this point, the postponed chunk has either been merged with
    ## the new one, or been sent downstream. At any rate, it's been dealt
    ## with, and s.postponedChunk is empty.
    ## This mean that the postponed chunk should ALWAYS have been cleared
    ## when processChunk() is called. If not, there's something shifty
    ## going on...
    
    if chunk.chunktype in s.relevant_types:
      chunks = s.processChunk(chunk)
      
    else:
      chunks = [chunk]
    
    for chunk, nextChunk in iter_and_peek_next(chunks):
    
#      if nextChunk is endOfIterationMarker:
#        chunk.lastOfPacket = True
        
      s.sendChunkDownstream(chunk)


  def sendChunkDownstream(s, chunk):

    for chunkeater in s.downstreamCallbacks:
      chunkeater(chunk)



## ---[ Class EndLineFilter ]------------------------------------------

class EndLineFilter(BaseFilter):
  
  relevant_types = [chunktypes.BYTES]
#  markers = ("\r\n", "\n")
  
  def processChunk(s, chunk):
    
    assert chunk.chunktype == chunktypes.BYTES
    
    text = chunk.data
    if text.endswith("\r"):
      s.postpone(chunk)
      done()
    
    while len(text) > 0:

      i = text.find("\r\n")
      
      if i == -1:
        yield BaseChunk(text)
        break
      
      else:
        
        if i != 0:
          yield BaseChunk(text[:i])
         
        text = text[i+2:]
        yield theEndLineChunk




## ---[ Class UnicodeTextFilter ]--------------------------------------

class UnicodeTextFilter(BaseFilter):
  
  relevant_types = [chunktypes.BYTES]
  
  def __init__(s, *args):
    
    s.encoding = "ascii"
    BaseFilter.__init__(s, *args)


  def processChunk(s, chunk):
 
    ## FIXME: this may break if the chunk ends with an unfinished UTF-8
    ## sequence. I.e., the character whose UTF-8 encoding is split over
    ## two packets (is that even possible?), would be ignored.
    ## Waiting for an end of line might suffice, though!
 
    if chunk.chunktype == chunktypes.BYTES:
      chunk = UnicodeTextChunk(chunk.data.decode(s.encoding, "ignore"))
    
    yield chunk



## TODO: Implement TelnetFilter and AnsiFilter.


## ---[ Class Pipeline ]-----------------------------------------------

class Pipeline:
  
  def __init__(s):

    s.firstFilter = None
    s.lastFilter = None
    s.downstreamCallbacks = []
    s.downstreamBucket = []
    s.isLastChunk = False


  def feedPacketIn(s, packet):
    ## 'packet' is a block of raw, unprocessed bytes. We make a chunk out of it
    ## and feed that to the real chunk sink.
    
    s.feedIn(BaseChunk(packet))
    
    ## Then we notify the filters that this is the end of the packet.
    s.feedIn(theEndOfPacketChunk)
  

  def feedIn(s, chunk):
  
    s.firstFilter.feedIn(chunk)
    s.notifyDownstreamBucketFull()
  
  
  def storeIntoDownstreamBucket(s, chunk):
  
    s.downstreamBucket.append(chunk)
  
  
  def notifyDownstreamBucketFull(s):
  
    for callback in s.downstreamCallbacks:
      callback(s.downstreamBucket)

    s.downstreamBucket = []

    
  def addFilter(s, filter):

    filter.setContext(s)
    
    if not s.firstFilter:
      s.firstFilter = s.lastFilter = filter
      
    else:
      s.lastFilter.attachDownstreamSink(filter.feedIn)
      s.lastFilter = filter


  def finalize(s):
    
    s.lastFilter.attachDownstreamSink(s.storeIntoDownstreamBucket)


  def attachDownstreamSink(s, callback):
    ## 'callback' should be a callable that takes a list of chunks.
    s.downstreamCallbacks.append(callback)


## ---[ Main ]---------------------------------------------------------

if __name__ == '__main__':

  pipe = Pipeline()
  
  pipe.addFilter(BaseFilter())
  pipe.addFilter(EndLineFilter())
  pipe.addFilter(UnicodeTextFilter())
  pipe.finalize()
  
  def output(chunks):
    for chunk in chunks:
      if chunk.chunktype != chunktypes.ENDOFPACKET:
        print chunk
  
  pipe.attachDownstreamSink(output)
  print "Begin..."

  pipe.feedPacketIn("Ceci est un test.")
  pipe.feedPacketIn("Mrehw!\r\nMrahw!\r\n")
  pipe.feedPacketIn("Plus dur maintenant.")
  pipe.feedPacketIn("\r")
  pipe.feedPacketIn("\n")

