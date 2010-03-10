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
## SplittableTextView.py
##
## This file contains the SplittableTextView class, a specialized read-only
## QTextEdit that can display the bottom of its contents in a split view while
## scrolling back.
##


from localqt import *

from PlatformSpecific import platformSpecific



class LineCount( QtGui.QLabel ):

  def __init__( s, parent ):

    QtGui.QLabel.__init__( s, parent )

    s.setAutoFillBackground( True )
    s.setAlignment( Qt.AlignHCenter | Qt.AlignVCenter )
    s.setMargin( 1 )
    s.hide()

    s.anchor_x   = 0
    s.anchor_y   = 0
    s.line_count = 0

    s.previous_size = QtCore.QSize()

    s.updateTimer = QtCore.QTimer( s )
    s.updateTimer.setSingleShot( True )

    connect( s.updateTimer, SIGNAL( "timeout()" ), s.applyChanges )


  def setAnchor( s, x, y ):

    s.anchor_x = x
    s.anchor_y = y

    s.reposition()


  def setLineCount( s, count ):

    s.line_count = count

    if not s.updateTimer.isActive():
      s.updateTimer.start()


  def applyChanges( s ):

    if s.isVisible() and s.line_count == 0:
      s.hide()

    elif not s.isVisible() and s.line_count > 0:
      s.show()

    count = s.line_count
    txt = ( count < 2 ) and " %d more line " or " %d more lines "
    s.setText( txt % count )

    new_size = s.sizeHint()

    if new_size != s.previous_size:

      s.resize( new_size )
      s.previous_size = new_size
      s.reposition()


  def reposition( s ):

    size = s.size()
    s.move( s.anchor_x - size.width(), s.anchor_y - size.height() )








class SplittableTextView( QtGui.QTextEdit ):

  SPLIT_FACTOR = 0.84  ## Corresponds to 1/6th of the height.


  def __init__( s, parent=None ):

    QtGui.QTextEdit.__init__( s, parent )

    s.setReadOnly( True )
    s.setUndoRedoEnabled( False )
    s.setAutoFormatting( QtGui.QTextEdit.AutoNone )
    s.viewport().setCursor( Qt.ArrowCursor )

    s.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
    s.setVerticalScrollBarPolicy(   Qt.ScrollBarAlwaysOn )

    s.atbottom  = True
    s.scrollbar = s.verticalScrollBar()

    s.split_scrollback   = True
    s.paging             = True
    s.next_page_position = 0
    s.previous_selection = -1, -1

    connect( s.scrollbar, SIGNAL( "valueChanged( int )" ), s.onScroll )
    connect( s.scrollbar, SIGNAL( "rangeChanged( int, int )" ),
                                                     s.onRangeChanged )

    connect( s, SIGNAL( "textChanged()" ),      s.perhapsRepaintText )
    connect( s, SIGNAL( "selectionChanged()" ), s.perhapsRepaintSelection )

    ## We call this once *after* the event loop has started; otherwise it
    ## occurs before the widget is done constructing, and the font metrics
    ## it uses are thus erroneous:

    QtCore.QTimer.singleShot( 0, s.computeLineStep )

    s.more = LineCount( s )
    s.setMoreAnchor()


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


  def setConfiguration( s, font_name, font_size, background_color ):

    stylesheet = "QTextEdit {\n"

    for key, value in ( 
                        ( 'font-family: "%s"',    font_name ),
                        ( 'font-size: %dpt',      font_size ),
                        ( 'background-color: %s', background_color ),
                      ):
      if value:
        stylesheet += ( key % value ) + ';\n'

    stylesheet += "}"

    s.setStyleSheet( stylesheet )
    s.computeLineStep()


  def computeLineStep( s ):

    s.scrollbar.setSingleStep( s.lineHeight() )
    s.computePageStep()


  def computePageStep( s ):

    if s.split_scrollback:
      pagestep = s.splitY()            - s.scrollbar.singleStep()

    else:
      pagestep = s.viewport().height() - s.scrollbar.singleStep()

    s.scrollbar.setPageStep( pagestep )


  def lineHeight( s ):

    metrics = s.viewport().fontMetrics()

    height = metrics.ascent() + metrics.descent() + 1

    ## Leading is ignored if negative, which can happen on certain platforms,
    ## such as X11.

    if metrics.leading() > 0:
      height += metrics.leading()

    return height


  def setPaging( s, is_paging ):

    s.paging = is_paging


  def setSplitScrollback( s, split_scrollback ):

    s.split_scrollback = split_scrollback

    s.computePageStep()
    s.setMoreAnchor()

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

    s.more.setLineCount( s.linesRemaining() )


  def nextPageForPos( s, pos ):

    l, t, r, b = s.getContentsMargins()

    return pos + s.viewport().height() - s.scrollbar.singleStep() - t - b


  def linesRemaining( s ):

    sb = s.scrollbar
    max, val, step = sb.maximum(), sb.value(), sb.singleStep()

    return ( max - val + step - 1 ) / step


  def remapMouseEvent( s, e ):

    if s.atbottom or not s.split_scrollback:
      return e

    if e.y() <= s.splitY():
      return e

    height  = s.viewport().height()

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

    palette = s.palette()

    QPalette = QtGui.QPalette

    focus  = ( qApp().focusWidget() is s )
    cgroup = not focus and QPalette.Inactive or QPalette.Active

    if cur.hasSelection():

      sel        = QtGui.QAbstractTextDocumentLayout.Selection()
      sel.cursor = cur
      sel.format.setBackground( palette.brush( cgroup, QPalette.Highlight) )
      sel.format.setForeground( palette.brush( cgroup, \
                                               QPalette.HighlightedText ) )

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

    s.more.setLineCount( s.linesRemaining() )


  def contextMenuEvent( s, e ):

    menu = s.createStandardContextMenu()
    menu.exec_( e.globalPos() )
    sip.delete( menu )


  def stepUp( s ):

    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderSingleStepSub )


  def stepDown( s ):

    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderSingleStepAdd )


  def pageUp( s ):
  
    s.computePageStep()
    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderPageStepSub )
   
   
  def pageDown( s ):
    
    s.computePageStep()
    s.scrollbar.triggerAction( QtGui.QScrollBar.SliderPageStepAdd )
   

  def resizeEvent( s, e ):

    res = QtGui.QTextEdit.resizeEvent( s, e )

    s.onRangeChanged( s.scrollbar.minimum(), s.scrollbar.maximum() )
    s.setMoreAnchor()

    return res


  def ensureCursorVisible( s ):

    ## Note: this method is never called from inside Qt, for instance during
    ## the mousePressEvent above, because in the underlying QTextEdit this
    ## method isn't declared as virtual. Bummer.
    ## It is only used in our own code to ensure cursor visibility in case of
    ## split scrollback.

    QtGui.QTextEdit.ensureCursorVisible( s )

    if s.split_scrollback and not s.atbottom:

      rect  = s.cursorRect()
      cur_y = s.viewport().mapToParent( rect.bottomLeft() ).y()

      split_y = s.splitY()

      if cur_y > split_y:

        ## Okay, the cursor is hidden by our scrollback overlay. Let us scroll
        ## some more so it is visible.

        y = s.scrollbar.value()
        s.scrollbar.setValue( y + cur_y - split_y - 1 )


  def setMoreAnchor( s ):

    x = s.viewport().width()

    if s.split_scrollback:
      y = s.splitY()

    else:
      y = s.viewport().height()

    s.more.setAnchor( x, y )


  def __del__( s ):

    s.scrollbar = None
