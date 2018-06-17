# -*- coding: utf-8 -*-

## Copyright (c) 2007-2018 Pascal Varet <p.varet@gmail.com>
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
## TelnetFilter.py
##
## This file holds the pipeline filter that's dedicated to extracting Telnet
## codes from the stream and take action accordingly: negociate options,
## and take the necessary action when a negotiated option requires a
## specific behavior from the client.
##

import re

from .BaseFilter import BaseFilter

from .ChunkData import ChunkType


class TelnetFilter( BaseFilter ):

  relevant_types = ChunkType.BYTES

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
    +   "|"
    +   "(?:"
    +     SB
    +     "(?P<subopt>.)"
    +     "(?P<subparam>.*)"
    +     IAC + SE
    +   ")"
    + ")"
  )

  unfinished = re.compile(
      IAC
    + "("
    +   WILL + "|" + WONT + "|" + DO + "|" + DONT
    +   "("
    +     SB + ".{0,256}"
    +   ")"
    + ")?"
    + "$"
  )


  def processChunk( self, chunk ):

    _, text = chunk

    while len( text ) > 0:

      telnet = self.match.search( text )

      if telnet:

        head = text[ :telnet.start() ]
        text = text[ telnet.end():   ]

        if head:
          yield ( ChunkType.BYTES, head )

        parameters = telnet.groupdict()

        command = parameters[ "cmd" ] or parameters[ "cmdopt" ]
        option  = parameters[ "opt" ]

        if command == self.IAC:
          ## This is an escaped IAC. Yield it as such.
          yield ( ChunkType.BYTES, self.IAC )
          continue

        ## TODO: Implement other commands?

        elif command in ( self.WILL, self.WONT, self.DO, self.DONT ):
          pass ## TODO: Implement option negociation.

      else:
        ## The remaining text doesn't contain any complete Telnet sequence.
        ## So we quit the loop.
        break


    if text:
      if self.unfinished.search( text ): ## Remaining text contains an
                                         ## unfinished Telnet sequence!
        self.postpone( ( ChunkType.BYTES, text ) )

      else:
        yield ( ChunkType.BYTES, text )


  def formatForSending( self, data ):

    ## Escape the character 0xff in accordance with the telnet specification.
    return data.replace( self.IAC, self.IAC * 2 )

