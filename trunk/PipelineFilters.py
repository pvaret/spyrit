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


  def formatForSending( s, data ):
    ## Reimplement this function if the filter inherently requires the data
    ## sent to the world to be modified. I.e., the telnet filter would espace
    ## occurences of the IAC in the data.

    return data


## ---[ Class TelnetFilter ]-------------------------------------------

class TelnetFilter( BaseFilter ):

  relevant_types = [ chunktypes.BYTES ]

  SE   = chr( 240 )
  SB   = chr( 250 )
  NOP  = chr( 241 )
  WILL = chr( 251 )
  WONT = chr( 252 )
  DO   = chr( 253 )
  DONT = chr( 254 )
  IAC  = chr( 255 )

  match = re.compile(
      IAC 
    + "(?:"
    +   "(?P<cmd>" + IAC + "|" + NOP + ")" 
    +   "|"
    +   "(?:"
    +     "(?P<cmdopt>" + WILL + "|" + WONT + "|" + DO + "|" + DONT + ")"
    +     "(?P<opt>.)"
    +   ")"
    + ")"
  )

  unfinished = re.compile( 
      IAC
    + "("
    +   WILL + "|" + WONT + "|" + DO + "|" + DONT
    + ")?"
    + "$"
  )


  def processChunk( s, chunk ):
    
    text = chunk.data

    while len( text ) > 0:

      telnet = s.match.search( text )
      
      if telnet:

        head = text[ :telnet.start() ]
        text = text[ telnet.end():   ]

        if head:
          yield ByteChunk( head )

        parameters = telnet.groupdict()

        command = parameters[ "cmd" ] or parameters[ "cmdopt" ]
        option  = parameters[ "opt" ]

        if   command == s.IAC:
          ## This is an escaped IAC. Yield it as such.
          yield ByteChunk( s.IAC )
          continue

        elif command == s.NOP:
          continue

        elif command in ( s.WILL, s.WONT, s.DO, s.DONT ):
          pass ## TODO: Implement option negociation.

      else:
        ## The remaining text doesn't contain any complete Telnet sequence.
        ## So we quit the loop.
        break


    if text:
      if s.unfinished.search( text ): ## Remaining text contains an unfinished
                                      ## Telnet sequence!
        s.postpone( ByteChunk( text ) )
        
      else:
        yield( ByteChunk( text ) )


  def formatForSending( s, data ):

    return data.replace( s.IAC, s.IAC + s.IAC )


## ---[ Class AnsiFilter ]---------------------------------------------

class AnsiFilter( BaseFilter ):

  relevant_types = [ chunktypes.BYTES ]

  ## For the time being, we only catch the SGR (Set Graphics Rendition) part
  ## of the ECMA 48 specification (a.k.a. ANSI escape codes).

  ESC   = "\x1b"
  CSI8b = "\x9b"

  CSI = "(?:" + ESC + r"\[" + "|" + CSI8b + ")"

  match = re.compile( CSI + r"((?:\d+;?)*)" + "m" )

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
        text = text[ ansi.end():   ]

        if head:
          yield ByteChunk( head )

        parameters = ansi.groups() [0]

        if not parameters:
          parameters = "0"  ## ESC [ m is an alias for ESC [ 0 m.

        formats = []

        for param in parameters.split( ';' ):

          format = FormatChunk.ANSI_TO_FORMAT.get( param )

          if format:
            formats.append( format )

        if formats:
          yield( FormatChunk( formats ) )

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
  
  def __init__( s, *args ):
    
    BaseFilter.__init__( s, *args )
    s.encoding = "ascii"


  def processChunk( s, chunk ):
 
    ## FIXME: this may break if the chunk ends with an unfinished UTF-8
    ## sequence. I.e., the character whose UTF-8 encoding is split over
    ## two packets (is that even possible?), would be ignored.
    ## Mostly a theorical concern, though, since the default encoding here is
    ## ASCII.
 
    if chunk.chunktype == chunktypes.BYTES:
      chunk = UnicodeTextChunk( chunk.data.decode( s.encoding, "replace" ) )
    
    yield chunk


  def formatForSending( s, data ):

    return data.encode( s.encoding, "replace" )
