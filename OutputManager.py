# -*- coding: utf-8 -*-

## Copyright (c) 2007-2009 Pascal Varet <p.varet@gmail.com>
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
## OutputManager.py
##
## This file contains the OutputManager class, which is in charge of content
## management in the output UI: text insertion, formatting, search, etc.
##


from localqt import *

from PipelineChunks import *
from Utilities      import check_alert_is_available
from SearchManager  import SearchManager
from ConfigObserver import ConfigObserver

from PlatformSpecific import platformSpecific


## This is used a lot, so define it right away.

NL = "\n"


## Special Unicode characters.

LEFTARROW = unichr( 0x2192 )


## Definition of the standard colors, highlighted and un-highlighted.

STANDARDCOLORS = {

  False: {  ## Un-highlighted colors
    "BLACK":   Qt.black,
    "RED":     Qt.darkRed,
    "GREEN":   Qt.darkGreen,
    "YELLOW":  Qt.darkYellow,
    "BLUE":    Qt.darkBlue,
    "MAGENTA": Qt.darkMagenta,
    "CYAN":    Qt.darkCyan,
    "WHITE":   Qt.lightGray,
  },

  True: {  ## Highlighted colors
    "BLACK":   Qt.darkGray,
    "RED":     Qt.red,
    "GREEN":   Qt.green,
    "YELLOW":  Qt.yellow,
    "BLUE":    Qt.blue,
    "MAGENTA": Qt.magenta,
    "CYAN":    Qt.cyan,
    "WHITE":   Qt.white,
  }

}



## Helper class to manage formatting.

class WorldOutputCharFormat( QtGui.QTextCharFormat ):

  BRUSH_CACHE = {}

  def __init__( s, conf, color_attribute, italic_by_default=False ):

    QtGui.QTextCharFormat.__init__( s )

    s.conf = conf

    s.highlight = False
    s.fgcolor   = None

    s.color_attribute   = color_attribute
    s.italic_by_default = italic_by_default

    s.observer = ConfigObserver( s.conf )
    s.observer.addCallback( [ color_attribute, "bold_as_highlight" ],
                            s.refresh )

    s.refresh()
    s.reset()


  def refresh( s ):

    default_color       = QtGui.QColor( s.conf[ s.color_attribute ] )
    default_highlighted = WorldOutputCharFormat.lighterColor( default_color )

    s.default_brush     = QtGui.QBrush( default_color )
    s.highlighted_brush = QtGui.QBrush( default_highlighted )
    s.bold_as_highlight = s.conf._bold_as_highlight

    s.setForeground( s.computeCurrentBrush() )


  def reset( s ):

    s.highlight = False
    s.fgcolor   = None

    s.clearForeground()
    s.clearBackground()
    s.setForeground( s.computeCurrentBrush() )

    s.setFontWeight( QtGui.QFont.Normal )
    s.setFontItalic( s.italic_by_default )
    s.setFontUnderline( False )


  def setHighlighted( s, highlighted ):

    if not s.bold_as_highlight:

      ## 'Highlighted' text is simply bold.
      s.setFontWeight( highlighted and QtGui.QFont.Bold
                                   or  QtGui.QFont.Normal )

    else:

      s.highlight = highlighted
      s.setForeground( s.computeCurrentBrush() )


  def setFgColor( s, colorname ):

    s.fgcolor = colorname
    s.setForeground( s.computeCurrentBrush() )


  def setBgColor( s, colorname ):

    if not colorname:
      s.clearBackground()

    else:

      ## We use 'False' because background colors are never highlighted.
      color = STANDARDCOLORS[ False ].get( colorname )

      if color:

        brush = s.BRUSH_CACHE.get( color )

        if not brush:
          brush = QtGui.QBrush( color )
          s.BRUSH_CACHE[ color ] = brush

        s.setBackground( brush )

      else:
        s.clearBackground()


  def computeCurrentBrush( s ):

      if not s.fgcolor:  ## If the default color is in use...
        return s.highlight and s.highlighted_brush or s.default_brush

      else:

        color = STANDARDCOLORS[ s.highlight ].get( s.fgcolor )
        brush = s.BRUSH_CACHE.get( color )

        if not brush:
          brush = QtGui.QBrush( color )
          s.BRUSH_CACHE[ color ] = brush

        return brush


  @staticmethod
  def lighterColor( color ):

    ## We need a highlighted variant of the user's default text color,
    ## in case we're in bold-as-highlight mode and the world wants to display
    ## bold text in the default color. This is what this static helper method
    ## computes.
    ## The value of 255/192 underneath (about 33% lighter) is the value that
    ## will turn Qt.lightGray (used as unhighlighted white in ANSI) into
    ## Qt.white (or hightlighted white in ANSI).

    H, S, V, A = color.getHsv()
    V = min( int( round( V * 255/192.0 ) ), 255 )
    return QtGui.QColor.fromHsv( H, S, V, A )


  def __del__( s ):

    s.observer = None







