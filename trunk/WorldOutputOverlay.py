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
## WorldOutputOverlay.py
##
## This file contains the WorldOutputOverlay class, which implements the logic
## for the fixed overlay that is displayed when the user scrolls back.
##


from localqt import *

from WorldBaseOutputUI import WorldBaseOutputUI


class WorldOutputOverlay ( WorldBaseOutputUI ):
 
  def __init__( s, outputui ):

    WorldBaseOutputUI.__init__( s, outputui )

    s.outputui = outputui
    s.outputui.installEventFilter( s )

    s.setLineWrapMode( QtGui.QTextEdit.NoWrap )  ## TODO: Allow manual wrap 
                                                 ## calculation.
    s.setDocument( outputui.document() )

    s.bar = QtGui.QWidget( s )
    s.bar.setStyleSheet( "QWidget { background-color: palette(window) }" )

    connect( s.verticalScrollBar(), SIGNAL( "rangeChanged( int, int )" ),
                                             s.ensureAtBottom )
    s.hide()


  def eventFilter( s, widget, e ):

    if e.type() == QtCore.QEvent.Resize:

      QtCore.QTimer.singleShot( 0, s.onResize )

    return QtCore.QObject.eventFilter( s, widget, e )


  def onResize( s ):

    if s.isVisible(): s.computeSizes()


  def computeSizes( s ):

    FACTOR = 4
    
    width  = s.outputui.viewport().width()
    height = s.outputui.viewport().height() / FACTOR

    x = 0
    y = s.outputui.viewport().height() - height

    frame_x = s.geometry().width() - s.viewport().geometry().width()
    frame_y = s.geometry().height() - s.viewport().geometry().height()

    s.bar.setGeometry( 0, 0, width+frame_x, 1 )

    s.setGeometry( x, y+frame_y, width+frame_x, height )


  def showEvent( s, e ):

    s.computeSizes()

    return WorldBaseOutputUI.showEvent( s, e )


  def mousePressEvent( s, e ):

    e.ignore()


  def mouseReleaseEvent( s, e ):

    e.ignore()


  def mouseDoubleClickEvent( s, e ):

    e.ignore()


  def mouseMoveEvent( s, e ):

    e.ignore()


  def tabletEvent( s, e ):

    e.ignore()


  def wheelEvent( s, e ):

    return s.outputui.wheelEvent( e )


  def keyPressEvent( s, e ):

    return s.outputui.keyPressEvent( e )


  def keyReleaseEvent( s, e ):

    return s.outputui.keyReleaseEvent( e )


  def contextMenuEvent( s, e ):

    return s.outputui.contextMenuEvent( e )


  def ensureAtBottom( s, min, max ):

    scrollbar = s.verticalScrollBar()

    if scrollbar.value() != max:
      scrollbar.setValue( max )


  def cleanupBeforeDelete( s ):

    del s.bar
    s.setDocument( None )
