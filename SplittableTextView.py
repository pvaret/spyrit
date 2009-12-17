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
## SplittableTextView.py
##
## This file contains the SplittableTextView class, a specialized read-only
## QTextEdit that can display the bottom of its contents in a split view while
## scrolling back.
##


from localqt import *

from PlatformSpecific import platformSpecific



class SplittableTextView( QtGui.QTextEdit ):

  SPLIT_FACTOR = 0.84  ## Corresponds to 1/6th of the height.


  def __init__( s, parent=None ):

    QtGui.QTextEdit.__init__( s, parent )

    s.setReadOnly( True )
    s.setUndoRedoEnabled( False )
    s.setAutoFormatting( QtGui.QTextEdit.AutoNone )
    s.setTabChangesFocus( True )
    s.viewport().setCursor( Qt.ArrowCursor )
    s.setFocusPolicy( Qt.NoFocus )

    s.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
    s.setVerticalScrollBarPolicy(   Qt.ScrollBarAlwaysOn )

    s.atbottom  = True
    s.scrollbar = s.verticalScrollBar()

    s.paging             = True
    s.next_page_position = 0
    s.previous_selection = -1, -1

    s.font_name        = None
    s.font_size        = 0
    s.background_color = None

    s.refresh_timer = QtCore.QTimer()
    s.refresh_timer.setInterval( 0 )
    s.refresh_timer.setSingleShot( True )

    connect( s.refresh_timer, SIGNAL( "timeout()" ), s.applyConfiguration )

    connect( s.scrollbar, SIGNAL( "valueChanged( int )" ), s.onScroll )
    connect( s.scrollbar, SIGNAL( "rangeChanged( int, int )" ),
                                                     s.onRangeChanged )

    connect( s, SIGNAL( "textChanged()" ),      s.perhapsRepaintText )
    connect( s, SIGNAL( "selectionChanged()" ), s.perhapsRepaintSelection )


  def perhapsRepaintText( s ):

    ## Right, so we've got a problem: when the text changes but the scrollbar
    ## is not to the bottom, Qt cleverly optimizes things by not repainting
    ## the contents. Only, due to our split screen thingie, we need to
    ## override that behavior. Hence this function.

    if s.atbottom:             return
    if not s.split_scrollback: return

    ## Right, the scrollbar is not at bottom, and the screen is split. So
    ## we repaint indeed, although only the bottom part, since the screen is
    ## split and the top part doesn't change.

    s.update( s.splitBottomRect() )


  def perhapsRepaintSelection( s ):

    if s.atbottom:             return
    if not s.split_scrollback: return

    ## We force a repaint of the bottom area in two cases: when the mouse
    ## pointer is in there, and thus may be updating the selection; and
    ## when the selection is all new, in case there was a former selection
    ## to be cleared. Hackish, but functional.

    cursor_pos = s.viewport().mapFromGlobal( QtGui.QCursor.pos() )

    if s.splitBottomRect().contains( cursor_pos ):
      s.update( s.splitBottomRect() )

    prev_pos, prev_anchor = s.previous_selection

    sel = s.textCursor()

    if sel.position() != prev_pos and sel.anchor() != prev_anchor:
      s.update( s.splitBottomRect() )

    s.previous_selection = sel.position(), sel.anchor()


  def applyConfiguration( s ):

    stylesheet = "QTextEdit {\n"

    for key, value in ( 
                        ( 'font-family: "%s"',    s.font_name ),
                        ( 'font-size: %dpt',      s.font_size ),
                        ( 'background-color: %s', s.background_color ),
                      ):
      if value:
        stylesheet += ( key % value ) + ';\n'

    stylesheet += "}"

    s.setStyleSheet( stylesheet )

    s.scrollbar.setSingleStep( s.lineHeight() )
    s.setPageStep()


  def lineHeight( s ):

    metrics = s.viewport().fontMetrics()

    height = metrics.ascent() + metrics.descent() + 1

    ## Leading is ignored if negative, which can happen on certain platforms,
    ## such as X11.

    if metrics.leading() > 0:
      height += metrics.leading()

    return height


  def setFontFamily( s, font_name ):

    s.font_name = font_name

    if not s.refresh_timer.isActive():
      s.refresh_timer.start()


  def setFontSize( s, font_size ):

    s.font_size = font_size

    if not s.refresh_timer.isActive():
      s.refresh_timer.start()


  def setBackgroundColor( s, color ):

    s.background_color = color

    if not s.refresh_timer.isActive():
      s.refresh_timer.start()


  def setPaging( s, is_paging ):

    s.paging = is_paging


  def setSplitScrollback( s, split_scrollback ):

    s.split_scrollback = split_scrollback

    s.setPageStep()

    if not s.atbottom:
      s.update()


  def onScroll( s, pos ):

    s.atbottom = ( pos == s.scrollbar.maximum() )

    ## When the user moves back to the bottom of the view, paging is reset:

    if s.atbottom:

      if s.next_page_position == -1:
        s.next_page_position = s.nextPageForPos( pos )

    else:
      s.next_page_position = -1

    if platformSpecific.should_repaint_on_scroll:
      s.update()


  def nextPageForPos( s, pos ):

    l, t, r, b = s.getContentsMargins()

    return pos + s.viewport().height() - s.scrollbar.singleStep() - t - b


  def remapMouseEvent( s, e ):

    if s.atbottom or not s.split_scrollback:
      return e

    height  = s.viewport().height()

    if e.y() <= s.splitY():
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

      cur = s.cursorForPosition( e.pos() )
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


  def splitY( s ):

    return int( s.viewport().height() * s.SPLIT_FACTOR )


  def splitTopRect( s ):

    w = s.viewport().width()

    return QtCore.QRect( 0, 0, w, s.splitY() )


  def splitBottomRect( s ):

    w = s.viewport().width()
    h = s.viewport().height()

    return QtCore.QRect( 0, s.splitY() + 1, w, h )


  def paintEvent( s, e ):

    if s.atbottom or not s.split_scrollback:

      QtGui.QTextEdit.paintEvent( s, e )
      return

    ## Draw the top half of the viewport if necessary.

    top_r = e.rect().intersected( s.splitTopRect() )

    if not top_r.isEmpty():
      QtGui.QTextEdit.paintEvent( s, QtGui.QPaintEvent( top_r ) )

    ## Likewise the bottom half.
    ## Create painter.

    p = QtGui.QPainter( s.viewport() )

    ## Draw separation line.

    split_y = s.splitY()
    width   = s.viewport().width()
    height  = s.viewport().height()

    if e.rect().contains( e.rect().left(), split_y ):

      p.setPen( qApp().palette().color( QtGui.QPalette.Window ) )
      p.drawLine( 0, split_y, width, split_y )

    ## Clip painter.

    clip_r = e.rect().intersected( s.splitBottomRect() )

    if clip_r.isEmpty():
      return

    doc        = s.document()
    doc_height = doc.size().height()

    p.setClipRect( clip_r )
    p.translate( 0, -doc_height + height )

    ## Draw the bottom of the document on the bottom half of the viewport.

    ctx      = QtGui.QAbstractTextDocumentLayout.PaintContext()
    ctx.clip = QtCore.QRectF( clip_r.translated( 0, doc_height - height ) )

    cur = s.textCursor()

    if cur.hasSelection():

      sel        = QtGui.QAbstractTextDocumentLayout.Selection()
      sel.cursor = cur
      sel.format.setBackground( s.palette().highlight() )
      sel.format.setForeground( s.palette().highlightedText() )

      ctx.selections = [ sel ]

    doc.documentLayout().draw( p, ctx )


  def pingPage( s ):

    ## Paging implementation:

    if s.atbottom and s.paging:
      s.next_page_position = s.nextPageForPos( s.scrollbar.value() )


  def moveScrollbarToBottom( s ):

    max = s.scrollbar.maximum()

    if s.scrollbar.value() == max:

      ## Trigger onScroll event even if not moving:
      s.onScroll( max )

    else:
      s.scrollbar.setValue( max )


  def moveScrollbarToTop( s ):

    s.scrollbar.setValue( s.scrollbar.minimum() )


  def onRangeChanged( s, min, max ):

    ## 'min' and 'max' are the values emitted by the scrollbar's 'rangeChanged'
    ## signal.

    pos = s.scrollbar.value()

    ## Handle rare case where the view got smaller, for instance if the user
    ## switches to a smaller font:

    if pos > max:
      return

    if s.next_page_position > s.nextPageForPos( max ):
      s.next_page_position = -1

    if pos != max and s.atbottom:  ## Do we need to scroll?

      if s.paging and s.next_page_position != -1:
        ## Case 1: We are paging and have a valid next page break.

        if max > s.next_page_position:
          ## Case 1.1: Scrolling would move us past the next page break.

          if pos != s.next_page_position:
            s.scrollbar.setValue( s.next_page_position )

          else:  ## If the scrollbar value shouldn't change even though we
                 ## switched to paging mode, trigger scroll event manually.
            s.onScroll( pos )

        else:
          ## Case 1.2: Not at page break yet. Proceed as usual for now.
          s.moveScrollbarToBottom()

      else:
        ## Case 2: We are not paging. Proceed as usual.
        s.moveScrollbarToBottom()


  def setPageStep( s ):

    if s.split_scrollback:
      pagestep = s.splitY()            - s.scrollbar.singleStep()

    else:
      pagestep = s.viewport().height() - s.scrollbar.singleStep()

    s.scrollbar.setPageStep( pagestep )


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
   

  def resizeEvent( s, e ):

    s.onRangeChanged( s.scrollbar.minimum(), s.scrollbar.maximum() )

    return QtGui.QTextEdit.resizeEvent( s, e )


  def __del__( s ):

    s.scrollbar = None
