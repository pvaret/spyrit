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
## TabIconBlinker.py
##
## Implements the tab icon blinking code.
##


from PyQt4.QtGui  import QIcon
from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import QTimeLine



class LED:

  def __init__( self ):

    self.CONNECTED_UNLIT    = QIcon( ":/icon/unlit_green_led" )
    self.CONNECTED_LIT      = QIcon( ":/icon/lit_green_led" )
    self.DISCONNECTED_UNLIT = QIcon( ":/icon/unlit_red_led" )
    self.DISCONNECTED_LIT   = QIcon( ":/icon/lit_red_led" )


  def select( self, connected, lit ):

    if connected:
      return lit and self.CONNECTED_LIT or self.CONNECTED_UNLIT

    else:
      return lit and self.DISCONNECTED_LIT or self.DISCONNECTED_UNLIT


class TabIconBlinker( QObject ):

  def __init__( self, world, tab ):

    QObject.__init__( self, parent=tab )

    self.led   = LED()
    self.tab   = tab
    self.world = world

    self.visible = True

    self.tab.tabChanged.connect( self.onTabChanged )

    self.blinker = QTimeLine( 200, self ) ## ms
    self.blinker.setFrameRange( 0, 3 )
    self.blinker.frameChanged.connect( self.iconBlink )
    self.blinker.finished.connect( self.steadyIcon )


  def startIconBlink( self, chunk ):

    ## Don't blink if already blinking:

    if self.blinker.state() != QTimeLine.NotRunning:
      return

    self.blinker.start()


  @pyqtSlot( int )
  def iconBlink( self, frame ):

    if not self.world:
      return

    led = self.led.select( connected = self.world.isConnected(),
                           lit       = ( frame % 2 != 1 ) )
    self.tab.setTabIcon( led )


  @pyqtSlot()
  def steadyIcon( self ):

    if self.blinker.state() == QTimeLine.Running:
      return

    if not self.world:
      return

    led = self.led.select( connected = self.world.isConnected(),
                           lit       = not self.visible )
    self.tab.setTabIcon( led )


  @pyqtSlot( bool )
  def onTabChanged( self, is_now_visible ):

    self.visible = is_now_visible

    if is_now_visible:
      self.steadyIcon()
