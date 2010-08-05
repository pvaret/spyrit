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


from OrderedDict import OrderedDict

import ChunkData



class FormatStack:

  BASE = "base"
  ANSI = "ansi"

  STATIC = ( BASE, ANSI )


  def __init__( s, formatter ):

    s.formatter  = formatter

    s.formatstack = OrderedDict()
    s.formatstack[ s.BASE ] = {}
    s.formatstack[ s.ANSI ] = {}


  def refreshProperty( s, property ):

    ## Explore the format stack for the topmost available value for property.

    values = [ format.get( property )
               for format in reversed( s.formatstack.values() )
               if property in format ] or [ None ]

    value = values[0]

    ## And then apply it!

    if not value:
      s.formatter.clearProperty( property )

    else:
      s.formatter.setProperty( property, value )


  def applyFormat( s, format_id, newformat ):

    ## Create or retrieve the format dict in the stack.

    oldformat = s.formatstack.setdefault( format_id, {} )

    ## Case 1: This is a reset of the format.

    if not newformat:  ## reset all

      keys = oldformat.keys()

      if format_id in s.STATIC:
        ## This is one of the static formatters. Clear it, but leave it in
        ## its place in the stack.
        oldformat.clear()

      else:
        ## This was one of the temporary formatters. Delete it.
        if format_id in s.formatstack:
          del s.formatstack[ format_id ]

      for prop in keys:
        s.refreshProperty( prop )

      return

    ## Case 2: Apply new format definition.

    for k, v in newformat.iteritems():

      if not v:  ## reset property

        if k in oldformat:
          del oldformat[ k ]

      else:      ## apply property
        oldformat[ k ] = v

      s.refreshProperty( k )


  def setBaseFormat( s, format ):

    ## Unlike the applyFormat method, this one doesn't update, but replaces the
    ## existing format outright. We implement this by explicitly setting all
    ## the existing keys in the format to None in the new format definition.

    newformat = dict( ( k, None )
                      for k in s.formatstack.get( s.BASE, {} ).keys() )

    ## Then we apply the requested format modifier.
    newformat.update( format )

    s.applyFormat( s.BASE, newformat )


  def processChunk( s, chunk ):

    chunk_type, payload = chunk

    if chunk_type == ChunkData.ANSI:
      s.applyFormat( s.ANSI, payload )

    elif chunk_type == ChunkData.HIGHLIGHT:

      id, format = payload
      s.applyFormat( id, format )
