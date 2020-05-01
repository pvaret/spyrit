# -*- coding: utf-8 -*-

## Copyright (c) 2007-2020 Pascal Varet <p.varet@gmail.com>
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

from __future__ import absolute_import
from __future__ import unicode_literals

import re

from .BaseFilter import BaseFilter

from .ChunkData import ChunkType


def bytechr( i ):
  if type( chr( 32 ) ) is type( u"" ):
    ## Python 3 compatibility.
    return bytes( [ i ] )
  else:
    return chr( i )


class TelnetFilter( BaseFilter ):

  relevant_types = ChunkType.BYTES

  SE   = bytechr( 240 )  ## End option subnegotiation
  NOP  = bytechr( 241 )  ## No operation
  DM   = bytechr( 242 )  ## Data mark for Synch operation
  BRK  = bytechr( 243 )  ## Break
  IP   = bytechr( 244 )  ## Interrupt process
  AO   = bytechr( 245 )  ## Abort output
  AYT  = bytechr( 246 )  ## Are You There function
  EC   = bytechr( 247 )  ## Erase character
  EL   = bytechr( 248 )  ## Erase line
  GA   = bytechr( 249 )  ## Go ahead
  SB   = bytechr( 250 )  ## Begin option subnegotiation

  WILL = bytechr( 251 )
  WONT = bytechr( 252 )
  DO   = bytechr( 253 )
  DONT = bytechr( 254 )

  IAC  = bytechr( 255 )

  match = re.compile(
      IAC
    + b"(?:"
    +   b"(?P<cmd>" + b"|".join( [ NOP, DM, BRK, IP, AO,
                                   AYT, EC, EL, GA, IAC ] ) + b")"
    +   b"|"
    +   b"(?:"
    +     b"(?P<cmdopt>" + WILL + b"|" + WONT + b"|" + DO + b"|" + DONT + b")"
    +     b"(?P<opt>.)"
    +   b")"
    +   b"|"
    +   b"(?:"
    +     SB
    +     b"(?P<subopt>.)"
    +     b"(?P<subparam>.*)"
    +     IAC + SE
    +   b")"
    + b")"
  )

  unfinished = re.compile(
      IAC
    + b"("
    +   WILL + b"|" + WONT + b"|" + DO + b"|" + DONT
    +   b"("
    +     SB + b".{0,256}"
    +   b")"
    + b")?"
    + b"$"
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

