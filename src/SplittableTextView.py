# -*- coding: utf-8 -*-

## Copyright (c) 2007-2011 Pascal Varet <p.varet@gmail.com>
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


import sip

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QRect
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QPoint
from PyQt4.QtCore import QRectF
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui  import QFont
from PyQt4.QtGui  import QLabel
from PyQt4.QtGui  import QCursor
from PyQt4.QtGui  import QPainter
from PyQt4.QtGui  import QPalette
from PyQt4.QtGui  import QTextEdit
from PyQt4.QtGui  import QScrollBar
from PyQt4.QtGui  import QTextLayout
from PyQt4.QtGui  import QMouseEvent
from PyQt4.QtGui  import QPaintEvent
from PyQt4.QtGui  import QTextOption
from PyQt4.QtGui  import QApplication
from PyQt4.QtGui  import QFontMetrics
from PyQt4.QtGui  import QAbstractTextDocumentLayout


from CheckVersions    import qt_version
from SingleShotTimer  import SingleShotTimer
from PlatformSpecific import platformSpecific


class LineCount( QLabel ):

  def __init__( self, parent ):

    QLabel.__init__( self, parent )

    self.setAutoFillBackground( True )
    self.setAlignment( Qt.AlignHCenter | Qt.AlignVCenter )
    self.setMargin( 1 )
    self.hide()

    self.anchor_x   = 0
    self.anchor_y   = 0
    self.line_count = 0

    self.previous_size = QSize()

    self.update_timer = SingleShotTimer( self.applyChanges )


  def setAnchor( self, x, y ):

    self.anchor_x = x
    self.anchor_y = y

    self.reposition()


  def setLineCount( self, count ):

    self.line_count = count

    if not self.update_timer.isActive():
      self.update_timer.start()


  def applyChanges( self ):

    if self.isVisible() and self.line_count == 0:
      self.hide()

    elif not self.isVisible() and self.line_count > 0:
      self.show()

    count = self.line_count
    txt = ( count < 2 ) and " %d more line " or " %d more lines "
    self.setText( txt % count )

    new_size = self.sizeHint()

    if new_size != self.previous_size:

      self.resize( new_size )
      self.previous_size = new_size
      self.reposition()


  def reposition( self ):

    size = self.size()
    self.move( self.anchor_x - size.width(), self.anchor_y - size.height() )








