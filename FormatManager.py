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
## FormatManager.py
##
## This file implements the FormatManager, a helper class which can absorb
## formatting information from a variety of sources and apply it to a
## QTextCharFormat.
##

from localqt import *

from Globals        import FORMAT_PROPERTIES
from OrderedDict    import OrderedDict

import ChunkData



class FormatManager:

  BASE = "base"
  ANSI = "ansi"

  STATIC = ( BASE, ANSI )


  def __init__( s, textformat ):

    s.textformat  = textformat
    s.brush_cache = {}

    s.formatstack = OrderedDict()
    s.formatstack[ s.BASE ] = {}
    s.formatstack[ s.ANSI ] = {}

    s.property_setter_mapping = {}

    s.setupPropertyMapping()


  def setupPropertyMapping( s ):

    for property, setter in (
      ( FORMAT_PROPERTIES.COLOR     , s.setForegroundProperty ),
      ( FORMAT_PROPERTIES.BACKGROUND, s.setBackgroundProperty ),
      ( FORMAT_PROPERTIES.ITALIC    , s.setItalicProperty     ),
      ( FORMAT_PROPERTIES.UNDERLINE , s.setUnderlineProperty  ),
      ( FORMAT_PROPERTIES.BOLD      , s.setFontWeightProperty ),
    ):
      s.property_setter_mapping[ property ] = setter


  def setForegroundProperty( s, property, value ):

    value = value.lower()

    brush = s.brush_cache.get( value )

    if brush is None:
      brush = s.brush_cache.setdefault( value,
                                        QtGui.QBrush( QtGui.QColor( value ) ) )

    s.textformat.setForeground( brush )


  def setBackgroundProperty( s, property, value ):

    value = value.lower()

    brush = s.brush_cache.get( value )

    if brush is None:
      brush = s.brush_cache.setdefault( value,
                                        QtGui.QBrush( QtGui.QColor( value ) ) )

    s.textformat.setBackground( brush )


  def setUnderlineProperty( s, property, value ):

    s.textformat.setFontUnderline( True )


  def setItalicProperty( s, property, value ):

    s.textformat.setFontItalic( True )


  def setFontWeightProperty( s, property, value ):

    s.textformat.setFontWeight( QtGui.QFont.Black )


  def refreshProperty( s, property ):

    ## Explore the format stack for the topmost available value for property.

    values = [ format.get( property )
               for format in reversed( s.formatstack.values() )
               if property in format ] or [ None ]

    value = values[0]

    ## And then apply it!

    if not value:
      s.clearProperty( property )

    else:
      s.setProperty( property, value )


  def clearProperty( s, property ):

    s.textformat.clearProperty( property )


  def setProperty( s, property, value ):

    s.property_setter_mapping[ property ]( property, value )


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

    ## Unlike apply*Format methods, this one doesn't update, but replaces
    ## the existing format outright. We implement this by explicitly
    ## setting all the existing keys in the format to None in the new
    ## format definition.

    newformat = dict( ( k, None ) \
                      for k in s.formatstack[ s.BASE ].keys() )

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
