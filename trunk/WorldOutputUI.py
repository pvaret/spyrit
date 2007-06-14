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


  def refresh( s ):

    s.viewport().palette().setColor( QtGui.QPalette.Base,
                       QtGui.QColor( s.conf._output_background_color ) )

    s.defaultcharformat = QtGui.QTextCharFormat()
    s.defaultcharformat.clearForeground()
    s.defaultcharformat.clearBackground()
    s.defaultcharformat.setFontFamily( s.conf._output_font_name )
    s.defaultcharformat.setFontPointSize( s.conf._output_font_size )
    s.defaultcharformat.setForeground( QtGui.QBrush( \
                                 QtGui.QColor( s.conf._output_font_color ) ) )
    s.defaultcharformat.setFontWeight( QtGui.QFont.Normal )
   
    s.infocharformat = QtGui.QTextCharFormat()
    s.infocharformat.clearForeground()
    s.infocharformat.clearBackground()
    s.infocharformat.setFontFamily( s.conf._output_font_name )
    s.infocharformat.setFontPointSize( s.conf._output_font_size )
    s.infocharformat.setForeground( QtGui.QBrush( \
                              QtGui.QColor( s.conf._info_font_color ) ) )
    s.infocharformat.setFontWeight( QtGui.QFont.Normal )
    s.infocharformat.setFontItalic( True )
 

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

    s.textCursor().insertText( text, s.defaultcharformat )
    

  def insertInfoText( s, text ):
    
    s.textCursor().insertText( "% " + text + "\n", s.infocharformat )
