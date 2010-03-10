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

from FormatData import FORMAT_PROPERTIES



class FormatManager:

  def __init__( s, textformat ):

    s.textformat = textformat

    s.baseformat      = {}
    s.ansiformat      = {}
    s.highlightformat = {}

    s.brush_cache = {}


  def refreshProperties( s, *props ):

    for property in props:
      s.refreshProperty( property )


  def refreshProperty( s, property ):

    values = [ format.get( property )
               for format in ( s.highlightformat, s.ansiformat, s.baseformat )
               if property in format ] or [ None ]

    value = values[0]

    if not value:
      s.clearProperty( property )

    else:
      s.setProperty( property, value )


  def setBaseFormat( s, format ):

    props = set( s.baseformat.keys() )
    props.update( format.keys() )

    s.baseformat = format

    s.refreshProperties( *props )


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


  def applyAnsiFormat( s, format ):

    props = set( s.ansiformat.keys() )
    props.update( format.keys() )

    if not format:  ## reset all

      s.ansiformat.clear()

    for k, v in format.iteritems():

      if not v:  ## reset property

        if k in s.ansiformat:
          del s.ansiformat[k]

      else:      ## apply property
        s.ansiformat[ k ] = v

    s.refreshProperties( *props )


  def applyHighlightFormat( s, format ):

    props = set( s.highlightformat.keys() )
    props.update( format.keys() )

    if not format:  ## reset all

      s.highlightformat.clear()

    for k, v in format.iteritems():

      if not v:  ## reset property

        if k in s.highlightformat:
          del s.highlightformat[k]

      else:      ## apply property
        s.highlightformat[ k ] = v

    s.refreshProperties( *props )
