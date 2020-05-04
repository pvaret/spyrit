# -*- coding: utf-8 -*-

## Copyright (c) 2007-2020 Pascal Varet <p.varet@gmail.com>
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
## QTextEditWithClickableLinks.py
##
## This file contains the QTextEditWithClickableLinks class, which implements
## the same interaction between mouse and links as in QTextBrowser.
##


from PyQt5.QtCore    import Qt
from PyQt5.QtCore    import QUrl
from PyQt5.QtCore    import QPoint
from PyQt5.QtCore    import pyqtSignal
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui     import QDesktopServices


class QTextEditWithClickableLinks( QTextEdit ):

  linkClicked = pyqtSignal( str )

  def __init__( self, parent=None ):

    super( QTextEditWithClickableLinks, self ).__init__( parent )

    self.previous_anchor = ""
    self.click_pos = QPoint()
    self.click_link = ""

    self.setMouseTracking( True )

    flags = self.textInteractionFlags()
    flags |= Qt.LinksAccessibleByMouse
    self.setTextInteractionFlags( flags )

    self.linkClicked.connect( self.onLinkClicked )


  def mouseMoveEvent( self, e ):

    maybe_anchor = self.anchorAt( e.pos() )

    if maybe_anchor != self.previous_anchor:

      if maybe_anchor:
        self.viewport().setCursor( Qt.PointingHandCursor )

      else:
        self.viewport().setCursor( Qt.ArrowCursor )

      self.previous_anchor = maybe_anchor

    return super( QTextEditWithClickableLinks, self ).mouseMoveEvent( e )


  def mousePressEvent( self, e ):

    self.click_pos = e.pos()
    self.click_link = self.anchorAt( e.pos() )

    return super( QTextEditWithClickableLinks, self ).mousePressEvent( e )


  def mouseReleaseEvent( self, e ):

    if ( e.pos() - self.click_pos ).manhattanLength() <= 3:
      if self.click_link and self.click_link == self.anchorAt( e.pos() ):
        self.linkClicked.emit( self.click_link )

    return super( QTextEditWithClickableLinks, self ).mouseReleaseEvent( e )


  def onLinkClicked( self, href ):

    QDesktopServices.openUrl( QUrl( href ) )
