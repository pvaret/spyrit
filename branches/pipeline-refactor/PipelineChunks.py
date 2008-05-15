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


## ---[ Class FormatChunk ]--------------------------------------------

class FormatChunk:
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


## ---[ Class NetworkChunk ]-------------------------------------------

class NetworkChunk:
  
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