class SplittableTextView( QTextEdit ):

  SPLIT_FACTOR = 0.84  ## Corresponds to 1/6th of the height.


  def __init__( self, parent=None ):

    QTextEdit.__init__( self, parent )

    self.setReadOnly( True )
    self.setUndoRedoEnabled( False )
    self.setAutoFormatting( QTextEdit.AutoNone )
    self.viewport().setCursor( Qt.ArrowCursor )

    self.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
    self.setVerticalScrollBarPolicy(   Qt.ScrollBarAlwaysOn )

    self.atbottom  = True
    self.scrollbar = self.verticalScrollBar()

    self.split_scrollback   = True
    self.paging             = True
    self.next_page_position = 0
    self.previous_selection = -1, -1

    self.scrollbar.valueChanged.connect( self.onScroll )
    self.scrollbar.rangeChanged.connect( self.onRangeChanged )

    self.textChanged.connect( self.perhapsRepaintText )
    self.selectionChanged.connect( self.perhapsRepaintSelection )

    self.computeLineStep()
    self.more = LineCount( self )
    self.setMoreAnchor()


  def setWordWrapColumn( self, column ):

    ## WORKAROUND: Normally we'd use WrapAtWordBoundaryOrAnywhere and leave the
    ## scrollbar the heck alone. But that option doesn't work as advertised in
    ## Qt 4.7 and so we have to use WordWrap instead, and account for the case
    ## where a line doesn't fit in the view's width. Bummer.

    if column > 0:
      self.setLineWrapMode( self.FixedColumnWidth )
      self.setWordWrapMode( QTextOption.WordWrap )
      self.setHorizontalScrollBarPolicy( Qt.ScrollBarAsNeeded )

    else:
      self.setLineWrapMode( self.WidgetWidth )
      self.setWordWrapMode( QTextOption.WrapAtWordBoundaryOrAnywhere )
      self.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )

    self.setLineWrapColumnOrWidth( column )


  @pyqtSlot()
  def perhapsRepaintText( self ):

    ## Right, so we've got a problem: when the text changes but the scrollbar
    ## is not to the bottom, Qt cleverly optimizes things by not repainting
    ## the contents. Only, due to our split screen thingie, we need to
    ## override that behavior. Hence this function.

    if self.atbottom:             return
    if not self.split_scrollback: return

    ## Right, the scrollbar is not at bottom, and the screen is split. So
    ## we repaint indeed, although only the bottom part, since the screen is
    ## split and the top part doesn't change.

    self.update( self.splitBottomRect() )


  @pyqtSlot()
  def perhapsRepaintSelection( self ):

    if self.atbottom:             return
    if not self.split_scrollback: return

    ## We force a repaint of the bottom area in two cases: when the mouse
    ## pointer is in there, and thus may be updating the selection; and
    ## when the selection is all new, in case there was a former selection
    ## to be cleared. Hackish, but functional.

    cursor_pos = self.viewport().mapFromGlobal( QCursor.pos() )

    if self.splitBottomRect().contains( cursor_pos ):
      self.update( self.splitBottomRect() )

    prev_pos, prev_anchor = self.previous_selection

    sel = self.textCursor()

    if sel.position() != prev_pos and sel.anchor() != prev_anchor:
      self.update( self.splitBottomRect() )

    self.previous_selection = sel.position(), sel.anchor()


  def pinSelection( self ):

    ## By default, if the selection is at text end, it expands when more text
    ## is appended. We don't want this. So we need to set up the cursor so it
    ## won't move on insert.

    cur = self.textCursor()

    if not cur.hasSelection():
      return

    ## setKeepPositionOnInsert() only works on position, not anchor, so we need
    ## to ensure the anchor is at the start of the selection and the position
    ## at the end. Feh.

    start, end = cur.selectionStart(), cur.selectionEnd()
    cur.setPosition( start )
    cur.setPosition( end, cur.KeepAnchor )
    cur.setKeepPositionOnInsert( True )

    self.setTextCursor( cur )


  def setConfiguration( self, font_name, font_size, background_color ):

    if background_color:
      stylesheet = u"QTextEdit { background-color: %s }" % background_color
      self.setStyleSheet( stylesheet )

    font = QFont( font_name )

    if font_size:
      font.setPointSize( font_size )

    ## Encourage possible character substitutions to favor vectorial
    ## fixed-pitch fonts:
    font.setFixedPitch( True )
    font.setStyleHint( font.TypeWriter )
    font.setStyleStrategy( font.PreferOutline | font.PreferMatch )

    self.setFont( font )

    self.computeLineStep()


  def computeLineStep( self ):

    self.scrollbar.setSingleStep( self.lineHeight() )
    self.computePageStep()


  def computePageStep( self ):

    if self.split_scrollback:
      pagestep = self.splitY()            - self.scrollbar.singleStep()

    else:
      pagestep = self.viewport().height() - self.scrollbar.singleStep()

    self.scrollbar.setPageStep( pagestep )


  def lineHeight( self ):

    font = self.font()

    ## Generate the layout for one line of text using this font:
    layout = QTextLayout( u"---", font )
    layout.beginLayout()
    line = layout.createLine()
    layout.endLayout()

    ## Obtain the font's leading metric, if positive. (Qt ignores the leading
    ## if it's negative at this point in time.)
    fm = QFontMetrics( font )
    leading = max( fm.leading(), 0 )

    ## WORKAROUND: Qt versions < 4.6 omitted the leading altogether in line
    ## height calculations. We account for this here.
    if qt_version() < ( 4, 6 ):
      leading = 0

    ## This here is the actual line height for this font. Phew.
    return int( line.height() + leading )


  def setPaging( self, is_paging ):

    self.paging = is_paging


  def setSplitScrollback( self, split_scrollback ):

    self.split_scrollback = split_scrollback

    self.computePageStep()
    self.setMoreAnchor()

    if not self.atbottom:
      self.update()


  @pyqtSlot( int )
  def onScroll( self, pos ):

    ## Scrollbar values are not reliable when the widget is not visible:
    if not self.isVisible():
      return

    self.atbottom = ( pos == self.scrollbar.maximum() )

    ## When the user moves back to the bottom of the view, paging is reset:

    if self.atbottom:

      if self.next_page_position == -1:
        self.next_page_position = self.nextPageForPos( pos )

    else:
      self.next_page_position = -1

    if platformSpecific.should_repaint_on_scroll:
      self.update()

    self.more.setLineCount( self.linesRemaining() )


  def nextPageForPos( self, pos ):

    if pos == 0:
      height = int( self.document().documentLayout().documentSize().height() )

    else:
      height = pos + self.viewport().height()

    l, t, r, b = self.getContentsMargins()

    return height - self.scrollbar.singleStep() - t - b - 1


  def linesRemaining( self ):

    sb = self.scrollbar
    max, val, step = sb.maximum(), sb.value(), sb.singleStep()

    return ( max - val + step - 1 ) / step


  def remapMouseEvent( self, e ):

    if self.atbottom or not self.split_scrollback:
      return e

    if e.y() <= self.splitY():
      return e

    height  = self.viewport().height()

    y = e.y() + self.document().size().height() - height - self.scrollbar.value()

    e = QMouseEvent( e.type(), QPoint( e.x(), y ), e.globalPos(),
                           e.button(), e.buttons(), e.modifiers() )
    return e


  def mouseMoveEvent( self, e ):

    return QTextEdit.mouseMoveEvent( self, self.remapMouseEvent( e ) )


  def mousePressEvent( self, e ):

    ## WORKAROUND: We need to clear the selection before the click, so the
    ## drag and drop event that may otherwise follow doesn't get confused
    ## by our remapped mouse coordinates. But doing so requires calling
    ## setTextCursor(), and that method, itself, calls ensureCursorVisible(),
    ## causing an unwanted scrolling of the viewport. So we 'pin down' the
    ## viewport by saving the scrollbar's value and then restoring it, while
    ## blocking its signals.

    block = self.scrollbar.blockSignals( True )
    val   = self.scrollbar.value()

    cur = self.textCursor()

    if cur.hasSelection() and e.buttons() & Qt.LeftButton:

      cur = self.cursorForPosition( e.pos() )
      self.setTextCursor( cur )

    res = QTextEdit.mousePressEvent( self, self.remapMouseEvent( e ) )

    self.scrollbar.setValue( val )
    self.scrollbar.blockSignals( block )

    return res


  def mouseReleaseEvent( self, e ):

    ## WORKAROUND: The same workaround as above is used here. Without it, Qt's
    ## calling of ensureCursorVisible() while handling the mouse release event
    ## causes the viewport to scroll if the mouse is released in the split
    ## area.

    block = self.scrollbar.blockSignals( True )
    val   = self.scrollbar.value()

    res = QTextEdit.mouseReleaseEvent( self, self.remapMouseEvent( e ) )

    self.pinSelection()

    self.scrollbar.setValue( val )
    self.scrollbar.blockSignals( block )

    return res


  def mouseDoubleClickEvent( self, e ):

    return QTextEdit.mouseDoubleClickEvent( self, self.remapMouseEvent( e ) )


  def splitY( self ):

    return int( self.viewport().height() * self.SPLIT_FACTOR )


  def splitTopRect( self ):

    w = self.viewport().width()

    return QRect( 0, 0, w, self.splitY() )


  def splitBottomRect( self ):

    w = self.viewport().width()
    h = self.viewport().height()

    return QRect( 0, self.splitY() + 1, w, h )


  def paintEvent( self, e ):

    if self.atbottom or not self.split_scrollback:

      QTextEdit.paintEvent( self, e )
      return

    ## Draw the top half of the viewport if necessary.

    top_r = e.rect().intersected( self.splitTopRect() )

    if not top_r.isEmpty():
      QTextEdit.paintEvent( self, QPaintEvent( top_r ) )

    ## Likewise the bottom half.
    ## Create painter.

    p = QPainter( self.viewport() )

    ## Draw separation line.

    split_y = self.splitY()
    width   = self.viewport().width()
    height  = self.viewport().height()

    if e.rect().contains( e.rect().left(), split_y ):

      p.setPen( QApplication.instance().palette().color( QPalette.Window ) )
      p.drawLine( 0, split_y, width, split_y )

    ## Clip painter.

    clip_r = e.rect().intersected( self.splitBottomRect() )

    if clip_r.isEmpty():
      return

    doc        = self.document()
    doc_height = doc.size().height()

    p.setClipRect( clip_r )
    p.translate( 0, -doc_height + height )

    ## Draw the bottom of the document on the bottom half of the viewport.

    ctx      = QAbstractTextDocumentLayout.PaintContext()
    ctx.clip = QRectF( clip_r.translated( 0, doc_height - height ) )

    cur = self.textCursor()

    palette = self.palette()

    focus  = ( QApplication.instance().focusWidget() is self )
    cgroup = not focus and QPalette.Inactive or QPalette.Active

    if cur.hasSelection():

      sel        = QAbstractTextDocumentLayout.Selection()
      sel.cursor = cur
      sel.format.setBackground( palette.brush( cgroup, QPalette.Highlight) )
      sel.format.setForeground( palette.brush( cgroup, \
                                               QPalette.HighlightedText ) )

      ctx.selections = [ sel ]

    doc.documentLayout().draw( p, ctx )


  @pyqtSlot()
  def pingPage( self ):

    ## Paging implementation:

    if self.atbottom and self.paging:
      self.next_page_position = self.nextPageForPos( self.scrollbar.value() )


  def moveScrollbarToBottom( self ):

    max = self.scrollbar.maximum()

    if self.scrollbar.value() == max:

      ## Trigger onScroll event even if not moving:
      self.onScroll( max )

    else:
      self.scrollbar.setValue( max )


  def moveScrollbarToTop( self ):

    self.scrollbar.setValue( self.scrollbar.minimum() )


  @pyqtSlot( int, int )
  def onRangeChanged( self, min, max ):

    ## 'min' and 'max' are the values emitted by the scrollbar's 'rangeChanged'
    ## signal.

    pos = self.scrollbar.value()

    ## Handle rare case where the view got smaller, for instance if the user
    ## switches to a smaller font:

    if pos > max:
      return

    if self.next_page_position > self.nextPageForPos( max ):
      self.next_page_position = -1

    if pos != max and self.atbottom:  ## Do we need to scroll?

      if self.paging and self.next_page_position != -1:
        ## Case 1: We are paging and have a valid next page break.

        if max > self.next_page_position:
          ## Case 1.1: Scrolling would move us past the next page break.

          if pos != self.next_page_position:
            self.scrollbar.setValue( self.next_page_position )

          else:  ## If the scrollbar value shouldn't change even though we
                 ## switched to paging mode, trigger scroll event manually.
            self.onScroll( pos )

        else:
          ## Case 1.2: Not at page break yet. Proceed as usual for now.
          self.moveScrollbarToBottom()

      else:
        ## Case 2: We are not paging. Proceed as usual.
        self.moveScrollbarToBottom()

    self.more.setLineCount( self.linesRemaining() )


  def contextMenuEvent( self, e ):

    menu = self.createStandardContextMenu()
    menu.exec_( e.globalPos() )
    sip.delete( menu )


  def stepUp( self ):

    self.scrollbar.triggerAction( QScrollBar.SliderSingleStepSub )


  def stepDown( self ):

    self.scrollbar.triggerAction( QScrollBar.SliderSingleStepAdd )


  def pageUp( self ):

    self.computePageStep()
    self.scrollbar.triggerAction( QScrollBar.SliderPageStepSub )


  def pageDown( self ):

    self.computePageStep()
    self.scrollbar.triggerAction( QScrollBar.SliderPageStepAdd )


  def resizeEvent( self, e ):

    res = QTextEdit.resizeEvent( self, e )

    self.onRangeChanged( self.scrollbar.minimum(), self.scrollbar.maximum() )
    self.setMoreAnchor()

    return res


  def ensureCursorVisible( self ):

    ## Note: this method is never called from inside Qt, for instance during
    ## the mousePressEvent above, because in the underlying QTextEdit this
    ## method isn't declared as virtual. Bummer.
    ## It is only used in our own code to ensure cursor visibility in case of
    ## split scrollback.

    QTextEdit.ensureCursorVisible( self )

    if self.split_scrollback and not self.atbottom:

      rect  = self.cursorRect()
      cur_y = self.viewport().mapToParent( rect.bottomLeft() ).y()

      split_y = self.splitY()

      if cur_y > split_y:

        ## Okay, the cursor is hidden by our scrollback overlay. Let us scroll
        ## some more so it is visible.

        y = self.scrollbar.value()
        self.scrollbar.setValue( y + cur_y - split_y - 1 )


  def setMoreAnchor( self ):

    x = self.viewport().width()

    if self.split_scrollback:
      y = self.splitY()

    else:
      y = self.viewport().height()

    self.more.setAnchor( x, y )


  def __del__( self ):

    self.scrollbar = None
