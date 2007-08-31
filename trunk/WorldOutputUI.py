# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
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
## WorldOutputUI.py
##
## This file contains the WorldOutputUI class, which is the visualization
## widget in which all the current world's output is displayed. Mostly it's
## a custom QTextEdit with a few niceties thrown in.
##


from localqt import *

from PipelineChunks import *


## This is used a lot, so define it right away.

NL = "\n"


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

  def __init__( s, conf ):

    QtGui.QTextCharFormat.__init__( s )

    default_color       = QtGui.QColor( conf._output_font_color )
    default_highlighted = WorldOutputCharFormat.lighterColor( default_color )

    s.default_brush     = QtGui.QBrush( default_color )
    s.highlighted_brush = QtGui.QBrush( default_highlighted )

    s.bold_as_highlight = conf._bold_as_highlight

    s.reset()


  def reset( s ):

    s.highlight = False
    s.fgcolor   = None

    s.clearForeground()
    s.clearBackground()
    s.setForeground( s.computeCurrentBrush() )

    s.setFontWeight( QtGui.QFont.Normal )
    s.setFontItalic( False )
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
    ## bold text in the default color. This is what this static help method
    ## computes.
    ## The value of 1.4 (40% lighter) is admittedly somewhat arbitrary.

    H, S, V, A = color.getHsv()
    V = min( V * 1.4, 256 )
    return QtGui.QColor.fromHsv( H, S, V, A )




class WorldOutputUI( QtGui.QTextEdit ):
 
  def __init__( s, parent, world ):

    QtGui.QTextEdit.__init__( s, parent )

    s.setReadOnly( True )
    s.setUndoRedoEnabled( False )
    s.setAutoFormatting( QtGui.QTextEdit.AutoNone )
    s.setTabChangesFocus( True )
    s.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOn )
    s.viewport().setCursor( Qt.ArrowCursor )

    s.world = world
    s.conf  = world.conf

    s.atbottom       = True
    s.scrollbar      = s.verticalScrollBar()
    s.textcursor     = QtGui.QTextCursor( s.document() )
    s.charformat     = WorldOutputCharFormat( s.conf )
    s.infocharformat = WorldOutputCharFormat( s.conf )

    connect( s.scrollbar, SIGNAL( "valueChanged( int )" ), s.onScroll )

    s.pending_newline = False
   
    s.refresh()


  def refresh( s ):

    s.setStyleSheet( 'QTextEdit { font-family: "%s" ;  font-size: %dpt }'
                              % ( s.conf._output_font_name,
                                  s.conf._output_font_size ) )

    s.viewport().palette().setColor( QtGui.QPalette.Base,
                       QtGui.QColor( s.conf._output_background_color ) )

    s.charformat.reset()

    s.infocharformat.reset()
    s.infocharformat.setFontItalic( True )
    s.infocharformat.setForeground( \
               QtGui.QBrush( QtGui.QColor( s.conf._info_font_color ) ) )


  def onScroll( s, pos ):

    s.atbottom = ( pos == s.scrollbar.maximum() )


  def pageUp( s ):
    
    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderPageStepSub )
   
   
  def pageDown( s ):
    
    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderPageStepAdd )
   
   
  def formatAndDisplay( s, chunks ):

    scrollpos = s.scrollbar.value()

    s.textcursor.beginEditBlock()

    for chunk in chunks:

      ## Then process each chunk according to its type.

      ## Text:

      if   chunk.chunktype == chunktypes.TEXT:
        s.insertText( chunk.data )


      ## Newline:

      elif chunk.chunktype == chunktypes.ENDOFLINE:
        s.insertNewLine()


      ## Formatting information:
      
      elif chunk.chunktype == chunktypes.FORMAT:

        for param, value in chunk.data:

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


      ## Network events:

      elif chunk.chunktype == chunktypes.NETWORK:

        ## Handle the network event...

        if   chunk.data == NetworkChunk.CONNECTING:
          s.insertInfoText( "Connecting..." )

        elif chunk.data == NetworkChunk.CONNECTED:

          if not s.world.connected:
            s.insertInfoText( "Connected!" )

        elif chunk.data == NetworkChunk.ENCRYPTED:
          s.insertInfoText( "SSL encryption started." )

        elif chunk.data == NetworkChunk.DISCONNECTED:

          if s.world.connected:
            s.insertInfoText( "Connection closed." )

        elif chunk.data == NetworkChunk.RESOLVING:
          s.insertInfoText( "Resolving %s ..." % s.world.host )

        ## ... Or the network error.

        elif chunk.data == NetworkChunk.CONNECTIONREFUSED:
          s.insertInfoText( "Connection refused." )

        elif chunk.data == NetworkChunk.HOSTNOTFOUND:
          s.insertInfoText( "Host not found." )

        elif chunk.data == NetworkChunk.TIMEOUT:
          s.insertInfoText( "Network timeout." )

        elif chunk.data == NetworkChunk.OTHERERROR:
          s.insertInfoText( "Network error." )


    ## We're done processing this set of chunks.

    s.textcursor.endEditBlock()

    ## Update scrollbar position.

    if s.atbottom and s.scrollbar.value() != s.scrollbar.maximum():
      s.scrollbar.setValue( s.scrollbar.maximum() )

    else:
      s.scrollbar.setValue( scrollpos )

    ## And whew, we're done!


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

    if s.pending_newline:
      s.textcursor.insertText( NL, s.infocharformat )

    s.textcursor.insertText( "% " + text, s.infocharformat )
    s.pending_newline = True  ## There is always a new line after info text.


  def resizeEvent( s, e ):

    if s.atbottom and s.scrollbar.value() != s.scrollbar.maximum():
      s.scrollbar.setValue( s.scrollbar.maximum() )

    return QtGui.QTextEdit.resizeEvent( s, e )
