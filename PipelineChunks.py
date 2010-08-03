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
## PipelineChunks.py
##
## This file holds the various types of chunks that are going to be treated
## through our pipeline.
##


class ChunkTypeMismatch( Exception ):
  """
  Exception ChunkTypeMismatch

  Raised when a combining operation is attempted on two chunks of incompatible
  types.
  """
  pass



## Define chunk types:

class ChunkTypes:

  NETWORK     = 1 << 0
  PACKETBOUND = 1 << 1
  PROMPTSWEEP = 1 << 2
  BYTES       = 1 << 3
  TELNET      = 1 << 4
  ANSI        = 1 << 5
  FLOWCONTROL = 1 << 6
  TEXT        = 1 << 7
  HIGHLIGHT   = 1 << 8

  ALL_TYPES   = ( 1 << 9 ) - 1


  ## The following is an ugly hack to generate the reverse mapping from value
  ## to chunk type name based on the above information.

  @classmethod
  def name( cls, chunk_type ):

    chunk_names = dict( ( getattr( cls, name ), name )
                        for name in dir( cls )
                        if name.isalpha()
                           and name.isupper()
                           and type( getattr( cls, name ) ) is int )

    return chunk_names.get( chunk_type )


  @classmethod
  def list( cls ):

    type = 0x01

    while type < cls.ALL_TYPES:

      yield type
      type = type << 1




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

      chunktypename      = ChunkTypes.name(     s.chunktype )
      otherchunktypename = ChunkTypes.name( other.chunktype )

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

    chunktype = ChunkTypes.name( s.chunktype )

    if s.data is not None:
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

  chunktype = ChunkTypes.BYTES


## ---[ Class FormatChunk ]--------------------------------------------

from Globals import FORMAT_PROPERTIES
from Globals import ANSI_COLORS as COL

class FormatChunk( BaseChunk ):
  """
  This chunk type represents a formatting parameter, typically extracted from
  an ANSI SGR escape sequences, although they might conceivably come from
  other sources such as MXP codes.
  """

  chunktype = ChunkTypes.ANSI

  ANSI_MAPPING = (
    ( "1",  ( FORMAT_PROPERTIES.BOLD,      True ) ),
    ( "3",  ( FORMAT_PROPERTIES.ITALIC,    True ) ),
    ( "4",  ( FORMAT_PROPERTIES.UNDERLINE, True ) ),
    ( "22", ( FORMAT_PROPERTIES.BOLD,      False ) ),
    ( "23", ( FORMAT_PROPERTIES.ITALIC,    False ) ),
    ( "24", ( FORMAT_PROPERTIES.UNDERLINE, False ) ),
    ( "30", ( FORMAT_PROPERTIES.COLOR, ( COL.black,     COL.darkgray ) ) ),
    ( "31", ( FORMAT_PROPERTIES.COLOR, ( COL.red,       COL.red_h ) ) ),
    ( "32", ( FORMAT_PROPERTIES.COLOR, ( COL.green,     COL.green_h ) ) ),
    ( "33", ( FORMAT_PROPERTIES.COLOR, ( COL.yellow,    COL.yellow_h ) ) ),
    ( "34", ( FORMAT_PROPERTIES.COLOR, ( COL.blue,      COL.blue_h ) ) ),
    ( "35", ( FORMAT_PROPERTIES.COLOR, ( COL.magenta,   COL.magenta_h ) ) ),
    ( "36", ( FORMAT_PROPERTIES.COLOR, ( COL.cyan,      COL.cyan_h ) ) ),
    ( "37", ( FORMAT_PROPERTIES.COLOR, ( COL.lightgray, COL.white ) ) ),
    ( "39", ( FORMAT_PROPERTIES.COLOR, ( None,          COL.white ) ) ),
    ( "40", ( FORMAT_PROPERTIES.BACKGROUND, COL.black ) ),
    ( "41", ( FORMAT_PROPERTIES.BACKGROUND, COL.red ) ),
    ( "42", ( FORMAT_PROPERTIES.BACKGROUND, COL.green ) ),
    ( "43", ( FORMAT_PROPERTIES.BACKGROUND, COL.yellow ) ),
    ( "44", ( FORMAT_PROPERTIES.BACKGROUND, COL.blue ) ),
    ( "45", ( FORMAT_PROPERTIES.BACKGROUND, COL.magenta ) ),
    ( "46", ( FORMAT_PROPERTIES.BACKGROUND, COL.cyan ) ),
    ( "47", ( FORMAT_PROPERTIES.BACKGROUND, COL.white ) ),
    ( "49", ( FORMAT_PROPERTIES.BACKGROUND, None ) ),
  )

  ANSI_TO_FORMAT = dict( ANSI_MAPPING )


## ---[ Class UnicodeTextChunk ]---------------------------------------

class UnicodeTextChunk( BaseChunk ):

  chunktype = ChunkTypes.TEXT


## ---[ Class NetworkChunk ]-------------------------------------------

class NetworkChunk( BaseChunk ):

  chunktype = ChunkTypes.NETWORK

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

    stateList = [ name for name in dir( NetworkChunk )
                    if  name.isalpha()
                    and name.isupper()
                    and type( getattr( NetworkChunk, name ) ) is int ]

    s.states = dict( ( getattr( NetworkChunk, name ), name )
                                     for name in stateList )


    BaseChunk.__init__( s, data )


  def __repr__( s ):

    chunktype = ChunkTypes.name( s.chunktype )
    return '<Chunk Type: %s; State: %s>' % ( chunktype, s.states[ s.data ] )


## ---[ Class PacketBoundChunk ]---------------------------------------

class PacketBoundChunk( BaseChunk ):
  """
  This chunk type represents the end of a given packet. It is necessary
  because some filters in the pipeline need to be informed that the current
  packet is done, so they can wrap up their processing.
  """

  chunktype = ChunkTypes.PACKETBOUND

  START = 0
  END   = 1


thePacketStartChunk = PacketBoundChunk( PacketBoundChunk.START )
thePacketEndChunk   = PacketBoundChunk( PacketBoundChunk.END )


## ---[ Class PromptSweepChunk ]-----------------------------------------

class PromptSweepChunk( BaseChunk ):
  """
  This chunk type is sent down the pipeline when nothing has been received
  after a given timeout (in TinyFugue it is 700ms). The purpose is to inform
  filters that a line that doesn't end with a carriage return might be a
  prompt, as opposed to a line unfinished because the rest is in an upcoming
  packet.
  """

  chunktype = ChunkTypes.PROMPTSWEEP


thePromptSweepChunk = PromptSweepChunk()



## ---[ Class FlowControlChunk ]-----------------------------------------

class FlowControlChunk( BaseChunk ):

  chunktype = ChunkTypes.FLOWCONTROL

  LINEFEED       = 0
  CARRIAGERETURN = 1

  ## Reverse table of the above, for convenience.
  types = {
    0: "LINEFEED",
    1: "CARRIAGERETURN",
  }


  def __repr__( s ):

    chunktype = ChunkTypes.name( s.chunktype )
    return '<Chunk Type: %s; Type: %s>' % ( chunktype, s.types[ s.data ] )


## ---[ Class HighlightChunk ]-------------------------------------------


class HighlightChunk( BaseChunk ):
  """
  This chunk type represents a highlighting parameter, to be inserted by
  TriggersFilter when a line matches one of the user's triggers.
  """

  chunktype = ChunkTypes.HIGHLIGHT
