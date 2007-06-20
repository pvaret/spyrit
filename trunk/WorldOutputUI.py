##
## WorldOutputUI.py
##
## This file contains the WorldOutputUI class, which is the visualization
## widget in which all the current world's output is displayed. Mostly it's
## a custom QTextEdit with a few niceties thrown in.
##


from localqt import *

from PipelineChunks import *


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

    connect( s.scrollbar, SIGNAL( "valueChanged( int )" ), s.onScroll )
    
    s.refresh()


  def getDefaultCharFormat( s ):

    defaultcharformat = QtGui.QTextCharFormat()
    defaultcharformat.clearForeground()
    defaultcharformat.clearBackground()
    defaultcharformat.setForeground( QtGui.QBrush( \
                               QtGui.QColor( s.conf._output_font_color ) ) )
    return defaultcharformat


  def refresh( s ):

    s.setStyleSheet( 'QTextEdit { font-family: "%s" ;  font-size: %dpt }'
                              % ( s.conf._output_font_name,
                                  s.conf._output_font_size ) )

    s.viewport().palette().setColor( QtGui.QPalette.Base,
                       QtGui.QColor( s.conf._output_background_color ) )

    s.charformat = s.getDefaultCharFormat()
   
    s.infocharformat = s.getDefaultCharFormat()
    s.infocharformat.setFontItalic( True )
    s.infocharformat.setForeground( QtGui.QBrush( \
                              QtGui.QColor( s.conf._info_font_color ) ) )
 

  def onScroll( s, pos ):

    s.atbottom = ( pos == s.scrollbar.maximum() )

   
  def sink( s, chunks ):

    scrollpos = s.scrollbar.value()

    ## Ensure that the cursor is at the end of the document. (The cursor may
    ## have been moved when the user clicked somewhere on the widget... even
    ## if it's set read-only. Bummer.)
    if not s.textCursor().atEnd():
      s.moveCursor( QtGui.QTextCursor.End )

    s.setUpdatesEnabled( False )

    pending = []

    for chunk in chunks:

      if   chunk.chunktype == chunktypes.TEXT:
        pending.append( chunk.data )

      elif chunk.chunktype == chunktypes.ENDOFLINE:
        pending.append( "\n" )

      elif chunk.chunktype == chunktypes.FORMAT:

        if pending:
          s.insertText( "".join( pending ) )
          pending = []

        if chunk.data   == "RESET":
          s.charformat = s.getDefaultCharFormat()

        elif chunk.data == "BOLD":
          s.charformat.setFontWeight( QtGui.QFont.Bold )

        elif chunk.data == "ITALIC":
          s.charformat.setFontItalic( True )

        elif chunk.data == "UNDERLINE":
          s.charformat.setFontUnderline( True )

        elif chunk.data == "NO_BOLD":
          s.charformat.setFontWeight( QtGui.QFont.Normal )

        elif chunk.data == "NO_ITALIC":
          s.charformat.setFontItalic( False )

        elif chunk.data == "NO_UNDERLINE":
          s.charformat.setFontUnderline( False )

        elif chunk.data == "FG_BLACK":
          s.charformat.setForeground( QtGui.QBrush( Qt.black ) )

        elif chunk.data == "FG_RED":
          s.charformat.setForeground( QtGui.QBrush( Qt.red ) )

        elif chunk.data == "FG_GREEN":
          s.charformat.setForeground( QtGui.QBrush( Qt.green ) )

        elif chunk.data == "FG_YELLOW":
          s.charformat.setForeground( QtGui.QBrush( Qt.yellow ) )

        elif chunk.data == "FG_BLUE":
          s.charformat.setForeground( QtGui.QBrush( Qt.blue ) )

        elif chunk.data == "FG_MAGENTA":
          s.charformat.setForeground( QtGui.QBrush( Qt.magenta ) )

        elif chunk.data == "FG_CYAN":
          s.charformat.setForeground( QtGui.QBrush( Qt.cyan ) )

        elif chunk.data == "FG_WHITE":
          s.charformat.setForeground( QtGui.QBrush( Qt.white ) )

        elif chunk.data == "FG_DEFAULT":
          s.charformat.setForeground( QtGui.QBrush( \
                        QtGui.QColor( s.conf._output_font_color ) ) )

        elif chunk.data == "BG_BLACK":
          s.charformat.setBackground( QtGui.QBrush( Qt.black ) )

        elif chunk.data == "BG_RED":
          s.charformat.setBackground( QtGui.QBrush( Qt.red ) )

        elif chunk.data == "BG_GREEN":
          s.charformat.setBackground( QtGui.QBrush( Qt.green ) )

        elif chunk.data == "BG_YELLOW":
          s.charformat.setBackground( QtGui.QBrush( Qt.yellow ) )

        elif chunk.data == "BG_BLUE":
          s.charformat.setBackground( QtGui.QBrush( Qt.blue ) )

        elif chunk.data == "BG_MAGENTA":
          s.charformat.setBackground( QtGui.QBrush( Qt.magenta ) )

        elif chunk.data == "BG_CYAN":
          s.charformat.setBackground( QtGui.QBrush( Qt.cyan ) )

        elif chunk.data == "BG_WHITE":
          s.charformat.setBackground( QtGui.QBrush( Qt.white ) )

        elif chunk.data == "BG_DEFAULT":
          s.charformat.clearBackground()



      elif chunk.chunktype == chunktypes.NETWORK:

        if pending:
          pending.append( "\n" )
          s.insertText( "".join( pending ) )
          pending = []

        ## Network state changes.
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

        ## Network errors.
        elif chunk.data == NetworkChunk.CONNECTIONREFUSED:
          s.insertInfoText( "Connection refused." )

        elif chunk.data == NetworkChunk.HOSTNOTFOUND:
          s.insertInfoText( "Host not found." )

        elif chunk.data == NetworkChunk.TIMEOUT:
          s.insertInfoText( "Network timeout." )

        elif chunk.data == NetworkChunk.OTHERERROR:
          s.insertInfoText( "Network error." )

    if pending:
      s.insertText( "".join( pending ) )

    if s.atbottom and s.scrollbar.value() != s.scrollbar.maximum():
      s.scrollbar.setValue( s.scrollbar.maximum() )

    else:
      s.scrollbar.setValue( scrollpos )

    s.setUpdatesEnabled( True )


  def insertText( s, text ):

    s.textCursor().insertText( text, s.charformat )
    

  def insertInfoText( s, text ):
    
    s.textCursor().insertText( "% " + text + "\n", s.infocharformat )
