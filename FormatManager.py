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

from FormatData  import FORMAT_PROPERTIES
from OrderedDict import OrderedDict



class FormatManager:

  BASE = "base"
  ANSI = "ansi"

  def __init__( s, textformat ):

    s.textformat  = textformat
    s.brush_cache = {}

    s.formatstack = OrderedDict()
    s.formatstack[ s.BASE ] = {}
    s.formatstack[ s.ANSI ] = {}


  def refreshProperties( s, *props ):

    for property in props:
      s.refreshProperty( property )


  def refreshProperty( s, property ):

    values = [ format.get( property )
               for format in reversed( s.formatstack.values() )
               if property in format ] or [ None ]

    value = values[0]

    if not value:
      s.clearProperty( property )

    else:
      s.setProperty( property, value )


  def clearProperty( s, property ):

    s.textformat.clearProperty( property )


  def setProperty( s, property, value ):

    if property == FORMAT_PROPERTIES.COLOR:

      brush = s.brush_cache.setdefault(
              value.lower(), QtGui.QBrush( QtGui.QColor( value ) ) )
      s.textformat.setForeground( brush )

    elif property == FORMAT_PROPERTIES.BACKGROUND:

      brush = s.brush_cache.setdefault(
              value.lower(), QtGui.QBrush( QtGui.QColor( value ) ) )
      s.textformat.setBackground( brush )

    elif property == FORMAT_PROPERTIES.BOLD:
      s.textformat.setFontWeight( QtGui.QFont.Bold )

    elif property == FORMAT_PROPERTIES.ITALIC:
      s.textformat.setFontItalic( True )

    elif property == FORMAT_PROPERTIES.UNDERLINE:
      s.textformat.setFontUnderline( True )


  def applyFormat( s, format, level ):

    ## TODO: Find better names than level and formatlevel.
    formatlevel = s.formatstack.setdefault( level, {} )

    props = set( formatlevel.keys() )
    props.update( format.keys() )

    if not format:  ## reset all

      if level in ( s.BASE, s.ANSI ):
        ## This is one of the static formatters.
        formatlevel.clear()

      else:
        ## This was one of the temporary formatters. Delete it.
        if level in s.formatstack:
          del s.formatstack[ level ]

      if props:
        s.refreshProperties( *props )

      return

    ## Apply new format definition.

    for k, v in format.iteritems():

      if not v:  ## reset property

        if k in formatlevel:
          del formatlevel[k]

      else:      ## apply property
        formatlevel[ k ] = v

    s.refreshProperties( *props )


  def setBaseFormat( s, format ):

    ## Unlike apply*Format methods, this one doesn't update, but replaces
    ## the existing format outright. We implement this by explicitly
    ## setting all the existing keys in the format to None in the new
    ## format definition.

    newformat = dict( ( k, None ) \
                      for k in s.formatstack[ s.BASE ].keys() )

    ## Then we apply the requested format modifier.
    newformat.update( format )

    s.applyFormat( newformat, s.BASE )


  def applyAnsiFormat( s, format ):

    s.applyFormat( format, s.ANSI )


  def applyHighlightFormat( s, format ):

    ## TODO: Have highlighter return named formats.
    s.applyFormat( format, "highlight" )
