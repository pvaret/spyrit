# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
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
## PipelineChunks.py
##
## This file holds the various types of chunks that are going to be treated
## through our pipeline.
##


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
  FORMAT      = 4
  ENDOFLINE   = 5
  TEXT        = 6


  def __init__( s ):
    
    ## The following is an ugly hack to generate the reverse mapping from value
    ## to chunk type name based on the above information.
    ## It allows you to look up ChunkTypes by value, for instance:
    ## ChunkType.name[0] returns the string "NETWORK"
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
  This is the base class for all chunks. It should never be used on its own;
  use a subclass instead.
  """

  chunktype = None

  def __init__( s, data=None ):

    s.data = data


  def concat( s, other ):
  
    ## Only chunks of the same type and whose data are strings can be
    ## concatenated.
    if s.chunktype != other.chunktype \
                   or type( other.data ) not in ( type( "" ), type( u"" ) ):
    
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


## ---[ Class FormatChunk ]--------------------------------------------

class FormatChunk( BaseChunk ):
  """
  This chunk type represents a formatting parameter, typically extracted from
  an ANSI SGR escape sequences, although they might conceivably come from
  other sources such as MXP codes.
  """

  chunktype = chunktypes.FORMAT

  ANSI_MAPPING = (
    ( "0",  ( "RESET",     None ) ),
    ( "1",  ( "BOLD",      True ) ),
    ( "3",  ( "ITALIC",    True ) ),
    ( "4",  ( "UNDERLINE", True ) ),
    ( "22", ( "BOLD",      False ) ),
    ( "23", ( "ITALIC",    False ) ),
    ( "24", ( "UNDERLINE", False ) ),
    ( "30", ( "FG",       "BLACK" ) ),
    ( "31", ( "FG",       "RED" ) ),
    ( "32", ( "FG",       "GREEN" ) ),
    ( "33", ( "FG",       "YELLOW" ) ),
    ( "34", ( "FG",       "BLUE" ) ),
    ( "35", ( "FG",       "MAGENTA" ) ),
    ( "36", ( "FG",       "CYAN" ) ),
    ( "37", ( "FG",       "WHITE" ) ),
    ( "39", ( "FG",       "DEFAULT" ) ),
    ( "40", ( "BG",       "BLACK" ) ),
    ( "41", ( "BG",       "RED" ) ),
    ( "42", ( "BG",       "GREEN" ) ),
    ( "43", ( "BG",       "YELLOW" ) ),
    ( "44", ( "BG",       "BLUE" ) ),
    ( "45", ( "BG",       "MAGENTA" ) ),
    ( "46", ( "BG",       "CYAN" ) ),
    ( "47", ( "BG",       "WHITE" ) ),
    ( "49", ( "BG",       "DEFAULT" ) ),
  )

  ANSI_TO_FORMAT = dict( ANSI_MAPPING )


## ---[ Class UnicodeTextChunk ]---------------------------------------

class UnicodeTextChunk( BaseChunk ):
  
  chunktype = chunktypes.TEXT


## ---[ Class NetworkChunk ]-------------------------------------------

class NetworkChunk( BaseChunk ):
  
  chunktype = chunktypes.NETWORK

  DISCONNECTED  = 0
  RESOLVING     = 1
  CONNECTING    = 2
  CONNECTED     = 3
  ENCRYPTED     = 4
  DISCONNECTING = 5

  CONNECTIONREFUSED = 6
  HOSTNOTFOUND      = 7
  TIMEOUT           = 8
  OTHERERROR        = 9


  def __init__( s, data ):

    ## The following is an ugly hack to generate the reverse mapping from value
    ## to network state, as above.

    IntegerType = type( 1 )

    stateList = [ name for name in dir( NetworkChunk )
                    if  name.isalpha()
                    and name.isupper()
                    and type( getattr( NetworkChunk, name ) ) is IntegerType ]

    s.states = dict( ( getattr( NetworkChunk, name ), name )
                                     for name in stateList )


    BaseChunk.__init__( s, data )


  def __repr__( s ):

    chunktype = chunktypes.name[ s.chunktype ]
    return '<Chunk Type: %s; State: %s>' % ( chunktype, s.states[ s.data ] )


## ---[ Class EndOfPacketChunk ]---------------------------------------

class EndOfPacketChunk( BaseChunk ):
  """
  This chunk type represents the end of a given packet. It is necessary
  because some filters in the pipeline need to be informed that the current
  packet is done, so they can wrap up their processing.
  """

  chunktype = chunktypes.ENDOFPACKET


theEndOfPacketChunk = EndOfPacketChunk()


## ---[ Class EndOfLineChunk ]-----------------------------------------

class EndOfLineChunk( BaseChunk ):
  
  chunktype = chunktypes.ENDOFLINE


theEndOfLineChunk = EndOfLineChunk()

