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

    self.property_setter_mapping = dict((
      ( FORMAT_PROPERTIES.COLOR     , self._setForegroundProperty ),
      ( FORMAT_PROPERTIES.BACKGROUND, self._setBackgroundProperty ),
      ( FORMAT_PROPERTIES.ITALIC    , self._setItalicProperty     ),
      ( FORMAT_PROPERTIES.UNDERLINE , self._setUnderlineProperty  ),
      ( FORMAT_PROPERTIES.BOLD      , self._setFontWeightProperty ),
      ( FORMAT_PROPERTIES.HREF      , self._setHrefProperty       ),
    ))


  def _getCachedColor( self, value ):

    value = value.lower()
    color = self.color_cache.get( value )

    if color is None:
      color = self.color_cache.setdefault( value, QColor( value ) )

    return color


  def _setForegroundProperty( self, value ):

    self.qtextformat.setForeground( self._getCachedColor( value ) )


  def _setBackgroundProperty( self, value ):

    self.qtextformat.setBackground( self._getCachedColor( value ) )


  def _setUnderlineProperty( self, value ):

    self.qtextformat.setFontUnderline( True )


  def _setItalicProperty( self, value ):

    self.qtextformat.setFontItalic( True )


  def _setFontWeightProperty( self, value ):

    self.qtextformat.setFontWeight( QFont.Black )


  def _setHrefProperty( self, value ):

    self.qtextformat.setAnchorHref( value )


  def clearProperty( self, property_id ):

    self.qtextformat.clearProperty( property_id )


  def setProperty( self, property_id, value ):

    setter = self.property_setter_mapping.get( property_id )

    if setter is not None:
      setter( value )