class OutputManager:

  def __init__( s, world, textview ):

    s.world = world
    s.conf  = world.conf

    s.textview = textview

    s.textcursor     = QtGui.QTextCursor( textview.document() )
    s.charformat     = WorldOutputCharFormat( s.conf, "output_font_color" )
    s.infocharformat = WorldOutputCharFormat( s.conf, "info_font_color", True )

    s.searchmanager  = SearchManager( textview, s.conf )

    s.was_connected  = False

    s.observer = ConfigObserver( s.conf )

    s.pending_newline = False

    s.refresh()

    s.observer.addCallback( [ "output_font_name",
                              "output_font_size",
                              "output_background_color" ],
                            s.refresh )

    s.setupScrollback()
    s.setupPaging()

    s.observer.addCallback( "split_scrollback", s.setupScrollback )
    s.observer.addCallback( "paging",           s.setupPaging )


  def refresh( s ):

    s.textview.setConfiguration( s.conf._output_font_name,
                                 s.conf._output_font_size,
                                 s.conf._output_background_color )


  def setupScrollback( s ):

    s.textview.setSplitScrollback( s.conf._split_scrollback )


  def setupPaging( s ):

    s.textview.setPaging( s.conf._paging )


  def findInHistory( s, string ):

    return s.searchmanager.find( string )


  def processChunks( s, chunks ):
    
    s.textcursor.beginEditBlock()

    for chunk in chunks:

      if   chunk.chunktype == chunktypes.TEXT:
        s.insertText( chunk.data )

      elif chunk.chunktype == chunktypes.FLOWCONTROL:
        s.processFlowControlChunk( chunk.data )

      elif chunk.chunktype == chunktypes.FORMAT:
        s.processFormatChunk( chunk.data )

      elif chunk.chunktype == chunktypes.NETWORK:
        s.processNetworkChunk( chunk.data )

    s.textcursor.endEditBlock()

    if check_alert_is_available() and s.conf._alert_on_activity: 
      qApp().alert( s.textview.window() )


  def processFlowControlChunk( s, event ):

    if event == FlowControlChunk.LINEFEED:
      s.insertNewLine()


  def processFormatChunk( s, format ):

    for param, value in format:

      if   param == "RESET":
        s.charformat.reset()

      elif param == "BOLD":
        s.charformat.setHighlighted( value )

      elif param == "ITALIC":
        s.charformat.setFontItalic( value )

      elif param == "UNDERLINE":
        s.charformat.setFontUnderline( value )

      elif param == "FG":
        s.charformat.setFgColor( value != "DEFAULT" and value or None )

      elif param == "BG":
        s.charformat.setBgColor( value != "DEFAULT" and value or None )


  def processNetworkChunk( s, event ):

    if   event == NetworkChunk.CONNECTING:
      s.insertInfoText( u"Connecting..." )

    elif event == NetworkChunk.CONNECTED:

      if not s.was_connected:
        s.insertInfoText( u"Connected!" )
        s.was_connected = True

    elif event == NetworkChunk.ENCRYPTED:
      s.insertInfoText( u"SSL encryption started." )

    elif event == NetworkChunk.DISCONNECTED:

      if s.was_connected:
        s.insertInfoText( u"Connection closed." )
        s.was_connected = False

    elif event == NetworkChunk.RESOLVING:
      s.insertInfoText( u"Resolving %s ..." % s.world.host() )


    elif event == NetworkChunk.CONNECTIONREFUSED:
      s.insertInfoText( u"Connection refused." )

    elif event == NetworkChunk.HOSTNOTFOUND:
      s.insertInfoText( u"Host not found." )

    elif event == NetworkChunk.TIMEOUT:
      s.insertInfoText( u"Network timeout." )

    elif event == NetworkChunk.OTHERERROR:
      s.insertInfoText( u"Network error." )


  def insertNewLine( s ):

    if s.pending_newline:
      s.textcursor.insertText( NL, s.charformat )

    s.pending_newline = True


  def insertText( s, text ):

    if s.pending_newline:

      s.textcursor.insertText( NL, s.charformat )
      s.pending_newline = False

    s.textcursor.insertText( text, s.charformat )
    

  def insertInfoText( s, text ):

    if s.textcursor.columnNumber() > 0:
      s.textcursor.insertText( NL, s.infocharformat )

    s.textcursor.insertText( LEFTARROW + " " + text, s.infocharformat )
    s.pending_newline = True  ## There is always a new line after info text.


  def __del__( s ):

    s.world          = None
    s.conf           = None
    s.textcursor     = None
    s.charformat     = None
    s.infocharformat = None
    s.observer       = None
    s.searchmanager  = None
