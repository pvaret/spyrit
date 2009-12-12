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
## WorldOutputUI.py
##
## This file contains the WorldOutputUI class, which is the visualization
## widget in which all the current world's output is displayed. Mostly it's
## a custom QTextEdit with a few niceties thrown in.
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
    s.observer.addCallback( [ color_attribute, "bold_as_highlight" ], s.refresh )

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







class WorldOutputUI( QtGui.QTextEdit ):

  SPLIT_FACTOR = 0.84  ## Corresponds to 1/6th of the height.

  def __init__( s, parent, world ):

    QtGui.QTextEdit.__init__( s, parent )

    s.setReadOnly( True )
    s.setUndoRedoEnabled( False )
    s.setAutoFormatting( QtGui.QTextEdit.AutoNone )
    s.setTabChangesFocus( True )
    s.viewport().setCursor( Qt.ArrowCursor )
    s.setFocusPolicy( Qt.NoFocus )

    s.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
    s.setVerticalScrollBarPolicy(   Qt.ScrollBarAlwaysOn )

    s.world = world
    s.conf  = world.conf

    s.atbottom       = True
    s.scrollbar      = s.verticalScrollBar()
    s.textcursor     = QtGui.QTextCursor( s.document() )
    s.charformat     = WorldOutputCharFormat( s.conf, "output_font_color" )
    s.infocharformat = WorldOutputCharFormat( s.conf, "info_font_color", True )

    s.searchmanager  = SearchManager( s )

    s.was_connected  = False

    s.currently_updating = False
    s.last_page_position = 0

    s.observer = ConfigObserver( s.conf )

    if platformSpecific.should_repaint_on_scroll:
      s.scrollbar.setTracking( True )

    connect( s.scrollbar, SIGNAL( "valueChanged( int )" ), s.onScroll )
    connect( s.scrollbar, SIGNAL( "rangeChanged( int, int )" ),
                                                     s.onRangeChanged )

    s.pending_newline = False

    s.refresh()

    s.observer.addCallback( [ "output_font_name",
                              "output_font_size",
                              "output_background_color" ],
                            s.refresh )

    s.observer.addCallback( "split_scrollback", s.setupScrollback )

    connect( s, SIGNAL( "textChanged()" ),      s.perhapsRepaint )
    connect( s, SIGNAL( "selectionChanged()" ), s.perhapsRepaint )


  def perhapsRepaint( s ):

    ## Right, so we've got a problem: when the text changes but the scrollbar
    ## is not to the bottom, Qt cleverly optimizes things by not repainting
    ## the contents. Only, due to our split screen thingie, we need to
    ## override that behavior. Hence this function.

    if s.atbottom:             return
    if not s.split_scrollback: return
    if s.currently_updating:   return

    ## Right, the scrollbar is not at bottom, and the screen is split. So
    ## we repaint indeed.

    s.repaint()


  def refresh( s ):

    stylesheet = 'QTextEdit { font-family: "%s" ' % s.conf._output_font_name

    if s.conf._output_font_size:
      stylesheet += ';  font-size: %dpt ' % s.conf._output_font_size

    stylesheet += "; background-color: %s }" % s.conf._output_background_color

    s.setStyleSheet( stylesheet )


  def setupScrollback( s ):

    s.split_scrollback = s.conf._split_scrollback
    s.repaint()


  def onScroll( s, pos ):

    previous   = s.atbottom
    s.atbottom = ( pos == s.scrollbar.maximum() )

    if s.atbottom and previous != s.atbottom:
      s.last_page_position = s.scrollbar.maximum()

    if platformSpecific.should_repaint_on_scroll:
      s.repaint()


  def remapMouseEvent( s, e ):

    if s.atbottom or not s.split_scrollback:
      return e

    height  = s.viewport().height()
    split_y = int( height * s.SPLIT_FACTOR )

    if e.y() <= split_y:
      return e

    y = e.y() + s.document().size().height() - height - s.scrollbar.value()

    e = QtGui.QMouseEvent( e.type(), QtCore.QPoint( e.x(), y ), e.globalPos(),
                           e.button(), e.buttons(), e.modifiers() )
    return e


  def mouseMoveEvent( s, e ):

    return QtGui.QTextEdit.mouseMoveEvent( s, s.remapMouseEvent( e ) )


  def mousePressEvent( s, e ):

    ## WORKAROUND: We need to clear the selection before the click, so the
    ## drag and drop event that may otherwise follow doesn't get confused
    ## by our remapped mouse coordinates. But doing so requires calling
    ## setTextCursor(), and that method, itself, calls ensureCursorVisible(),
    ## causing an unwanted scrolling of the viewport. So we 'pin down' the
    ## viewport by saving the scrollbar's value and then restoring it, while
    ## blocking its signals.

    block = s.scrollbar.blockSignals( True )
    val   = s.scrollbar.value()

    cur = s.textCursor()

    if cur.hasSelection() and e.buttons() & Qt.LeftButton:

      cur.clearSelection()
      s.setTextCursor( cur )

    res = QtGui.QTextEdit.mousePressEvent( s, s.remapMouseEvent( e ) )

    s.scrollbar.setValue( val )
    s.scrollbar.blockSignals( block )

    return res


  def mouseReleaseEvent( s, e ):

    ## WORKAROUND: The same workaround as above is used here. Without it, Qt's
    ## calling of ensureCursorVisible() while handling the mouse release event
    ## causes the viewport to scroll if the mouse is released in the split
    ## area.

    block = s.scrollbar.blockSignals( True )
    val   = s.scrollbar.value()

    res = QtGui.QTextEdit.mouseReleaseEvent( s, s.remapMouseEvent( e ) )

    s.scrollbar.setValue( val )
    s.scrollbar.blockSignals( block )

    return res


  def mouseDoubleClickEvent( s, e ):

    return QtGui.QTextEdit.mouseDoubleClickEvent( s, s.remapMouseEvent( e ) )


  def paintEvent( s, e ):

    if s.atbottom or not s.split_scrollback:

      QtGui.QTextEdit.paintEvent( s, e )
      return

    ## Draw the top half of the viewport.

    height, width = s.viewport().height(), s.viewport().width()
    split_y = int( height * s.SPLIT_FACTOR )

    rect = e.rect().intersected( QtCore.QRect( 0, 0, width, split_y ) )

    if not rect.isEmpty():
      QtGui.QTextEdit.paintEvent( s, QtGui.QPaintEvent( rect ) )

    ## Draw separation line.

    p = QtGui.QPainter( s.viewport() )
    p.setClipRect( QtCore.QRectF( 0, split_y, width, height ) )

    p.setPen( qApp().palette().color( QtGui.QPalette.Window ) )
    p.drawLine( 0, split_y, width, split_y )

    ## Draw the bottom of the document on the bottom half of the viewport.

    doc        = s.document()
    doc_height = doc.size().height()

    p.translate( 0, -doc_height + height )

    ctx      = QtGui.QAbstractTextDocumentLayout.PaintContext()
    ctx.clip = QtCore.QRectF( 0, doc_height - height + split_y + 1,
                              width, height - split_y - 1 )

    cur = s.textCursor()

    if cur.hasSelection():

      sel        = QtGui.QAbstractTextDocumentLayout.Selection()
      sel.cursor = cur
      sel.format.setBackground( s.palette().highlight() )
      sel.format.setForeground( s.palette().highlightedText() )

      ctx.selections = [ sel ]

    doc.documentLayout().draw( p, ctx )


  def userSentText( s, text ):

    ## The user has just sent text. Handle accordingly.

    ## Paging implementation:

    if s.atbottom and s.conf._paging:
      s.last_page_position = s.scrollbar.value()


  def moveScrollbarToBottom( s ):

    ## Since this triggers a valueChanged() signal, s.atbottom will be set
    ## to True automatically.
 
    s.scrollbar.setValue( s.scrollbar.maximum() )


  def onRangeChanged( s, min, max ):
    
    ## 'min' and 'max' are the values emitted by the scrollbar's 'rangeChanged'
    ## signal.

    if s.atbottom and s.scrollbar.value() != max:

      next_page_position = s.last_page_position + s.scrollbar.pageStep() \
                                                - s.scrollbar.singleStep()
      if s.conf._paging and s.scrollbar.value() >= next_page_position:
        s.scrollbar.setValue( next_page_position )

      else:
        s.scrollbar.setValue( max )


  def setPageStep( s ):

    pagestep = s.viewport().height() - 1

    if s.split_scrollback:
      pagestep = int( pagestep * s.SPLIT_FACTOR )

    s.scrollbar.setPageStep( pagestep )


  def findInHistory( s, string ):

    return s.searchmanager.find( string )


  def contextMenuEvent( s, e ):

    menu = s.createStandardContextMenu()
    menu.exec_( e.globalPos() )
    sip.delete( menu )


  def stepUp( s ):

    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderSingleStepSub )


  def stepDown( s ):

    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderSingleStepAdd )


  def pageUp( s ):
   
    s.setPageStep()
    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderPageStepSub )
   
   
  def pageDown( s ):
    
    s.setPageStep()
    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderPageStepAdd )
   
   
  def formatAndDisplay( s, chunks ):

    s.currently_updating = True
    s.textcursor.beginEditBlock()

    for chunk in chunks:

      ## Then process each chunk according to its type.

      ## Text:

      if   chunk.chunktype == chunktypes.TEXT:
        s.insertText( chunk.data )


      ## Newline:

      elif     chunk.chunktype == chunktypes.FLOWCONTROL \
           and chunk.data == FlowControlChunk.LINEFEED:
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
          s.insertInfoText( u"Connecting..." )

        elif chunk.data == NetworkChunk.CONNECTED:

          if not s.was_connected:
            s.insertInfoText( u"Connected!" )
            s.was_connected = True

        elif chunk.data == NetworkChunk.ENCRYPTED:
          s.insertInfoText( u"SSL encryption started." )

        elif chunk.data == NetworkChunk.DISCONNECTED:

          if s.was_connected:
            s.insertInfoText( u"Connection closed." )
            s.was_connected = False

        elif chunk.data == NetworkChunk.RESOLVING:
          s.insertInfoText( u"Resolving %s ..." % s.world.host() )

        ## ... Or the network error.

        elif chunk.data == NetworkChunk.CONNECTIONREFUSED:
          s.insertInfoText( u"Connection refused." )

        elif chunk.data == NetworkChunk.HOSTNOTFOUND:
          s.insertInfoText( u"Host not found." )

        elif chunk.data == NetworkChunk.TIMEOUT:
          s.insertInfoText( u"Network timeout." )

        elif chunk.data == NetworkChunk.OTHERERROR:
          s.insertInfoText( u"Network error." )


    ## We're done processing this set of chunks.

    s.textcursor.endEditBlock()
    s.currently_updating = False


    ## And whew, we're done! Now let the application notify the user there's
    ## some new stuff in the window. :)

    if check_alert_is_available() and s.conf._alert_on_activity: 
      qApp().alert( s.window() )


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


  def resizeEvent( s, e ):

    s.onRangeChanged( s.scrollbar.minimum(), s.scrollbar.maximum() )

    return QtGui.QTextEdit.resizeEvent( s, e )


  def __del__( s ):

    s.world          = None
    s.conf           = None
    s.scrollbar      = None
    s.textcursor     = None
    s.charformat     = None
    s.infocharformat = None
    s.observer       = None
    s.searchmanager  = None
