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
## ChunkData.py
##
## This file holds the various bits of chunk data that are going to transit
## through our pipeline.
##


class ChunkTypeMismatch( Exception ):
  """\
  Raised when a combining operation is attempted on two chunks of incompatible
  types.
  """
  pass



## Define chunk types:

CHUNK_TYPES = dict(
  NETWORK     = 1 << 0,
  PACKETBOUND = 1 << 1,
  PROMPTSWEEP = 1 << 2,
  BYTES       = 1 << 3,
  TELNET      = 1 << 4,
  ANSI        = 1 << 5,
  FLOWCONTROL = 1 << 6,
  TEXT        = 1 << 7,
  HIGHLIGHT   = 1 << 8,

  ALL_TYPES   = ( 1 << 9 ) - 1
)

## Make entries available directly from module namespace:
globals().update( CHUNK_TYPES )


def chunk_type_list():

  type = 0x01

  while type < ALL_TYPES:

    yield type
    type = type << 1



## Chunk-related functions:

def concat_chunks( chunk1, chunk2 ):

  chunk1_type, chunk1_payload = chunk1
  chunk2_type, chunk2_payload = chunk2

  ## Only chunks of the same type and whose data are strings can be
  ## concatenated.
  if chunk1_type != chunk2_type \
                 or type( chunk2_payload ) not in ( type( "" ), type( u"" ) ):

    raise ChunkTypeMismatch( "Trying to concat %d chunk with %d chunk!" % \
                             ( chunk1_type, chunk2_type ) )

  ## The chunks are compatible, so we concatenate their data.
  ## We just need to be careful in case one of the two is None,
  ## because None and strings don't add up too well.
  if chunk1_payload is None:
    return ( chunk2_type, chunk2_payload or None )

  else:
    return ( chunk1_type, chunk1_payload + ( chunk2_payload or "" ) )


def chunk_repr( chunk ):

  chunk_type, payload = chunk

  if chunk_type not in CHUNK_TYPES.values():
    type_str = u"(unknown)"

  else:
    type_str = [ k for k, v in CHUNK_TYPES.iteritems()
                 if v == chunk_type ].pop()

  if payload is None:
    return u"<Chunk: %s>" % type_str

  return u"<Chunk: %s; %r>" % ( type_str, payload )


## ANSI-related data:

from Globals import FORMAT_PROPERTIES
from Globals import ANSI_COLORS as COL

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




## Network-related data:

NETWORK_STATE = dict(
  DISCONNECTED  = 0,
  RESOLVING     = 1,
  CONNECTING    = 2,
  CONNECTED     = 3,
  ENCRYPTED     = 4,
  DISCONNECTING = 5,

  CONNECTIONREFUSED = 6,
  HOSTNOTFOUND      = 7,
  TIMEOUT           = 8,
  OTHERERROR        = 9,
)

## Make entries available directly from module namespace:
globals().update( NETWORK_STATE )


## Packet-related data:

PACKET_BOUNDARY = dict(
  START = 0,
  END   = 1,
)

## Make entries available directly from module namespace:
globals().update( PACKET_BOUNDARY )

thePacketStartChunk = ( PACKETBOUND, START )
thePacketEndChunk   = ( PACKETBOUND, END )



## Prompt-sweeper chunk:

thePromptSweepChunk = ( PROMPTSWEEP, None )




## Flow control data:

FLOW_CONTROL = dict(
  LINEFEED       = 0,
  CARRIAGERETURN = 1,
)

## Make entries available directly from module namespace:
globals().update( FLOW_CONTROL )