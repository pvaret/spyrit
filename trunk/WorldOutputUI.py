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
from Logger         import logger


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

    s.atbottom  = True
    s.scrollbar = s.verticalScrollBar()

    s.pending_newline = False

    s.textcursor = QtGui.QTextCursor( s.document() )

    connect( s.scrollbar, SIGNAL( "valueChanged( int )" ), s.onScroll )

    s.standardcolors = { 
      0: {  ## Un-highlighted colors
            "BLACK":   Qt.black,
            "RED":     Qt.darkRed,
            "GREEN":   Qt.darkGreen,
            "YELLOW":  Qt.darkYellow,
            "BLUE":    Qt.darkBlue,
            "MAGENTA": Qt.darkMagenta,
            "CYAN":    Qt.darkCyan,
            "WHITE":   Qt.lightGray,
         },
      1: {  ## Highlighted colors
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
    
    s.refresh()


  def getDefaultCharFormat( s ):

    default_fg = QtGui.QColor( s.conf._output_font_color )

    defaultcharformat = QtGui.QTextCharFormat()
    defaultcharformat.clearForeground()
    defaultcharformat.clearBackground()
    defaultcharformat.setForeground( QtGui.QBrush( default_fg ) )

    defaultcharformat.highlight = 0
    defaultcharformat.fgcolor   = None

    ## We also need a highlighted variant of the user's default text color,
    ## in case we're in bold-as-highlight mode and the world wants to display
    ## bold text in the default color.
    ## The value of 1.4 (40% lighter) is admittedly somewhat arbitrary.

    H, S, V, A = default_fg.getHsv()
    V = min( V * 1.4, 256 )
    defaultcharformat.highlighted_default_fg = \
                                             QtGui.QColor.fromHsv( H, S, V, A )

    return defaultcharformat


  def refresh( s ):

    s.setStyleSheet( 'QTextEdit { font-family: "%s" ;  font-size: %dpt }'
                              % ( s.conf._output_font_name,
                                  s.conf._output_font_size ) )

    s.viewport().palette().setColor( QtGui.QPalette.Base,
                       QtGui.QColor( s.conf._output_background_color ) )

    s.charformat     = s.getDefaultCharFormat()
   
    s.infocharformat = s.getDefaultCharFormat()
    s.infocharformat.setFontItalic( True )
    s.infocharformat.setForeground( \
               QtGui.QBrush( QtGui.QColor( s.conf._info_font_color ) ) )
 

  def applyCharFormatColor( s ):

    fgcolor   = s.charformat.fgcolor
    highlight = s.charformat.highlight

    if fgcolor:

      color = s.standardcolors[ highlight ].get( fgcolor )

      if color:

        s.charformat.setForeground( QtGui.QBrush( QtGui.QColor( color ) ) )
        return

    if highlight and s.conf._bold_as_highlight:
      s.charformat.setForeground( s.charformat.highlighted_default_fg )

    else:
      s.charformat.setForeground( \
                    QtGui.QBrush( QtGui.QColor( s.conf._output_font_color ) ) )


  def onScroll( s, pos ):

    s.atbottom = ( pos == s.scrollbar.maximum() )


  def pageUp( s ):
    
    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderPageStepSub )
   
   
  def pageDown( s ):
    
    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderPageStepAdd )
   
   
  def formatAndDisplay( s, chunks ):

    scrollpos = s.scrollbar.value()

    s.textcursor.beginEditBlock()

    pending = []

    for chunk in chunks:

      ## Firstly, print out any pending new line character we might have.

      if s.pending_newline:

        pending.append( "\n" )
        s.pending_newline = False

      ## Then process each chunk according to its type.

      ## Text:

      if   chunk.chunktype == chunktypes.TEXT:
        pending.append( chunk.data )


      ## Newline:

      elif chunk.chunktype == chunktypes.ENDOFLINE:
        ## If there is a new line, we postpone printing it until the next
        ## chunk arrive. Otherwise there would always be an empty line at
        ## the bottom of the text.
        s.pending_newline = True


      ## Formatting information:
      
      elif chunk.chunktype == chunktypes.FORMAT:

        if pending: ## Flush the pending text before changing format.

          s.insertText( "".join( pending ) )
          pending = []

        for param, value in chunk.data:

          if   param == "RESET":
            s.charformat = s.getDefaultCharFormat()

          elif param == "BOLD":

            if s.conf._bold_as_highlight:

              if value == True:
                s.charformat.highlight = 1

              else:
                s.charformat.highlight = 0

              s.applyCharFormatColor()

            else:

              if value == True:
                s.charformat.setFontWeight( QtGui.QFont.Bold )

              else:
                s.charformat.setFontWeight( QtGui.QFont.Normal )

          elif param == "ITALIC":
            s.charformat.setFontItalic( value )

          elif param == "UNDERLINE":
            s.charformat.setFontUnderline( value )

          elif param == "FG":

            if value == "DEFAULT":
              s.charformat.fgcolor = None

            else:
              s.charformat.fgcolor = value

            s.applyCharFormatColor()

          elif param == "BG":

            if color == "DEFAULT":
              s.charformat.clearBackground()

            else:
              ## highlight = 0: Backgrounds are never highlighted/bold.
              color = s.standardcolors[0].get( value )

              if color:
                s.charformat.setBackground( QtGui.QBrush( color ) )

              else: s.charformat.clearBackground()


      ## Network events:

      elif chunk.chunktype == chunktypes.NETWORK:

        ## Flush pending text.

        if pending:
          pending.append( "\n" )
          s.insertText( "".join( pending ) )
          pending = []

        ## Then process the network event.

        if   chunk.data == NetworkChunk.CONNECTING:
          s.insertInfoText( "Connecting..." )

        elif chunk.data == NetworkChunk.CONNECTED:

          if not s.world.connected:
            s.insertInfoText( "Connected!" )

        elif chunk.data == NetworkChunk.DISCONNECTING:
          pass

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

    ## Flush pending text.

    if pending:
      s.insertText( "".join( pending ) )

    s.textcursor.endEditBlock()

    ## Update scrollbar position.

    if s.atbottom and s.scrollbar.value() != s.scrollbar.maximum():
      s.scrollbar.setValue( s.scrollbar.maximum() )

    else:
      s.scrollbar.setValue( scrollpos )

    ## And whew, we're done!


  def insertText( s, text ):

    s.textcursor.insertText( text, s.charformat )
    

  def insertInfoText( s, text ):
    
    s.textcursor.insertText( "% " + text + "\n", s.infocharformat )
