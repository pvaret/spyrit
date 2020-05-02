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
## TabIconBlinker.py
##
## Implements the tab icon blinking code.
##


from PyQt5.QtGui  import QIcon
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QTimeLine



class LED:

  def __init__( self ):

    self.ON_UNLIT  = QIcon( ":/icon/unlit_green_led" )
    self.ON_LIT    = QIcon( ":/icon/lit_green_led" )
    self.OFF_UNLIT = QIcon( ":/icon/unlit_red_led" )
    self.OFF_LIT   = QIcon( ":/icon/lit_red_led" )


  def select( self, on, lit ):

    if on:
      return self.ON_LIT if lit else self.ON_UNLIT

    else:
      return self.OFF_LIT if lit else self.OFF_UNLIT


class TabIconBlinker( QObject ):

  def __init__( self, tab ):

    QObject.__init__( self, parent=tab )

    self.led     = LED()
    self.tab     = tab
    self.is_on   = False
    self.visible = True

    self.tab.tabChanged.connect( self.onTabChanged )

    self.blinker = QTimeLine( 50, self ) ## ms
    self.blinker.setFrameRange( 0, 1 )
    self.blinker.frameChanged.connect( self.iconBlink )
    self.blinker.finished.connect( self.steadyIcon )


  def startIconBlink( self ):

    if self.blinker.state() == QTimeLine.NotRunning:
      self.blinker.start()


  @pyqtSlot( int )
  def iconBlink( self, frame ):

    led = self.led.select( on  = self.is_on,
                           lit = ( frame % 2 == 0 ) )
    self.tab.setTabIcon( led )


  @pyqtSlot()
  def steadyIcon( self ):

    if self.blinker.state() == QTimeLine.Running:
      return

    led = self.led.select( on  = self.is_on,
                           lit = not self.visible )
    self.tab.setTabIcon( led )


  @pyqtSlot( bool )
  def onTabChanged( self, is_now_visible ):

    self.visible = is_now_visible

    if is_now_visible:
      self.steadyIcon()


  @pyqtSlot( bool )
  def setLedOn( self, is_on=True ):

    if is_on and not self.is_on:
      self.is_on = True
      self.startIconBlink()


  @pyqtSlot( bool )
  def setLedOff( self, is_off=True ):

    if is_off and self.is_on:
      self.is_on = False
      self.startIconBlink()
