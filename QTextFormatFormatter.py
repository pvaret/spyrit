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
## QTextFormatFormatter.py
##
## A QTextFormatFormatter can be used by a FormatStack to apply formats to,
## specifically, a QTextFormat, as used in our output UI.
##

from localqt import *

from Globals import FORMAT_PROPERTIES



class QTextFormatFormatter:

  def __init__( s, qtextformat ):

    s.qtextformat = qtextformat
    s.color_cache = {}

    s.property_setter_mapping = {}

    s._setupPropertyMapping()


  def _setupPropertyMapping( s ):

    for property, setter in (
      ( FORMAT_PROPERTIES.COLOR     , s._setForegroundProperty ),
      ( FORMAT_PROPERTIES.BACKGROUND, s._setBackgroundProperty ),
      ( FORMAT_PROPERTIES.ITALIC    , s._setItalicProperty     ),
      ( FORMAT_PROPERTIES.UNDERLINE , s._setUnderlineProperty  ),
      ( FORMAT_PROPERTIES.BOLD      , s._setFontWeightProperty ),
    ):
      s.property_setter_mapping[ property ] = setter


  def _setForegroundProperty( s, property, value ):

    value = value.lower()

    color = s.color_cache.get( value )

    if color is None:
      color = s.color_cache.setdefault( value, QtGui.QColor( value ) )

    s.qtextformat.setForeground( color )


  def _setBackgroundProperty( s, property, value ):

    value = value.lower()

    color = s.color_cache.get( value )

    if color is None:
      color = s.color_cache.setdefault( value, QtGui.QColor( value ) )

    s.qtextformat.setBackground( color )


  def _setUnderlineProperty( s, property, value ):

    s.qtextformat.setFontUnderline( True )


  def _setItalicProperty( s, property, value ):

    s.qtextformat.setFontItalic( True )


  def _setFontWeightProperty( s, property, value ):

    s.qtextformat.setFontWeight( QtGui.QFont.Black )


  def clearProperty( s, property ):

    s.qtextformat.clearProperty( property )


  def setProperty( s, property, value ):

    setter = s.property_setter_mapping.get( property )

    if setter:
      setter( property, value )
