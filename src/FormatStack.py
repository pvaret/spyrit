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
## FormatStack.py
##
## This file implements the FormatStack helper class, which can absorb
## formatting information from a variety of chunk sources, computes the
## resulting format, and feed the information to a formatter object that knows
## how to apply it.
##


from collections import defaultdict
from OrderedDict import OrderedDict

from pipeline    import ChunkData


BASE = 0
ANSI = 1


class FormatStack:

  def __init__( s, formatter ):

    s.formatter = formatter
    s.stacks    = defaultdict( OrderedDict )


  def processChunk( s, chunk ):

    chunk_type, payload = chunk

    if chunk_type == ChunkData.ANSI:
      s._applyFormat( ANSI, payload )

    elif chunk_type == ChunkData.HIGHLIGHT:

      id, format = payload
      s._applyFormat( id, format )


  def setBaseFormat( s, format ):

    actual_format = dict( ( k, None ) for k in s.stacks )
    actual_format.update( format )

    s._applyFormat( BASE, actual_format )


  def _applyFormat( s, id, format ):

    if not format:

      s._clearFormat( id )
      return

    for property, value in format.iteritems():

      stack = s.stacks[ property ]

      old_end_value = stack.last()

      if value:

        if id not in stack and id in ( BASE, ANSI ):
          stack.insert( id, id, value )

        else:
          stack[ id ] = value

      else:

        if id in stack:
          del stack[ id ]

        else:
          continue

      new_end_value = stack.last()

      if new_end_value == old_end_value:
        continue

      if new_end_value:
        s.formatter.setProperty( property, new_end_value )

      else:
        s.formatter.clearProperty( property )


  def _clearFormat( s, id ):

    for property, stack in s.stacks.iteritems():

      if id in stack:

        old_end_value = stack.last()
        del stack[ id ]
        new_end_value = stack.last()

        if new_end_value == old_end_value:
          continue

        if new_end_value:
          s.formatter.setProperty( property, new_end_value )

        else:
          s.formatter.clearProperty( property )
