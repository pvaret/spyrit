# -*- coding: utf-8 -*-

## Copyright (c) 2007-2013 Pascal Varet <p.varet@gmail.com>
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

from Globals import FORMAT_PROPERTIES

from PyQt4.QtGui import QColor
from PyQt4.QtGui import QFont


class QTextFormatFormatter:

  def __init__( self, qtextformat ):

    self.qtextformat = qtextformat
    self.color_cache = {}

    self.property_setter_mapping = {}

    self._setupPropertyMapping()


  def _setupPropertyMapping( self ):

    for property, setter in (
      ( FORMAT_PROPERTIES.COLOR     , self._setForegroundProperty ),
      ( FORMAT_PROPERTIES.BACKGROUND, self._setBackgroundProperty ),
      ( FORMAT_PROPERTIES.ITALIC    , self._setItalicProperty     ),
      ( FORMAT_PROPERTIES.UNDERLINE , self._setUnderlineProperty  ),
      ( FORMAT_PROPERTIES.BOLD      , self._setFontWeightProperty ),
    ):
      self.property_setter_mapping[ property ] = setter


  def _setForegroundProperty( self, property, value ):

    value = value.lower()

    color = self.color_cache.get( value )

    if color is None:
      color = self.color_cache.setdefault( value, QColor( value ) )

    self.qtextformat.setForeground( color )


  def _setBackgroundProperty( self, property, value ):

    value = value.lower()

    color = self.color_cache.get( value )

    if color is None:
      color = self.color_cache.setdefault( value, QColor( value ) )

    self.qtextformat.setBackground( color )


  def _setUnderlineProperty( self, property, value ):

    self.qtextformat.setFontUnderline( True )


  def _setItalicProperty( self, property, value ):

    self.qtextformat.setFontItalic( True )


  def _setFontWeightProperty( self, property, value ):

    self.qtextformat.setFontWeight( QFont.Black )


  def clearProperty( self, property ):

    self.qtextformat.clearProperty( property )


  def setProperty( self, property, value ):

    setter = self.property_setter_mapping.get( property )

    if setter:
      setter( property, value )
