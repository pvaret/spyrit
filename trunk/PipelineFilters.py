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

from Messages       import messages
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

    s.resetInternalState()


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


  def resetInternalState( s ):
    ## Initialize the filter at the beginning of a connection (or when
    ## reconnecting). For instance the Telnet filter would drop all negociated
    ## options.
    ## Override this when implementing your filter if your filter uses any
    ## internal data.
    s.postponedChunk = []


  def concatPostponed( s, chunk ):

    if not s.postponedChunk:
      return chunk

    if chunk is theEndOfPacketChunk:
      ## The End Of Packet chunk is a special case, and is never merged
      ## with other chunks.
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
    ## sent to the world to be modified. I.e., the telnet filter would escape
    ## occurences of the IAC in the data.

    return data


## ---[ Class TelnetFilter ]-------------------------------------------

class TelnetFilter( BaseFilter ):

  relevant_types = [ chunktypes.BYTES ]

  SE   = chr( 240 )  ## End option subnegotiation
  NOP  = chr( 241 )  ## No operation
  DM   = chr( 242 )  ## Data mark for Synch operation
  BRK  = chr( 243 )  ## Break
  IP   = chr( 244 )  ## Interrupt process
  AO   = chr( 245 )  ## Abort output
  AYT  = chr( 246 )  ## Are You There function
  EC   = chr( 247 )  ## Erase character
  EL   = chr( 248 )  ## Erase line
  GA   = chr( 249 )  ## Go ahead
  SB   = chr( 250 )  ## Begin option subnegotiation

  WILL = chr( 251 )
  WONT = chr( 252 )
  DO   = chr( 253 )
  DONT = chr( 254 )

  IAC  = chr( 255 )

  match = re.compile(
      IAC 
    + "(?:"
    +   "(?P<cmd>" + "|".join( [ NOP, DM, BRK, IP, AO,
                                 AYT, EC, EL, GA, IAC ] ) + ")" 
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

        ## TODO: Implement other commands?

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

    ## Escape the character 0xff in accordance with the telnet specification.
    return data.replace( s.IAC, s.IAC * 2 )


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
   
    text       = chunk.data
    currentpos = 0

    while True:

      ansi = s.match.search( text, currentpos )
      
      if not ansi:
        break

      startmatch = ansi.start()

      if startmatch > currentpos:
        yield ByteChunk( text[ currentpos:startmatch ] )

      currentpos = ansi.end()

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

      ## Done searching for complete ANSI sequences.


    if currentpos < len( text ):

      possible_unfinished = s.unfinished.search( text, currentpos )

      if possible_unfinished:

        ## Remaining text ends with an unfinished ANSI sequence!
        ## So we feed what remains of the raw text, if any, down the pipe, and
        ## then postpone the unfinished ANSI sequence.

        startmatch = possible_unfinished.start()

        if startmatch > currentpos:
          yield( ByteChunk( text[ currentpos:startmatch ] ) )

        s.postpone( ByteChunk( text[ startmatch: ] ) )
        
      else:
        yield( ByteChunk( text[ currentpos: ] ) )






## ---[ Class EndLineFilter ]------------------------------------------

class EndLineFilter( BaseFilter ):
  
  relevant_types = [ chunktypes.BYTES ]

  unix_like_cr   = re.compile( r'(?<!\r)\n' )

  match          = re.compile( r'(\r\n)|\n' )
  unfinished     = "\r"

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


  def formatForSending( s, data ):

    return s.unix_like_cr.sub( "\r\n", data )


## ---[ Class UnicodeTextFilter ]--------------------------------------

import codecs

class StreamingDecoder:

  ## WORKAROUND: Python 2.4 doesn't come with an incremental Unicode decoder,
  ## so we need to provide one until Python 2.5 is installed everywhere.

  class Buffer:

    ## Small file-like buffer class meant for use by the Unicode stream decoder.

    def __init__( s ):

      s._buffer = ""


    def write( s, str ):

      s._buffer = str


    def read( s ):

      data      = s._buffer
      s._buffer = ""
      return data


  def __init__( s, encoding, errors="strict" ):

    s.buffer  = s.Buffer()
    s.decoder = codecs.getreader( encoding ) ( s.buffer, errors )
  

  def decode( s, str ):

    s.buffer.write( str )
    return s.decoder.read()


  def reset( s ):

    s.buffer.read()
    s.decoder.reset()



class UnicodeTextFilter( BaseFilter ):
  
  relevant_types = [ chunktypes.BYTES ]


  def setEncoding( s, encoding="ascii" ):

    try:
      codecs.lookup( encoding )

    except LookupError:

      messages.warn( "Unknown encoding '%s'; reverting to ASCII." % encoding )
      encoding = "ascii"

    s.encoding = encoding

    if hasattr( codecs, "getincrementaldecoder" ):  ## True as of Python 2.5
      s.decoder = codecs.getincrementaldecoder( encoding ) ( "replace" )

    else:
      s.decoder = StreamingDecoder( encoding, "replace" )


  def resetInternalState( s ):

    BaseFilter.resetInternalState( s )

    s.setEncoding()
    s.decoder.reset()


  def processChunk( s, chunk ):
 
    text = s.decoder.decode( chunk.data )

    if text: yield UnicodeTextChunk( text )


  def formatForSending( s, data ):

    return data.encode( s.encoding, "replace" )
